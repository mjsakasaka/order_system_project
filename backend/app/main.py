from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .config import settings
from .db import Base, engine, get_db
from . import crud
from .schemas import ProductOut, OrderCreateIn, OrderOut, OrderListOut

app = FastAPI(title="Order Management System (MVP)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- error handling ---
@app.exception_handler(crud.BizError)
def biz_error_handler(_, exc: crud.BizError):
    return JSONResponse(
        status_code=400,
        content={"error": exc.code, "message": exc.message},
    )

@app.on_event("startup")
def on_startup():
    # MVP 直接用 create_all，后面你再换 Alembic
    Base.metadata.create_all(bind=engine)
    # seed
    from .db import SessionLocal
    db = SessionLocal()
    try:
        crud.seed_products(db)
    finally:
        db.close()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/products", response_model=list[ProductOut])
def products(db: Session = Depends(get_db)):
    return crud.list_products(db)

@app.post("/orders", response_model=OrderOut)
def create_order(payload: OrderCreateIn, db: Session = Depends(get_db)):
    items = [(it.product_id, it.quantity) for it in payload.items]
    order = crud.create_order(db, items)
    return _to_order_out(order)

@app.get("/orders", response_model=list[OrderListOut])
def orders(status: str | None = None, db: Session = Depends(get_db)):
    rows = crud.list_orders(db, status=status)
    return [
        OrderListOut(
            id=o.id, status=o.status, total_amount=o.total_amount, created_at=o.created_at
        )
        for o in rows
    ]

@app.get("/orders/{order_id}", response_model=OrderOut)
def order_detail(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id)
    return _to_order_out(order)

@app.post("/orders/{order_id}/pay", response_model=OrderOut)
def pay(order_id: int, db: Session = Depends(get_db)):
    order = crud.pay_order(db, order_id)
    return _to_order_out(order)

@app.post("/orders/{order_id}/ship", response_model=OrderOut)
def ship(order_id: int, db: Session = Depends(get_db)):
    order = crud.ship_order(db, order_id)
    return _to_order_out(order)

@app.post("/orders/{order_id}/cancel", response_model=OrderOut)
def cancel(order_id: int, db: Session = Depends(get_db)):
    order = crud.cancel_order(db, order_id)
    return _to_order_out(order)

def _to_order_out(order):
    return OrderOut(
        id=order.id,
        status=order.status,
        total_amount=order.total_amount,
        created_at=order.created_at,
        items=[
            {
                "product_id": it.product_id,
                "quantity": it.quantity,
                "unit_price": it.unit_price,
                "product_name": it.product.name if it.product else "",
            }
            for it in order.items
        ],
    )
