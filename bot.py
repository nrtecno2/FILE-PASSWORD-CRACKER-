import os
import pyzipper
import py7zr
import pdfplumber
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

def load_wordlist(path="wordlist.txt"):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    return ['123456', 'password', 'admin', '1234', '0000']

WORDLIST = load_wordlist()

def crack_zip(file_path):
    for pwd in WORDLIST:
        try:
            with pyzipper.AESZipFile(file_path) as zf:
                zf.extractall(pwd=pwd.encode())
                return pwd
        except:
            continue
    return None

def crack_7z(file_path):
    for pwd in WORDLIST:
        try:
            with py7zr.SevenZipFile(file_path, password=pwd) as archive:
                archive.extractall()
                return pwd
        except:
            continue
    return None

def crack_pdf(file_path):
    for pwd in WORDLIST:
        try:
            with pdfplumber.open(file_path, password=pwd) as pdf:
                if len(pdf.pages) > 0:
                    return pwd
        except:
            continue
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔐 *Password Cracker Bot*\n\n"
        "मुझे फाइल भेजें और मैं पासवर्ड क्रैक करूंगा।\n"
        "✅ ZIP, 7z, PDF सपोर्ट\n"
        "⚠️ केवल अपनी फाइलों के लिए",
        parse_mode='Markdown'
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if not file:
        await update.message.reply_text("❌ कृपया फाइल भेजें।")
        return
    
    file_obj = await file.get_file()
    file_path = f"downloads/{file.file_name}"
    os.makedirs("downloads", exist_ok=True)
    await file_obj.download_to_drive(file_path)
    
    await update.message.reply_text("🔍 *क्रैकिंग शुरू...*", parse_mode='Markdown')
    
    ext = file.file_name.split('.')[-1].lower()
    password = None
    
    if ext == 'zip':
        password = crack_zip(file_path)
    elif ext == '7z':
        password = crack_7z(file_path)
    elif ext == 'pdf':
        password = crack_pdf(file_path)
    else:
        await update.message.reply_text("❌ अनसपोर्टेड फाइल।")
        os.remove(file_path)
        return
    
    if password:
        await update.message.reply_text(
            f"✅ *पासवर्ड मिल गया!*\n\n🔑 `{password}`",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(f"❌ *पासवर्ड नहीं मिला*\n{len(WORDLIST)} पासवर्ड चेक किए गए।")
    
    os.remove(file_path)

def main():
    if not TOKEN:
        print("❌ BOT_TOKEN not found! Set in Render Environment Variables")
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    print("🤖 NRTECNO BOT STARTED...")
    app.run_polling()

if __name__ == "__main__":
    main()
