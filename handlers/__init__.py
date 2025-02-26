from aiogram import Router
from handlers.admin import router as admin_router
from handlers.users import router as user_router
from handlers.start import router as start_router
from handlers.keys import router as keys_router
from handlers.buy_menu import router as buy_router
from handlers.new_key import router as new_key_router
from handlers.balance import router as balance_router

main_router = Router()

main_router.include_routers(
    start_router,
    admin_router,
    user_router,
    keys_router,
    buy_router,
    new_key_router,
    balance_router
)
