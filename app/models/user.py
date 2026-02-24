from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class LoginPayload(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")

    username: str
