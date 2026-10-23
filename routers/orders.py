from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from dependencies import require_role
from models import User
from schemas import OrderCreate, OrderOut, OrderStatusUpdate
from services.order_service import cancel_order, create_order, get_order_for_user, list_all_orders, list_my_orders, list_seller_orders, update_order_status

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("", response_model=OrderOut, status_code=201)
def place_order(data: OrderCreate, db: Session = Depends(get_db), user: User = Depends(require_role("customer"))):
    return create_order(db, data, user)

@router.get("/my", response_model=list[OrderOut])
def my_orders(db: Session = Depends(get_db), user: User = Depends(require_role("customer"))):
    return list_my_orders(db, user)

@router.get("/seller", response_model=list[OrderOut])
def seller_orders(db: Session = Depends(get_db), user: User = Depends(require_role("seller", "admin"))):
    return list_seller_orders(db, user)

@router.get("", response_model=list[OrderOut])
def all_orders(db: Session = Depends(get_db), user: User = Depends(require_role("admin"))):
    return list_all_orders(db)

@router.get("/{order_id}", response_model=OrderOut)
def order_detail(order_id: int, db: Session = Depends(get_db), user: User = Depends(require_role("customer", "seller", "admin"))):
    return get_order_for_user(db, order_id, user)

@router.patch("/{order_id}/cancel", response_model=OrderOut)
def order_cancel(order_id: int, db: Session = Depends(get_db), user: User = Depends(require_role("customer"))):
    return cancel_order(db, order_id, user)

@router.patch("/{order_id}/status", response_model=OrderOut)
def order_status(order_id: int, data: OrderStatusUpdate, db: Session = Depends(get_db), user: User = Depends(require_role("admin"))):
    return update_order_status(db, order_id, data.status)

# Requested seller-scoped URL: GET /seller/orders
seller_router = APIRouter(prefix="/seller", tags=["Seller Orders"])

@seller_router.get("/orders", response_model=list[OrderOut])
def seller_orders_endpoint(db: Session = Depends(get_db), user: User = Depends(require_role("seller", "admin"))):
    return list_seller_orders(db, user)
