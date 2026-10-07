from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timezone
import secrets
import httpx
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import *
from app.models.user import User
from app.schemas import UserRegister, UserLogin, Token, UserOut, UserUpdate

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=201)
async def register(data: UserRegister, request: Request, db: AsyncSession = Depends(get_db)):
    ip = request.client.host if request.client else "unknown"
    email = data.email.lower().strip() if data.email else None
    r1 = await db.execute(select(User).where(User.phone == data.phone))
    if r1.scalar_one_or_none():
        raise HTTPException(400, "Phone already registered")
    if email:
        r2 = await db.execute(select(User).where(User.email == email))
        if r2.scalar_one_or_none():
            raise HTTPException(400, "Email already registered")
    if data.purpose not in (None, "sell", "buy"):
        raise HTTPException(400, "Purpose must be sell or buy")
    if data.purpose == "sell" and data.role.value != "farmer":
        raise HTTPException(400, "Selling accounts must be farmer accounts")
    if data.purpose == "buy" and data.role.value != "buyer":
        raise HTTPException(400, "Buying accounts must be buyer accounts")
    await check_rate_limit(f"register:v2:{ip}:{data.phone}", 5, 3600)
    user = User(full_name=data.full_name, phone=data.phone, email=email,
                hashed_password=get_password_hash(data.password), role=data.role.value,
                village=data.village, district=data.district, state=data.state,
                taluk=data.taluk, area=data.area, door_no_farm=data.door_no_farm,
                purpose=data.purpose, products_to_sell=data.products_to_sell,
                products_to_buy=data.products_to_buy, farm_type=data.farm_type,
                farm_agriculture_details=data.farm_agriculture_details,
                latitude=data.latitude, longitude=data.longitude)
    db.add(user); await db.flush(); await db.refresh(user)
    at = create_access_token({"sub": str(user.id), "role": user.role})
    rt = create_refresh_token({"sub": str(user.id)})
    rp = decode_token(rt); await store_refresh_token(user.id, rp["jti"])
    return Token(access_token=at, refresh_token=rt, user=UserOut.model_validate(user))

@router.post("/login", response_model=Token)
async def login(data: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    await check_rate_limit(f"login:{data.phone}", 10, 900)
    result = await db.execute(select(User).where(User.phone == data.phone))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid phone or password")
    if not user.is_active:
        raise HTTPException(400, "Account deactivated")
    at = create_access_token({"sub": str(user.id), "role": user.role})
    rt = create_refresh_token({"sub": str(user.id)})
    rp = decode_token(rt); await store_refresh_token(user.id, rp["jti"])
    return Token(access_token=at, refresh_token=rt, user=UserOut.model_validate(user))

class LogoutReq(BaseModel):
    refresh_token: Optional[str] = None

@router.post("/logout")
async def logout(body: LogoutReq, request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    jti = getattr(request.state, "jti", None)
    if jti:
        auth = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            p = decode_token(auth); await blacklist_token(jti, p.get("exp", 0))
        except Exception: pass
    if body.refresh_token:
        try:
            rp = decode_token(body.refresh_token)
            if rp.get("type") == "refresh":
                await validate_and_rotate_refresh(current_user.id, rp["jti"])
        except Exception: pass
    return {"message": "Logged out successfully"}

@router.post("/logout-all")
async def logout_all(current_user: User = Depends(get_current_user)):
    await blacklist_all_user_tokens(current_user.id)
    await revoke_all_refresh_tokens(current_user.id)
    return {"message": "All sessions terminated"}

class RefreshReq(BaseModel):
    refresh_token: str

@router.post("/refresh")
async def refresh_tokens(body: RefreshReq, db: AsyncSession = Depends(get_db)):
    try: payload = decode_token(body.refresh_token)
    except: raise HTTPException(401, "Invalid refresh token")
    if payload.get("type") != "refresh":
        raise HTTPException(401, "Expected refresh token")
    user_id = int(payload.get("sub", 0)); jti = payload.get("jti")
    if not await validate_and_rotate_refresh(user_id, jti):
        await blacklist_all_user_tokens(user_id); await revoke_all_refresh_tokens(user_id)
        raise HTTPException(401, "Refresh token reuse detected. All sessions revoked.")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active: raise HTTPException(401, "User not found")
    new_at = create_access_token({"sub": str(user.id), "role": user.role})
    new_rt = create_refresh_token({"sub": str(user.id)})
    nrp = decode_token(new_rt); await store_refresh_token(user.id, nrp["jti"])
    return {"access_token": new_at, "refresh_token": new_rt, "token_type": "bearer"}

class ForgotPwdReq(BaseModel):
    email: str

class ResetPwdReq(BaseModel):
    email: str; otp: str; new_password: str = Field(..., min_length=6)

RESET_OTP_TTL_SECONDS = 60

async def send_password_reset_email(email: str, otp: str):
    if not settings.RESEND_API_KEY:
        raise HTTPException(503, "Email delivery is not configured. Set RESEND_API_KEY and FROM_EMAIL.")
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
                json={
                    "from": settings.FROM_EMAIL,
                    "to": [email],
                    "subject": "AgriMarket password reset OTP",
                    "text": f"Your AgriMarket password reset OTP is {otp}. It expires in 1 minute.",
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                502,
                "Email provider rejected the email. Check RESEND_API_KEY and verify FROM_EMAIL in Resend.",
            ) from exc
        except httpx.HTTPError as exc:
            raise HTTPException(503, "Email provider is unavailable. Please try again later.") from exc

@router.post("/forgot-password")
async def forgot_password(data: ForgotPwdReq, request: Request, db: AsyncSession = Depends(get_db)):
    email = data.email.lower()
    await check_rate_limit(f"forgot:v2:{email}", 60, 3600)
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user: return {"message": "If this email is registered, an OTP has been sent."}
    r = await get_redis()
    cooldown_key = f"pwd_reset_cooldown:{email}"
    cooldown = await r.ttl(cooldown_key)
    if cooldown > 0:
        raise HTTPException(429, f"Please wait {cooldown} seconds before requesting another OTP.")
    otp = f"{secrets.randbelow(1000000):06d}"
    await send_password_reset_email(email, otp)
    await r.setex(f"pwd_reset:{email}", RESET_OTP_TTL_SECONDS, f"{user.id}:{otp}")
    await r.setex(cooldown_key, RESET_OTP_TTL_SECONDS, "1")
    return {"message": "If this email is registered, an OTP has been sent."}

@router.post("/reset-password")
async def reset_password(data: ResetPwdReq, db: AsyncSession = Depends(get_db)):
    email = data.email.lower()
    r = await get_redis(); stored = await r.getdel(f"pwd_reset:{email}")
    if not stored: raise HTTPException(400, "OTP expired or already used")
    stored_value = stored.decode() if isinstance(stored, bytes) else stored
    try: user_id, expected_otp = stored_value.split(":", 1)
    except ValueError: raise HTTPException(400, "Invalid reset request")
    if not secrets.compare_digest(data.otp, expected_otp):
        raise HTTPException(400, "Invalid OTP")
    result = await db.execute(select(User).where(User.id == int(user_id), User.email == email))
    user = result.scalar_one_or_none()
    if not user: raise HTTPException(404, "User not found")
    user.hashed_password = get_password_hash(data.new_password); await db.flush()
    await blacklist_all_user_tokens(user.id); await revoke_all_refresh_tokens(user.id)
    return {"message": "Password reset successfully. Please login."}

class ChangePwdReq(BaseModel):
    current_password: str; new_password: str = Field(..., min_length=6)

@router.post("/change-password")
async def change_password(data: ChangePwdReq, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(400, "Current password incorrect")
    current_user.hashed_password = get_password_hash(data.new_password); await db.flush()
    await blacklist_all_user_tokens(current_user.id); await revoke_all_refresh_tokens(current_user.id)
    return {"message": "Password changed. Please login again."}

@router.post("/send-verification")
async def send_verification(current_user: User = Depends(get_current_user)):
    if current_user.is_verified: return {"message": "Already verified"}
    token = create_verification_token(current_user.id, "phone_verify")
    payload = decode_token(token); r = await get_redis()
    await r.setex(f"verify:{payload['jti']}", 900, str(current_user.id))
    return {"message": "Verification token generated.", "verify_token": token}

class VerifyReq(BaseModel):
    verify_token: str

@router.post("/verify-phone")
async def verify_phone(data: VerifyReq, db: AsyncSession = Depends(get_db)):
    try: payload = decode_token(data.verify_token)
    except: raise HTTPException(400, "Invalid token")
    if payload.get("type") != "otp" or payload.get("purpose") != "phone_verify":
        raise HTTPException(400, "Wrong token type")
    r = await get_redis(); uid = await r.getdel(f"verify:{payload['jti']}")
    if not uid: raise HTTPException(400, "Token used or expired")
    result = await db.execute(select(User).where(User.id == int(uid)))
    user = result.scalar_one_or_none()
    if user: user.is_verified = True; await db.flush()
    return {"message": "Phone verified! ✅"}

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

class FarmerConversionRequest(BaseModel):
    terms_accepted: bool

@router.post("/farmer-conversion/request")
async def request_farmer_conversion(data: FarmerConversionRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.role == "admin":
        raise HTTPException(403, "Admin accounts cannot be converted")
    if current_user.role == "farmer":
        raise HTTPException(400, "Account is already a farmer account")
    if not data.terms_accepted:
        raise HTTPException(400, "You must accept the terms and agreement")
    if current_user.farmer_conversion_status == "pending":
        raise HTTPException(400, "Your conversion request is already pending")
    current_user.farmer_conversion_status = "pending"
    current_user.farmer_terms_accepted = True
    current_user.farmer_conversion_requested_at = datetime.now(timezone.utc)
    current_user.farmer_conversion_reviewed_at = None
    current_user.farmer_conversion_reviewed_by = None
    await db.flush()
    return {"status": "pending", "message": "Request sent to admin for review"}

@router.get("/farmer-conversion/status")
async def farmer_conversion_status(current_user: User = Depends(get_current_user)):
    return {
        "status": current_user.farmer_conversion_status or "not_requested",
        "role": current_user.role,
        "requested_at": current_user.farmer_conversion_requested_at,
    }

@router.put("/me", response_model=UserOut)
async def update_profile(data: UserUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    await db.flush(); await db.refresh(current_user); return current_user

@router.get("/sessions")
async def list_sessions(current_user: User = Depends(get_current_user)):
    r = await get_redis(); keys = await r.keys(f"rt:{current_user.id}:*")
    return {"active_sessions": len(keys)}

@router.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user: raise HTTPException(404, "User not found")
    return user
