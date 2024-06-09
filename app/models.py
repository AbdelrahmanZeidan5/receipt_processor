from pydantic import BaseModel, Field, validator
from typing import List
from datetime import datetime

class Item(BaseModel):
    """Represents an item on the receipt."""
    shortDescription: str = Field(..., min_length=1)
    price: str = Field(..., pattern=r'^\d+(\.\d{1,2})?$')

    @validator('shortDescription')
    def description_not_empty(cls, v):
        """Ensures the short description is not empty or whitespace."""
        if not v.strip():
            raise ValueError('shortDescription cannot be empty or whitespace')
        return v

class Receipt(BaseModel):
    """Represents a receipt with multiple items."""
    retailer: str = Field(..., min_length=1)
    purchaseDate: str
    purchaseTime: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    items: List[Item]
    total: str = Field(..., pattern=r'^\d+(\.\d{1,2})?$')


    @validator('purchaseDate')
    def valid_date(cls, v):
        """Validates and formats the purchase date."""
        date_formats = ["%Y-%m-%d", "%Y/%m/%d"]
        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(v, date_format)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        raise ValueError('purchaseDate must be a valid date in YYYY-MM-DD or YYYY/MM/DD format')


    @validator('purchaseTime')
    def valid_time(cls, v):
        """Validates the purchase time."""
        try:
            hour, minute = map(int, v.split(':'))
            if hour < 0 or hour >= 24 or minute < 0 or minute >= 60:
                raise ValueError
        except ValueError:
            raise ValueError('purchaseTime must be a valid time in HH:MM format')
        return v
