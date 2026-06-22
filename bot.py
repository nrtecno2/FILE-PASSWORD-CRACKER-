import os
import json
import time
import requests
import pyzipper
import py7zr
import pdfplumber
import itertools
import random
from flask import Flask, request, jsonify
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")
RENDER_URL = os.environ.get("RENDER_URL", "https://your-bot.onrender.com")
PRIVATE_CHANNEL = -1004491770657
CHANNEL_USERNAME = "@nrtecno2"

app = Flask(__name__)

# ============================================================
# USER SESSION STORAGE (Info collect karne ke liye)
# ============================================================
user_sessions = {}

# ============================================================
# SMART PASSWORD GENERATOR (Info Based)
# ============================================================
class SmartPasswordGenerator:
    def __init__(self, info=None):
        self.info = info or {}
        self.common_words = [
            'password', 'admin', 'root', 'toor', 'iloveyou', 'sunshine',
            'princess', 'dragon', 'baseball', 'superman', 'batman',
            'trustno', 'hello', 'freedom', 'whatever', 'qwerty',
            'letmein', 'welcome', 'monkey', 'secret', 'love', 'angel',
            'rainbow', 'tiger', 'eagle', 'phoenix', 'shadow', 'night',
            'star', 'moon', 'sun', 'cloud', 'thunder', 'lightning'
        ]
        self.special_chars = ['@', '#', '&', '%', '!', '$', '_', '-']
        self.numbers = ['1', '12', '123', '1234', '12345', '123456', '1234567', '12345678', '123456789', '1234567890']
        self.years = ['2020', '2021', '2022', '2023', '2024', '2025', '2026']
    
    def generate_from_info(self):
        """Generate passwords using user info"""
        passwords = set()
        
        name = self.info.get('name', '').strip().lower()
        dob = self.info.get('dob', '').strip()
        father = self.info.get('father', '').strip().lower()
        mother = self.info.get('mother', '').strip().lower()
        city = self.info.get('city', '').strip().lower()
        mobile = self.info.get('mobile', '').strip()
        
        # Extract year from DOB
        year = ''
        if dob:
            if '/' in dob:
                parts = dob.split('/')
                if len(parts) == 3:
                    year = parts[-1]
            elif '-' in dob:
                parts = dob.split('-')
                if len(parts) == 3:
                    year = parts[-1]
        
        # List of all info pieces
        info_pieces = [name, father, mother, city]
        info_pieces = [p for p in info_pieces if p]
        
        # 1. Name + Number
        if name:
            for num in self.numbers[:10]:
                passwords.add(f"{name}{num}")
                passwords.add(f"{name}{num}@")
                passwords.add(f"{name}{num}#")
                passwords.add(f"{name}@{num}")
                passwords.add(f"{name}#{num}")
                passwords.add(f"{name.capitalize()}{num}")
                passwords.add(f"{name}{num}!")
            
            if year:
                passwords.add(f"{name}{year}")
                passwords.add(f"{name}@{year}")
                passwords.add(f"{name}#{year}")
                passwords.add(f"{name}{year}!")
            
            if mobile:
                passwords.add(f"{name}{mobile[-4:]}")
                passwords.add(f"{name}@{mobile[-4:]}")
        
        # 2. Father + Number
        if father:
            for num in self.numbers[:5]:
                passwords.add(f"{father}{num}")
                passwords.add(f"{father}{num}@")
                passwords.add(f"{father}@{num}")
                if year:
                    passwords.add(f"{father}{year}")
            if mobile:
                passwords.add(f"{father}{mobile[-4:]}")
        
        # 3. Mother + Number
        if mother:
            for num in self.numbers[:5]:
                passwords.add(f"{mother}{num}")
                passwords.add(f"{mother}{num}@")
                if year:
                    passwords.add(f"{mother}{year}")
        
        # 4. City + Number
        if city:
            for num in self.numbers[:5]:
                passwords.add(f"{city}{num}")
                passwords.add(f"{city}{num}@")
                if year:
                    passwords.add(f"{city}{year}")
        
        # 5. Name + Father
        if name and father:
            passwords.add(f"{name}{father}")
            passwords.add(f"{name}@{father}")
            passwords.add(f"{name}#{father}")
            passwords.add(f"{name.capitalize()}{father.capitalize()}")
        
        # 6. Name + Mother
        if name and mother:
            passwords.add(f"{name}{mother}")
            passwords.add(f"{name}@{mother}")
            passwords.add(f"{name}#{mother}")
        
        # 7. Name + City
        if name and city:
            passwords.add(f"{name}{city}")
            passwords.add(f"{name}@{city}")
        
        # 8. Father + Mother
        if father and mother:
            passwords.add(f"{father}{mother}")
            passwords.add(f"{father}@{mother}")
        
        # 9. Mobile number combinations
        if mobile:
            passwords.add(mobile)
            passwords.add(mobile[-6:])
            passwords.add(mobile[-4:])
            passwords.add(f"{name}{mobile[-4:]}")
            passwords.add(f"{name}{mobile[-6:]}")
        
        # 10. Year combinations
        if year:
            passwords.add(year)
            for word in [name, father, mother, city]:
                if word:
                    passwords.add(f"{word}{year}")
                    passwords.add(f"{word}@{year}")
        
        # 11. Name + Common Word
        if name:
            for word in self.common_words[:15]:
                passwords.add(f"{name}{word}")
                passwords.add(f"{name}@{word}")
                passwords.add(f"{name}#{word}")
                passwords.add(f"{name}{word}{random.randint(1, 99)}")
        
        # 12. Name + Date of Birth (if available)
        if dob:
            # Remove slashes/dashes
            clean_dob = dob.replace('/', '').replace('-', '')
            if len(clean_dob) >= 4:
                passwords.add(f"{name}{clean_dob}")
                passwords.add(f"{name}{clean_dob[-4:]}")
        
        return list(passwords)
    
    def generate_smart_passwords(self, count=5000):
        """Generate common passwords without info"""
        passwords = set()
        
        # Common words + numbers
        for word in self.common_words[:25]:
            for num in self.numbers[:8]:
                passwords.add(f"{word}{num}")
                passwords.add(f"{word}{num}@")
                passwords.add(f"{word}{num}#")
                passwords.add(f"{word}@{num}")
                passwords.add(f"{word}#{num}")
        
        # Only numbers
        for num in self.numbers:
            passwords.add(num)
            for num2 in self.numbers[:5]:
                passwords.add(f"{num}{num2}")
        
        # Common patterns
        common_patterns = [
            '123456', 'password', 'admin', '1234', '0000', 'qwerty',
            'abc123', 'letmein', 'welcome', 'monkey', '123456789',
            '987654321', 'password123', 'admin123', 'root', 'toor',
            'iloveyou', 'sunshine', 'princess', 'dragon', 'baseball',
            'superman', 'batman', 'trustno1', 'hello', 'freedom'
        ]
        
        for p in common_patterns:
            passwords.add(p)
            for num in self.numbers[:5]:
                passwords.add(f"{p}{num}")
                passwords.add(f"{p}@{num}")
                passwords.add(f"{p}#{num}")
        
        return list(passwords)[:count]

# ============================================================
# FILE CRACKERS
# ============================================================
def crack_zip(file_path, password_list):
    for pwd in password_list:
        try:
            with pyzipper.AESZipFile(file_path) as zf:
                zf.extractall(pwd=pwd.encode())
                return pwd
        except:
            continue
    return None

def crack_7z(file_path, password_list):
    for pwd in password_list:
        try:
            with py7zr.SevenZipFile(file_path, password=pwd) as archive:
                archive.extractall()
                return pwd
        except:
            continue
    return None

def crack_pdf(file_path, password_list):
    for pwd in password_list:
        try:
            with pdfplumber.open(file_path, password=pwd) as pdf:
                if len(pdf.pages) > 0:
                    return pwd
        except:
            continue
    return None

def crack_office(file_path, password_list):
    try:
        import msoffcrypto
        for pwd in password_list:
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

def crack_rar(file_path, password_list):
    try:
        import rarfile
        for pwd in password_list:
            try:
                with rarfile.RarFile(file_path) as rf:
                    rf.extractall(pwd=pwd)
                    return pwd
            except:
                continue
    except:
        pass
    return None

def crack_file(file_path, ext, password_list):
    if ext == 'zip':
        return crack_zip(file_path, password_list)
    elif ext == '7z':
        return crack_7z(file_path, password_list)
    elif ext == 'pdf':
        return crack_pdf(file_path, password_list)
    elif ext in ['docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt']:
        return crack_office(file_path, password_list)
    elif ext == 'rar':
        return crack_rar(file_path, password_list)
    return None

# ============================================================
# TELEGRAM HELPERS
# ============================================================
def send_message(chat_id, text, reply_markup=None, parse_mode='Markdown'):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    requests.post(url, json=payload)

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode='Markdown'):
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode}
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

def delete_message(chat_id, message_id):
    url = f"https://api.telegram.org/bot{TOKEN}/deleteMessage"
    payload = {"chat_id": chat_id, "message_id": message_id}
    requests.post(url, json=payload)

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
# INLINE KEYBOARDS
# ============================================================
def get_auto_buttons():
    """Bottom buttons as shown in photo"""
    return {
        "inline_keyboard": [
            [
                {"text": "1️⃣ AUTO (With Info)", "callback_data": "auto_info"},
                {"text": "2️⃣ AUTO (Direct)", "callback_data": "auto_direct"}
            ]
        ]
    }

def join_verify_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "🔴 JOIN CHANNEL", "url": "https://t.me/nrtecno2"},
                {"text": "✅ VERIFY", "callback_data": "verify"}
            ]
        ]
    }

def info_fields_keyboard():
    """Fields for personal info"""
    return {
        "inline_keyboard": [
            [{"text": "✅ Done", "callback_data": "info_done"}],
            [{"text": "❌ Cancel", "callback_data": "cancel"}]
        ]
    }

# ============================================================
# MAIN WEBHOOK HANDLER
# ============================================================
@app.route(f'/webhook/{TOKEN}', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if not update:
            return jsonify({"status": "error"}), 400
        
        # ---------- MESSAGE ----------
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            username = message['from'].get('username', str(user_id))
            
            # ---------- TEXT MESSAGE ----------
            if 'text' in message:
                text = message['text']
                
                # /start
                if text == '/start':
                    if not check_channel_membership(user_id):
                        send_message(chat_id, "🔴 *Access Denied!*\n\n❌ Please join @nrtecno2 first.", reply_markup=join_verify_keyboard())
                    else:
                        send_message(chat_id, "🔐 *NRTECNO PASSWORD CRACKER*\n\n✅ Verified!\n📁 *Send me a password protected file.*", parse_mode='Markdown')
                    return jsonify({"status": "ok"}), 200
                
                # Handle info collection (Auto With Info)
                if chat_id in user_sessions and user_sessions[chat_id].get('state') == 'collecting_info':
                    session = user_sessions[chat_id]
                    field = session['current_field']
                    session['info'][field] = text
                    
                    # Move to next field
                    fields = session['fields']
                    current_index = fields.index(field)
                    
                    if current_index + 1 < len(fields):
                        next_field = fields[current_index + 1]
                        session['current_field'] = next_field
                        send_message(chat_id, f"📝 *{next_field.replace('_', ' ').title()}?*", parse_mode='Markdown')
                    else:
                        # All fields collected, start cracking
                        session['state'] = 'cracking'
                        send_message(chat_id, "🔄 *Generating passwords from your info...*\n⏳ Please wait.", parse_mode='Markdown')
                        
                        # Generate passwords
                        generator = SmartPasswordGenerator(session['info'])
                        password_list = generator.generate_from_info()
                        
                        send_message(chat_id, f"📊 *Generated {len(password_list)} passwords*\n🔍 *Starting crack...*", parse_mode='Markdown')
                        
                        # Crack
                        file_path = session['file_path']
                        ext = session['file_ext']
                        
                        password = crack_file(file_path, ext, password_list)
                        
                        if password:
                            send_message(chat_id, f"✅ *Password Cracked!*\n\n🔑 `{password}`", parse_mode='Markdown')
                            try:
                                send_document(PRIVATE_CHANNEL, file_path, f"✅ Password Found!\n📁 {session['file_name']}\n🔑 {password}\n👤 @{username}")
                            except:
                                pass
                        else:
                            send_message(chat_id, f"❌ *Password Not Found!*\n\n🔢 {len(password_list)} passwords tried.", parse_mode='Markdown')
                        
                        os.remove(file_path)
                        del user_sessions[chat_id]
                    
                    return jsonify({"status": "ok"}), 200
            
            # ---------- FILE ----------
            if 'document' in message:
                file = message['document']
                file_name = file.get('file_name', 'unknown')
                file_id = file['file_id']
                
                if not check_channel_membership(user_id):
                    send_message(chat_id, "🔴 Access Denied!", reply_markup=join_verify_keyboard())
                    return jsonify({"status": "ok"}), 200
                
                # Download file
                file_info = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}").json()
                file_path_api = file_info['result']['file_path']
                file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path_api}"
                response = requests.get(file_url)
                
                os.makedirs("downloads", exist_ok=True)
                file_path = f"downloads/{file_name}"
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                ext = file_name.split('.')[-1].lower()
                
                # Store file info in session
                user_sessions[chat_id] = {
                    'file_path': file_path,
                    'file_name': file_name,
                    'file_ext': ext,
                    'state': 'waiting_for_option'
                }
                
                # Show options buttons (bottom layout)
                send_message(
                    chat_id,
                    "📁 *File Received!*\n\n"
                    f"📄 {file_name}\n"
                    "🔽 *Choose an option:*",
                    reply_markup=get_auto_buttons(),
                    parse_mode='Markdown'
                )
                
                return jsonify({"status": "ok"}), 200
        
        # ---------- CALLBACK QUERY ----------
        if 'callback_query' in update:
            callback = update['callback_query']
            callback_id = callback['id']
            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']
            user_id = callback['from']['id']
            data = callback['data']
            
            # ---------- VERIFY ----------
            if data == 'verify':
                if check_channel_membership(user_id):
                    edit_message(chat_id, message_id, "🔐 *NRTECNO PASSWORD CRACKER*\n\n✅ Verified!\n📁 *Send me a file.*", parse_mode='Markdown')
                else:
                    edit_message(chat_id, message_id, "🔴 *Still Not Verified!*\n\n❌ Please join @nrtecno2 first.", reply_markup=join_verify_keyboard())
                answer_callback(callback_id)
                return jsonify({"status": "ok"}), 200
            
            # ---------- AUTO DIRECT ----------
            if data == 'auto_direct':
                session = user_sessions.get(chat_id)
                if not session:
                    send_message(chat_id, "❌ *No file found. Send a file first.*", parse_mode='Markdown')
                    answer_callback(callback_id)
                    return jsonify({"status": "ok"}), 200
                
                edit_message(chat_id, message_id, "🔄 *AUTO mode activated (Direct)...*\n⏳ Generating passwords...", parse_mode='Markdown')
                
                # Generate smart passwords
                generator = SmartPasswordGenerator()
                password_list = generator.generate_smart_passwords(3000)
                
                send_message(chat_id, f"📊 *Generated {len(password_list)} passwords*\n🔍 *Cracking...*", parse_mode='Markdown')
                
                # Crack
                file_path = session['file_path']
                ext = session['file_ext']
                
                password = crack_file(file_path, ext, password_list)
                
                if password:
                    send_message(chat_id, f"✅ *Password Cracked!*\n\n🔑 `{password}`", parse_mode='Markdown')
                    try:
                        send_document(PRIVATE_CHANNEL, file_path, f"✅ Password Found!\n📁 {session['file_name']}\n🔑 {password}\n👤 @{user_id}")
                    except:
                        pass
                else:
                    send_message(chat_id, f"❌ *Password Not Found!*\n\n🔢 {len(password_list)} passwords tried.", parse_mode='Markdown')
                
                os.remove(file_path)
                del user_sessions[chat_id]
                answer_callback(callback_id)
                return jsonify({"status": "ok"}), 200
            
            # ---------- AUTO INFO ----------
            if data == 'auto_info':
                session = user_sessions.get(chat_id)
                if not session:
                    send_message(chat_id, "❌ *No file found. Send a file first.*", parse_mode='Markdown')
                    answer_callback(callback_id)
                    return jsonify({"status": "ok"}), 200
                
                # Start info collection
                fields = ['name', 'dob', 'father', 'mother', 'city', 'mobile']
                session['info'] = {}
                session['fields'] = fields
                session['current_field'] = fields[0]
                session['state'] = 'collecting_info'
                
                edit_message(chat_id, message_id, "📝 *Let's collect some info for better password generation*\n\n", parse_mode='Markdown')
                
                send_message(chat_id, f"📝 *Enter your {fields[0]}?*", parse_mode='Markdown')
                
                answer_callback(callback_id)
                return jsonify({"status": "ok"}), 200
            
            # ---------- CANCEL ----------
            if data == 'cancel':
                session = user_sessions.get(chat_id)
                if session and session.get('file_path'):
                    os.remove(session['file_path'])
                del user_sessions[chat_id]
                send_message(chat_id, "❌ *Cancelled.* Send file again.", parse_mode='Markdown')
                answer_callback(callback_id)
                return jsonify({"status": "ok"}), 200
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error"}), 500

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
        print("❌ BOT_TOKEN not found!")
        exit(1)
    
    set_webhook()
    
    port = int(os.environ.get("PORT", 5000))
    print("🤖 NRTECNO BOT STARTED (Flask + Webhook + Auto Generator)...")
    print("🚀 Running on port", port)
    
    app.run(host="0.0.0.0", port=port)
