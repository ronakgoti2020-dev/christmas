from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models.token import EmailVerificationToken, PasswordResetToken
from app.models.user import User
from app.schemas.common import (
    ForgotPasswordRequest,
    GoogleAuthRequest,
    LoginRequest,
    MessageResponse,
    ProfileUpdateRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserPublic,
    VerifyEmailRequest,
)
from app.api.deps import get_current_user
from app.services.mailer import send_email
from app.services.security import (
    create_access_token,
    generate_url_token,
    hash_password,
    hash_token,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _token_response(user: User) -> TokenResponse:
    return TokenResponse(access_token=create_access_token(user.id), user=UserPublic.model_validate(user))


def _issue_email_token(db: Session, user: User) -> str:
    raw = generate_url_token()
    db.add(
        EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_token(raw),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=48),
        )
    )
    return raw


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.query(User).filter(User.email == payload.email.lower()).one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")
    user = User(
        full_name=payload.full_name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        country=payload.country,
        email_verified=False,
    )
    db.add(user)
    db.flush()
    raw = _issue_email_token(db, user)
    settings = get_settings()
    send_email(
        user.email,
        "Verify your SecretSanta email",
        f"Hi {user.full_name},\n\nConfirm your email with this code:\n{raw}\n\nOr visit {settings.api_public_url}/api/auth/verify-email\n",
    )
    db.commit()
    db.refresh(user)
    return _token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email.lower()).one_or_none()
    if user is None or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account has been disabled")
    return _token_response(user)


@router.post("/google", response_model=TokenResponse)
def google_login(payload: GoogleAuthRequest, db: Session = Depends(get_db)) -> TokenResponse:
    settings = get_settings()
    if not settings.google_client_id:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Google sign-in is not configured")
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        info = id_token.verify_oauth2_token(payload.id_token, google_requests.Request(), settings.google_client_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token") from exc

    sub = info.get("sub")
    email = (info.get("email") or "").lower()
    name = info.get("name") or email.split("@")[0]
    if not sub or not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google account is missing an email")

    user = db.query(User).filter((User.google_sub == sub) | (User.email == email)).one_or_none()
    if user is None:
        user = User(
            full_name=name,
            email=email,
            google_sub=sub,
            email_verified=bool(info.get("email_verified")),
            profile_image=info.get("picture"),
        )
        db.add(user)
    else:
        user.google_sub = sub
        if info.get("email_verified"):
            user.email_verified = True
    db.commit()
    db.refresh(user)
    return _token_response(user)


@router.post("/verify-email", response_model=MessageResponse)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)) -> MessageResponse:
    token = (
        db.query(EmailVerificationToken)
        .filter(EmailVerificationToken.token_hash == hash_token(payload.token))
        .one_or_none()
    )
    if token is None or token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification link is invalid or expired")
    user = db.get(User, token.user_id)
    if user:
        user.email_verified = True
    db.delete(token)
    db.commit()
    return MessageResponse(message="Email verified")


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    user = db.query(User).filter(User.email == payload.email.lower()).one_or_none()
    if user:
        raw = generate_url_token()
        db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hash_token(raw),
                expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
            )
        )
        db.commit()
        send_email(
            user.email,
            "Reset your SecretSanta password",
            f"Hi {user.full_name},\n\nUse this reset code in the app:\n{raw}\n\nIt expires in two hours.",
        )
    return MessageResponse(message="If that email is registered, a reset code is on its way.")


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> MessageResponse:
    token = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == hash_token(payload.token))
        .one_or_none()
    )
    if token is None or token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset code is invalid or expired")
    user = db.get(User, token.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset code is invalid or expired")
    user.password_hash = hash_password(payload.password)
    db.delete(token)
    db.commit()
    return MessageResponse(message="Password updated")


@router.post("/logout", response_model=MessageResponse)
def logout(current: User = Depends(get_current_user)) -> MessageResponse:
    return MessageResponse(message="Signed out. Discard the token on the device.")


@router.get("/me", response_model=UserPublic)
def me(current: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(current)


@router.patch("/me", response_model=UserPublic)
def update_me(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> UserPublic:
    if payload.full_name:
        current.full_name = payload.full_name
    if payload.country is not None:
        current.country = payload.country
    if payload.profile_image is not None:
        current.profile_image = payload.profile_image
    db.add(current)
    db.commit()
    db.refresh(current)
    return UserPublic.model_validate(current)
