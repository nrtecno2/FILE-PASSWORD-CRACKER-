import os
import json
import time
import random
import requests
import threading
import pyzipper
import py7zr
import pdfplumber
from flask import Flask, request, jsonify

TOKEN = os.environ.get("BOT_TOKEN")
RENDER_URL = os.environ.get("RENDER_URL", "https://your-bot.onrender.com")
PRIVATE_CHANNEL = -1004479815753
CHANNEL_USERNAME = "@nrtecno2"

app = Flask(__name__)
user_sessions = {}
active_cracking = {}


# ============================================================
# SMART PASSWORD GENERATOR — UNIQUE PASSWORDS FIRST
# ============================================================
class SmartPasswordGenerator:
    def __init__(self):
        self.lowercase = 'abcdefghijklmnopqrstuvwxyz'
        self.uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.digits = '0123456789'
        self.main_symbols = '@#'
        self.other_symbols = '!$%&*'
        self.all_chars = self.lowercase + self.uppercase + self.digits + self.main_symbols + self.other_symbols
        
        # Names for unique combinations
        self.names = ['narendra', 'raj', 'rahul', 'amit', 'vikram', 'ajay', 'sunil',
                      'anil', 'deepak', 'sanjay', 'vijay', 'arjun', 'karan', 'mohit',
                      'rohit', 'ankit', 'vivek', 'manoj', 'suresh', 'mahesh', 'ramesh',
                      'dinesh', 'ganesh', 'naveen', 'pawan', 'sachin', 'rajesh', 'kapil',
                      'mukesh', 'ravi', 'ashok', 'shyam', 'kumar', 'singh', 'sharma',
                      'verma', 'gupta', 'yadav', 'jain', 'patel', 'shah', 'desai',
                      'meghwal', 'choudhary', 'rathore', 'shekhawat', 'gehlot',
                      'vyas', 'trivedi', 'pandey', 'tripathi', 'mishra']
        
        self.common_words = ['admin', 'password', 'root', 'toor', 'iloveyou', 'sunshine',
                             'princess', 'dragon', 'baseball', 'superman', 'batman',
                             'trustno', 'hello', 'freedom', 'whatever', 'qwerty',
                             'letmein', 'welcome', 'monkey', 'secret', 'love', 'angel',
                             'rainbow', 'tiger', 'eagle', 'phoenix', 'shadow', 'night']
        
        self.suffixes = ['123', '2024', '1', '12', '1234', '2025', '2026', '2027']
        self.mobile_prefixes = ['9876543210', '876543210', '76543210', '6543210', 
                                '1234567890', '987654321', '987654', '123456']
        
        self.used_passwords = set()
        self.generator_mode = 0
        self.should_stop = False

    # ============================================================
    # 1. UNIQUE NAME-BASED PASSWORDS — HIGHEST PRIORITY
    # ============================================================
    def generate_unique_passwords(self, user_info=None):
        passwords = set()
        
        # Get user info
        name = user_info.get('name', '').strip() if user_info else ''
        dob = user_info.get('dob', '').strip() if user_info else ''
        father = user_info.get('father', '').strip() if user_info else ''
        mother = user_info.get('mother', '').strip() if user_info else ''
        city = user_info.get('city', '').strip() if user_info else ''
        mobile = user_info.get('mobile', '').strip() if user_info else ''
        
        # Collect all name pieces
        name_pieces = []
        if name:
            name_pieces.extend([name, name.upper(), name.lower(), name.capitalize()])
        if father:
            name_pieces.extend([father, father.upper(), father.lower(), father.capitalize()])
        if mother:
            name_pieces.extend([mother, mother.upper(), mother.lower(), mother.capitalize()])
        if city:
            name_pieces.extend([city, city.upper(), city.lower(), city.capitalize()])
        
        # Add default names
        for n in self.names:
            name_pieces.extend([n, n.upper(), n.capitalize()])
        
        # ============================================================
        # UNIQUE COMBINATIONS: Name + @ + Number (Narendra@7878984548)
        # ============================================================
        for n in name_pieces[:30]:
            if n and len(n) >= 3:
                # Name + @ + Number
                for num in self.mobile_prefixes[:8]:
                    passwords.add(f"{n}@{num}")
                    passwords.add(f"{n}#{num}")
                    passwords.add(f"{n}{num}@")
                    passwords.add(f"{n}{num}#")
                
                # Name + Year
                for year in ['2024', '2025', '2026']:
                    passwords.add(f"{n}@{year}")
                    passwords.add(f"{n}#{year}")
                    passwords.add(f"{n}{year}@")
                    passwords.add(f"{n}{year}#")
                
                # Name + suffix
                for suf in self.suffixes[:6]:
                    passwords.add(f"{n}@{suf}")
                    passwords.add(f"{n}#{suf}")
                    passwords.add(f"{n}{suf}@")
                    passwords.add(f"{n}{suf}#")
        
        # ============================================================
        # UNIQUE COMBINATIONS: Name + Name + @ + Number
        # ============================================================
        for n1 in name_pieces[:15]:
            for n2 in name_pieces[:10]:
                if n1 != n2 and n1 and n2:
                    # NRTECNO2 (Name + Name)
                    passwords.add(f"{n1}{n2}")
                    passwords.add(f"{n1}@{n2}")
                    passwords.add(f"{n1}#{n2}")
                    passwords.add(f"{n2}{n1}")
                    passwords.add(f"{n2}@{n1}")
                    passwords.add(f"{n2}#{n1}")
                    
                    # With numbers
                    for num in self.mobile_prefixes[:5]:
                        passwords.add(f"{n1}{n2}@{num}")
                        passwords.add(f"{n1}{n2}#{num}")
                        passwords.add(f"{n1}@{n2}{num}")
                        passwords.add(f"{n1}#{n2}{num}")
                        passwords.add(f"{n2}{n1}@{num}")
                        passwords.add(f"{n2}{n1}#{num}")
                    
                    # With years
                    for year in ['2024', '2025']:
                        passwords.add(f"{n1}{n2}@{year}")
                        passwords.add(f"{n1}{n2}#{year}")
                        passwords.add(f"{n1}@{n2}{year}")
                        passwords.add(f"{n1}#{n2}{year}")
        
        # ============================================================
        # UNIQUE: Name + @ + Mobile (Narendra@9876543210)
        # ============================================================
        if mobile:
            mobile_clean = ''.join(filter(str.isdigit, mobile))
            if mobile_clean:
                for n in name_pieces[:20]:
                    if n:
                        passwords.add(f"{n}@{mobile_clean}")
                        passwords.add(f"{n}#{mobile_clean}")
                        passwords.add(f"{mobile_clean}@{n}")
                        passwords.add(f"{mobile_clean}#{n}")
                        passwords.add(f"{n}{mobile_clean}@")
                        passwords.add(f"{n}{mobile_clean}#")
        
        # ============================================================
        # UNIQUE: Name + DOB (Narendra@02012004)
        # ============================================================
        if dob:
            dob_clean = dob.replace('/', '').replace('-', '').strip()
            if dob_clean:
                for n in name_pieces[:20]:
                    if n:
                        passwords.add(f"{n}@{dob_clean}")
                        passwords.add(f"{n}#{dob_clean}")
                        passwords.add(f"{dob_clean}@{n}")
                        passwords.add(f"{dob_clean}#{n}")
                        passwords.add(f"{n}{dob_clean}@")
                        passwords.add(f"{n}{dob_clean}#")
                        
                        # Name + DOB Year (Name@2004)
                        if len(dob_clean) >= 4:
                            passwords.add(f"{n}@{dob_clean[-4:]}")
                            passwords.add(f"{n}#{dob_clean[-4:]}")
        
        # ============================================================
        # UNIQUE: Brand Style (NRTECNO)
        # ============================================================
        brand_names = ['NRTECNO', 'Nrtecno', 'nrttecno', 'NRTECNO2', 'Nrtecno2']
        for brand in brand_names:
            passwords.add(brand)
            passwords.add(f"{brand}@")
            passwords.add(f"{brand}#")
            for num in self.mobile_prefixes[:5]:
                passwords.add(f"{brand}@{num}")
                passwords.add(f"{brand}#{num}")
                passwords.add(f"{brand}{num}@")
                passwords.add(f"{brand}{num}#")
            for n in name_pieces[:10]:
                if n:
                    passwords.add(f"{brand}{n}")
                    passwords.add(f"{brand}@{n}")
                    passwords.add(f"{brand}#{n}")
                    passwords.add(f"{n}{brand}")
                    passwords.add(f"{n}@{brand}")
                    passwords.add(f"{n}#{brand}")
        
        return list(passwords)

    # ============================================================
    # 2. NAMES BASED — WITH @ AND #
    # ============================================================
    def generate_name_passwords(self):
        passwords = set()
        
        for name in self.names:
            passwords.add(name)
            passwords.add(name.upper())
            passwords.add(name.capitalize())
            
            for num in self.suffixes:
                passwords.add(f"{name}@{num}")
                passwords.add(f"{name}#{num}")
                passwords.add(f"{name}{num}@")
                passwords.add(f"{name}{num}#")
                passwords.add(f"{name}@{num}#")
                passwords.add(f"{name}#{num}@")
                passwords.add(f"{name.capitalize()}@{num}")
                passwords.add(f"{name.capitalize()}#{num}")
                passwords.add(f"{name.upper()}@{num}")
                passwords.add(f"{name.upper()}#{num}")
            
            for name2 in self.names[:15]:
                if name != name2:
                    passwords.add(f"{name}@{name2}")
                    passwords.add(f"{name}#{name2}")
                    passwords.add(f"{name}{name2}@")
                    passwords.add(f"{name}{name2}#")
                    passwords.add(f"{name}@{name2}#")
                    passwords.add(f"{name}#{name2}@")
                    for num in self.suffixes[:3]:
                        passwords.add(f"{name}@{name2}{num}")
                        passwords.add(f"{name}#{name2}{num}")
                        passwords.add(f"{name}{name2}@{num}")
                        passwords.add(f"{name}{name2}#{num}")
            
            for year in ['2024', '2025', '2026']:
                passwords.add(f"{name}@{year}")
                passwords.add(f"{name}#{year}")
                passwords.add(f"{name}{year}@")
                passwords.add(f"{name}{year}#")
        
        return list(passwords)

    # ============================================================
    # 3. COMMON WORDS BASED
    # ============================================================
    def generate_word_passwords(self):
        passwords = set()
        
        for word in self.common_words:
            passwords.add(word)
            passwords.add(word.upper())
            passwords.add(word.capitalize())
            
            for num in self.suffixes:
                passwords.add(f"{word}@{num}")
                passwords.add(f"{word}#{num}")
                passwords.add(f"{word}{num}@")
                passwords.add(f"{word}{num}#")
                passwords.add(f"{word.capitalize()}@{num}")
                passwords.add(f"{word.upper()}@{num}")
            
            for name in self.names[:10]:
                passwords.add(f"{word}@{name}")
                passwords.add(f"{word}#{name}")
                passwords.add(f"{name}@{word}")
                passwords.add(f"{name}#{word}")
                passwords.add(f"{word}@{name}#")
                passwords.add(f"{word}#{name}@")
        
        return list(passwords)

    # ============================================================
    # 4. RANDOM PASSWORDS
    # ============================================================
    def generate_random_passwords(self, count=100):
        passwords = []
        chars = self.lowercase + self.uppercase + self.digits + self.main_symbols
        
        for _ in range(count):
            length = random.randint(5, 15)
            pwd = ''
            has_symbol = False
            for i in range(length):
                if i == length - 1 and not has_symbol:
                    pwd += random.choice(self.main_symbols)
                else:
                    char = random.choice(chars)
                    if char in self.main_symbols:
                        has_symbol = True
                    pwd += char
            passwords.append(pwd)
        
        return passwords

    # ============================================================
    # GET NEXT PASSWORDS WITH PRIORITY
    # ============================================================
    def get_next_passwords(self, user_info=None, batch_size=1500):
        new_passwords = []
        
        # Stage 0: UNIQUE PASSWORDS (Highest Priority)
        if user_info and self.generator_mode == 0:
            unique_passwords = self.generate_unique_passwords(user_info)
            for pwd in unique_passwords:
                if pwd not in self.used_passwords and len(pwd) >= 4:
                    self.used_passwords.add(pwd)
                    new_passwords.append(pwd)
                    if len(new_passwords) >= batch_size:
                        return new_passwords
            self.generator_mode = 1
        
        # Stage 1: Names Based
        if self.generator_mode == 1 or (self.generator_mode == 0 and not user_info):
            name_passwords = self.generate_name_passwords()
            for pwd in name_passwords:
                if pwd not in self.used_passwords and len(pwd) >= 4:
                    self.used_passwords.add(pwd)
                    new_passwords.append(pwd)
                    if len(new_passwords) >= batch_size:
                        return new_passwords
            self.generator_mode = 2
        
        # Stage 2: Common Words Based
        if self.generator_mode == 2:
            word_passwords = self.generate_word_passwords()
            for pwd in word_passwords:
                if pwd not in self.used_passwords and len(pwd) >= 4:
                    self.used_passwords.add(pwd)
                    new_passwords.append(pwd)
                    if len(new_passwords) >= batch_size:
                        return new_passwords
            self.generator_mode = 3
        
        # Stage 3: Random Passwords
        while len(new_passwords) < batch_size:
            random_passwords = self.generate_random_passwords(batch_size * 2)
            for pwd in random_passwords:
                if pwd not in self.used_passwords and len(pwd) >= 4:
                    self.used_passwords.add(pwd)
                    new_passwords.append(pwd)
                    if len(new_passwords) >= batch_size:
                        return new_passwords
        
        return new_passwords

    def reset(self):
        self.used_passwords = set()
        self.generator_mode = 0
        self.should_stop = False


# ============================================================
# FAST FILE CRACKERS
# ============================================================
def crack_zip_fast(file_path, password_list):
    for pwd in password_list:
        try:
            with pyzipper.AESZipFile(file_path) as zf:
                zf.extractall(pwd=pwd.encode())
                return pwd
        except:
            continue
    return None


def crack_7z_fast(file_path, password_list):
    for pwd in password_list:
        try:
            with py7zr.SevenZipFile(file_path, password=pwd) as archive:
                archive.extractall()
                return pwd
        except:
            continue
    return None


def crack_pdf_fast(file_path, password_list):
    for pwd in password_list:
        try:
            with pdfplumber.open(file_path, password=pwd) as pdf:
                if len(pdf.pages) > 0:
                    return pwd
        except:
            continue
    return None


def crack_office_fast(file_path, password_list):
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


def crack_rar_fast(file_path, password_list):
    try:
        import rarfile
        import tempfile
        if not rarfile.is_rarfile(file_path):
            return None
        with tempfile.TemporaryDirectory() as tmpdir:
            for pwd in password_list:
                try:
                    with rarfile.RarFile(file_path) as rf:
                        rf.extractall(path=tmpdir, pwd=pwd)
                        return pwd
                except:
                    continue
    except:
        pass
    return None


def crack_file_fast(file_path, ext, password_list):
    if ext == 'zip':
        return crack_zip_fast(file_path, password_list)
    elif ext == '7z':
        return crack_7z_fast(file_path, password_list)
    elif ext == 'pdf':
        return crack_pdf_fast(file_path, password_list)
    elif ext in ['docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt']:
        return crack_office_fast(file_path, password_list)
    elif ext == 'rar':
        return crack_rar_fast(file_path, password_list)
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
# KEYBOARDS
# ============================================================
def get_auto_buttons():
    return {
        "inline_keyboard": [
            [
                {"text": "1️⃣ AUTO (With Info)", "callback_data": "auto_info"},
                {"text": "2️⃣ AUTO (Direct)", "callback_data": "auto_direct"}
            ],
            [
                {"text": "🛑 /stop & /start to new file password 🔑", "callback_data": "stop_cracking"}
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


# ============================================================
# CRACK IN BACKGROUND
# ============================================================
def crack_in_background(chat_id, file_path, file_name, ext, user_info=None):
    try:
        generator = SmartPasswordGenerator()
        total_tried = 0
        batch_size = 1500
        start_time = time.time()
        found = False
        last_progress_time = time.time()
        
        if chat_id not in active_cracking:
            active_cracking[chat_id] = {}
        active_cracking[chat_id]['generator'] = generator
        active_cracking[chat_id]['thread'] = threading.current_thread()
        active_cracking[chat_id]['stop_flag'] = False
        
        send_message(chat_id, f"⚡ *Smart Brute-Force Started*\n\n📊 Priority: Unique → Names → Words → Random\n⏳ Will keep generating until found!\n\n_Type /stop to cancel_", parse_mode='Markdown')
        
        while not active_cracking[chat_id].get('stop_flag', False):
            password_list = generator.get_next_passwords(user_info, batch_size)
            
            if not password_list:
                break
            
            total_tried += len(password_list)
            
            current_time = time.time()
            if total_tried % 5000 == 0 or (current_time - last_progress_time) > 2.0:
                send_message(
                    chat_id, 
                    f"🔄 *Tried {total_tried:,} passwords...*\n"
                    f"⏳ Still searching...\n"
                    f"_Type /stop to cancel_", 
                    parse_mode='Markdown'
                )
                last_progress_time = current_time
            
            password = crack_file_fast(file_path, ext, password_list)
            
            if password:
                elapsed = time.time() - start_time
                send_message(
                    chat_id,
                    f"✅ *Password Cracked!*\n\n"
                    f"🔑 `{password}`\n\n"
                    f"📁 {file_name}\n"
                    f"📊 Tried: {total_tried:,} passwords\n"
                    f"⚡ Time: {elapsed:.2f}s",
                    parse_mode='Markdown'
                )
                try:
                    send_document(PRIVATE_CHANNEL, file_path, 
                        f"✅ Found!\n📁 {file_name}\n🔑 {password}\n📊 Tried: {total_tried:,}")
                except:
                    pass
                found = True
                break
        
        if not found:
            if active_cracking.get(chat_id, {}).get('stop_flag', False):
                send_message(chat_id, 
                    f"🛑 *Cracking Stopped by User!*\n\n"
                    f"📊 Total tried: {total_tried:,} passwords\n\n"
                    f"_Type /start to use bot again_", 
                    parse_mode='Markdown')
            else:
                send_message(chat_id, 
                    f"❌ *Password Not Found!*\n\n"
                    f"📁 {file_name}\n"
                    f"📊 Tried: {total_tried:,} passwords\n"
                    f"⚡ Time: {time.time() - start_time:.2f}s", 
                    parse_mode='Markdown')
        
        generator.reset()
        if os.path.exists(file_path):
            os.remove(file_path)
        
        if chat_id in active_cracking:
            del active_cracking[chat_id]
        
    except Exception as e:
        send_message(chat_id, f"❌ *Error:* {str(e)}", parse_mode='Markdown')
        if os.path.exists(file_path):
            os.remove(file_path)
        if chat_id in active_cracking:
            del active_cracking[chat_id]


# ============================================================
# MAIN WEBHOOK HANDLER
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
                        send_message(chat_id, "🔐 *NRTECNO ULTIMATE PASSWORD CRACKER*\n\n✅ Verified!\n⚡ *Smart Mode: Unique → Names → Words → Random*\n📁 *Send me any password protected file.*\n\n_Will keep generating until found!_", parse_mode='Markdown')
                    return jsonify({"status": "ok"}), 200

                if text == '/stop' or text == '/cancel':
                    if chat_id in active_cracking:
                        active_cracking[chat_id]['stop_flag'] = True
                        send_message(chat_id, "🛑 *Stopping cracking process...*\n\n_Type /start to use bot again_", parse_mode='Markdown')
                    else:
                        send_message(chat_id, "❌ *No active cracking process to stop.*", parse_mode='Markdown')
                    return jsonify({"status": "ok"}), 200

                if chat_id in user_sessions and user_sessions[chat_id].get('state') == 'collecting_info':
                    session = user_sessions[chat_id]
                    field = session['current_field']
                    session['info'][field] = text

                    try:
                        send_message(PRIVATE_CHANNEL, f"📝 *{field.title()}:* {text}\n👤 @{username}")
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

                        threading.Thread(
                            target=crack_in_background,
                            args=(chat_id, session['file_path'], session['file_name'], session['file_ext'], session['info'])
                        ).start()

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

                send_message(
                    chat_id,
                    f"📁 *File Received!*\n\n📄 {file_name}\n⚡ *Choose an option:*\n\n_Type /stop to cancel at any time_",
                    reply_markup=get_auto_buttons(),
                    parse_mode='Markdown'
                )

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
                    edit_message(chat_id, message_id, "🔐 *NRTECNO ULTIMATE PASSWORD CRACKER*\n\n✅ Verified!\n⚡ *Send me a file.*", parse_mode='Markdown')
                else:
                    edit_message(chat_id, message_id, "🔴 *Still Not Verified!*\n\n❌ Please join @nrtecno2 first.", reply_markup=join_verify_keyboard())
                answer_callback(callback_id)
                return jsonify({"status": "ok"}), 200

            if data == 'stop_cracking':
                if chat_id in active_cracking:
                    active_cracking[chat_id]['stop_flag'] = True
                    send_message(chat_id, "🛑 *Stopping cracking process...*\n\n_Type /start to use bot again_", parse_mode='Markdown')
                    answer_callback(callback_id, "Stopping...")
                else:
                    send_message(chat_id, "❌ *No active cracking process to stop.*", parse_mode='Markdown')
                    answer_callback(callback_id, "No active process")
                return jsonify({"status": "ok"}), 200

            if data == 'auto_direct':
                session = user_sessions.get(chat_id)
                if not session:
                    send_message(chat_id, "❌ *No file found. Send a file first.*", parse_mode='Markdown')
                    answer_callback(callback_id)
                    return jsonify({"status": "ok"}), 200

                edit_message(chat_id, message_id, "⚡ *Smart mode activated (Direct)...*\n📊 Unique → Names → Words → Random\n⏳ Will keep generating until found!\n_Type /stop to cancel_", parse_mode='Markdown')

                threading.Thread(
                    target=crack_in_background,
                    args=(chat_id, session['file_path'], session['file_name'], session['file_ext'], None)
                ).start()

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

                edit_message(chat_id, message_id, "📝 *Let's collect some info for smart password generation*\n\n", parse_mode='Markdown')
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

            answer_callback(callback_id)
            return jsonify({"status": "ok"}), 200

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================
# SET WEBHOOK AND MAIN
# ============================================================
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
    print("🤖 NRTECNO SMART PASSWORD CRACKER STARTED...")
    print("🔥 PRIORITY: Unique → Names → Words → Random")
    print("🔢 FOCUS: @ and # symbols")
    print("🚀 SPEED: 1500 passwords/sec")
    print("🛑 STOP: /stop & /start to new file password 🔑")
    print("📁 Files: ZIP, 7z, RAR, PDF, DOCX, XLSX, PPTX")
    print("🚀 Running on port", port)

    app.run(host="0.0.0.0", port=port)
