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
from datetime import datetime

# ===============================
# WEB SERVER FOR RENDER (KEEP ALIVE)
# ===============================
app_web = Flask('')

@app_web.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rabbit AI Pro</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                color: white;
            }
            .container {
                text-align: center;
                padding: 2rem;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            h1 { font-size: 3rem; margin-bottom: 0; }
            .status { 
                display: inline-block;
                padding: 10px 20px;
                background: #4ade80;
                border-radius: 30px;
                margin-top: 20px;
            }
            .rabbit { font-size: 5rem; animation: bounce 1s infinite; }
            @keyframes bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-20px); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="rabbit">🐰</div>
            <h1>Rabbit AI Pro</h1>
            <p>Your Friendly Telegram AI Assistant</p>
            <div class="status">✅ Bot is Online & Running</div>
            <p style="margin-top: 20px; font-size: 14px;">✨ Premium AI Assistant | 24/7 Active</p>
        </div>
    </body>
    </html>
    """

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
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
if not AI_API_KEY:
    logger.error("❌ AI_API_KEY environment variable not set!")

BOT_USERNAME = None

# ===============================
# SMART GREETING BASED ON TIME
# ===============================
def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "🌅 မင်္ဂလာနံနက်ခင်းပါ"
    elif hour < 18:
        return "☀️ မင်္ဂလာနေ့လယ်ခင်းပါ"
    else:
        return "🌙 မင်္ဂလာညချမ်းပါ"

# ===============================
# START COMMAND (PREMIUM UI)
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_USERNAME
    if BOT_USERNAME is None:
        user_me = await context.bot.get_me()
        BOT_USERNAME = user_me.username
    
    greeting = get_greeting()

    text = f"""
╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
┃      🌟 *RABBIT AI PRO* 🌟        ┃
┃      ═════════════════════════    ┃
┃                                   ┃
┃      {greeting} မိတ်ဆွေ။          ┃
┃                                   ┃
┃      🐰 ကျွန်တော်က Rabbit AI Pro ပါ  ┃
┃      မေးခွန်းတိုင်းကို လှလှပပ ဖြေပေးမယ် ┃
┃                                   ┃
┃      ═════════════════════════    ┃
┃      📌 *အသုံးပြုပုံ*              ┃
┃                                   ┃
┃      • `ai [မေးခွန်း]`            ┃
┃      • `[မေးခွန်း] ai`            ┃
┃      • `@{BOT_USERNAME} [မေးခွန်း]` ┃
┃                                   ┃
┃      ═════════════════════════    ┃
┃      💬 *ဥပမာများ*               ┃
┃                                   ┃
┃      `ai python ဆိုတာဘာလဲ`       ┃
┃      `nested loop ရှင်းပြပါ ai`   ┃
┃                                   ┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

✨ *Tip:* /help မှာ အသေးစိတ် လေ့လာနိုင်ပါတယ်
"""
    await update.message.reply_text(text, parse_mode="Markdown")

# ===============================
# HELP COMMAND (PREMIUM UI)
# ===============================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_USERNAME
    if BOT_USERNAME is None:
        user_me = await context.bot.get_me()
        BOT_USERNAME = user_me.username

    text = f"""
╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
┃        📖 *HELP & COMMANDS* 📖     ┃
┃      ═════════════════════════    ┃
┃                                   ┃
┃  ⚡ *Group Commands*               ┃
┃                                   ┃
┃  ① `ai [question]`               ┃
┃     → အစမှာ ai ထည့်မေးခြင်း      ┃
┃                                   ┃
┃  ② `[question] ai`               ┃
┃     → အဆုံးမှာ ai ထည့်မေးခြင်း    ┃
┃                                   ┃
┃  ③ `@{BOT_USERNAME} [question]`  ┃
┃     → Bot ကို Tag လုပ်မေးခြင်း    ┃
┃                                   ┃
┃  ═════════════════════════       ┃
┃  💡 *Examples*                    ┃
┃                                   ┃
┃  `ai python loop ရှင်းပြပါ`      ┃
┃  `telegram bot လုပ်နည်း ai`      ┃
┃  `@{BOT_USERNAME} ဟာသတစ်ခုပြောပါ` ┃
┃                                   ┃
┃  ═════════════════════════       ┃
┃  ✨ *Private Chat*                ┃
┃                                   ┃
┃  မေးခွန်းတိုက်ရိုက် ရိုက်ပါ      ┃
┃  `python ဆိုတာဘာလဲ`              ┃
┃                                   ┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

🔥 *Powered by DeepSeek AI*
"""
    await update.message.reply_text(text, parse_mode="Markdown")

# ===============================
# AI FUNCTION (ENHANCED)
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
You are Rabbit AI Pro — a premium Myanmar AI assistant.

🎨 **DESIGN RULES:**
- Start with a relevant emoji (💡, 📚, ✅, 🤖, 🎯, 🔥)
- Use Myanmar language (Burmese) primarily
- Break answers into short, readable paragraphs (2-3 lines max)
- Use bullet points with • or ✓
- Use **bold** for important terms
- Use `inline code` for commands/variables
- Use ```code blocks``` for multi-line code
- End with a helpful tip or warm closing
- Keep tone: professional + cute + modern
- NEVER say "as an AI" or "I cannot answer"
"""
            },
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
# EXTRACT QUESTION FROM MESSAGE
# ===============================
def extract_question(text, bot_username):
    """Extract question if ai at start, end, or bot mention"""
    if not text:
        return None
    
    text = text.strip()
    text_lower = text.lower()
    
    # Case 1: ai at start
    if text_lower.startswith("ai "):
        return text[3:].strip()
    
    # Case 2: ai at end
    if text_lower.endswith(" ai"):
        return text[:-3].strip()
    
    # Case 3: Bot mention
    if bot_username:
        pattern = rf"@{re.escape(bot_username)}"
        if re.search(pattern, text, re.IGNORECASE):
            cleaned = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
            if cleaned:
                return cleaned
    
    return None

# ===============================
# CHECK IF BOT SHOULD REPLY
# ===============================
async def should_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_USERNAME
    if BOT_USERNAME is None:
        user_me = await context.bot.get_me()
        BOT_USERNAME = user_me.username
    
    message = update.message
    text = message.text or ""
    
    # Case 1: Private chat (always reply)
    if update.effective_chat.type == "private":
        return True, text
    
    # Case 2: Reply to bot's message
    if message.reply_to_message:
        if message.reply_to_message.from_user.id == context.bot.id:
            return True, text
    
    # Case 3: Extract question with ai pattern
    question = extract_question(text, BOT_USERNAME)
    if question:
        return True, question
    
    return False, None

# ===============================
# ANIMATED THINKING MESSAGE
# ===============================
async def send_thinking_animation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    thinking_msgs = [
        "🐰 စဉ်းစားနေပါတယ် ● ● ●",
        "🤔 Rabbit အတွေးလေးတွေ ● ● ●",
        "✨ အဖြေရှာနေပါတယ် ● ● ●",
        "📚 Knowledge ရှာနေတယ် ● ● ●"
    ]
    msg = await update.message.reply_text(random.choice(thinking_msgs))
    await asyncio.sleep(1)
    await msg.delete()

# ===============================
# MAIN REPLY FUNCTION (PREMIUM UI)
# ===============================
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    global BOT_USERNAME
    if BOT_USERNAME is None:
        user_me = await context.bot.get_me()
        BOT_USERNAME = user_me.username
    
    # Check if bot should reply
    should_reply_flag, question = await should_reply(update, context)
    
    if not should_reply_flag:
        return
    
    # If no question (just "ai" alone)
    if not question or len(question) < 1:
        hint_msg = """
╭━━━━━━━━━━━━━━━━━━━━━━╮
┃  🤔 *မေးခွန်းလေး ထည့်ပေးပါ* ┃
┃  ════════════════════ ┃
┃                       ┃
┃  📌 *Group မှာ ဒီလိုမေးပါ* ┃
┃                       ┃
┃  • `ai ဘာညာ`         ┃
┃  • `ဘာညာ ai`         ┃
┃  • `@bot ဘာညာ`       ┃
┃                       ┃
┃  💬 *ဥပမာ*           ┃
┃  `ai python ဆိုတာဘာလဲ` ┃
┃  `nested loop ai`    ┃
┃                       ┃
╰━━━━━━━━━━━━━━━━━━━━━━╯
"""
        await update.message.reply_text(hint_msg, parse_mode="Markdown")
        return
    
    # Send typing animation
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )
    
    # Show thinking animation
    await send_thinking_animation(update, context)
    
    # Natural delay
    await asyncio.sleep(random.uniform(0.3, 0.8))
    
    # Get AI answer
    answer = await asyncio.to_thread(ask_ai, question)
    
    # Error handling
    if not answer:
        error_msg = """
╭━━━━━━━━━━━━━━━━━━━━━━━━╮
┃  😢 *Rabbit ချော်သွားတယ်* ┃
┃  ════════════════════════ ┃
┃                          ┃
┃  နည်းပညာအရ အဆင်မပြေလို့ ┃
┃  အဖြေမပေးနိုင်သေးဘူး။    ┃
┃                          ┃
┃  🔧 *ဖြေရှင်းနည်း*      ┃
┃  • ခဏစောင့်ပြီး ပြန်စမ်းပါ ┃
┃  • မေးခွန်းကို ရှင်းရှင်းမေးပါ ┃
┃                          ┃
╰━━━━━━━━━━━━━━━━━━━━━━━━╯
🐰 ခွင့်လွှတ်ပါနော်
"""
        await update.message.reply_text(error_msg, parse_mode="Markdown")
        return
    
    # Random cute footer messages
    footers = [
        ("🐰", "နောက်ထပ်မေးချင်ရင် `ai` နဲ့ထည့်မေးပါ"),
        ("💫", "ကူညီနိုင်တာ ဝမ်းသာပါတယ်"),
        ("⚡", "Rabbit AI Pro — 24/7 အဆင်သင့်"),
        ("🎯", "အောင်မြင်ပါစေ မိတ်ဆွေ"),
        ("📚", "သင်ယူခြင်းဟာ အလင်းရောင်ပါ"),
        ("🔥", "ဒီအဖြေက သင့်အတွက် အသုံးဝင်မယ်လို့မျှော်လင့်ပါတယ်"),
        ("✨", "အချိန်မရွေး မေးမြန်းနိုင်ပါတယ်")
    ]
    
    emoji, footer_text = random.choice(footers)
    
    # Add group hint if in group
    group_hint = ""
    if update.effective_chat.type != "private":
        group_hint = f"\n\n💡 *Group:* `ai [မေးခွန်း]` or `[မေးခွန်း] ai`"
    
    # Premium card design
    final_text = f"""
╭━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╮
┃      🐰 *RABBIT AI PRO* ✨        ┃
┃      ═════════════════════════    ┃
┃                                   ┃
{answer}
┃                                   ┃
┃      ═════════════════════════    ┃
┃      {emoji} _{footer_text}_        ┃
┃                                   ┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯{group_hint}
"""
    
    # Send reply with markdown
    try:
        await update.message.reply_text(
            final_text,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Markdown error: {e}")
        # Fallback without markdown
        clean_reply = final_text.replace("*", "").replace("_", "").replace("`", "")
        await update.message.reply_text(clean_reply)

# ===============================
# ERROR HANDLER
# ===============================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error: {context.error}")
    if update and hasattr(update, 'effective_message'):
        try:
            await update.effective_message.reply_text(
                "╭━━━━━━━━━━━━━━━━━━━━╮\n"
                "┃  ⚠️ *System Glitch*  ┃\n"
                "┃  ════════════════   ┃\n"
                "┃  ခဏနေမှ ပြန်စမ်းပါ။  ┃\n"
                "┃  🐰 Rabbit အိပ်နေလို့ပါ ┃\n"
                "╰━━━━━━━━━━━━━━━━━━━━╯",
                parse_mode="Markdown"
            )
        except:
            pass

# ===============================
# MAIN FUNCTION
# ===============================
def main():
    # Start web server for Render
    keep_alive()
    
    # Print beautiful banner
    print("╔════════════════════════════════════════════════════╗")
    print("║                                                    ║")
    print("║     🐰✨ RABBIT AI PRO - PREMIUM EDITION ✨🐰      ║")
    print("║                                                    ║")
    print("╠════════════════════════════════════════════════════╣")
    print("║  Status: ✅ Bot is Running                         ║")
    print("║  Group:  🔘 ai [q] or [q] ai or @mention          ║")
    print("║  Private: 💬 Direct message                        ║")
    print("║  Web:    🌐 http://localhost:8080                  ║")
    print("╠════════════════════════════════════════════════════╣")
    print("║  🎨 Premium Features:                              ║")
    print("║  • Card-style UI/UX                                ║")
    print("║  • Animated thinking dots                          ║")
    print("║  • Smart time greeting                             ║")
    print("║  • Rich markdown formatting                        ║")
    print("║  • 24/7 Keep-alive for Render                      ║")
    print("╚════════════════════════════════════════════════════╝")
    
    # Build bot application
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    app.add_error_handler(error_handler)
    
    # Start bot
    app.run_polling()

if __name__ == "__main__":
    main()
