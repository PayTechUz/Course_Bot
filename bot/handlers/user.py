from contextlib import suppress
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from bot.gateways import get_gateway
from bot.database import create_payment, get_payment, set_payment_message_id, get_or_create_user, get_user
from bot.keyboards.inline import get_payment_methods_keyboard, get_payment_link_keyboard, get_tariffs_keyboard, get_main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = get_or_create_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    
    if user.is_subscription_active:
        # Show main menu for subscribed users
        await show_main_menu(message, user)
    else:
        # Show tariffs
        await message.answer(
            f"👋 <b>Assalomu alaykum, {message.from_user.full_name}!</b>\n\n"
            "Botdagi maxsus kurslardan foydalanish uchun obuna bo'lishingiz kerak.\n"
            "Iltimos, o'zingizga mos tarifni tanlang:",
            reply_markup=get_tariffs_keyboard()
        )


async def show_main_menu(message: Message, user):
    days_left = (user.subscription_end_date - datetime.utcnow()).days
    await message.answer(
        f"✅ <b>Xush kelibsiz!</b>\n\n"
        f"Sizning obunangiz faol.\n"
        f"Tarif: <b>{user.current_plan.upper() if user.current_plan else 'Nomsiz'}</b>\n"
        f"Qolgan vaqt: <b>{days_left} kun</b>\n\n"
        "Quyidagi havolalar orqali kurslarni ko'rishingiz mumkin:",
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data.startswith("tariff:"))
async def select_tariff(callback: CallbackQuery):
    _, tariff_name, price_str = callback.data.split(":")
    price = int(price_str)
    
    with suppress(TelegramBadRequest):
        await callback.answer()
        
    await callback.message.edit_text(
        f"💰 <b>Tarif: {tariff_name.upper()}</b>\n"
        f"Summa: {price:,} so'm\n\n"
        "To'lov usulini tanlang:",
        reply_markup=get_payment_methods_keyboard(price, tariff_name)
    )


@router.callback_query(F.data.startswith("pay:"))
async def create_payment_link(callback: CallbackQuery):
    with suppress(TelegramBadRequest):
        await callback.answer("⏳ To'lov yaratilmoqda...")
        
    # data format: pay:{amount}:{method}:{tariff}
    parts = callback.data.split(":")
    amount = int(parts[1])
    method = parts[2]
    tariff = parts[3]
    
    # 1. DB da to'lov yaratish
    payment = create_payment(callback.from_user.id, amount, method, tariff)
    
    # 2. Gateway orqali link olish
    gateway = get_gateway(method)
    payment_link = None
    
    # Get bot username for return_url (optional, assuming 'demorepresentrobot' from logs)
    bot_username = "demorepresentrobot" 
    
    try:
        if method == "payme":
            payment_link = gateway.create_payment(
                id=str(payment.id),
                amount=amount,
                return_url=f"https://t.me/{bot_username}"
            )
        elif method == "click":
            payment_link = gateway.create_payment(
                id=str(payment.id),
                amount=amount,
                return_url=f"https://t.me/{bot_username}"
            )
        elif method == "atmos":
            result = gateway.create_payment(
                account_id=str(payment.id),
                amount=amount * 100
            )
            payment_link = result.get("payment_url")
            
        if payment_link:
            await callback.message.edit_text(
                f"💳 <b>To'lov #{payment.id}</b>\n"
                f"Tarif: {tariff.upper()}\n"
                f"Summa: {amount:,} so'm\n\n"
                f"To'lovni amalga oshirish uchun quyidagi tugmani bosing:",
                reply_markup=get_payment_link_keyboard(payment_link, payment.id)
            )
            set_payment_message_id(payment.id, callback.message.message_id)
        else:
            await callback.message.edit_text("❌ Xatolik: Havola olinmadi", reply_markup=get_tariffs_keyboard())
            
    except Exception as e:
        await callback.message.edit_text(f"❌ Xatolik: {str(e)}", reply_markup=get_tariffs_keyboard())


@router.callback_query(F.data.startswith("check:"))
async def check_payment_status(callback: CallbackQuery):
    pid = int(callback.data.split(":")[1])
    payment = get_payment(pid)
    
    if payment and payment.status == "paid":
        with suppress(TelegramBadRequest):
            await callback.answer("✅ To'langan!", show_alert=True)
            
        # Userni yangilash
        user = get_user(payment.user_id)
        
        # O'chirib, Main menuni chiqarish yoki edit qilish
        await callback.message.delete()
        await show_main_menu(callback.message, user)
    else:
        with suppress(TelegramBadRequest):
            await callback.answer("⏳ Hali to'lanmagan", show_alert=True)


@router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    with suppress(TelegramBadRequest):
        await callback.answer("❌ Bekor qilindi")
    
    # Startga qaytadi
    await callback.message.delete()
    await cmd_start(callback.message)


@router.callback_query(F.data == "my_profile")
async def my_profile(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Profil topilmadi")
        return

    days_left = (user.subscription_end_date - datetime.utcnow()).days
    if days_left < 0:
        days_left = 0
        
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            f"👤 <b>Mening profilim</b>\n\n"
            f"🆔 ID: {user.telegram_id}\n"
            f"👤 Ism: {user.full_name}\n"
            f"📅 Tarif: <b>{user.current_plan.upper()}</b>\n"
            f"⏳ Qolgan vaqt: <b>{days_left} kun</b>\n"
            f"📅 Tugash sanasi: {user.subscription_end_date.strftime('%Y-%m-%d %H:%M')}",
            reply_markup=get_main_menu_keyboard()
        )
