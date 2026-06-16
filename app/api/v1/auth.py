import re

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="ثبت‌نام کاربر جدید",
    description="یک حساب کاربری جدید می‌سازد. ایمیل باید یکتا باشد و رمز عبور به‌صورت امن (bcrypt) ذخیره می‌شود.",
)
async def register(payload: UserCreate) -> User:
    existing = await User.find_one(User.email == payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=payload.email.strip().lower(),
        fullname=payload.fullname.strip(),
        hashed_password=get_password_hash(payload.password),
    )
    await user.insert()
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="ورود با فرم OAuth2",
    description=(
        "ورود با فرم `application/x-www-form-urlencoded`. "
        "فیلد `username` باید **ایمیل** یا **نام کامل** کاربر باشد (نه نام کاربری جداگانه). "
        "برای استفاده در Swagger Authorize مناسب است."
    ),
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    # Swagger OAuth2 form uses "username" — accept email or fullname
    return await _authenticate(form_data.username, form_data.password)


@router.post(
    "/login/json",
    response_model=Token,
    summary="ورود با JSON",
    description="ورود با بدنه JSON شامل `email` و `password`. ساده‌ترین روش برای تست در Swagger.",
)
async def login_json(payload: LoginRequest) -> Token:
    return await _authenticate(payload.email, payload.password)


async def _find_user(identifier: str) -> User | None:
    identifier = identifier.strip()
    if not identifier:
        return None

    user = await User.find_one(User.email == identifier.lower())
    if user is not None:
        return user

    return await User.find_one(
        {"fullname": {"$regex": f"^{re.escape(identifier)}$", "$options": "i"}}
    )


async def _authenticate(identifier: str, password: str) -> Token:
    user = await _find_user(identifier)
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=create_access_token(str(user.id)))


@router.get(
    "/me",
    response_model=UserRead,
    summary="پروفایل کاربر جاری",
    description="اطلاعات کاربر لاگین‌شده را برمی‌گرداند. نیاز به هدر `Authorization: Bearer <token>` دارد.",
)
async def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
