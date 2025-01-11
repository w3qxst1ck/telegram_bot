from aiogram import Router
from handlers.admin import router as admin_router


main_router = Router()

main_router.include_routers(admin_router)