from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Product, User
from schemas import ProductCreate, ProductUpdate

def list_products(db: Session, skip: int = 0, limit: int = 20):
    return db.scalars(select(Product).where(Product.is_active.is_(True)).order_by(Product.id).offset(skip).limit(limit)).all()

def get_product(db: Session, product_id: int, active_only: bool = True) -> Product:
    product = db.get(Product, product_id)
    if not product or (active_only and not product.is_active):
        raise HTTPException(status_code=404, detail="Product not found")
    return product

def create_product(db: Session, data: ProductCreate, seller: User) -> Product:
    product = Product(seller_id=seller.id, **data.model_dump())
    db.add(product); db.commit(); db.refresh(product)
    return product

def update_product(db: Session, product_id: int, data: ProductUpdate, user: User) -> Product:
    product = get_product(db, product_id, active_only=False)
    if user.role != "admin" and product.seller_id != user.id:
        raise HTTPException(status_code=403, detail="You can only update your own products")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit(); db.refresh(product)
    return product

def delete_product(db: Session, product_id: int, user: User) -> None:
    product = get_product(db, product_id, active_only=False)
    if user.role != "admin" and product.seller_id != user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own products")
    # Soft-delete preserves historical order references.
    product.is_active = False
    db.commit()
