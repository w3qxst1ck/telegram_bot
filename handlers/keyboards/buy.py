# from aiogram.types import InlineKeyboardButton
# from aiogram.utils.keyboard import InlineKeyboardBuilder
# from handlers.buttons import menu as btn
#
#
# def buy_keyboard(back_bnt: bool = None) -> InlineKeyboardBuilder:
#     """Клавиатура сообщения с покупкой"""
#     keyboard = InlineKeyboardBuilder()
#
#     keyboard.row(
#         InlineKeyboardButton(text=f"1 мес.", callback_data="buy_sub|1"),
#         InlineKeyboardButton(text=f"3 мес.", callback_data="buy_sub|3")
#     )
#     keyboard.row(
#         InlineKeyboardButton(text=f"6 мес.", callback_data="buy_sub|6"),
#         InlineKeyboardButton(text=f"12 мес.", callback_data="buy_sub|12")
#     )
#     keyboard.row(InlineKeyboardButton(text=f"{btn.BALANCE}", callback_data="balance"))
#
#     if back_bnt:
#         keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu"))
#
#     return keyboard
#
#
# def payment_confirm_keyboard() -> InlineKeyboardBuilder:
#     """Клавиатура с кнопкой подтверждения оплаты"""
#     keyboard = InlineKeyboardBuilder()
#     keyboard.row(
#         InlineKeyboardButton(
#             text="Оплатил(а)", callback_data=f"paid")
#     )
#
#     return keyboard
#
#
# def not_enough_balance_keyboard() -> InlineKeyboardBuilder:
#     """Клавиатура для сообщения при недостаточном балансе"""
#     keyboard = InlineKeyboardBuilder()
#
#     keyboard.row(InlineKeyboardButton(text=f"{btn.BALANCE}", callback_data="balance"))
#     keyboard.row(InlineKeyboardButton(text=f"{btn.BACK}", callback_data="menu|buy"))
#
#     return keyboard
#
#
# def cancel_keyboard() -> InlineKeyboardBuilder:
#     """Клавиатура для отмены пополнения баланса"""
#     keyboard = InlineKeyboardBuilder()
#     keyboard.row(InlineKeyboardButton(text="❌ Отмена", callback_data="button_cancel"))
#     return keyboard