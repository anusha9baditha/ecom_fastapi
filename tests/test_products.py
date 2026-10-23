def test_seller_can_create_product(client, make_user, auth_headers):
    make_user("seller", "seller@example.com")
    headers = auth_headers("seller@example.com")
    response = client.post("/products", headers=headers, json={"name": "Keyboard", "description": "USB keyboard", "price": "25.00", "stock_quantity": 8})
    assert response.status_code == 201
    assert response.json()["stock_quantity"] == 8

def test_customer_cannot_create_product(client, make_user, auth_headers):
    make_user("customer", "customer@example.com")
    response = client.post("/products", headers=auth_headers("customer@example.com"), json={"name": "Keyboard", "price": "25.00", "stock_quantity": 8})
    assert response.status_code == 403
