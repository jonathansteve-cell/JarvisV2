"""
Jarvis V2 - API Key Validator & Health Checker
===============================================
Validates API keys and monitors API health.

Features:
- Real-time API key validation
- Health monitoring with status dashboard
- Automatic failover detection
- Performance metrics
- Detailed error reporting
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Validation result status."""
    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    RATE_LIMITED = "rate_limited"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"


@dataclass
class ValidationResult:
    """Result of API key validation."""
    provider: str
    status: ValidationStatus
    message: str
    latency_ms: float = 0
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    quota_remaining: Optional[int] = None
    quota_limit: Optional[int] = None


@dataclass
class HealthMetrics:
    """API health metrics over time."""
    provider: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_latency_ms: float = 0
    p95_latency_ms: float = 0
    p99_latency_ms: float = 0
    uptime_percentage: float = 100.0
    last_downtime: Optional[datetime] = None
    consecutive_failures: int = 0


class APIValidator:
    """
    Comprehensive API validation and health monitoring.

    Usage:
        validator = APIValidator()
        result = validator.validate_groq("your-api-key")
        print(result.status, result.message)
    """

    # Validation endpoints for each provider
    VALIDATION_ENDPOINTS = {
        "groq": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "method": "POST",
            "headers": lambda key: {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            "body": {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 5,
            },
            "success_codes": [200],
            "error_codes": {
                401: "Invalid API key",
                429: "Rate limited - try again later",
                500: "Groq server error",
            },
        },
        "openai": {
            "url": "https://api.openai.com/v1/models",
            "method": "GET",
            "headers": lambda key: {
                "Authorization": f"Bearer {key}",
            },
            "success_codes": [200],
            "error_codes": {
                401: "Invalid API key",
                429: "Rate limited",
            },
        },
        "anthropic": {
            "url": "https://api.anthropic.com/v1/messages",
            "method": "POST",
            "headers": lambda key: {
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            "body": {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 5,
                "messages": [{"role": "user", "content": "hi"}],
            },
            "success_codes": [200],
            "error_codes": {
                401: "Invalid API key",
                429: "Rate limited",
            },
        },
        "spotify": {
            "url": "https://api.spotify.com/v1/me",
            "method": "GET",
            "headers": lambda key: {
                "Authorization": f"Bearer {key}",
            },
            "success_codes": [200],
            "error_codes": {
                401: "Invalid or expired access token",
                403: "Insufficient permissions",
                429: "Rate limited",
            },
        },
        "twilio": {
            "url": "https://api.twilio.com/2010-04-01/Accounts",
            "method": "GET",
            "auth": lambda sid, token: (sid, token),
            "success_codes": [200],
            "error_codes": {
                401: "Invalid credentials",
            },
        },
        "home_assistant": {
            "url": "{base_url}/api/",
            "method": "GET",
            "headers": lambda key: {
                "Authorization": f"Bearer {key}",
            },
            "success_codes": [200],
            "error_codes": {
                401: "Invalid token",
                404: "Home Assistant not found at this URL",
            },
        },
    }

    def __init__(self, metrics_dir: Optional[Path] = None):
        self.metrics_dir = metrics_dir or Path("data/api_metrics")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        # Load historical metrics
        self._metrics: dict[str, HealthMetrics] = {}
        self._load_metrics()

    def _load_metrics(self):
        """Load historical health metrics."""
        metrics_file = self.metrics_dir / "health_metrics.json"
        if metrics_file.exists():
            try:
                data = json.loads(metrics_file.read_text())
                for provider, metrics in data.items():
                    self._metrics[provider] = HealthMetrics(
                        provider=provider,
                        **metrics,
                    )
            except Exception as e:
                logger.warning(f"Failed to load metrics: {e}")

    def _save_metrics(self):
        """Save health metrics to disk."""
        metrics_file = self.metrics_dir / "health_metrics.json"
        data = {}
        for provider, metrics in self._metrics.items():
            data[provider] = {
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "avg_latency_ms": metrics.avg_latency_ms,
                "p95_latency_ms": metrics.p95_latency_ms,
                "p99_latency_ms": metrics.p99_latency_ms,
                "uptime_percentage": metrics.uptime_percentage,
                "consecutive_failures": metrics.consecutive_failures,
            }
        metrics_file.write_text(json.dumps(data, indent=2))

    def _update_metrics(self, provider: str, success: bool, latency_ms: float):
        """Update health metrics for a provider."""
        if provider not in self._metrics:
            self._metrics[provider] = HealthMetrics(provider=provider)

        metrics = self._metrics[provider]
        metrics.total_requests += 1

        if success:
            metrics.successful_requests += 1
            metrics.consecutive_failures = 0
        else:
            metrics.failed_requests += 1
            metrics.consecutive_failures += 1
            metrics.last_downtime = datetime.now()

        # Update latency (running average)
        if metrics.total_requests == 1:
            metrics.avg_latency_ms = latency_ms
        else:
            metrics.avg_latency_ms = (
                (metrics.avg_latency_ms * (metrics.total_requests - 1) + latency_ms)
                / metrics.total_requests
            )

        # Update uptime
        if metrics.total_requests > 0:
            metrics.uptime_percentage = (
                metrics.successful_requests / metrics.total_requests * 100
            )

        self._save_metrics()

    def validate_groq(self, api_key: str) -> ValidationResult:
        """Validate a Groq API key."""
        return self._validate_generic("groq", api_key)

    def validate_openai(self, api_key: str) -> ValidationResult:
        """Validate an OpenAI API key."""
        return self._validate_generic("openai", api_key)

    def validate_anthropic(self, api_key: str) -> ValidationResult:
        """Validate an Anthropic API key."""
        return self._validate_generic("anthropic", api_key)

    def validate_spotify(self, access_token: str) -> ValidationResult:
        """Validate a Spotify access token."""
        return self._validate_generic("spotify", access_token)

    def validate_twilio(self, account_sid: str, auth_token: str) -> ValidationResult:
        """Validate Twilio credentials."""
        import requests

        config = self.VALIDATION_ENDPOINTS.get("twilio")
        if not config:
            return ValidationResult(
                provider="twilio",
                status=ValidationStatus.UNKNOWN,
                message="Provider not configured",
            )

        start_time = time.time()

        try:
            auth = config["auth"](account_sid, auth_token)
            response = requests.get(
                config["url"],
                auth=auth,
                timeout=10,
            )

            latency = (time.time() - start_time) * 1000

            if response.status_code in config["success_codes"]:
                self._update_metrics("twilio", True, latency)
                return ValidationResult(
                    provider="twilio",
                    status=ValidationStatus.VALID,
                    message="Twilio credentials are valid",
                    latency_ms=latency,
                )
            else:
                error_msg = config["error_codes"].get(
                    response.status_code,
                    f"HTTP {response.status_code}",
                )
                self._update_metrics("twilio", False, latency)
                return ValidationResult(
                    provider="twilio",
                    status=ValidationStatus.INVALID,
                    message=error_msg,
                    latency_ms=latency,
                )

        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self._update_metrics("twilio", False, latency)
            return ValidationResult(
                provider="twilio",
                status=ValidationStatus.NETWORK_ERROR,
                message=str(e),
                latency_ms=latency,
            )

    def validate_home_assistant(self, url: str, token: str) -> ValidationResult:
        """Validate Home Assistant connection."""
        import requests

        start_time = time.time()

        try:
            response = requests.get(
                f"{url}/api/",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )

            latency = (time.time() - start_time) * 1000

            if response.status_code == 200:
                self._update_metrics("home_assistant", True, latency)
                return ValidationResult(
                    provider="home_assistant",
                    status=ValidationStatus.VALID,
                    message="Home Assistant connection successful",
                    latency_ms=latency,
                    details={"version": response.json().get("version", "unknown")},
                )
            else:
                self._update_metrics("home_assistant", False, latency)
                return ValidationResult(
                    provider="home_assistant",
                    status=ValidationStatus.INVALID,
                    message=f"HTTP {response.status_code}",
                    latency_ms=latency,
                )

        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self._update_metrics("home_assistant", False, latency)
            return ValidationResult(
                provider="home_assistant",
                status=ValidationStatus.NETWORK_ERROR,
                message=str(e),
                latency_ms=latency,
            )

    def _validate_generic(self, provider: str, api_key: str) -> ValidationResult:
        """Generic API key validation."""
        import requests

        config = self.VALIDATION_ENDPOINTS.get(provider)
        if not config:
            return ValidationResult(
                provider=provider,
                status=ValidationStatus.UNKNOWN,
                message="Provider not configured",
            )

        start_time = time.time()

        try:
            headers = config["headers"](api_key)
            body = config.get("body")

            if config["method"] == "GET":
                response = requests.get(
                    config["url"],
                    headers=headers,
                    timeout=10,
                )
            else:
                response = requests.post(
                    config["url"],
                    headers=headers,
                    json=body,
                    timeout=10,
                )

            latency = (time.time() - start_time) * 1000

            if response.status_code in config["success_codes"]:
                self._update_metrics(provider, True, latency)

                # Extract quota info if available
                quota_remaining = None
                quota_limit = None
                if "x-ratelimit-remaining" in response.headers:
                    quota_remaining = int(response.headers["x-ratelimit-remaining"])
                if "x-ratelimit-limit" in response.headers:
                    quota_limit = int(response.headers["x-ratelimit-limit"])

                return ValidationResult(
                    provider=provider,
                    status=ValidationStatus.VALID,
                    message="API key is valid",
                    latency_ms=latency,
                    quota_remaining=quota_remaining,
                    quota_limit=quota_limit,
                )
            else:
                error_msg = config["error_codes"].get(
                    response.status_code,
                    f"HTTP {response.status_code}",
                )
                self._update_metrics(provider, False, latency)

                status = ValidationStatus.INVALID
                if response.status_code == 429:
                    status = ValidationStatus.RATE_LIMITED

                return ValidationResult(
                    provider=provider,
                    status=status,
                    message=error_msg,
                    latency_ms=latency,
                )

        except requests.exceptions.Timeout:
            latency = (time.time() - start_time) * 1000
            self._update_metrics(provider, False, latency)
            return ValidationResult(
                provider=provider,
                status=ValidationStatus.NETWORK_ERROR,
                message="Request timed out",
                latency_ms=latency,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self._update_metrics(provider, False, latency)
            return ValidationResult(
                provider=provider,
                status=ValidationStatus.NETWORK_ERROR,
                message=str(e),
                latency_ms=latency,
            )

    def get_health_metrics(self, provider: str) -> Optional[HealthMetrics]:
        """Get health metrics for a provider."""
        return self._metrics.get(provider)

    def get_all_metrics(self) -> dict[str, HealthMetrics]:
        """Get health metrics for all providers."""
        return self._metrics.copy()

    def is_healthy(self, provider: str) -> bool:
        """Check if a provider is healthy."""
        metrics = self._metrics.get(provider)
        if not metrics:
            return True  # Unknown = assume healthy
        return (
            metrics.uptime_percentage >= 95.0
            and metrics.consecutive_failures < 3
        )

    def get_status_report(self) -> str:
        """Get a formatted status report."""
        lines = ["=" * 60]
        lines.append("  API HEALTH REPORT")
        lines.append("=" * 60)
        lines.append("")

        for provider, metrics in self._metrics.items():
            status = "✅" if self.is_healthy(provider) else "❌"
            lines.append(f"  {status} {provider.upper()}")
            lines.append(f"     Uptime: {metrics.uptime_percentage:.1f}%")
            lines.append(f"     Avg Latency: {metrics.avg_latency_ms:.0f}ms")
            lines.append(f"     Total Requests: {metrics.total_requests}")
            lines.append(f"     Failures: {metrics.failed_requests}")
            if metrics.consecutive_failures > 0:
                lines.append(f"     ⚠️  Consecutive Failures: {metrics.consecutive_failures}")
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)


def validate_all_keys() -> dict[str, ValidationResult]:
    """Validate all API keys from environment."""
    import os

    validator = APIValidator()
    results = {}

    # Groq
    groq_key = os.getenv("GROQ_API_KEY", "")
    if groq_key and not groq_key.startswith("your_"):
        results["groq"] = validator.validate_groq(groq_key)

    # OpenAI
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key and not openai_key.startswith("your_"):
        results["openai"] = validator.validate_openai(openai_key)

    # Anthropic
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if anthropic_key and not anthropic_key.startswith("your_"):
        results["anthropic"] = validator.validate_anthropic(anthropic_key)

    # Spotify
    spotify_token = os.getenv("SPOTIFY_ACCESS_TOKEN", "")
    if spotify_token and not spotify_token.startswith("your_"):
        results["spotify"] = validator.validate_spotify(spotify_token)

    # Twilio
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "")
    if twilio_sid and twilio_token and not twilio_sid.startswith("your_"):
        results["twilio"] = validator.validate_twilio(twilio_sid, twilio_token)

    # Home Assistant
    ha_url = os.getenv("HOME_ASSISTANT_URL", "")
    ha_token = os.getenv("HOME_ASSISTANT_TOKEN", "")
    if ha_url and ha_token and not ha_token.startswith("your_"):
        results["home_assistant"] = validator.validate_home_assistant(ha_url, ha_token)

    return results
