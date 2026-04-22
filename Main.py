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
    return "🐰 Rabbit AI Pro Bot is Running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# ===============================
# LOGGING
# ===============================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===============================
# ENV VARIABLES (SECURE)
# ===============================
TOKEN = os.getenv("TOKEN")
AI_API_KEY = os.getenv("AI_API_KEY")

if not TOKEN:
    logger.error("❌ TOKEN environment variable not set!")
if not AI_API_KEY:
    logger.error("❌ AI_API_KEY environment variable not set!")

BOT_USERNAME = None

# ===============================
# START COMMAND
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_USERNAME
    if BOT_USERNAME is None:
        bot_info = await context.bot.get_me()
        BOT_USERNAME = bot_info.username
    
    text = f"""
🌟 *RABBIT AI PRO* 🌟
━━━━━━━━━━━━━━━━━━━

🐰 *မင်္ဂလာပါ မိတ်ဆွေ။*

ကျွန်တော်က *Rabbit AI Pro* ပါ။  

━━━━━━━━━━━━━━━━━━━
📌 *Group မှာ အသုံးပြုပုံ*

• `ai [မေးခွန်း]` → အစမှာ ai ထည့်မေးရန်
• `[မေးခွန်း] ai` → အဆုံးမှာ ai ထည့်မေးရန်
• `@{BOT_USERNAME}` → Bot ကို Tag လုပ်မေးရန်

━━━━━━━━━━━━━━━━━━━
💬 *ဥပမာများ*

`ai python ဆိုတာဘာလဲ`
`nested loop ရှင်းပြပါ ai`
`@{BOT_USERNAME} မင်္ဂလာပါ`

━━━━━━━━━━━━━━━━━━━
✨ *မှတ်ချက်:*  
Group ထဲမှာ `ai` ပါမှသာ ဖြေပေးမှာပါ။
"""
    await update.message.reply_text(text, parse_mode="Markdown")

# ===============================
# HELP COMMAND
# ===============================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_USERNAME
    if BOT_USERNAME is None:
        bot_info = await context.bot.get_me()
        BOT_USERNAME = bot_info.username
    
    text = f"""
📖 *HELP MENU* 📖
━━━━━━━━━━━━━━━

⚡ *Private Chat*

• မေးခွန်းတိုက်ရိုက်ရိုက်ပါ

⚡ *Group Commands*

• `ai [question]` → အစမှာ ai
• `[question] ai` → အဆုံးမှာ ai  
• `@{BOT_USERNAME}` → Tag လုပ်မေးရန်

━━━━━━━━━━━━━━━
💡 *Examples*

`ai Python loop ဆိုတာဘာလဲ`
`nested pattern ရှင်းပြပါ ai`
`@{BOT_USERNAME} ဟာသတစ်ခုပြောပါ`

━━━━━━━━━━━━━━━
✨ *Tip*  
Group ထဲမှာ `ai` ပါမှသာ အလုပ်လုပ်ပါမယ်။
"""
    await update.message.reply_text(text, parse_mode="Markdown")

# ===============================
# AI FUNCTION
# ===============================
def ask_ai(question):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/rabbit_ai_pro_bot",
        "X-Title": "Rabbit AI Pro"
    }

    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": """
You are Rabbit AI Pro — a stylish, friendly, and super smart assistant.

🎨 YOUR STYLE RULES:
- Always start with an emoji (💡, ✅, 🤖, 📚, 🎯, etc.)
- Use Myanmar language (Burmese) primarily
- Break answers into short, readable paragraphs
- Use bullet points with • or - 
- Use **bold** for important terms
- Use `inline code` for small commands
- Use ```code blocks``` for multi-line code
- End with a helpful tip or warm closing
- Keep tone: professional + cute + modern
- NEVER say "as an AI" or "I cannot answer"
- For code questions, show actual working code
"""
            },
            {
                "role": "user",
                "content": question
            }
        ]
    }

    try:
        res = requests.post(url, headers=headers, json=data, timeout=30)
        result = res.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"AI Error: {e}")
        return None

# ===============================
# EXTRACT QUESTION
# ===============================
def extract_question(text, bot_username):
    text = text.strip()
    text_lower = text.lower()
    
    if bot_username and f"@{bot_username.lower()}" in text_lower:
        cleaned = re.sub(rf'@{bot_username.lower()}', '', text_lower, flags=re.IGNORECASE).strip()
        if cleaned:
            return cleaned
        return None
    
    if text_lower.startswith("ai "):
        cleaned = text[3:].strip()
        if cleaned:
            return cleaned
        return None
    
    if text_lower == "ai":
        return None
    
    if text_lower.endswith(" ai"):
        cleaned = text[:-3].strip()
        if cleaned:
            return cleaned
        return None
    
    return None

# ===============================
# SHOULD REPLY?
# ===============================
async def should_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_USERNAME
    if BOT_USERNAME is None:
        bot_info = await context.bot.get_me()
        BOT_USERNAME = bot_info.username
    
    message = update.message
    text = message.text or ""
    
    if update.effective_chat.type == "private":
        return True, text
    
    if message.reply_to_message and message.reply_to_message.from_user.id == context.bot.id:
        return True, text
    
    question = extract_question(text, BOT_USERNAME)
    if question:
        return True, question
    
    return False, None

# ===============================
# MAIN REPLY
# ===============================
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    should_reply_flag, question = await should_reply(update, context)
    
    if not should_reply_flag:
        return
    
    if not question or len(question) < 1:
        hint_msg = """
🤔 *မေးခွန်းလေး ထည့်ပေးပါဦး*

━━━━━━━━━━━━━━━━━━━
📌 *Group မှာ ဒီလိုမေးပါ*

• `ai ဘာညာ` → အစမှာ ai
• `ဘာညာ ai` → အဆုံးမှာ ai
• `@bot ဘာညာ` → Tag လုပ်ပါ

━━━━━━━━━━━━━━━━━━━
💬 *ဥပမာ*
`ai python ဆိုတာဘာလဲ`
`nested loop ရှင်းပြပါ ai`
"""
        await update.message.reply_text(hint_msg, parse_mode="Markdown")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(random.uniform(0.5, 1.2))

    raw_answer = await asyncio.to_thread(ask_ai, question)

    if not raw_answer:
        error_msg = """
😢 *Oops! Rabbit တစ်ကောင် ချော်သွားတယ်*

━━━━━━━━━━━━━━━━━━━
နည်းပညာအရ အဆင်မပြေလို့ ဖြေမရသေးဘူး။

🔧 *ဖြေရှင်းနည်း*
• ခဏစောင့်ပြီး ပြန်စမ်းပါ
• မေးခွန်းကို ရှင်းရှင်းလင်းလင်း ပြန်မေးပါ

━━━━━━━━━━━━━━━━━━━
🐰 ကျေးဇူးပါ — ခွင့်လွှတ်ပေးပါနော်
"""
        await update.message.reply_text(error_msg, parse_mode="Markdown")
        return

    footers = [
        "🐰 နောက်ထပ်မေးချင်ရင် `ai` နဲ့ထည့်မေးပါ",
        "💫 ကူညီနိုင်တာ ဝမ်းသာပါတယ်",
        "⚡ Rabbit AI Pro — အမြဲတမ်း အဆင်သင့်",
        "🎯 အောင်မြင်ပါစေ မိတ်ဆွေ",
        "📚 သင်ယူခြင်းဟာ အလင်းရောင်ပါ"
    ]
    
    group_hint = ""
    if update.effective_chat.type != "private":
        group_hint = f"\n\n💡 *သိကောင်းစရာ:* `ai [မေးခွန်း]` သို့ `[မေးခွန်း] ai`"
    
    nice_reply = f"""
✨ *Rabbit AI Pro* ✨
━━━━━━━━━━━━━━━━━━━

{raw_answer}

━━━━━━━━━━━━━━━━━━━
{random.choice(footers)}{group_hint}
"""

    try:
        await update.message.reply_text(nice_reply, parse_mode="Markdown", disable_web_page_preview=True)
    except:
        clean_reply = nice_reply.replace("*", "").replace("_", "").replace("`", "")
        await update.message.reply_text(clean_reply)

# ===============================
# ERROR HANDLER
# ===============================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ *Technical Glitch*\n━━━━━━━━━━━\nခဏနေမှ ပြန်ကြိုးစားပါ။\n🐰 Rabbit အိပ်နေလို့ပါ",
                parse_mode="Markdown"
            )
        except:
            pass

# ===============================
# MAIN
# ===============================
def main():
    keep_alive()
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    app.add_error_handler(error_handler)
    
    print("🐰✨ Rabbit AI Pro is running...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📌 Group Trigger Conditions:")
    print("   • Starts with 'ai ' → 'ai python'")
    print("   • Ends with ' ai' → 'python ai'")
    print("   • @mention → '@bot hello'")
    print("   • Reply to bot's message")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    app.run_polling()

if __name__ == "__main__":
    main()
