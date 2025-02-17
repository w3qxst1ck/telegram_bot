from aiogram import Router
from handlers.admin import router as admin_router
from handlers.users import router as user_router
from handlers.start import router as start_router
from handlers.profile import router as profile_router

main_router = Router()

main_router.include_routers(
    start_router,
    admin_router,
    user_router,
    profile_router
)
