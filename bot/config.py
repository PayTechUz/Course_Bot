from environs import Env

env = Env()
env.read_env()

# Bot
BOT_TOKEN = env.str("BOT_TOKEN")
ADMIN_IDS = list(map(int, env.list("ADMIN_IDS", [])))

# Webhook (ngrok or domain)
WEBHOOK_HOST = env.str("WEBHOOK_HOST", "https://muhammadali-akbarov.jprq.live")
WEBHOOK_PATH = f"/api/bot/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Server
HOST = env.str("HOST", "0.0.0.0")
PORT = env.int("PORT", 8000)

# Payment Gateways
PAYME_ID = env.str("PAYME_ID")
PAYME_KEY = env.str("PAYME_KEY")

CLICK_SERVICE_ID = env.str("CLICK_SERVICE_ID")
CLICK_MERCHANT_ID = env.str("CLICK_MERCHANT_ID")
CLICK_MERCHANT_USER_ID = env.str("CLICK_MERCHANT_USER_ID")
CLICK_SECRET_KEY = env.str("CLICK_SECRET_KEY")

ATMOS_CONSUMER_KEY = env.str("ATMOS_CONSUMER_KEY")
ATMOS_CONSUMER_SECRET = env.str("ATMOS_CONSUMER_SECRET")
ATMOS_STORE_ID = env.str("ATMOS_STORE_ID")
ATMOS_TERMINAL_ID = env.str("ATMOS_TERMINAL_ID")
ATMOS_API_KEY = env.str("ATMOS_API_KEY")

IS_TEST_MODE = env.bool("IS_TEST_MODE", True)
