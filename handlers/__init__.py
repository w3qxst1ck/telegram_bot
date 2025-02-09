from aiogram import Router
from handlers.admin import router as admin_router
from handlers.users import router as user_router
from handlers.start import router as start_router

main_router = Router()

main_router.include_routers(
    start_router,
    admin_router,
    user_router,
)
