import json
from fastapi import APIRouter, Request, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from paytechuz.integrations.fastapi import PaymeWebhookHandler, ClickWebhookHandler
from paytechuz.gateways.atmos.webhook import AtmosWebhookHandler

from bot import config
from bot.database import get_db, Payment, complete_payment, cancel_payment, get_payment
from bot.loader import bot

from datetime import datetime
from bot.keyboards.inline import get_main_menu_keyboard
from bot.database import get_db, Payment, complete_payment, cancel_payment, get_payment, get_user

router = APIRouter(prefix="/api/payments", tags=["payments"])


async def send_success_notification(payment_id: int):
    payment = get_payment(payment_id)
    if payment and payment.message_id and payment.user_id:
        user = get_user(payment.user_id)
        days_left = (user.subscription_end_date - datetime.utcnow()).days
        
        try:
            # Delete old payment message or edit it to success
            await bot.delete_message(chat_id=payment.user_id, message_id=payment.message_id)
            
            # Send new Welcome message
            await bot.send_message(
                chat_id=payment.user_id,
                text=f"✅ <b>To'lov muvaffaqiyatli amalga oshirildi!</b>\n\n"
                     f"Sizning obunangiz faol.\n"
                     f"Tarif: <b>{user.current_plan.upper()}</b>\n"
                     f"Qolgan vaqt: <b>{days_left} kun</b>\n\n"
                     "Quyidagi havolalar orqali kurslarni ko'rishingiz mumkin:",
                reply_markup=get_main_menu_keyboard()
            )
        except Exception as e:
            print(f"Failed to notify user: {e}")


class PaymeWebhook(PaymeWebhookHandler):
    def successfully_payment(self, params, transaction):
        complete_payment(int(transaction.account_id))
        if hasattr(self, 'background_tasks') and self.background_tasks:
            self.background_tasks.add_task(send_success_notification, int(transaction.account_id))

    def cancelled_payment(self, params, transaction):
        cancel_payment(int(transaction.account_id))


class ClickWebhook(ClickWebhookHandler):
    def successfully_payment(self, params, transaction):
        complete_payment(int(transaction.account_id))
        if hasattr(self, 'background_tasks') and self.background_tasks:
            self.background_tasks.add_task(send_success_notification, int(transaction.account_id))

    def cancelled_payment(self, params, transaction):
        cancel_payment(int(transaction.account_id))


@router.post("/payme/webhook/")
async def payme_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    handler = PaymeWebhook(
        payme_id=config.PAYME_ID,
        payme_key=config.PAYME_KEY,
        db=db,
        account_model=Payment,
        account_field='id',
        amount_field='amount'
    )
    handler.background_tasks = background_tasks
    return await handler.handle_webhook(request)


@router.post("/click/webhook/")
async def click_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    handler = ClickWebhook(
        service_id=config.CLICK_SERVICE_ID,
        secret_key=config.CLICK_SECRET_KEY,
        db=db,
        account_model=Payment,
        account_field='id',
        amount_field='amount'
    )
    handler.background_tasks = background_tasks
    return await handler.handle_webhook(request)


@router.post("/atmos/webhook/")
async def atmos_webhook(request: Request, background_tasks: BackgroundTasks):
    handler = AtmosWebhookHandler(
        api_key=config.ATMOS_API_KEY
    )
    try:
        data = json.loads(await request.body())
        response = handler.handle_webhook(data)
        if response["status"] == 1:
            invoice_id = int(data.get("invoice"))
            complete_payment(invoice_id)
            background_tasks.add_task(send_success_notification, invoice_id)
        return response
    except Exception as e:
        return {"status": 0, "message": str(e)}
