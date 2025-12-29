from contextlib import asynccontextmanager
from fastapi import FastAPI


# For webhook handling
from aiogram.types import Update

from bot import config
from bot.database import init_db
from bot.handlers.user import router as user_router
from bot.api.payments import router as payments_router
from bot.loader import bot, dp

# Initialize Bot & Dispatcher removed, imported from loader
dp.include_router(user_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    
    # Set Webhook
    if config.WEBHOOK_URL:
        await bot.set_webhook(config.WEBHOOK_URL)
        print(f"🚀 Webhook set to: {config.WEBHOOK_URL}")
    
    yield
    
    # Shutdown
    await bot.delete_webhook()
    await bot.session.close()
    print("👋 Bot stopped")


# Init FastAPI
app = FastAPI(title="Bot Server", version="2.0", lifespan=lifespan)

# Include Payment Webhooks
app.include_router(payments_router)


# Bot Webhook Endpoint
@app.post(config.WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = Update(**update)
    await dp.feed_update(bot, telegram_update)
    return {"ok": True}


@app.get("/")
def root():
    return {
        "status": "ok", 
        "mode": "webhook",
        "bot": "active", 
        "payments": ["payme", "click",]
    }
