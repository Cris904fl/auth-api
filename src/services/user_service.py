from typing import Optional

from boto3.dynamodb.conditions import Attr

from src.core.database import get_users_table
from src.core.security import hash_password, verify_password
from src.models.user import AuthProvider, User, UserCreate


class UserService:
    def __init__(self):
        self.table = get_users_table()

    def get_by_email(self, email: str) -> Optional[User]:
        response = self.table.scan(FilterExpression=Attr("email").eq(email))
        items = response.get("Items", [])
        return User(**items[0]) if items else None

    def get_by_id(self, user_id: str) -> Optional[User]:
        response = self.table.get_item(Key={"user_id": user_id})
        item = response.get("Item")
        return User(**item) if item else None

    def create(self, data: UserCreate) -> User:
        user = User(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
        )
        self.table.put_item(Item=user.to_dynamo())
        return user

    def create_from_google(self, email: str, full_name: str, google_id: str) -> User:
        user = User(
            user_id=f"google_{google_id}",
            email=email,
            full_name=full_name,
            provider=AuthProvider.google,
        )
        self.table.put_item(Item=user.to_dynamo())
        return user

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(email)
        if not user or not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
