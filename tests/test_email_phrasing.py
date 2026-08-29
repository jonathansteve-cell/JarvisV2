"""Email must understand natural phrasing and confirm before sending a draft."""

import pytest

from core.config_manager import ConfigManager
from modules.email_controller import EmailController


@pytest.fixture
def email(tmp_path, monkeypatch):
    cfg = ConfigManager(tmp_path / "config.json")
    controller = EmailController(cfg)
    sent = []
    monkeypatch.setattr(
        controller,
        "send_email",
        lambda to, subject, body: sent.append({"to": to, "subject": subject, "body": body})
        or f"Email sent to {to}, sir.",
    )
    controller.sent = sent
    return controller


def test_the_original_exact_phrasing_still_works(email):
    result = email.process("send email to tony@stark.com subject Update body The project is done")
    assert result["success"]
    assert email.sent == [
        {"to": "tony@stark.com", "subject": "Update", "body": "The project is done"}
    ]


def test_dropping_send_still_works(email):
    email.process("email to tony@stark.com subject Update body Hello there")
    assert email.sent[-1]["to"] == "tony@stark.com"


def test_the_natural_phrasing_that_used_to_fail(email):
    # This one previously fell through to AI chat and sent nothing.
    result = email.process("email tony@stark.com saying the report is attached")
    assert result["success"]
    assert email.sent[-1]["to"] == "tony@stark.com"
    assert email.sent[-1]["body"] == "the report is attached"
    assert email.sent[-1]["subject"]  # derived, never empty


def test_write_an_email_about_a_topic_drafts_and_waits(email):
    result = email.process("write an email to tony@stark.com about the reactor upgrade")
    assert result["success"]
    assert "Draft ready" in result["response"]
    assert email.sent == []  # nothing sent without confirmation

    confirm = email.process("send the email")
    assert confirm["success"]
    assert len(email.sent) == 1
    assert email.sent[0]["to"] == "tony@stark.com"
    assert "reactor upgrade" in email.sent[0]["body"].lower()


def test_draft_can_be_cancelled(email):
    email.process("draft an email to pep@potts.com regarding the board meeting")
    assert email._pending is not None
    cancelled = email.process("cancel the email")
    assert "discarded" in cancelled["response"]
    assert email._pending is None
    assert email.sent == []


def test_send_it_with_no_draft_says_so(email):
    assert "no email draft waiting" in email.process("send the email")["response"].lower()


def test_a_waiting_draft_reminds_you(email):
    email.process("compose an email to a@b.com about lunch")
    nudge = email.process("what about that email")
    assert "still waiting" in nudge["response"]


def test_subject_is_derived_from_the_body(email):
    email.process("email bob@builder.com saying the plumbing is fixed and the invoice follows")
    subject = email.sent[-1]["subject"]
    assert subject
    assert len(subject) <= 60


def test_inbox_commands_are_untouched(email, monkeypatch):
    monkeypatch.setattr(email, "unread_count", lambda: "You have 3 unread email messages, sir.")
    result = email.process("unread email count")
    assert "3 unread" in result["response"]


def test_unrelated_text_is_not_an_email_command(email):
    assert email.process("what is the weather")["success"] is False
