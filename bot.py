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

# Check if tokens are set
if not TOKEN:
    logger.error("❌ TOKEN environment variable not set!")
    exit(1)
if not AI_API_KEY:
    logger.error("❌ AI_API_KEY environment variable not set!")
    exit(1)

BOT_USERNAME = None

# ===============================
# START COMMAND (PREMIUM UI)
# ===============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_USERNAME
    if BOT_USERNAME is None:
        BOT_USERNAME = (await context.bot.get_me()).username

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
┃  ═══════════════════
┃  💬 *ဥပမာ*
┃
┃  `ai python ဆိုတာဘာလဲ`
┃  `nested loop ရှင်းပြပါ ai`
┃
╰━━━━━━━━━━━━━━━━━━━╯

💡 *Tip:* /help မှာ အသေးစိတ် ကြည့်ပါ
"""
    await update.message.reply_text(text, parse_mode="Markdown")

# ===============================
# HELP COMMAND
# ===============================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_USERNAME
    if BOT_USERNAME is None:
        BOT_USERNAME = (await context.bot.get_me()).username

    text = f"""
╭━━━━━━━━━━━━━━━━━━━╮
┃  📖 *HELP MENU* 📖
┃  ═══════════════════
┃
┃  ⚡ *Group Commands*
┃
┃  ① `ai [question]`
┃  ② `[question] ai`
┃  ③ `@{BOT_USERNAME} [question]`
┃
┃  ═══════════════════
┃  💡 *Examples*
┃
┃  `ai python loop`
┃  `telegram bot လုပ်နည်း ai`
┃  `@{BOT_USERNAME} hello`
┃
┃  ═══════════════════
┃  ✨ *Private Chat*
┃
┃  မေးခွန်းတိုက်ရိုက် ရိုက်ပါ
┃
╰━━━━━━━━━━━━━━━━━━━╯
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
        "HTTP-Referer": "https://t.me/rabbit_ai_bot",
        "X-Title": "Rabbit AI Pro"
    }

    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": """
You are Rabbit AI Pro - a friendly Myanmar AI assistant.

🎨 RULES:
- Start with an emoji (💡, 📚, ✅, 🤖, 🎯)
- Use Myanmar language
- Short paragraphs with bullet points
- Use **bold** for important words
- Use `code` for commands
- End with a helpful tip
- NEVER say "as an AI"
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
        logger.error(f"AI API Error: {e}")
        return None

# ===============================
# EXTRACT QUESTION
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
    
    # Case 4: Reply to bot (no need for ai)
    # This is handled in should_reply function
    
    return None

# ===============================
# CHECK IF BOT SHOULD REPLY
# ===============================
async def should_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if bot should reply based on context"""
    
    global BOT_USERNAME
    if BOT_USERNAME is None:
        BOT_USERNAME = (await context.bot.get_me()).username
    
    message = update.message
    text = message.text or ""
    
    # Case 1: Private chat (always reply)
    if update.effective_chat.type == "private":
        return True, text
    
    # Case 2: Reply to bot's message
    if message.reply_to_message:
        if message.reply_to_message.from_user.id == context.bot.id:
            return True, text
    
    # Case 3: Extract question with ai
    question = extract_question(text, BOT_USERNAME)
    if question:
        return True, question
    
    # Default: No reply
    return False, None

# ===============================
# MESSAGE HANDLER (MAIN)
# ===============================
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BOT_USERNAME
    if BOT_USERNAME is None:
        BOT_USERNAME = (await context.bot.get_me()).username
    
    # Check if bot should reply
    should_reply_flag, question = await should_reply(update, context)
    
    if not should_reply_flag:
        return  # Ignore message
    
    # If no question (just "ai" alone)
    if not question or len(question) < 1:
        hint_msg = """
🤔 *မေးခွန်းလေး ထည့်ပေးပါဦး*

━━━━━━━━━━━━━━━━━━━
📌 *Group မှာ ဒီလိုမေးပါ*

• `ai ဘာညာ`
• `ဘာညာ ai`
• `@bot ဘာညာ`

━━━━━━━━━━━━━━━━━━━
💬 *ဥပမာ*
`ai python ဆိုတာဘာလဲ`
`nested loop ရှင်းပြပါ ai`
"""
        await update.message.reply_text(hint_msg, parse_mode="Markdown")
        return
    
    # Typing animation
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )
    
    # Natural delay (better UX)
    await asyncio.sleep(random.uniform(0.5, 1.0))
    
    # Get AI answer
    answer = await asyncio.to_thread(ask_ai, question)
    
    # Error handling
    if not answer:
        error_msg = """
😢 *Rabbit AI Error*

━━━━━━━━━━━━━━━━━━━
နည်းပညာအရ အဆင်မပြေလို့
အဖြေမပေးနိုင်သေးဘူး။

🔧 *ဖြေရှင်းနည်း*
• ခဏစောင့်ပြီး ပြန်စမ်းပါ
• မေးခွန်းကို ရှင်းရှင်းလင်းလင်းမေးပါ

━━━━━━━━━━━━━━━━━━━
🐰 ခွင့်လွှတ်ပါနော်
"""
        await update.message.reply_text(error_msg, parse_mode="Markdown")
        return
    
    # Random cute footer
    footers = [
        "🐰 နောက်ထပ်မေးချင်ရင် `ai` နဲ့ထည့်မေးပါ",
        "💫 ကူညီနိုင်တာ ဝမ်းသာပါတယ်",
        "⚡ Rabbit AI Pro — 24/7 အဆင်သင့်",
        "🎯 အောင်မြင်ပါစေ မိတ်ဆွေ",
        "📚 သင်ယူခြင်းဟာ အလင်းရောင်ပါ"
    ]
    
    # Add group hint if in group
    group_hint = ""
    if update.effective_chat.type != "private":
        group_hint = f"\n\n💡 *Group:* `ai [မေး]` or `[မေး] ai`"
    
    # Premium card design
    final_text = f"""
╭━━━━━━━━━━━━━━━━━━━━━━━━╮
┃  🐰 *RABBIT AI PRO* ✨
┃  ════════════════════════
┃  
{answer}
┃  
┃  ════════════════════════
┃  {random.choice(footers)}
┃
╰━━━━━━━━━━━━━━━━━━━━━━━━╯{group_hint}
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
                "⚠️ *System Error*\n━━━━━━━━━━━\nခဏနေမှ ပြန်စမ်းပါ။\n🐰 Rabbit အိပ်နေလို့ပါ",
                parse_mode="Markdown"
            )
        except:
            pass

# ===============================
# MAIN
# ===============================
def main():
    """Start the bot"""
    print("╔══════════════════════════════════════╗")
    print("║     🐰 RABBIT AI PRO BOT 🐰         ║")
    print("╠══════════════════════════════════════╣")
    print("║  Status: Running...                  ║")
    print("║  Group: ai [q] or [q] ai             ║")
    print("║  Private: direct message             ║")
    print("╚══════════════════════════════════════╝")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    app.add_error_handler(error_handler)
    
    app.run_polling()

if __name__ == "__main__":
    main()
