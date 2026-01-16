from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from ...db.session import get_db
from ...models.order import Order
from ...api.deps import get_current_user
from ...schemas.order import (
    OrderCreateResponse,
    OrderTransitionRequest,
    OrderTransitionResponse,
)
from ...core.errors import AppError, ErrorCode
from ...services.order_state_machine import (
    Role,
    validate_transition,
    parse_status,
    parse_action,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderCreateResponse)
def create_order(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # 最小订单：先不含 customer/items，只为练状态机
    order = Order(status="CREATED")
    db.add(order)
    db.commit()
    db.refresh(order)
    return OrderCreateResponse(id=order.id, status=order.status)


@router.get("/{order_id}", response_model=OrderCreateResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    order = db.execute(select(Order).where(Order.id == order_id)).scalar_one_or_none()
    if not order:
        raise AppError(
            error_code=ErrorCode.ORDER_NOT_FOUND,
            message="Order not found",
            http_status=404,
            details={"order_id": order_id},
        )
    return OrderCreateResponse(id=order.id, status=order.status)


@router.post("/{order_id}/transition", response_model=OrderTransitionResponse)
def transition_order(
    order_id: int,
    payload: OrderTransitionRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    order = db.execute(select(Order).where(Order.id == order_id)).scalar_one_or_none()
    if not order:
        raise AppError(
            error_code=ErrorCode.ORDER_NOT_FOUND,
            message="Order not found",
            http_status=404,
            details={"order_id": order_id},
        )

    from_status_enum = parse_status(order.status)
    action_enum = parse_action(payload.action)

    # user.role 是 "ADMIN"/"CS"/"WH"
    role_enum = Role(user.role)

    to_status_enum = validate_transition(
        role=role_enum,
        from_status=from_status_enum,
        action=action_enum,
    )

    order.status = to_status_enum.value
    db.add(order)
    db.commit()
    db.refresh(order)

    return OrderTransitionResponse(
        id=order.id,
        from_status=from_status_enum.value,
        to_status=to_status_enum.value,
    )
