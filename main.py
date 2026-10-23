import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from dotenv import load_dotenv
from routers import auth, products, orders

load_dotenv()
limiter = Limiter(key_func=get_remote_address, default_limits=[os.getenv("RATE_LIMIT_DEFAULT", "100/minute")])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Use Alembic migrations to create/update tables; do not use create_all in production.
    yield

app = FastAPI(title=os.getenv("APP_NAME", "E-Commerce Order Management API"), version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(orders.seller_router)

@app.get("/")
def root():
    return {"message": "E-Commerce Order Management API", "docs": "/docs", "health": "/health"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Avoid exposing internal exception details in API responses.
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
