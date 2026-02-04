from datetime import date

from pydantic import BaseModel


class Sale(BaseModel):
    sale_date: date
    product_id: str
    quantity: int
    total_value: float
