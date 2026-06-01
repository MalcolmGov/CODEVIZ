"""
Email Service — Gmail SMTP
Sends HTML reports with PDF attachments via Gmail.
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Optional


def send_report_email(
    to: str,
    subject: str,
    html_body: str,
    pdf_bytes: Optional[bytes] = None,
    pdf_filename: str = 'codeviz-report.pdf',
) -> dict:
    """
    Send an HTML email with an optional PDF attachment via Gmail SMTP.
    Reads GMAIL_ADDRESS and GMAIL_PASSWORD from environment.
    For Gmail, use an App Password (not your account password):
      Gmail → Settings → Security → 2-Step Verification → App Passwords
    """
    gmail_address = os.getenv('GMAIL_ADDRESS', '')
    gmail_password = os.getenv('GMAIL_PASSWORD', '')

    if not gmail_address or not gmail_password:
        return {
            'success': False,
            'error': 'GMAIL_ADDRESS or GMAIL_PASSWORD not set in .env'
        }

    msg = MIMEMultipart('mixed')
    msg['From'] = f'CodeViz Reports <{gmail_address}>'
    msg['To'] = to
    msg['Subject'] = subject

    # Attach HTML body
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    # Attach PDF if provided
    if pdf_bytes:
        pdf_part = MIMEApplication(pdf_bytes, _subtype='pdf')
        pdf_part.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
        msg.attach(pdf_part)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_address, gmail_password)
            server.sendmail(gmail_address, to, msg.as_string())
        return {'success': True, 'to': to}
    except smtplib.SMTPAuthenticationError:
        return {
            'success': False,
            'error': 'Gmail authentication failed. Use an App Password, not your account password.'
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
