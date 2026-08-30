# Jarvis V2 - Complete API Configuration Guide

## 🚀 Quick Start

### Option 1: Interactive Setup Wizard (Recommended)
```bash
python -m core.api_setup_wizard
```

This will guide you through setting up each API integration step-by-step.

### Option 2: Manual Configuration
Edit the `.env` file in your JarvisV2 directory:

```bash
# Copy the template
cp .env.example .env

# Edit with your credentials
nano .env  # or use any text editor
```

### Option 3: One-Click Setup Script
```bash
python setup_apis.py
```

---

## 🔑 API Keys Overview

### Required for Core Features
| API | Purpose | Get Key At |
|-----|---------|------------|
| **Groq AI** | AI conversations | https://console.groq.com |

### Optional Integrations
| API | Purpose | Get Key At |
|-----|---------|------------|
| **OpenAI** | Alternative AI (GPT-4) | https://platform.openai.com |
| **Anthropic** | Alternative AI (Claude) | https://console.anthropic.com |
| **Email** | Send/receive emails | Gmail App Passwords |
| **Twilio** | WhatsApp & Phone | https://console.twilio.com |
| **Spotify** | Music control | https://developer.spotify.com |
| **Home Assistant** | Smart home | Your HA instance |

---

## 📝 Detailed Setup Instructions

### 1. Groq AI (Recommended - Fastest)

**Why Groq?**
- Fastest inference speeds
- Free tier available
- Llama 3.3 70B model
- No credit card required

**Setup Steps:**
1. Go to https://console.groq.com
2. Sign up with email or GitHub
3. Go to "API Keys" in the left sidebar
4. Click "Create API Key"
5. Copy the key (starts with `gsk_`)
6. Add to `.env`:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```

**Rate Limits (Free Tier):**
- 30 requests/minute
- 15,000 tokens/minute

---

### 2. OpenAI (Alternative - Most Capable)

**Setup Steps:**
1. Go to https://platform.openai.com
2. Sign up and add billing
3. Go to "API Keys"
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)
6. Add to `.env`:
   ```
   OPENAI_API_KEY=sk-your_key_here
   ```

**Rate Limits:**
- Varies by tier
- Pay-as-you-go pricing

---

### 3. Anthropic (Alternative - Best for Safety)

**Setup Steps:**
1. Go to https://console.anthropic.com
2. Sign up and add billing
3. Go to "API Keys"
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-`)
6. Add to `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-your_key_here
   ```

---

### 4. Email (Gmail)

**Setup Steps:**
1. Enable 2-Factor Authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" and your device
4. Click "Generate"
5. Copy the 16-character password
6. Add to `.env`:
   ```
   JARVIS_EMAIL_ADDRESS=your.email@gmail.com
   JARVIS_EMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
   JARVIS_SMTP_HOST=smtp.gmail.com
   JARVIS_SMTP_PORT=587
   JARVIS_IMAP_HOST=imap.gmail.com
   ```

**Important:**
- Use App Password, NOT your regular password
- Requires 2FA enabled on Google account

---

### 5. Twilio (WhatsApp & Phone)

**Setup Steps:**
1. Go to https://console.twilio.com
2. Sign up for free account ($15 trial credit)
3. Find your credentials on the dashboard:
   - Account SID (starts with `AC`)
   - Auth Token
4. Get a phone number:
   - Go to Phone Numbers → Buy a Number
   - Select a number with SMS capability
5. For WhatsApp:
   - Go to Messaging → Try it out → Send a WhatsApp message
   - Follow sandbox setup instructions
6. Add to `.env`:
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_FROM_PHONE=+1234567890
   TWILIO_FROM_WHATSAPP=whatsapp:+14155238886
   ```

**Rate Limits:**
- Free trial: $15 credit
- Pay-as-you-go after trial

---

### 6. Spotify (Music Control)

**Setup Steps:**
1. Go to https://developer.spotify.com/dashboard
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in:
   - App name: "Jarvis V2"
   - Description: "Desktop AI Assistant"
   - Redirect URI: `http://localhost:8888/callback`
5. Click "Save"
6. Copy Client ID and Client Secret
7. Add to `.env`:
   ```
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
   ```

**Required Scopes:**
- user-read-playback-state
- user-modify-playback-state
- user-read-currently-playing
- playlist-read-private

---

### 7. Home Assistant (Smart Home)

**Setup Steps:**
1. Open your Home Assistant dashboard
2. Click on your user profile (bottom left)
3. Scroll to "Long-Lived Access Tokens"
4. Click "Create Token"
5. Give it a name: "Jarvis V2"
6. Copy the token immediately (shown only once!)
7. Add to `.env`:
   ```
   HOME_ASSISTANT_URL=http://homeassistant.local:8123
   HOME_ASSISTANT_TOKEN=your_long_lived_token
   ```

**Requirements:**
- Home Assistant must be accessible on your network
- Token must have appropriate permissions

---

## 🔒 Security Best Practices

### 1. Never Commit .env to Git
The `.env` file is already in `.gitignore`. Never share it publicly.

### 2. Use App Passwords
For email, use App Passwords instead of your main password.

### 3. Rotate Keys Regularly
Change API keys every 90 days for security.

### 4. Use Environment Variables
Never hardcode API keys in your source code.

### 5. Enable 2FA
Enable 2-Factor Authentication on all API provider accounts.

### 6. Monitor Usage
Regularly check your API usage dashboards for unexpected activity.

---

## 🧪 Testing Your Configuration

### Validate All APIs
```bash
python -m core.api_validator
```

### Test Specific API
```bash
# Test Groq
python -c "from core.api_validator import APIValidator; v = APIValidator(); print(v.validate_groq('your_key'))"

# Test all configured APIs
python -c "from core.api_validator import validate_all_keys; print(validate_all_keys())"
```

### Run Health Check
```bash
python -c "from core.api_manager import get_api_status_report; print(get_api_status_report())"
```

---

## 📊 API Status Dashboard

### View Status
```bash
python -c "from core.api_manager import get_api_status_report; print(get_api_status_report())"
```

### Example Output:
```
============================================================
  JARVIS V2 - API STATUS REPORT
============================================================

  ✅ GROQ                   Configured: ✓  Valid: ✓
     API key is valid
  ⬜ OPENAI                 Configured: ✗  Valid: ✗
  ⬜ ANTHROPIC              Configured: ✗  Valid: ✗
  ✅ TWILIO                 Configured: ✓  Valid: ✓
     Twilio credentials are valid
  ⬜ SPOTIFY                Configured: ✗  Valid: ✗
  ✅ HOME_ASSISTANT         Configured: ✓  Valid: ✓
     Home Assistant connection successful

============================================================
```

---

## 🔄 Rate Limiting

Jarvis V2 includes built-in rate limiting to prevent API abuse:

| Provider | Requests/Minute | Tokens/Minute |
|----------|-----------------|---------------|
| Groq | 30 | 15,000 |
| OpenAI | 60 | 40,000 |
| Anthropic | 50 | 30,000 |
| Spotify | 100 | - |
| Twilio | 100 | - |
| Home Assistant | 200 | - |

**Automatic Handling:**
- Requests are queued when rate limit is approached
- Exponential backoff on 429 errors
- Automatic retry on transient failures

---

## 🛡️ Error Handling

### Common Errors and Solutions

**"Invalid API Key"**
- Double-check the key in `.env`
- Make sure there are no extra spaces
- Regenerate the key if needed

**"Rate Limited"**
- Wait a minute and try again
- Reduce request frequency
- Upgrade your API plan

**"Network Error"**
- Check your internet connection
- Verify the API endpoint is accessible
- Check firewall settings

**"Timeout"**
- Increase timeout in config
- Check network stability
- Try again later

---

## 🔧 Advanced Configuration

### Custom API Endpoints
Edit `config/api_config.json` to customize:
- Timeout values
- Retry policies
- Rate limits
- Model selections

### Multiple AI Providers
Configure fallback providers:
```json
{
  "ai_providers": {
    "primary": {"provider": "groq"},
    "alternatives": [
      {"provider": "openai"},
      {"provider": "anthropic"}
    ]
  }
}
```

### Encrypted Storage
Enable encrypted credential storage:
```bash
pip install cryptography
```

Credentials will be automatically encrypted at rest.

---

## 📁 Configuration Files

| File | Purpose |
|------|---------|
| `.env` | API keys and secrets |
| `config/config.json` | App configuration |
| `config/api_config.json` | API-specific settings |
| `config/.credentials.enc` | Encrypted credentials |
| `config/.master.key` | Encryption key |

---

## 🆘 Troubleshooting

### "Module not found: cryptography"
```bash
pip install cryptography
```

### "Permission denied" on .env
```bash
chmod 600 .env
```

### "Invalid JSON in config"
Check `config/config.json` for syntax errors.

### API keys not loading
1. Check `.env` file exists
2. Verify key format
3. Restart Jarvis after changes

---

## 📚 Additional Resources

- **Groq Documentation**: https://console.groq.com/docs
- **OpenAI Documentation**: https://platform.openai.com/docs
- **Twilio Documentation**: https://www.twilio.com/docs
- **Spotify API**: https://developer.spotify.com/documentation
- **Home Assistant**: https://www.home-assistant.io/integrations/

---

## 🎯 Quick Reference

### Minimum Setup (AI Only)
```bash
# .env
GROQ_API_KEY=gsk_your_key_here
```

### Full Setup (All Features)
```bash
# .env
GROQ_API_KEY=gsk_your_key_here
JARVIS_EMAIL_ADDRESS=you@gmail.com
JARVIS_EMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=xxxx
SPOTIFY_CLIENT_ID=xxxx
SPOTIFY_CLIENT_SECRET=xxxx
HOME_ASSISTANT_URL=http://homeassistant.local:8123
HOME_ASSISTANT_TOKEN=xxxx
```

---

**Need help?** Check the troubleshooting section or open an issue on GitHub.
