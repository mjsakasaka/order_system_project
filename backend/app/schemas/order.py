from pydantic import BaseModel

class OrderCreateResponse(BaseModel):
    id: int
    status: str

class OrderTransitionRequest(BaseModel):
    action: str
    note: str | None = None  # 先占位，后面做 order_events 会用到

class OrderTransitionResponse(BaseModel):
    id: int
    from_status: str
    to_status: str
