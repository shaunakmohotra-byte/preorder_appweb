"""Email delivery through SendGrid's HTTPS API.

Render cannot reach Gmail's SMTP ports, so this module uses an HTTPS API
instead. SendGrid can verify a single Gmail sender address.
"""

import json
import logging
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SENDGRID_MAIL_SEND_URL = "https://api.sendgrid.com/v3/mail/send"
REQUEST_TIMEOUT_SECONDS = 30
logger = logging.getLogger(__name__)


class EmailConfigurationError(RuntimeError):
    """Raised when the SendGrid email provider has not been configured."""


def get_email_configuration_error():
    """Return a safe-to-display configuration error, or None when ready."""
    if not os.environ.get("SENDGRID_API_KEY", "").strip():
        return "SENDGRID_API_KEY is not configured."
    if not os.environ.get("EMAIL_FROM", "").strip():
        return "EMAIL_FROM is not configured."
    return None


def _sendgrid_configuration():
    error = get_email_configuration_error()
    if error:
        raise EmailConfigurationError(error)

    return (
        os.environ["SENDGRID_API_KEY"].strip(),
        os.environ["EMAIL_FROM"].strip(),
    )


def _send_one_email(api_key, sender, recipient, subject, body):
    """Send one private message and return only when SendGrid accepts it."""
    payload = {
        "personalizations": [{"to": [{"email": recipient}]}],
        "from": {"email": sender},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}],
    }
    request = Request(
        SENDGRID_MAIL_SEND_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        if response.status != 202:
            raise RuntimeError(f"SendGrid returned HTTP {response.status}")


def send_bulk_email(subject, body, recipients):
    """Send one private plain-text email per recipient via SendGrid HTTPS."""
    api_key, sender = _sendgrid_configuration()
    recipients = list(dict.fromkeys(
        email.strip().lower() for email in recipients
        if isinstance(email, str) and email.strip()
    ))

    sent = 0
    failed = []
    for recipient in recipients:
        try:
            _send_one_email(api_key, sender, recipient, subject, body)
            sent += 1
        except (HTTPError, URLError, OSError, RuntimeError):
            failed.append(recipient)
            logger.exception("SendGrid did not accept an email for one recipient")

    return sent, failed
