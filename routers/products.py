from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user, require_role
from models import User
from schemas import ProductCreate, ProductOut, ProductUpdate
from services.product_service import create_product, delete_product, get_product, list_products, update_product

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("", response_model=list[ProductOut])
def products(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    return list_products(db, skip, limit)

@router.get("/{product_id}", response_model=ProductOut)
def product_detail(product_id: int, db: Session = Depends(get_db)):
    return get_product(db, product_id)

@router.post("", response_model=ProductOut, status_code=201)
def product_create(data: ProductCreate, db: Session = Depends(get_db), user: User = Depends(require_role("seller", "admin"))):
    return create_product(db, data, user)

@router.put("/{product_id}", response_model=ProductOut)
def product_update(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), user: User = Depends(require_role("seller", "admin"))):
    return update_product(db, product_id, data, user)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def product_delete(product_id: int, db: Session = Depends(get_db), user: User = Depends(require_role("seller", "admin"))):
    delete_product(db, product_id, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
