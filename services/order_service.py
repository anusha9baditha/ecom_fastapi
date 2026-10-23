from datetime import datetime, timedelta, timezone
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from models import Order, OrderItem, Product, User
from schemas import OrderCreate

ALLOWED_TRANSITIONS = {"pending": {"confirmed", "cancelled"}, "confirmed": {"shipped", "cancelled"}, "shipped": {"delivered"}, "delivered": set(), "cancelled": set()}

def _load_order(db: Session, order_id: int) -> Order:
    order = db.scalar(select(Order).options(selectinload(Order.items)).where(Order.id == order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

def create_order(db: Session, data: OrderCreate, customer: User) -> Order:
    # Combine duplicate product IDs so the request cannot bypass stock checks.
    quantities: dict[int, int] = {}
    for item in data.items:
        quantities[item.product_id] = quantities.get(item.product_id, 0) + item.quantity
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    cutoff = now - timedelta(minutes=10)
    recent = db.scalars(select(Order).options(selectinload(Order.items)).where(Order.customer_id == customer.id, Order.created_at >= cutoff, Order.status != "cancelled")).all()
    requested_signature = tuple(sorted(quantities.items()))
    for old in recent:
        old_signature = tuple(sorted((item.product_id, item.quantity) for item in old.items))
        if old_signature == requested_signature:
            raise HTTPException(status_code=409, detail="Duplicate order detected within 10 minutes")

    try:
        products = {}
        # Lock rows to prevent concurrent orders from overselling stock (MySQL/InnoDB).
        for product_id in sorted(quantities):
            product = db.scalar(select(Product).where(Product.id == product_id).with_for_update())
            if not product or not product.is_active:
                raise HTTPException(status_code=404, detail=f"Product {product_id} not found or inactive")
            if product.stock_quantity < quantities[product_id]:
                raise HTTPException(status_code=409, detail=f"Insufficient stock for product {product_id}")
            products[product_id] = product
        order = Order(customer_id=customer.id, total_amount=Decimal("0.00"), status="pending", created_at=now)
        db.add(order); db.flush()
        total = Decimal("0.00")
        for product_id, quantity in quantities.items():
            product = products[product_id]
            unit_price = Decimal(product.price)
            total += unit_price * quantity
            product.stock_quantity -= quantity
            db.add(OrderItem(order_id=order.id, product_id=product_id, quantity=quantity, unit_price=unit_price))
        order.total_amount = total
        db.commit()
        return _load_order(db, order.id)
    except Exception:
        db.rollback()
        raise

def list_my_orders(db: Session, customer: User):
    return db.scalars(select(Order).options(selectinload(Order.items)).where(Order.customer_id == customer.id).order_by(Order.created_at.desc())).all()

def get_order_for_user(db: Session, order_id: int, user: User) -> Order:
    order = _load_order(db, order_id)
    if user.role == "admin" or order.customer_id == user.id:
        return order
    if user.role == "seller" and any(item.product and item.product.seller_id == user.id for item in order.items):
        return order
    raise HTTPException(status_code=403, detail="You cannot access this order")

def list_all_orders(db: Session):
    return db.scalars(select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc())).all()

def list_seller_orders(db: Session, seller: User):
    orders = db.scalars(select(Order).join(Order.items).join(Product).where(Product.seller_id == seller.id).options(selectinload(Order.items)).distinct().order_by(Order.created_at.desc())).all()
    return orders

def cancel_order(db: Session, order_id: int, customer: User) -> Order:
    order = _load_order(db, order_id)
    if order.customer_id != customer.id:
        raise HTTPException(status_code=403, detail="You can only cancel your own orders")
    if order.status != "pending":
        raise HTTPException(status_code=409, detail="Only pending orders can be cancelled")
    try:
        for item in order.items:
            product = db.scalar(select(Product).where(Product.id == item.product_id).with_for_update())
            if product:
                product.stock_quantity += item.quantity
        order.status = "cancelled"
        db.commit()
        return _load_order(db, order.id)
    except Exception:
        db.rollback(); raise

def update_order_status(db: Session, order_id: int, new_status: str) -> Order:
    order = _load_order(db, order_id)
    if new_status not in ALLOWED_TRANSITIONS.get(order.status, set()):
        raise HTTPException(status_code=409, detail=f"Cannot change order status from {order.status} to {new_status}")
    order.status = new_status
    db.commit()
    return _load_order(db, order.id)
