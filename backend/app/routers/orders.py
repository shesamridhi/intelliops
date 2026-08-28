from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order, InventoryItem, Role, User
from app.schemas import OrderCreate, OrderOut, OrderStatusUpdate
from app.auth import get_current_user, require_roles
from app.redis_client import cache_invalidate
from app.websocket_manager import manager

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Order).order_by(Order.created_at.desc()).all()


@router.post("", response_model=OrderOut, status_code=201)
async def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    item = db.query(InventoryItem).filter(InventoryItem.sku == payload.item_sku).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    if item.quantity < payload.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    order = Order(item_sku=payload.item_sku, quantity=payload.quantity, created_by=user.id)
    item.quantity -= payload.quantity
    db.add(order)
    db.commit()
    db.refresh(order)

    cache_invalidate("dashboard:stats")
    await manager.broadcast("order_created", {"id": order.id, "sku": order.item_sku, "status": order.status.value})
    return order


@router.patch("/{order_id}/status", response_model=OrderOut)
async def update_status(
    order_id: str,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(Role.ADMIN, Role.MANAGER)),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = payload.status
    db.commit()
    db.refresh(order)

    cache_invalidate("dashboard:stats")
    await manager.broadcast("order_status_changed", {"id": order.id, "status": order.status.value})
    return order
