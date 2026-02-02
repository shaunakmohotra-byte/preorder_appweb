import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # TLS port
EMAIL_ADDRESS = "preorder.apptis@gmail.com"
EMAIL_PASSWORD = "bzmf ugav dbcy podq"  # Gmail App Password

def send_order_email(to_email, subject, body):
    try:
        # Create email message
        msg = MIMEMultipart()
        msg["From"] = preorder.apptis@gmail.com
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect to Gmail SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.ehlo()          # Identify ourselves to SMTP server
            server.starttls()      # Secure the connection
            server.ehlo()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"EMAIL SENT to {to_email}")

    except smtplib.SMTPException as e:
        print("SMTP ERROR:", e)
    except Exception as e:
        print("EMAIL FAILED:", e)

