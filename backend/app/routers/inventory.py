from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import InventoryItem, Role
from app.schemas import InventoryItemCreate, InventoryItemOut
from app.auth import get_current_user, require_roles
from app.redis_client import cache_invalidate

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("", response_model=list[InventoryItemOut])
def list_items(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(InventoryItem).all()


@router.post("", response_model=InventoryItemOut, status_code=201)
def create_item(
    payload: InventoryItemCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(Role.ADMIN, Role.MANAGER)),
):
    if db.query(InventoryItem).filter(InventoryItem.sku == payload.sku).first():
        raise HTTPException(status_code=400, detail="SKU already exists")
    item = InventoryItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    cache_invalidate("dashboard:stats")  # keep cached dashboard consistent
    return item


@router.patch("/{sku}/quantity", response_model=InventoryItemOut)
def adjust_quantity(
    sku: str,
    delta: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(Role.ADMIN, Role.MANAGER, Role.STAFF)),
):
    item = db.query(InventoryItem).filter(InventoryItem.sku == sku).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.quantity = max(0, item.quantity + delta)
    db.commit()
    db.refresh(item)
    cache_invalidate("dashboard:stats")
    return item
