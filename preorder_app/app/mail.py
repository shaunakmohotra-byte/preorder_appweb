from flask import flash


def send_bulk_email(subject, body, recipients):
    """Email sending is currently disabled."""
    flash("The email sending operation is currently under work.")
    return 0, []
