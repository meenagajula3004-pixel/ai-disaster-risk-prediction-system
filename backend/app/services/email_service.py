import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

def send_otp_email(to_email: str, otp: str, purpose: str = "registration") -> bool:
    """
    Sends 6-digit OTP to user's email via SMTP service.
    If SMTP credentials are not configured, logs event to secure backend server console.
    """
    subject = "AI Disaster Risk System - Email Verification Code"
    if purpose == "password_reset":
        subject = "AI Disaster Risk System - Password Reset Code"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
        .card {{ max-width: 500px; margin: 0 auto; background-color: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 32px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
        .header {{ font-size: 20px; font-weight: bold; color: #38bdf8; margin-bottom: 16px; display: flex; align-items: center; }}
        .otp-box {{ background-color: #0f172a; border: 2px dashed #0284c7; border-radius: 12px; font-size: 32px; font-weight: 900; letter-spacing: 8px; color: #38bdf8; text-align: center; padding: 16px; margin: 24px 0; }}
        .footer {{ font-size: 12px; color: #94a3b8; margin-top: 24px; border-top: 1px solid #334155; padding-top: 16px; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">🛡️ AI Multi-Disaster Risk System</div>
        <p style="font-size: 14px; color: #cbd5e1;">Your verification code for <strong>{purpose.replace('_', ' ').title()}</strong> is:</p>
        <div class="otp-box">{otp}</div>
        <p style="font-size: 13px; color: #94a3b8;">This verification code expires in <strong>10 minutes</strong>. If you did not request this code, please ignore this email.</p>
        <div class="footer">
          AI Multi-Disaster Risk Prediction & Early Warning System &bull; Autonomous Security Module
        </div>
      </div>
    </body>
    </html>
    """

    # If SMTP settings are fully configured
    if settings.SMTP_HOST and settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.EMAIL_FROM or settings.SMTP_USERNAME
            msg["To"] = to_email

            text_part = MIMEText(f"Your AI Disaster Risk verification code is: {otp}. This code expires in 10 minutes.", "plain")
            html_part = MIMEText(html_content, "html")
            msg.attach(text_part)
            msg.attach(html_part)

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.sendmail(msg["From"], [to_email], msg.as_string())

            logger.info(f"Successfully sent OTP email to {to_email} via SMTP server {settings.SMTP_HOST}.")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMTP email to {to_email}: {e}")

    # Fallback log for local development or when SMTP is not configured
    logger.info("==========================================================")
    logger.info(f"[SECURE BACKEND EMAIL DISPATCHER] To: {to_email}")
    logger.info(f"[OTP VERIFICATION CODE]: {otp} (Purpose: {purpose}, Exp: 10 mins)")
    logger.info("==========================================================")
    return True
