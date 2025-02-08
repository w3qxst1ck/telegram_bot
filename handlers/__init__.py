from aiogram import Router
from handlers.admin import router as admin_router
from handlers.users import router as user_router


main_router = Router()

main_router.include_routers(admin_router, user_router)