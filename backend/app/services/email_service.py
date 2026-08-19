import smtplib
import logging
import socket
from typing import Tuple, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

def verify_smtp_connection_safe() -> Dict[str, Any]:
    """
    Safely tests runtime SMTP connection steps without exposing passwords or credentials.
    Returns structured diagnostic status dictionary.
    """
    has_host = bool(settings.SMTP_HOST and settings.SMTP_HOST.strip())
    has_port = bool(settings.SMTP_PORT)
    has_user = bool(settings.SMTP_USERNAME and settings.SMTP_USERNAME.strip())
    has_pass = bool(settings.SMTP_PASSWORD and settings.SMTP_PASSWORD.strip())
    has_from = bool(settings.EMAIL_FROM and settings.EMAIL_FROM.strip())

    diag = {
        "smtp_configured": has_host and has_user and has_pass,
        "env_variables": {
            "SMTP_HOST_SET": "YES" if has_host else "NO",
            "SMTP_PORT_SET": "YES" if has_port else "NO",
            "SMTP_USERNAME_SET": "YES" if has_user else "NO",
            "SMTP_PASSWORD_SET": "YES" if has_pass else "NO",
            "EMAIL_FROM_SET": "YES" if has_from else "NO",
            "SMTP_TLS_SET": "YES" if settings.SMTP_TLS else "NO",
        },
        "runtime_settings": {
            "smtp_host": settings.SMTP_HOST or "not-set",
            "smtp_port": settings.SMTP_PORT,
            "smtp_tls": settings.SMTP_TLS,
        },
        "connection_test": {
            "status": "PENDING",
            "stage": "INITIALIZATION",
            "detail": ""
        }
    }

    if not (has_host and has_user and has_pass):
        missing = []
        if not has_host: missing.append("SMTP_HOST")
        if not has_user: missing.append("SMTP_USERNAME")
        if not has_pass: missing.append("SMTP_PASSWORD")
        diag["connection_test"]["status"] = "SKIPPED"
        diag["connection_test"]["stage"] = "MISSING_ENV_VARS"
        diag["connection_test"]["detail"] = f"SMTP configuration incomplete. Missing: {', '.join(missing)}"
        return diag

    try:
        logger.info(f"[SMTP DIAGNOSTIC] Testing connection to {settings.SMTP_HOST}:{settings.SMTP_PORT}...")
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            diag["connection_test"]["stage"] = "CONNECT"
            if settings.SMTP_TLS:
                server.starttls()
                diag["connection_test"]["stage"] = "STARTTLS"
            
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            diag["connection_test"]["stage"] = "AUTHENTICATION"
            diag["connection_test"]["status"] = "SUCCESS"
            diag["connection_test"]["detail"] = f"Successfully connected, TLS handshaked, and authenticated with {settings.SMTP_HOST}:{settings.SMTP_PORT}"
            return diag
    except smtplib.SMTPAuthenticationError as auth_err:
        diag["connection_test"]["status"] = "FAILED"
        diag["connection_test"]["stage"] = "AUTHENTICATION"
        diag["connection_test"]["detail"] = f"Authentication failed (SMTP Code {auth_err.smtp_code}): Invalid username or App Password."
        logger.error(f"[SMTP DIAGNOSTIC FAILED] Auth error: {auth_err.smtp_code} - {auth_err.smtp_error}")
    except smtplib.SMTPConnectError as conn_err:
        diag["connection_test"]["status"] = "FAILED"
        diag["connection_test"]["stage"] = "CONNECT"
        diag["connection_test"]["detail"] = f"Failed to connect to SMTP host: {conn_err}"
        logger.error(f"[SMTP DIAGNOSTIC FAILED] Connect error: {conn_err}")
    except socket.timeout:
        diag["connection_test"]["status"] = "FAILED"
        diag["connection_test"]["stage"] = "TIMEOUT"
        diag["connection_test"]["detail"] = f"Connection to {settings.SMTP_HOST}:{settings.SMTP_PORT} timed out after 10s."
        logger.error(f"[SMTP DIAGNOSTIC FAILED] Connection timeout.")
    except Exception as e:
        diag["connection_test"]["status"] = "FAILED"
        diag["connection_test"]["stage"] = "UNEXPECTED_ERROR"
        diag["connection_test"]["detail"] = f"{type(e).__name__}: {str(e)}"
        logger.error(f"[SMTP DIAGNOSTIC FAILED] Unexpected error: {e}")

    return diag

def send_otp_email(to_email: str, otp: str, purpose: str = "registration") -> Tuple[bool, str]:
    """
    Sends 6-digit OTP to user's email via SMTP service.
    Returns Tuple[bool, str]: (success, status_message)
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

    has_host = bool(settings.SMTP_HOST and settings.SMTP_HOST.strip())
    has_user = bool(settings.SMTP_USERNAME and settings.SMTP_USERNAME.strip())
    has_pass = bool(settings.SMTP_PASSWORD and settings.SMTP_PASSWORD.strip())

    if not (has_host and has_user and has_pass):
        msg = "SMTP environment variables (SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD) are missing in Render Environment."
        logger.warning(f"[SMTP DISPATCH SKIPPED] {msg}")
        return False, msg

    try:
        logger.info(f"Attempting real SMTP email delivery to {to_email} via {settings.SMTP_HOST}:{settings.SMTP_PORT}...")
        msg_mime = MIMEMultipart("alternative")
        msg_mime["Subject"] = subject
        msg_mime["From"] = settings.EMAIL_FROM or settings.SMTP_USERNAME
        msg_mime["To"] = to_email

        text_part = MIMEText(f"Your AI Disaster Risk verification code is: {otp}. This code expires in 10 minutes.", "plain")
        html_part = MIMEText(html_content, "html")
        msg_mime.attach(text_part)
        msg_mime.attach(html_part)

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=12) as server:
            if settings.SMTP_TLS:
                server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(msg_mime["From"], [to_email], msg_mime.as_string())

        logger.info(f"[SUCCESS] OTP verification email dispatched to {to_email} via SMTP server {settings.SMTP_HOST}.")
        return True, "Email dispatched successfully via SMTP."
    except smtplib.SMTPAuthenticationError as auth_err:
        err_msg = f"Gmail/SMTP authentication failed (Code {auth_err.smtp_code}). Please verify SMTP_USERNAME and App Password."
        logger.error(f"[SMTP AUTH ERROR] {err_msg}")
        return False, err_msg
    except smtplib.SMTPConnectError as conn_err:
        err_msg = f"Failed to connect to SMTP server {settings.SMTP_HOST}:{settings.SMTP_PORT}."
        logger.error(f"[SMTP CONNECT ERROR] {err_msg}")
        return False, err_msg
    except socket.timeout:
        err_msg = f"Connection to SMTP server {settings.SMTP_HOST}:{settings.SMTP_PORT} timed out."
        logger.error(f"[SMTP TIMEOUT] {err_msg}")
        return False, err_msg
    except Exception as e:
        err_msg = f"Unexpected SMTP error: {type(e).__name__} - {str(e)}"
        logger.error(f"[SMTP ERROR] {err_msg}")
        return False, err_msg
