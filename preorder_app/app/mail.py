import os
import resend

resend.api_key = os.environ.get("RESEND_API_KEY")

# Until you verify your own domain on resend.com, you can only send
# FROM this address, and only TO the email you signed up to Resend
# with (their sandbox restriction). Once you verify a domain, set
# RESEND_FROM_EMAIL to something like "noreply@yourdomain.com" and
# you can send to any recipient.
DEFAULT_SENDER = os.environ.get("RESEND_FROM_EMAIL", "onboarding@resend.dev")

BATCH_SIZE = 100  # Resend's batch endpoint accepts up to 100 emails per call


def send_bulk_email(subject, body, recipients):
    """
    Sends one individual email per recipient (not one email with
    everyone CC'd/BCC'd), batched in groups of up to 100 per API call.

    Returns (sent_count, failed_recipients).
    """
    sent = 0
    failed = []

    for i in range(0, len(recipients), BATCH_SIZE):
        chunk = recipients[i:i + BATCH_SIZE]

        payload = [
            {
                "from": DEFAULT_SENDER,
                "to": [email],
                "subject": subject,
                "text": body,
            }
            for email in chunk
        ]

        try:
            resend.Batch.send(payload)
            sent += len(chunk)
        except Exception as e:
            failed.extend(chunk)

    return sent, failed
