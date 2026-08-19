import datetime
from datetime import timedelta
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user
from backend.app.models.db_models import UserDB, OTPRecordDB
from backend.app.models.schemas import (
    UserRegisterRequest, OTPVerifyRequest, OTPResendRequest,
    UserLoginRequest, ForgotPasswordRequest, ResetPasswordRequest,
    Token, UserOut
)
from backend.app.services.security_service import (
    validate_and_normalize_email, validate_strong_password,
    hash_password, verify_password, generate_secure_otp,
    hash_otp, verify_otp_hash, verify_captcha
)
from backend.app.services.email_service import send_otp_email

logger = logging.getLogger(__name__)
router = APIRouter()

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post("/auth/register")
async def register_user(req: UserRegisterRequest, db: Session = Depends(get_db)):
    # 1. Validate email format
    is_valid_email, clean_email, email_err = validate_and_normalize_email(req.email)
    if not is_valid_email:
        raise HTTPException(status_code=400, detail=email_err)

    # 2. Validate strong password policy
    is_valid_pwd, pwd_err = validate_strong_password(req.password, req.confirm_password)
    if not is_valid_pwd:
        raise HTTPException(status_code=400, detail=pwd_err)

    # 3. Verify CAPTCHA
    is_captcha_valid, captcha_err = await verify_captcha(req.captcha_token)
    if not is_captcha_valid:
        raise HTTPException(status_code=400, detail=captcha_err)

    try:
        # 4. Check for existing user
        existing_user = db.query(UserDB).filter(UserDB.email == clean_email).first()
        if existing_user:
            if existing_user.is_verified:
                raise HTTPException(
                    status_code=400,
                    detail="An account with this email address already exists. Please log in."
                )
            else:
                # Update password and full name for unverified existing user
                existing_user.full_name = req.full_name.strip()
                existing_user.hashed_password = hash_password(req.password)
                existing_user.updated_at = datetime.datetime.utcnow()
        else:
            user_record = UserDB(
                email=clean_email,
                full_name=req.full_name.strip(),
                hashed_password=hash_password(req.password),
                role="user",
                is_verified=False,
                is_active=True
            )
            db.add(user_record)

        # 5. Invalidate any existing unused OTPs for this email and purpose safely
        existing_otps = db.query(OTPRecordDB).filter(
            OTPRecordDB.email == clean_email,
            OTPRecordDB.purpose == "registration",
            OTPRecordDB.is_used == False
        ).all()
        for old_otp in existing_otps:
            old_otp.is_used = True

        # 6. Generate secure 6-digit OTP & store hash
        otp_code = generate_secure_otp()
        otp_entry = OTPRecordDB(
            email=clean_email,
            otp_hash=hash_otp(otp_code),
            purpose="registration",
            expires_at=datetime.datetime.utcnow() + timedelta(minutes=10),
            resend_available_at=datetime.datetime.utcnow() + timedelta(seconds=60),
            attempts=0,
            is_used=False
        )
        db.add(otp_entry)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as err:
        db.rollback()
        logger.error(f"Error during registration DB processing for {clean_email}: {err}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process registration record: {str(err)}"
        )

    # 7. Send OTP via email
    email_ok, email_msg = send_otp_email(clean_email, otp_code, purpose="registration")
    if not email_ok:
        logger.error(f"Registration accepted for {clean_email}, but SMTP delivery failed: {email_msg}")
        raise HTTPException(
            status_code=500,
            detail=f"Registration record created, but verification email delivery failed: {email_msg}"
        )

    return {
        "status": "success",
        "message": f"Registration details accepted. Verification code sent to {clean_email}.",
        "email": clean_email
    }

@router.post("/auth/verify-otp")
def verify_otp(req: OTPVerifyRequest, db: Session = Depends(get_db)):
    is_valid_email, clean_email, email_err = validate_and_normalize_email(req.email)
    if not is_valid_email:
        raise HTTPException(status_code=400, detail=email_err)

    try:
        # Fetch latest active OTP record for this email and purpose
        otp_record = (
            db.query(OTPRecordDB)
            .filter(
                OTPRecordDB.email == clean_email,
                OTPRecordDB.purpose == req.purpose,
                OTPRecordDB.is_used == False
            )
            .order_by(OTPRecordDB.created_at.desc())
            .first()
        )

        if not otp_record:
            raise HTTPException(
                status_code=400,
                detail="No active verification code found for this email address. Please request a new OTP."
            )

        # Check expiration (10 minutes)
        if datetime.datetime.utcnow() > otp_record.expires_at:
            otp_record.is_used = True
            db.commit()
            raise HTTPException(
                status_code=400,
                detail="Verification code has expired. Please request a new OTP."
            )

        # Check maximum verification attempts (5 max)
        if otp_record.attempts >= 5:
            otp_record.is_used = True
            db.commit()
            raise HTTPException(
                status_code=400,
                detail="Maximum verification attempts exceeded. Please request a new OTP."
            )

        # Verify OTP Hash
        if not verify_otp_hash(req.otp.strip(), otp_record.otp_hash):
            otp_record.attempts += 1
            db.commit()
            remaining = 5 - otp_record.attempts
            raise HTTPException(
                status_code=400,
                detail=f"Invalid verification code. {remaining} attempt(s) remaining."
            )

        # Mark OTP as used
        otp_record.is_used = True

        # Activate User Account if Purpose is Registration
        user = db.query(UserDB).filter(UserDB.email == clean_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Associated user account not found.")

        if req.purpose == "registration":
            user.is_verified = True
            user.updated_at = datetime.datetime.utcnow()
            db.commit()

            access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
            return {
                "status": "success",
                "message": "Email address verified successfully. Welcome!",
                "access_token": access_token,
                "token_type": "bearer",
                "user": UserOut.model_validate(user)
            }
        else:
            db.commit()
            return {
                "status": "success",
                "message": "OTP verified successfully. You may now reset your password."
            }
    except HTTPException:
        db.rollback()
        raise
    except Exception as err:
        db.rollback()
        logger.error(f"Error during OTP verification for {clean_email}: {err}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify OTP record: {str(err)}"
        )

@router.post("/auth/resend-otp")
async def resend_otp(req: OTPResendRequest, db: Session = Depends(get_db)):
    is_valid_email, clean_email, email_err = validate_and_normalize_email(req.email)
    if not is_valid_email:
        raise HTTPException(status_code=400, detail=email_err)

    is_captcha_valid, captcha_err = await verify_captcha(req.captcha_token)
    if not is_captcha_valid:
        raise HTTPException(status_code=400, detail=captcha_err)

    try:
        user = db.query(UserDB).filter(UserDB.email == clean_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="No account registered with this email address.")

        if req.purpose == "registration" and user.is_verified:
            raise HTTPException(status_code=400, detail="Account is already verified. Please log in.")

        # Rate Limit / Cooldown Check: 60 Seconds
        last_otp = (
            db.query(OTPRecordDB)
            .filter(OTPRecordDB.email == clean_email, OTPRecordDB.purpose == req.purpose)
            .order_by(OTPRecordDB.created_at.desc())
            .first()
        )

        if last_otp and last_otp.resend_available_at and datetime.datetime.utcnow() < last_otp.resend_available_at:
            wait_seconds = int((last_otp.resend_available_at - datetime.datetime.utcnow()).total_seconds()) + 1
            raise HTTPException(
                status_code=400,
                detail=f"Please wait {wait_seconds} second(s) before requesting a new OTP."
            )

        # Invalidate previous OTPs
        existing_otps = db.query(OTPRecordDB).filter(
            OTPRecordDB.email == clean_email,
            OTPRecordDB.purpose == req.purpose,
            OTPRecordDB.is_used == False
        ).all()
        for old_otp in existing_otps:
            old_otp.is_used = True

        otp_code = generate_secure_otp()
        new_otp = OTPRecordDB(
            email=clean_email,
            otp_hash=hash_otp(otp_code),
            purpose=req.purpose,
            expires_at=datetime.datetime.utcnow() + timedelta(minutes=10),
            resend_available_at=datetime.datetime.utcnow() + timedelta(seconds=60),
            attempts=0,
            is_used=False
        )
        db.add(new_otp)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as err:
        db.rollback()
        logger.error(f"Error during OTP resend for {clean_email}: {err}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process OTP resend: {str(err)}"
        )

    email_ok, email_msg = send_otp_email(clean_email, otp_code, purpose=req.purpose)
    if not email_ok:
        logger.error(f"OTP generated for {clean_email}, but resend email failed: {email_msg}")
        raise HTTPException(
            status_code=500,
            detail=f"Verification code generated, but email delivery failed: {email_msg}"
        )

    return {
        "status": "success",
        "message": f"A new verification code has been dispatched to {clean_email}.",
        "email": clean_email
    }

@router.post("/auth/login")
async def login_user(req: UserLoginRequest, db: Session = Depends(get_db)):
    is_valid_email, clean_email, email_err = validate_and_normalize_email(req.email)
    if not is_valid_email:
        raise HTTPException(status_code=400, detail=email_err)

    is_captcha_valid, captcha_err = await verify_captcha(req.captcha_token)
    if not is_captcha_valid:
        raise HTTPException(status_code=400, detail=captcha_err)

    try:
        user = db.query(UserDB).filter(UserDB.email == clean_email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="Your account has been deactivated. Please contact support.")

        # Check Account Lockout status
        if user.locked_until and datetime.datetime.utcnow() < user.locked_until:
            wait_mins = int((user.locked_until - datetime.datetime.utcnow()).total_seconds() / 60) + 1
            raise HTTPException(
                status_code=400,
                detail=f"Account is temporarily locked due to multiple failed login attempts. Please try again after {wait_mins} minute(s)."
            )

        # Verify Password
        if not verify_password(req.password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.datetime.utcnow() + timedelta(minutes=15)
                db.commit()
                raise HTTPException(
                    status_code=400,
                    detail="Account locked for 15 minutes due to 5 consecutive failed login attempts."
                )
            db.commit()
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        # Reset failed attempts on success
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.datetime.utcnow()
        db.commit()

        if not user.is_verified:
            raise HTTPException(
                status_code=400,
                detail="Your email is not verified yet. Please verify your OTP."
            )

        access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})
        return {
            "status": "success",
            "message": "Login successful.",
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserOut.model_validate(user)
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as err:
        db.rollback()
        logger.error(f"Error during login processing for {clean_email}: {err}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process login: {str(err)}"
        )

@router.post("/auth/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    is_valid_email, clean_email, email_err = validate_and_normalize_email(req.email)
    if not is_valid_email:
        raise HTTPException(status_code=400, detail=email_err)

    is_captcha_valid, captcha_err = await verify_captcha(req.captcha_token)
    if not is_captcha_valid:
        raise HTTPException(status_code=400, detail=captcha_err)

    try:
        user = db.query(UserDB).filter(UserDB.email == clean_email).first()
        if not user or not user.is_verified:
            return {
                "status": "success",
                "message": "If an active account exists for this email address, a password reset verification code has been sent."
            }

        # Rate Limit / Cooldown Check: 60 Seconds
        last_otp = (
            db.query(OTPRecordDB)
            .filter(OTPRecordDB.email == clean_email, OTPRecordDB.purpose == "password_reset")
            .order_by(OTPRecordDB.created_at.desc())
            .first()
        )

        if last_otp and last_otp.resend_available_at and datetime.datetime.utcnow() < last_otp.resend_available_at:
            wait_seconds = int((last_otp.resend_available_at - datetime.datetime.utcnow()).total_seconds()) + 1
            raise HTTPException(
                status_code=400,
                detail=f"Please wait {wait_seconds} second(s) before requesting a new OTP."
            )

        # Invalidate previous reset OTPs
        existing_otps = db.query(OTPRecordDB).filter(
            OTPRecordDB.email == clean_email,
            OTPRecordDB.purpose == "password_reset",
            OTPRecordDB.is_used == False
        ).all()
        for old_otp in existing_otps:
            old_otp.is_used = True

        otp_code = generate_secure_otp()
        new_otp = OTPRecordDB(
            email=clean_email,
            otp_hash=hash_otp(otp_code),
            purpose="password_reset",
            expires_at=datetime.datetime.utcnow() + timedelta(minutes=10),
            resend_available_at=datetime.datetime.utcnow() + timedelta(seconds=60),
            attempts=0,
            is_used=False
        )
        db.add(new_otp)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as err:
        db.rollback()
        logger.error(f"Error during forgot-password processing for {clean_email}: {err}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process password reset request: {str(err)}"
        )

    email_ok, email_msg = send_otp_email(clean_email, otp_code, purpose="password_reset")
    if not email_ok:
        logger.error(f"Reset OTP generated for {clean_email}, but email delivery failed: {email_msg}")
        raise HTTPException(
            status_code=500,
            detail=f"Password reset code generated, but email delivery failed: {email_msg}"
        )

    return {
        "status": "success",
        "message": "If an active account exists for this email address, a password reset verification code has been sent."
    }

@router.post("/auth/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    is_valid_email, clean_email, email_err = validate_and_normalize_email(req.email)
    if not is_valid_email:
        raise HTTPException(status_code=400, detail=email_err)

    is_valid_pwd, pwd_err = validate_strong_password(req.new_password, req.confirm_password)
    if not is_valid_pwd:
        raise HTTPException(status_code=400, detail=pwd_err)

    try:
        user = db.query(UserDB).filter(UserDB.email == clean_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Associated user account not found.")

        # Verify latest active reset OTP
        otp_record = (
            db.query(OTPRecordDB)
            .filter(
                OTPRecordDB.email == clean_email,
                OTPRecordDB.purpose == "password_reset",
                OTPRecordDB.is_used == False
            )
            .order_by(OTPRecordDB.created_at.desc())
            .first()
        )

        if not otp_record or not verify_otp_hash(req.otp.strip(), otp_record.otp_hash):
            raise HTTPException(status_code=400, detail="Invalid or unverified password reset OTP.")

        # Update Password & Clear Lockouts
        user.hashed_password = hash_password(req.new_password)
        user.failed_login_attempts = 0
        user.locked_until = None
        user.updated_at = datetime.datetime.utcnow()
        otp_record.is_used = True

        db.commit()
        return {
            "status": "success",
            "message": "Password updated successfully. Please log in with your new password."
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as err:
        db.rollback()
        logger.error(f"Error during password reset for {clean_email}: {err}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset password: {str(err)}"
        )

@router.get("/auth/me", response_model=UserOut)
def get_current_user_profile(current_user: UserDB = Depends(get_current_user)):
    return current_user
