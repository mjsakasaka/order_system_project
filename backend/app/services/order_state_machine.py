from enum import Enum
from typing import Dict, Set, Tuple

from ..core.errors import AppError, ErrorCode


class Role(str, Enum):
    ADMIN = "ADMIN"
    CS = "CS"   # customer service
    WH = "WH"   # warehouse


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    PAID = "PAID"
    PACKED = "PACKED"
    SHIPPED = "SHIPPED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"


class OrderAction(str, Enum):
    PAY = "PAY"
    CANCEL = "CANCEL"
    PACK = "PACK"
    SHIP = "SHIP"
    COMPLETE = "COMPLETE"
    REFUND = "REFUND"


# ---- 1) 状态流转规则表： (from_status, action) -> to_status ----
TRANSITIONS: Dict[Tuple[OrderStatus, OrderAction], OrderStatus] = {
    (OrderStatus.CREATED, OrderAction.PAY): OrderStatus.PAID,
    (OrderStatus.CREATED, OrderAction.CANCEL): OrderStatus.CANCELLED,

    (OrderStatus.PAID, OrderAction.PACK): OrderStatus.PACKED,
    (OrderStatus.PAID, OrderAction.REFUND): OrderStatus.REFUNDED,

    (OrderStatus.PACKED, OrderAction.SHIP): OrderStatus.SHIPPED,

    (OrderStatus.SHIPPED, OrderAction.COMPLETE): OrderStatus.COMPLETED,
}

TERMINAL_STATUSES: Set[OrderStatus] = {
    OrderStatus.CANCELLED,
    OrderStatus.REFUNDED,
    OrderStatus.COMPLETED,
}

# ---- 2) 角色权限规则表： role -> allowed actions ----
ROLE_ALLOWED_ACTIONS: Dict[Role, Set[OrderAction]] = {
    Role.ADMIN: {
        OrderAction.PAY,
        OrderAction.CANCEL,
        OrderAction.PACK,
        OrderAction.SHIP,
        OrderAction.COMPLETE,
        OrderAction.REFUND,
    },
    Role.CS: {
        OrderAction.PAY,
        OrderAction.CANCEL,
        # 是否允许退款：你可以按需求调，这里先允许
        OrderAction.REFUND,
    },
    Role.WH: {
        OrderAction.PACK,
        OrderAction.SHIP,
        # COMPLETE 通常由系统或客服/管理员触发，这里先不给仓库
    },
}


def can_role_do_action(role: Role, action: OrderAction) -> bool:
    return action in ROLE_ALLOWED_ACTIONS.get(role, set())


def get_next_status(from_status: OrderStatus, action: OrderAction) -> OrderStatus:
    key = (from_status, action)
    if key not in TRANSITIONS:
        raise AppError(
            error_code=ErrorCode.ORDER_STATE_INVALID,
            message=f"Illegal transition: {from_status} + {action}",
            http_status=409,
            details={"from_status": from_status, "action": action},
        )
    return TRANSITIONS[key]


def validate_transition(
    *,
    role: Role,
    from_status: OrderStatus,
    action: OrderAction,
) -> OrderStatus:
    # 终态不允许再流转
    if from_status in TERMINAL_STATUSES:
        raise AppError(
            error_code=ErrorCode.ORDER_STATE_INVALID,
            message=f"Order is in terminal status: {from_status}",
            http_status=409,
            details={"from_status": from_status, "action": action},
        )

    # 角色权限校验
    if not can_role_do_action(role, action):
        raise AppError(
            error_code=ErrorCode.AUTH_FORBIDDEN,
            message=f"Role {role} is not allowed to perform action {action}",
            http_status=403,
            details={"role": role, "action": action},
        )

    # 状态机校验
    return get_next_status(from_status, action)

def parse_status(status_str: str) -> OrderStatus:
    try:
        return OrderStatus(status_str)
    except ValueError:
        raise AppError(
            error_code=ErrorCode.ORDER_STATE_INVALID,
            message=f"Unknown order status: {status_str}",
            http_status=409,
            details={"status": status_str},
        )

def parse_action(action_str: str) -> OrderAction:
    try:
        return OrderAction(action_str)
    except ValueError:
        raise AppError(
            error_code=ErrorCode.ORDER_STATE_INVALID,
            message=f"Unknown order action: {action_str}",
            http_status=409,
            details={"action": action_str},
        )
