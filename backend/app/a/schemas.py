from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .models import OrderStatus

class ProductOut(BaseModel):
    id: int
    sku: str
    name: str
    price: int
    stock: int

class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)

class OrderCreateIn(BaseModel):
    items: List[OrderItemIn]

class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    unit_price: int
    product_name: str

class OrderOut(BaseModel):
    id: int
    status: OrderStatus
    total_amount: int
    created_at: datetime
    items: List[OrderItemOut]

class OrderListOut(BaseModel):
    id: int
    status: OrderStatus
    total_amount: int
    created_at: datetime
