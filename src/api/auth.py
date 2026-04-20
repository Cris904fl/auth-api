import httpx
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from src.core.config import settings
from src.core.security import create_access_token
from src.models.user import TokenResponse, UserCreate, UserLogin
from src.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate):
    svc = UserService()
    if svc.get_by_email(data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = svc.create(data)
    token = create_access_token({"sub": user.user_id, "role": user.role})
    return TokenResponse(access_token=token, user=user.to_out())


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin):
    user = UserService().authenticate(data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.user_id, "role": user.role})
    return TokenResponse(access_token=token, user=user.to_out())


@router.get("/google")
def google_login():
    params = (
        f"?client_id={settings.google_client_id}"
        f"&redirect_uri={settings.google_redirect_uri}"
        f"&response_type=code"
        f"&scope=openid email profile"
    )
    return RedirectResponse(url=GOOGLE_AUTH_URL + params)


@router.get("/google/callback", response_model=TokenResponse)
async def google_callback(code: str):
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange Google token")

        google_token = token_resp.json()["access_token"]
        userinfo_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {google_token}"},
        )
        userinfo = userinfo_resp.json()

    svc = UserService()
    user = svc.get_by_email(userinfo["email"])
    if not user:
        user = svc.create_from_google(
            email=userinfo["email"],
            full_name=userinfo.get("name", ""),
            google_id=userinfo["sub"],
        )

    token = create_access_token({"sub": user.user_id, "role": user.role})
    return TokenResponse(access_token=token, user=user.to_out())
