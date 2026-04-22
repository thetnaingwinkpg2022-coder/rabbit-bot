from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import requests
import asyncio
import random
import re
import os
import logging
from flask import Flask
from threading import Thread

# ===============================
# WEB SERVER FOR RENDER (KEEP ALIVE)
# ===============================
app_web = Flask('')

@app_web.route('/')
def home():
    return "🐰 Rabbit AI is Online and Running!"

def run_web():
    # Render သည် ပုံမှန်အားဖြင့် PORT variable ပေးတတ်သည်
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ===============================
# LOGGING SETUP
# ===============================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===============================
# SECURITY (ENV VARIABLES)
# ===============================
TOKEN = os.getenv("TOKEN")
AI_API_KEY = os.getenv("AI_API_KEY")

if not TOKEN:
    logger.error("❌ TOKEN environment variable not set!")
    # Render တွင် Error မတက်စေရန် exit မလုပ်ဘဲ ထားနိုင်သည်
if not AI_API_KEY:
    logger.error("❌ AI_API_KEY environment variable not set!")

BOT_USERNAME = None

# ===============================
# COMMAND HANDLERS
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_USERNAME
    if BOT_USERNAME is None:
        user_me = await context.bot.get_me()
        BOT_USERNAME = user_me.username

    text = f"""
╭━━━━━━━━━━━━━━━━━━━╮
┃  🌟 *RABBIT AI PRO* 🌟
┃  ═══════════════════
┃
┃  🐰 *မင်္ဂလာပါ မိတ်ဆွေ*
┃
┃  ကျွန်တော်က Rabbit AI Pro ပါ
┃  မေးခွန်းတိုင်းကို လှလှပပ ဖြေပေးမယ်
┃
┃  ═══════════════════
┃  📌 *အသုံးပြုပုံ*
┃
┃  • `ai [မေးခွန်း]`
┃  • `[မေးခွန်း] ai`
┃  • `@{BOT_USERNAME} [မေးခွန်း]`
┃
╰━━━━━━━━━━━━━━━━━━━╯
"""
    await update.message.reply_text(text, parse_mode="Markdown")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📖 *Help Menu*\n\nGroup ထဲတွင် `ai` ရှေ့ကဖြစ်စေ၊ နောက်ကဖြစ်စေ ထည့်မေးပါ။\nဥပမာ - `python ဆိုတာဘာလဲ ai`"
    await update.message.reply_text(text, parse_mode="Markdown")

# ===============================
# AI FUNCTION
# ===============================
def ask_ai(question):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are Rabbit AI Pro - a friendly Myanmar AI assistant. Use Myanmar language, bold important words, and add emojis."},
            {"role": "user", "content": question}
        ]
    }
    try:
        res = requests.post(url, headers=headers, json=data, timeout=30)
        result = res.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"AI API Error: {e}")
        return None

# ===============================
# MESSAGE LOGIC
# ===============================
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    # Simple logic to check for "ai"
    if "ai" in text.lower() or update.effective_chat.type == "private":
        question = text.lower().replace("ai", "").strip()
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        answer = await asyncio.to_thread(ask_ai, question)
        
        if answer:
            await update.message.reply_text(f"🐰 *Rabbit AI*\n\n{answer}", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ အဆင်မပြေဖြစ်သွားလို့ ခဏနေမှ ပြန်မေးပေးပါ")

# ===============================
# MAIN FUNCTION
# ===============================
def main():
    # Render အိပ်မသွားစေရန် Web Server ကို အရင်နှိုးမည်
    keep_alive()
    
    print("🚀 Rabbit AI Pro is starting...")
    
    # Bot Application ဆောက်ခြင်း
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Handler များ ထည့်ခြင်း
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    
    # Bot ကို စတင် Run ခြင်း
    app.run_polling()

if __name__ == "__main__":
    main()
