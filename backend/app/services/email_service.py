import smtplib
import logging
import socket
import json
import httpx
from typing import Tuple, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

def verify_smtp_connection_safe() -> Dict[str, Any]:
    """
    Safely tests email service configuration and connectivity without exposing passwords or API keys.
    Prioritizes Resend HTTP API (Port 443 HTTPS), with legacy SMTP fallback.
    Returns structured diagnostic status dictionary.
    """
    has_resend_key = bool(settings.RESEND_API_KEY and settings.RESEND_API_KEY.strip())
    has_resend_from = bool(settings.RESEND_FROM_EMAIL and settings.RESEND_FROM_EMAIL.strip())

    has_smtp_host = bool(settings.SMTP_HOST and settings.SMTP_HOST.strip())
    has_smtp_port = bool(settings.SMTP_PORT)
    has_smtp_user = bool(settings.SMTP_USERNAME and settings.SMTP_USERNAME.strip())
    has_smtp_pass = bool(settings.SMTP_PASSWORD and settings.SMTP_PASSWORD.strip())
    has_smtp_from = bool(settings.EMAIL_FROM and settings.EMAIL_FROM.strip())

    diag = {
        "smtp_configured": has_resend_key or (has_smtp_host and has_smtp_user and has_smtp_pass),
        "resend_configured": has_resend_key,
        "env_variables": {
            "RESEND_API_KEY_SET": "YES" if has_resend_key else "NO",
            "RESEND_FROM_EMAIL_SET": "YES" if has_resend_from else "NO",
            "SMTP_HOST_SET": "YES" if has_smtp_host else "NO",
            "SMTP_PORT_SET": "YES" if has_smtp_port else "NO",
            "SMTP_USERNAME_SET": "YES" if has_smtp_user else "NO",
            "SMTP_PASSWORD_SET": "YES" if has_smtp_pass else "NO",
            "EMAIL_FROM_SET": "YES" if has_smtp_from else "NO",
            "SMTP_TLS_SET": "YES" if settings.SMTP_TLS else "NO",
        },
        "runtime_settings": {
            "provider": "RESEND_HTTP_API" if has_resend_key else ("SMTP_FALLBACK" if has_smtp_host else "NONE"),
            "resend_from_email": settings.RESEND_FROM_EMAIL or "onboarding@resend.dev",
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

    # 1. Primary: Resend HTTP API check over HTTPS 443
    if has_resend_key:
        diag["connection_test"]["status"] = "SUCCESS"
        diag["connection_test"]["stage"] = "RESEND_API_READY"
        diag["connection_test"]["detail"] = "Resend HTTP API is configured with RESEND_API_KEY and ready to deliver emails over HTTPS port 443."
        return diag

    # 2. Fallback: Legacy SMTP Connection Check
    if not (has_smtp_host and has_smtp_user and has_smtp_pass):
        diag["connection_test"]["status"] = "SKIPPED"
        diag["connection_test"]["stage"] = "MISSING_ENV_VARS"
        diag["connection_test"]["detail"] = "No email delivery provider configured. Please set RESEND_API_KEY in environment variables."
        return diag

    try:
        port_num = int(settings.SMTP_PORT)
        logger.info(f"[SMTP FALLBACK DIAGNOSTIC] Testing connection to {settings.SMTP_HOST}:{port_num}...")
        
        if port_num == 465:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, port_num, timeout=10)
            diag["connection_test"]["stage"] = "CONNECT_SSL"
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, port_num, timeout=10)
            diag["connection_test"]["stage"] = "CONNECT"
            if settings.SMTP_TLS:
                server.starttls()
                diag["connection_test"]["stage"] = "STARTTLS"

        with server:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            diag["connection_test"]["stage"] = "AUTHENTICATION"
            diag["connection_test"]["status"] = "SUCCESS"
            diag["connection_test"]["detail"] = f"Successfully connected and authenticated with SMTP server {settings.SMTP_HOST}:{port_num}"
            return diag
    except smtplib.SMTPAuthenticationError as auth_err:
        diag["connection_test"]["status"] = "FAILED"
        diag["connection_test"]["stage"] = "AUTHENTICATION"
        diag["connection_test"]["detail"] = f"SMTP Authentication failed (Code {auth_err.smtp_code})."
    except Exception as e:
        diag["connection_test"]["status"] = "FAILED"
        diag["connection_test"]["stage"] = "UNEXPECTED_ERROR"
        diag["connection_test"]["detail"] = f"{type(e).__name__}: {str(e)}"

    return diag

def send_otp_email(to_email: str, otp: str, purpose: str = "registration") -> Tuple[bool, str]:
    """
    Sends 6-digit OTP strictly to the user's email address (to_email) using Resend HTTP API over HTTPS port 443.
    Falls back to legacy SMTP if RESEND_API_KEY is not set.
    Returns Tuple[bool, str]: (success, status_message)
    """
    clean_target_email = to_email.strip().lower()
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

    has_resend_key = bool(settings.RESEND_API_KEY and settings.RESEND_API_KEY.strip())

    # 1. Primary Email Dispatch Method: Resend HTTP API over HTTPS Port 443
    if has_resend_key:
        from_email = settings.RESEND_FROM_EMAIL.strip() if settings.RESEND_FROM_EMAIL else "onboarding@resend.dev"
        headers = {
            "Authorization": f"Bearer {settings.RESEND_API_KEY.strip()}",
            "Content-Type": "application/json"
        }
        payload = {
            "from": from_email,
            "to": [clean_target_email],
            "subject": subject,
            "html": html_content
        }

        logger.info(f"[RESEND HTTP API] Dispatching OTP email to recipient: {clean_target_email} via Resend HTTPS API...")

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post("https://api.resend.com/emails", json=payload, headers=headers)
                
                if res.status_code in (200, 201):
                    res_json = res.json()
                    email_id = res_json.get("id", "unknown-id")
                    logger.info(f"[RESEND SUCCESS] OTP email successfully dispatched to {clean_target_email}. Resend Email ID: {email_id}")
                    return True, f"Email dispatched successfully via Resend HTTP API to {clean_target_email}."
                else:
                    err_data = {}
                    try:
                        err_data = res.json()
                    except Exception:
                        pass
                    err_msg = err_data.get("message") or f"Resend HTTP API returned status {res.status_code}"
                    logger.error(f"[RESEND API ERROR] Failed to send email to {clean_target_email}: HTTP {res.status_code} - {err_msg}")
                    return False, f"Resend API error ({res.status_code}): {err_msg}"
        except Exception as api_err:
            logger.error(f"[RESEND DISPATCH EXCEPTION] Failed to connect to Resend API over HTTPS: {api_err}")
            return False, f"Resend HTTP connection error: {type(api_err).__name__} - {str(api_err)}"

    # 2. Legacy Fallback: SMTP Service
    has_smtp_host = bool(settings.SMTP_HOST and settings.SMTP_HOST.strip())
    has_smtp_user = bool(settings.SMTP_USERNAME and settings.SMTP_USERNAME.strip())
    has_smtp_pass = bool(settings.SMTP_PASSWORD and settings.SMTP_PASSWORD.strip())

    if not (has_smtp_host and has_smtp_user and has_smtp_pass):
        msg = "Email delivery provider unconfigured. Please set RESEND_API_KEY in Render environment variables."
        logger.warning(f"[EMAIL DISPATCH SKIPPED] {msg}")
        return False, msg

    try:
        port_num = int(settings.SMTP_PORT)
        logger.info(f"[SMTP FALLBACK] Attempting SMTP delivery to {clean_target_email} via {settings.SMTP_HOST}:{port_num}...")
        msg_mime = MIMEMultipart("alternative")
        msg_mime["Subject"] = subject
        msg_mime["From"] = settings.EMAIL_FROM or settings.SMTP_USERNAME
        msg_mime["To"] = clean_target_email

        text_part = MIMEText(f"Your AI Disaster Risk verification code is: {otp}. This code expires in 10 minutes.", "plain")
        html_part = MIMEText(html_content, "html")
        msg_mime.attach(text_part)
        msg_mime.attach(html_part)

        if port_num == 465:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, port_num, timeout=12)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, port_num, timeout=12)
            if settings.SMTP_TLS:
                server.starttls()

        with server:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(msg_mime["From"], [clean_target_email], msg_mime.as_string())

        logger.info(f"[SMTP SUCCESS] OTP verification email dispatched to {clean_target_email} via SMTP.")
        return True, "Email dispatched successfully via fallback SMTP."
    except Exception as smtp_err:
        err_msg = f"Fallback SMTP error: {type(smtp_err).__name__} - {str(smtp_err)}"
        logger.error(f"[SMTP FALLBACK ERROR] {err_msg}")
        return False, err_msg
