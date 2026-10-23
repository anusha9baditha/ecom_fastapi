def test_register_customer(client):
    response = client.post("/auth/register", json={"name": "Test Customer", "email": "customer@example.com", "password": "TestPass123!", "role": "customer"})
    assert response.status_code == 201
    assert response.json()["role"] == "customer"
    assert "hashed_password" not in response.json()

def test_duplicate_registration(client):
    payload = {"name": "Test Customer", "email": "same@example.com", "password": "TestPass123!", "role": "customer"}
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409
