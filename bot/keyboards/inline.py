from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_tariffs_keyboard() -> InlineKeyboardMarkup:
    """Tariffs selection"""
    builder = InlineKeyboardBuilder()
    
    # Prices are hardcoded here for simplicity, matching what we will use in logic
    builder.row(
        InlineKeyboardButton(text="🔹 Basic - 1 oy - 50,000 so'm", callback_data="tariff:basic:50000")
    )
    builder.row(
        InlineKeyboardButton(text="⭐ Standard - 3 oy - 120,000 so'm", callback_data="tariff:standard:120000")
    )
    builder.row(
        InlineKeyboardButton(text="👑 Premium - 1 yil - 400,000 so'm", callback_data="tariff:premium:400000")
    )
    
    return builder.as_markup()


def get_payment_methods_keyboard(amount: int, tariff: str) -> InlineKeyboardMarkup:
    """Payment methods selection"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💳 Payme", callback_data=f"pay:{amount}:payme:{tariff}"),
        InlineKeyboardButton(text="💳 Click", callback_data=f"pay:{amount}:click:{tariff}")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")
    )
    
    return builder.as_markup()


def get_payment_link_keyboard(payment_link: str, payment_id: int) -> InlineKeyboardMarkup:
    """Payment link keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💳 To'lovga o'tish", url=payment_link)
    )
    builder.row(
        InlineKeyboardButton(text="✅ To'lov qildim", callback_data=f"check:{payment_id}")
    )
    
    return builder.as_markup()


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard for subscribed users"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="Django Payme Integratsiyasi", url="https://youtu.be/beIJGe2ftcw?si=83fLzcIVd-j20fWy")
    )
    builder.row(
        InlineKeyboardButton(text="Django Click Integratsiyasi", url="https://youtu.be/7q7-c72tHpc?si=puYQnQVSPLJB5idB")
    )
    builder.row(
        InlineKeyboardButton(text="👤 Mening hisobim", callback_data="my_profile")
    )
    
    return builder.as_markup()
