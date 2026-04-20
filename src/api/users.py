from fastapi import APIRouter, Depends

from src.api.dependencies import get_current_user, require_admin
from src.models.user import User, UserOut
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user's profile."""
    return current_user.to_out()


@router.get("/", response_model=list[UserOut])
def list_users(admin: User = Depends(require_admin)):
    """Admin only — lists all users."""
    table = UserService().table
    response = table.scan()
    return [User(**item).to_out() for item in response.get("Items", [])]
