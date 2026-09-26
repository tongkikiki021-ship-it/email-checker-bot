import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def check_email_logic(email: str) -> str:
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        target_url = "https://httpbin.org/post" 
        payload = {"email": email}

        response = session.post(target_url, data=payload, timeout=10)
        content = response.text.lower()

        if "g-recaptcha" in content or "captcha_text" in content:
            return "CAPTCHA_TULISAN"
        elif "h-captcha" in content or "captcha_image" in content:
            return "CAPTCHA_GAMBAR"
        elif "disabled" in content or "suspended" in content:
            return "DISABLED"
        elif "not found" in content or "unregistered" in content:
            return "UNREGISTERED"
        elif response.status_code == 200:
            return "GOOD"
        else:
            return "UNKNOWN"

    except Exception as e:
        logging.error(f"Error checking {email}: {e}")
        return "ERROR"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ **Bot Checker Email Gacor 24/7 Active!**\n\n"
        "Kirimkan list email (satu per baris) untuk dicek secara otomatis.\n\n"
        "Kategori Status:\n"
        "✅ GOOD\n"
        "🚫 DISABLED\n"
        "❌ UNREGISTERED\n"
        "⚠️ CAPTCHA TULISAN\n"
        "🖼️ CAPTCHA GAMBAR",
        parse_mode="Markdown"
    )

async def handle_checker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    emails = [e.strip() for e in text.splitlines() if "@" in e]

    if not emails:
        await update.message.reply_text("❌ Mohon kirimkan format email yang benar!")
        return

    status_msg = await update.message.reply_text(f"⏳ Memproses {len(emails)} email...")

    results = []
    for email in emails:
        status = check_email_logic(email)

        if status == "GOOD":
            results.append(f"✅ `{email}` ➔ **GOOD**")
        elif status == "DISABLED":
            results.append(f"🚫 `{email}` ➔ **DISABLED**")
        elif status == "UNREGISTERED":
            results.append(f"❌ `{email}` ➔ **UNREGISTERED**")
        elif status == "CAPTCHA_TULISAN":
            results.append(f"⚠️ `{email}` ➔ **CAPTCHA TULISAN**")
        elif status == "CAPTCHA_GAMBAR":
            results.append(f"🖼️ `{email}` ➔ **CAPTCHA GAMBAR**")
        else:
            results.append(f"❓ `{email}` ➔ **ERROR/UNKNOWN**")

    response_text = "\n".join(results)
    await status_msg.edit_text(response_text, parse_mode="Markdown")

if __name__ == "__main__":
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN belum dipasang!")
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_checker))

    print("Bot berhasil berjalan 24/7...")
    app.run_polling()
          
