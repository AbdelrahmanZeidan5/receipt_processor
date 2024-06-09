from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime, time
from typing import Dict
import math
from .models import Receipt

app = FastAPI()

# In-memory storage for receipts
receipts: Dict[str, int] = {}

@app.post("/receipts/process")
async def process_receipt(receipt: Receipt):
    """
    Process a receipt and calculate points based on predefined rules.

    Args:
        receipt (Receipt): The receipt to process.

    Returns:
        dict: A dictionary containing the unique ID of the processed receipt.
    """
    receipt_id = str(uuid4())
    receipts[receipt_id] = calculate_points(receipt)
    return {"id": receipt_id}


@app.get("/receipts/{receipt_id}/points")
async def get_points(receipt_id: str):
    """
    Retrieve the points for a given receipt ID.

    Args:
        receipt_id (str): The unique ID of the receipt.

    Returns:
        dict: A dictionary containing the points awarded for the receipt.

    Raises:
        HTTPException: If the receipt ID is not found.
    """
    if receipt_id in receipts:
        return {"points": receipts[receipt_id]}
    else:
        raise HTTPException(status_code=404, detail="Receipt not found")


def calculate_points(receipt: Receipt) -> int:
    """
    Calculate points for a given receipt based on predefined rules.

    Args:
        receipt (Receipt): The receipt for which to calculate points.

    Returns:
        int: The total points awarded for the receipt.
    """
    points = 0
    
    # One point for every alphanumeric character in the retailer name
    points += sum(c.isalnum() for c in receipt.retailer)
    
    # 50 points if the total is a round dollar amount with no cents
    total_float = float(receipt.total)
    if total_float.is_integer():
        points += 50
    
    # 25 points if the total is a multiple of 0.25
    if total_float % 0.25 == 0:
        points += 25
    
    # 5 points for every two items on the receipt
    points += (len(receipt.items) // 2) * 5
    
    # If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer
    for item in receipt.items:
        trimmed_length = len(item.shortDescription.strip())
        if trimmed_length % 3 == 0:
            points += math.ceil(float(item.price) * 0.2)
    
    # 6 points if the day in the purchase date is odd
    purchase_date = datetime.strptime(receipt.purchaseDate, "%Y-%m-%d")
    if purchase_date.day % 2 != 0:
        points += 6
    
    # 10 points if the time of purchase is after 2:00pm and before 4:00pm
    purchase_time = datetime.strptime(receipt.purchaseTime, "%H:%M").time()
    start_time = time(14, 0)
    end_time = time(16, 0)
    if start_time < purchase_time < end_time:
        points += 10

    return points