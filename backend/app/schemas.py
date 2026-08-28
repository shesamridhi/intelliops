from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models import Role, OrderStatus


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    role: Role = Role.STAFF


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------- Inventory ----------
class InventoryItemCreate(BaseModel):
    sku: str
    name: str
    quantity: int = 0
    reorder_threshold: int = 10
    unit_price: float = 0.0


class InventoryItemOut(InventoryItemCreate):
    id: str
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------- Orders ----------
class OrderCreate(BaseModel):
    item_sku: str
    quantity: int = Field(gt=0)


class OrderOut(BaseModel):
    id: str
    item_sku: str
    quantity: int
    status: OrderStatus
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


# ---------- Dashboard ----------
class DashboardStats(BaseModel):
    total_orders: int
    pending_orders: int
    low_stock_items: int
    total_inventory_value: float
    cached: bool = False


# ---------- AI Agent ----------
class AgentQuery(BaseModel):
    prompt: str


class AgentResponse(BaseModel):
    answer: str
    provider_used: str
    actions_taken: list[str] = []
