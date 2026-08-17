import logging
import os
import smtplib
from email.message import EmailMessage


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # Gmail SMTP over SSL
SMTP_TIMEOUT_SECONDS = 30
logger = logging.getLogger(__name__)


class EmailConfigurationError(RuntimeError):
    """Raised when Gmail SMTP has not been configured."""


def get_email_configuration_error():
    """Return a safe-to-display configuration error, or None when ready."""
    if not os.environ.get("GMAIL_SMTP_EMAIL", "").strip():
        return "GMAIL_SMTP_EMAIL is not configured."
    if not os.environ.get("GMAIL_APP_PASSWORD", "").strip():
        return "GMAIL_APP_PASSWORD is not configured."
    return None


def _smtp_configuration():
    error = get_email_configuration_error()
    if error:
        raise EmailConfigurationError(error)

    username = os.environ["GMAIL_SMTP_EMAIL"].strip()
    password = os.environ["GMAIL_APP_PASSWORD"].replace(" ", "").strip()
    sender = os.environ.get("EMAIL_FROM", username).strip()
    return username, password, sender


def _message(sender, recipient, subject, body):
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)
    return message


def send_bulk_email(subject, body, recipients):
    """Send one private plain-text email per recipient through Gmail SMTP.

    Returns ``(sent_count, failed_recipients)``. Gmail is kept to one SMTP
    connection per broadcast, which is faster than opening one per recipient.
    """
    username, password, sender = _smtp_configuration()
    recipients = list(dict.fromkeys(
        email.strip().lower() for email in recipients
        if isinstance(email, str) and email.strip()
    ))

    sent = 0
    failed = []

    try:
        with smtplib.SMTP_SSL(
            SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT_SECONDS
        ) as smtp:
            smtp.login(username, password)

            for recipient in recipients:
                try:
                    refused = smtp.send_message(
                        _message(sender, recipient, subject, body)
                    )
                    if refused:
                        failed.append(recipient)
                        logger.error("Gmail refused delivery to one recipient")
                    else:
                        sent += 1
                except smtplib.SMTPException:
                    failed.append(recipient)
                    logger.exception("Gmail failed to deliver to one recipient")
    except (OSError, smtplib.SMTPException):
        logger.exception("Could not connect to or authenticate with Gmail SMTP")
        failed.extend(recipients)

    return sent, failed
