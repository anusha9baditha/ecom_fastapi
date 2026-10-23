from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

Role = Literal["customer", "seller"]
OrderStatus = Literal["pending", "confirmed", "shipped", "delivered", "cancelled"]

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Role = "customer"

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    description: str = ""
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock_quantity: int = Field(ge=0)

class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock_quantity: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    seller_id: int
    name: str
    description: str
    price: Decimal
    stock_quantity: int
    is_active: bool

class OrderItemIn(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=10000)

class OrderCreate(BaseModel):
    items: list[OrderItemIn] = Field(min_length=1, max_length=100)

class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal

class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    customer_id: int
    total_amount: Decimal
    status: str
    created_at: datetime
    items: list[OrderItemOut]

class OrderStatusUpdate(BaseModel):
    status: Literal["confirmed", "shipped", "delivered"]
