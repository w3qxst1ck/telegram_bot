from aiogram import Router
from handlers.admin import router as admin_router
from handlers.users import router as user_router
from handlers.start import router as start_router
from handlers.keys import router as keys_router
from handlers.buy_menu import router as buy_router
from handlers.new_key import router as new_key_router
from handlers.balance import router as balance_router
from handlers.extend_key import router as extend_router
from handlers.trial_key import router as trial_key_router
from handlers.extra_traffic import router as extra_traffic_router
from handlers.delete_key import router as delete_key_router
from handlers.payments import router as payment_router
from handlers.referral import router as referral_router
from handlers.paymaster import router as paymaster_router
from handlers.star_payment import router as star_payment_router

main_router = Router()

main_router.include_routers(
    start_router,
    admin_router,
    user_router,
    keys_router,
    buy_router,
    new_key_router,
    balance_router,
    extend_router,
    trial_key_router,
    extra_traffic_router,
    delete_key_router,
    payment_router,
    referral_router,
    paymaster_router,
    star_payment_router,
)
