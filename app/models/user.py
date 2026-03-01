from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class LoginPayload(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")

    username: str

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
