# E-Commerce Order Management API

FastAPI + SQLAlchemy 2 + MySQL 8 + JWT + Alembic + Docker + pytest.

## Local setup
1. Create and activate a Python 3.11 virtual environment.
2. Run `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env`; set `DATABASE_URL` and a random `JWT_SECRET_KEY`.
4. Create the MySQL database/user specified in `.env`.
5. Initialize migrations once: `alembic init alembic` is not needed because this repository already includes the Alembic environment. Create a revision with `alembic revision --autogenerate -m "create ecommerce tables"` then run `alembic upgrade head`.
6. Run `uvicorn main:app --reload`.
7. Open `http://127.0.0.1:8000/docs`.

## Docker setup
Set `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD`, and `JWT_SECRET_KEY` in `.env`, then run `docker compose up --build -d`. Run migrations in the API container with `docker compose exec api alembic revision --autogenerate -m "create ecommerce tables"` (only when creating the first revision) and `docker compose exec api alembic upgrade head`.

## Tests
`pytest -q`

## Important security note
Public registration intentionally permits only `customer` and `seller`; it does not permit registering an admin account. Create the first admin through a controlled, trusted administrative script or database operation. Never expose an unrestricted public admin-registration endpoint.

## API overview
- `POST /auth/register`, `POST /auth/login`
- `GET /products?skip=0&limit=20`, `GET /products/{id}`
- `POST /products`, `PUT /products/{id}`, `DELETE /products/{id}`
- `POST /orders`, `GET /orders/my`, `GET /orders/{id}`, `PATCH /orders/{id}/cancel`
- `GET /orders` (admin), `GET /seller/orders` (seller)
- `PATCH /orders/{id}/status` (admin)

Use `Authorization: Bearer <access_token>` for protected endpoints.
