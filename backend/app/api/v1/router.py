from fastapi import APIRouter
from .auth import router as auth_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)

from .orders import router as orders_router

router.include_router(orders_router)