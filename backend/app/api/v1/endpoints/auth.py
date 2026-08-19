import datetime
from datetime import timedelta
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
            user_record = existing_user
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

    # 5. Invalidate any existing OTPs for this email and purpose
    db.query(OTPRecordDB).filter(
        OTPRecordDB.email == clean_email,
        OTPRecordDB.purpose == "registration",
        OTPRecordDB.is_used == False
    ).update({"is_used": True})

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

    # 7. Send OTP via email
    send_otp_email(clean_email, otp_code, purpose="registration")

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
        raise HTTPException(status_code=400, detail="No active verification code found. Please request a new OTP.")

    # Check expiration
    if datetime.datetime.utcnow() > otp_record.expires_at:
        otp_record.is_used = True
        db.commit()
        raise HTTPException(status_code=400, detail="Verification code has expired. Please request a new OTP.")

    # Check attempt limit
    if otp_record.attempts >= 5:
        otp_record.is_used = True
        db.commit()
        raise HTTPException(status_code=400, detail="Maximum OTP verification attempts exceeded. Please request a new OTP.")

    # Increment attempts
    otp_record.attempts += 1

    # Verify OTP hash
    if not verify_otp_hash(req.otp.strip(), otp_record.otp_hash):
        db.commit()
        remaining_attempts = 5 - otp_record.attempts
        raise HTTPException(
            status_code=400,
            detail=f"Invalid verification code. {remaining_attempts} attempt(s) remaining."
        )

    # OTP is valid -> Mark as used
    otp_record.is_used = True

    if req.purpose == "registration":
        user = db.query(UserDB).filter(UserDB.email == clean_email).first()
        if not user:
            raise HTTPException(status_code=400, detail="Associated user account not found.")
        
        user.is_verified = True
        user.is_active = True
        user.last_login_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(user)

        token = create_access_token({"sub": user.email, "user_id": user.id, "role": user.role})
        return {
            "status": "success",
            "message": "Email address successfully verified. Account is now active.",
            "access_token": token,
            "token_type": "bearer",
            "user": UserOut.model_validate(user)
        }
    elif req.purpose == "password_reset":
        db.commit()
        return {
            "status": "success",
            "message": "Verification code verified successfully. You may now reset your password.",
            "email": clean_email
        }
    else:
        db.commit()
        return {"status": "success", "message": "Verification successful."}

@router.post("/auth/resend-otp")
async def resend_otp(req: OTPResendRequest, db: Session = Depends(get_db)):
    is_valid_email, clean_email, email_err = validate_and_normalize_email(req.email)
    if not is_valid_email:
        raise HTTPException(status_code=400, detail=email_err)

    # Check latest OTP for cooldown
    latest_otp = (
        db.query(OTPRecordDB)
        .filter(
            OTPRecordDB.email == clean_email,
            OTPRecordDB.purpose == req.purpose
        )
        .order_by(OTPRecordDB.created_at.desc())
        .first()
    )

    now = datetime.datetime.utcnow()
    if latest_otp and latest_otp.resend_available_at and now < latest_otp.resend_available_at:
        remaining_secs = int((latest_otp.resend_available_at - now).total_seconds())
        raise HTTPException(
            status_code=400,
            detail=f"Please wait {remaining_secs} second(s) before requesting a new OTP."
        )

    # Verify CAPTCHA
    is_captcha_valid, captcha_err = await verify_captcha(req.captcha_token)
    if not is_captcha_valid:
        raise HTTPException(status_code=400, detail=captcha_err)

    # Invalidate previous OTPs
    db.query(OTPRecordDB).filter(
        OTPRecordDB.email == clean_email,
        OTPRecordDB.purpose == req.purpose,
        OTPRecordDB.is_used == False
    ).update({"is_used": True})

    # Generate new OTP
    new_otp = generate_secure_otp()
    otp_entry = OTPRecordDB(
        email=clean_email,
        otp_hash=hash_otp(new_otp),
        purpose=req.purpose,
        expires_at=now + timedelta(minutes=10),
        resend_available_at=now + timedelta(seconds=60),
        attempts=0,
        is_used=False
    )
    db.add(otp_entry)
    db.commit()

    send_otp_email(clean_email, new_otp, purpose=req.purpose)

    return {
        "status": "success",
        "message": f"A new verification code has been sent to {clean_email}.",
        "email": clean_email
    }

@router.post("/auth/login", response_model=Token)
async def login_user(req: UserLoginRequest, db: Session = Depends(get_db)):
    is_valid_email, clean_email, email_err = validate_and_normalize_email(req.email)
    if not is_valid_email:
        raise HTTPException(status_code=400, detail="Invalid email or password.")

    user = db.query(UserDB).filter(UserDB.email == clean_email).first()

    # Check temporary account lock
    now = datetime.datetime.utcnow()
    if user and user.locked_until and now < user.locked_until:
        remaining_mins = max(1, int((user.locked_until - now).total_seconds() / 60))
        raise HTTPException(
            status_code=400,
            detail=f"Account is temporarily locked due to multiple failed login attempts. Please try again after {remaining_mins} minute(s)."
        )

    # Adaptive CAPTCHA requirement if failed attempts >= 3
    if user and user.failed_login_attempts >= 3:
        is_captcha_valid, captcha_err = await verify_captcha(req.captcha_token)
        if not is_captcha_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Security verification required: {captcha_err or 'Please complete CAPTCHA verification.'}"
            )

    # Verify credentials
    if not user or not verify_password(req.password, user.hashed_password):
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = now + timedelta(minutes=15)
            db.commit()
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # Check email verification status
    if not user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="Your email is not verified. Please verify your email before logging in."
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Your account has been deactivated.")

    # Successful login -> Reset lockout and failed attempts
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = now
    db.commit()

    token = create_access_token({"sub": user.email, "user_id": user.id, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserOut.model_validate(user)
    }

@router.post("/auth/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    is_valid_email, clean_email, email_err = validate_and_normalize_email(req.email)
    if not is_valid_email:
        # Return generic message to prevent user enumeration
        return {
            "status": "success",
            "message": "If an account with that email exists, a password reset verification code has been sent."
        }

    # Verify CAPTCHA
    is_captcha_valid, captcha_err = await verify_captcha(req.captcha_token)
    if not is_captcha_valid:
        raise HTTPException(status_code=400, detail=captcha_err)

    user = db.query(UserDB).filter(UserDB.email == clean_email).first()

    if user and user.is_verified:
        # Invalidate prior reset OTPs
        db.query(OTPRecordDB).filter(
            OTPRecordDB.email == clean_email,
            OTPRecordDB.purpose == "password_reset",
            OTPRecordDB.is_used == False
        ).update({"is_used": True})

        otp_code = generate_secure_otp()
        otp_entry = OTPRecordDB(
            email=clean_email,
            otp_hash=hash_otp(otp_code),
            purpose="password_reset",
            expires_at=datetime.datetime.utcnow() + timedelta(minutes=10),
            resend_available_at=datetime.datetime.utcnow() + timedelta(seconds=60),
            attempts=0,
            is_used=False
        )
        db.add(otp_entry)
        db.commit()

        send_otp_email(clean_email, otp_code, purpose="password_reset")

    return {
        "status": "success",
        "message": "If an account with that email exists, a password reset verification code has been sent."
    }

@router.post("/auth/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    is_valid_email, clean_email, email_err = validate_and_normalize_email(req.email)
    if not is_valid_email:
        raise HTTPException(status_code=400, detail=email_err)

    # Validate strong new password policy
    is_valid_pwd, pwd_err = validate_strong_password(req.new_password, req.confirm_password)
    if not is_valid_pwd:
        raise HTTPException(status_code=400, detail=pwd_err)

    # Find active password reset OTP
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

    if not otp_record:
        raise HTTPException(status_code=400, detail="No active password reset request found. Please request a new reset OTP.")

    now = datetime.datetime.utcnow()
    if now > otp_record.expires_at:
        otp_record.is_used = True
        db.commit()
        raise HTTPException(status_code=400, detail="Password reset code has expired. Please request a new OTP.")

    if otp_record.attempts >= 5:
        otp_record.is_used = True
        db.commit()
        raise HTTPException(status_code=400, detail="Maximum OTP verification attempts exceeded. Please request a new reset OTP.")

    otp_record.attempts += 1

    if not verify_otp_hash(req.otp.strip(), otp_record.otp_hash):
        db.commit()
        remaining_attempts = 5 - otp_record.attempts
        raise HTTPException(
            status_code=400,
            detail=f"Invalid verification code. {remaining_attempts} attempt(s) remaining."
        )

    otp_record.is_used = True

    user = db.query(UserDB).filter(UserDB.email == clean_email).first()
    if not user:
        raise HTTPException(status_code=400, detail="User account not found.")

    user.hashed_password = hash_password(req.new_password)
    user.failed_login_attempts = 0
    user.locked_until = None
    user.updated_at = now
    db.commit()

    return {
        "status": "success",
        "message": "Password has been successfully updated. Please log in with your new password."
    }

@router.get("/auth/me", response_model=UserOut)
def get_current_user_profile(current_user: UserDB = Depends(get_current_user)):
    return current_user
