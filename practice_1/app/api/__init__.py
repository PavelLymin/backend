from fastapi import APIRouter

from config import settings

from .items import router as items_router
from .auth import router as auth_router
from .students import router as students_router
from .images import router as images_router
from .recipes import router as recipes_router

router = APIRouter(
    prefix=settings.url.prefix,
)

router.include_router(items_router)
router.include_router(auth_router)
router.include_router(students_router)
router.include_router(images_router)
router.include_router(recipes_router)
