from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(max_length=100)

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserUpdate(UserBase):
    username: str | None = Field(default=None, max_length=100)
    current_password: str | None = Field(default=None, min_length=8)
    password: str | None = Field(default=None, min_length=8)

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginatedUserResponse(BaseModel):
    users: list[UserResponse]
    total: int
    skip: int
    limit: int
    has_more: bool