from models import Product

def test_order_reduces_stock(client, db, make_user, auth_headers):
    customer = make_user("customer", "buyer@example.com")
    seller = make_user("seller", "seller@example.com")
    product = Product(seller_id=seller.id, name="Mouse", description="", price=10, stock_quantity=5, is_active=True)
    db.add(product); db.commit(); db.refresh(product)
    response = client.post("/orders", headers=auth_headers("buyer@example.com"), json={"items": [{"product_id": product.id, "quantity": 2}]})
    assert response.status_code == 201, response.text
    assert float(response.json()["total_amount"]) == 20
    db.refresh(product)
    assert product.stock_quantity == 3

def test_insufficient_stock_rejected(client, db, make_user, auth_headers):
    make_user("customer", "buyer@example.com")
    seller = make_user("seller", "seller@example.com")
    product = Product(seller_id=seller.id, name="Mouse", description="", price=10, stock_quantity=1, is_active=True)
    db.add(product); db.commit(); db.refresh(product)
    response = client.post("/orders", headers=auth_headers("buyer@example.com"), json={"items": [{"product_id": product.id, "quantity": 2}]})
    assert response.status_code == 409
    db.refresh(product)
    assert product.stock_quantity == 1

def test_cancel_restores_stock(client, db, make_user, auth_headers):
    make_user("customer", "buyer@example.com")
    seller = make_user("seller", "seller@example.com")
    product = Product(seller_id=seller.id, name="Mouse", description="", price=10, stock_quantity=5, is_active=True)
    db.add(product); db.commit(); db.refresh(product)
    headers = auth_headers("buyer@example.com")
    order_response = client.post("/orders", headers=headers, json={"items": [{"product_id": product.id, "quantity": 2}]})
    assert order_response.status_code == 201
    order_id = order_response.json()["id"]
    cancel_response = client.patch(f"/orders/{order_id}/cancel", headers=headers)
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"
    db.refresh(product)
    assert product.stock_quantity == 5
