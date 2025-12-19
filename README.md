# 🎓 PayTechUZ Education Bot

Ushbu loyiha **PayTechUZ** kutubxonasi yordamida Telegram bot orqali to'lovlarni qabul qilish va obuna (subscription) tizimini qanday tashkil etish mumkinligini ko'rsatib beradi.

Bot orqali foydalanuvchilar maxsus video darsliklar va kurslarga kirish huquqini sotib olishlari mumkin. To'lovlar **Payme**, **Click** va **Atmos** tizimlari orqali avtomatlashtirilgan.

## ✨ Imkoniyatlar

*   **Obuna tizimi:** Foydalanuvchilar o'zlariga mos tarifni (Basic, Standard, Premium) tanlab, obuna bo'lishlari mumkin.
*   **Avtomatlashtirilgan to'lovlar:** To'lovlar real vaqt rejimida webhook orqali tasdiqlanadi va foydalanuvchi darhol ruxsat oladi.
*   **Maxsus kontent:** To'lov amalga oshirilgandan so'ng, foydalanuvchilarga yopiq video darsliklar (Django Payme/Click integratsiyasi) taqdim etiladi.
*   **Foydalanuvchi profili:** Obuna muddati, tanlangan tarif va statusni kuzatib borish imkoniyati.

## 🚀 Ishga tushirish

Loyihani o'z kompyuteringizda ishga tushirish uchun quyidagi qadamlarni bajaring:

### 1. Loyihani yuklab olish va kutubxonalarni o'rnatish

```bash
git clone https://github.com/PayTechUz/fastapi_paytechuz.git
cd fastapi_paytechuz
pip install -r requirements.txt
```

### 2. Sozlamalarni kiritish

`.env.example` faylidan nusxa olib, `.env` faylini yarating va keraksi ma'lumotlarni to'ldiring:

```bash
cp .env.example .env
```

`.env` faylida quyidagi ma'lumotlar bo'lishi kerak:
*   `BOT_TOKEN`: Telegram bot tokeni.
*   Merchant ID va kalitlari (Payme, Click, Atmos uchun).

### 3. Dasturni ishga tushirish

Loyiha **FastAPI** (webhook serveri) va **Aiogram** (bot) yordamida ishlaydi. Ularni bitta buyruq orqali ishga tushirish mumkin:

```bash
python -m bot.main
```

_Eslatma: Bu buyruq ham Webhook serverini (FastAPI), ham Telegram botni bir vaqtda ishga tushiradi._

### 4. Webhookni sozlash (Localhosda test qilish uchun)

To'lov tizimlari sizning serveringizga so'rov yuborishi uchun `jprq` yoki `ngrok` dan foydalaning:

```bash
jprq http 8000
```

Olingan HTTPS havolani `.env` faylidagi `WEBHOOK_URL` ga yozing (masalan: `https://example.jprq.live/api/bot/updates`).

## 📚 Resurslar

*   [PayTechUZ hujjatlari](https://paytechuz.readthedocs.io/)
*   [Aiogram hujjatlari](https://docs.aiogram.dev/)
*   [FastAPI hujjatlari](https://fastapi.tiangolo.com/)
