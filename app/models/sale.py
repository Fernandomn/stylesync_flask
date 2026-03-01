from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class Sale(BaseModel):
    sale_date: datetime
    product_id: str
    quantity: int
    total_value: float

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
