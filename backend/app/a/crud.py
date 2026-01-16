from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy import text
from .models import Product, Order, OrderItem, OrderStatus

class BizError(Exception):
    def __init__(self, message: str, code: str = "BIZ_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)

def seed_products(db: Session):
    existing = db.scalar(select(Product.id).limit(1))
    if existing:
        return
    db.add_all([
        Product(sku="SKU-APPLE", name="Apple", price=3000, stock=10),
        Product(sku="SKU-BANANA", name="Banana", price=1500, stock=10),
        Product(sku="SKU-COFFEE", name="Coffee", price=4500, stock=10),
    ])
    db.commit()

def list_products(db: Session):
    return db.scalars(select(Product).order_by(Product.id)).all()

def _lock_product_rows(db: Session, product_ids: list[int]) -> list[Product]:
    # MySQL 行锁：FOR UPDATE，避免并发超卖
    rows = db.execute(
        select(Product).where(Product.id.in_(product_ids)).with_for_update()
    ).scalars().all()
    return rows

def create_order(db: Session, items: list[tuple[int, int]]) -> Order:
    product_ids = [pid for pid, qty in items]
    products = _lock_product_rows(db, product_ids)

    product_map = {p.id: p for p in products}
    for pid, qty in items:
        if pid not in product_map:
            raise BizError(f"Product {pid} not found", "PRODUCT_NOT_FOUND")
        if product_map[pid].stock < qty:
            raise BizError(f"Insufficient stock for product {pid}", "INSUFFICIENT_STOCK")

    order = Order(status=OrderStatus.CREATED, total_amount=0)
    db.add(order)
    db.flush()  # 拿到 order.id

    total = 0
    for pid, qty in items:
        p = product_map[pid]
        p.stock -= qty
        oi = OrderItem(order_id=order.id, product_id=pid, quantity=qty, unit_price=p.price)
        db.add(oi)
        total += p.price * qty

    order.total_amount = total
    db.commit()
    db.refresh(order)
    return order

def get_order(db: Session, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if not order:
        raise BizError("Order not found", "ORDER_NOT_FOUND")
    # items lazy=selectin 已经会加载
    return order

def list_orders(db: Session, status: str | None = None) -> list[Order]:
    stmt = select(Order).order_by(Order.id.desc())
    if status:
        stmt = stmt.where(Order.status == status)
    return db.scalars(stmt).all()

def pay_order(db: Session, order_id: int) -> Order:
    order = get_order(db, order_id)
    if order.status != OrderStatus.CREATED:
        raise BizError("Only CREATED order can be paid", "INVALID_STATUS")
    order.status = OrderStatus.PAID
    db.commit()
    db.refresh(order)
    return order

def ship_order(db: Session, order_id: int) -> Order:
    order = get_order(db, order_id)
    if order.status != OrderStatus.PAID:
        raise BizError("Only PAID order can be shipped", "INVALID_STATUS")
    order.status = OrderStatus.SHIPPED
    db.commit()
    db.refresh(order)
    return order

def cancel_order(db: Session, order_id: int) -> Order:
    order = get_order(db, order_id)
    if order.status != OrderStatus.CREATED:
        raise BizError("Only CREATED order can be cancelled", "INVALID_STATUS")

    # 取消需要把库存加回去：锁住相关商品行
    product_ids = [it.product_id for it in order.items]
    products = _lock_product_rows(db, product_ids)
    pmap = {p.id: p for p in products}
    for it in order.items:
        pmap[it.product_id].stock += it.quantity

    order.status = OrderStatus.CANCELLED
    db.commit()
    db.refresh(order)
    return order
