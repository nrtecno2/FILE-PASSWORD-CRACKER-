import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from utils.cracker import PasswordCracker

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not found!")

# लॉगिंग
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cracker = PasswordCracker()
user_sessions = {}

# === कमांड हैंडलर ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔐 *Password Cracker Bot*\n\n"
        "मुझे फाइल भेजें और मैं पासवर्ड क्रैक करने की कोशिश करूंगा।\n\n"
        "✅ ZIP, 7z, PDF सपोर्ट\n"
        "⚠️ केवल अपनी फाइलों के लिए\n\n"
        "फाइल भेजें ➡️",
        parse_mode='Markdown'
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if not file:
        await update.message.reply_text("❌ कृपया फाइल भेजें।")
        return
    
    # फाइल डाउनलोड
    file_obj = await file.get_file()
    file_path = f"downloads/{file.file_name}"
    os.makedirs("downloads", exist_ok=True)
    await file_obj.download_to_drive(file_path)
    
    await update.message.reply_text("🔍 *क्रैकिंग शुरू...*", parse_mode='Markdown')
    
    # फाइल टाइप डिटेक्ट करें
    ext = file.file_name.split('.')[-1].lower()
    password = None
    
    if ext == 'zip':
        password = cracker.crack_zip(file_path)
    elif ext == '7z':
        password = cracker.crack_7z(file_path)
    elif ext == 'pdf':
        password = cracker.crack_pdf(file_path)
    else:
        await update.message.reply_text("❌ अनसपोर्टेड फाइल फॉर्मेट। ZIP, 7z, PDF भेजें।")
        return
    
    # रिजल्ट
    if password:
        await update.message.reply_text(
            f"✅ *पासवर्ड मिल गया!*\n\n"
            f"🔑 `{password}`\n\n"
            f"📁 फाइल: {file.file_name}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ *पासवर्ड नहीं मिला*\n\n"
            f"वर्डलिस्ट में {len(cracker.wordlist)} पासवर्ड चेक किए गए।\n"
            f"बड़ी वर्डलिस्ट अपलोड करें या फिर से try करें।",
            parse_mode='Markdown'
        )
    
    # क्लीनअप
    os.remove(file_path)

async def add_wordlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """वर्डलिस्ट अपडेट करें"""
    file = update.message.document
    if not file:
        await update.message.reply_text("❌ वर्डलिस्ट .txt फाइल भेजें।")
        return
    
    file_obj = await file.get_file()
    await file_obj.download_to_drive("wordlist.txt")
    cracker.wordlist = cracker.load_wordlist("wordlist.txt")
    
    await update.message.reply_text(
        f"✅ वर्डलिस्ट अपडेट!\n"
        f"📊 {len(cracker.wordlist)} पासवर्ड लोड किए गए।"
    )

# === मेन ===
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addlist", add_wordlist))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    
    print("🤖 NRTECNO BOT STARTED...")
    app.run_polling()

if __name__ == "__main__":
    main()
