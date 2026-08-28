from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Order, InventoryItem, OrderStatus
from app.schemas import DashboardStats
from app.auth import get_current_user
from app.redis_client import cache_get, cache_set

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

CACHE_KEY = "dashboard:stats"


@router.get("/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    cached = cache_get(CACHE_KEY)
    if cached:
        return DashboardStats(**cached, cached=True)

    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
    low_stock_items = db.query(InventoryItem).filter(
        InventoryItem.quantity <= InventoryItem.reorder_threshold
    ).count()
    total_value = db.query(func.sum(InventoryItem.quantity * InventoryItem.unit_price)).scalar() or 0

    stats = {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "low_stock_items": low_stock_items,
        "total_inventory_value": float(total_value),
    }
    cache_set(CACHE_KEY, stats)
    return DashboardStats(**stats, cached=False)
