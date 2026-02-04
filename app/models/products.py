from typing import Optional

from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    stock: int
    sku: str
