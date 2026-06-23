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
# INFINITE PASSWORD GENERATOR — NO REPEAT
# ============================================================
class InfinitePasswordGenerator:
    def __init__(self):
        self.all_chars = 'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890~`|•√π÷×§∆£€$¢^°={}%©®™✓[]<>@#₹_&-+()/*"\'":;!?,. '
        
        self.names = ['admin', 'root', 'user', 'guest', 'login', 'test', 'demo',
                      'narendra', 'raj', 'rahul', 'amit', 'vikram', 'ajay', 'sunil',
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
                             'rainbow', 'tiger', 'eagle', 'phoenix', 'shadow', 'night',
                             'star', 'moon', 'sun', 'cloud', 'thunder', 'lightning']
        
        self.special_chars = ['@', '#', '&', '%', '!', '$', '_', '-', '+', '=', '~', '^', '*', '?']
        self.numbers = ['1', '12', '123', '1234', '12345', '123456', '1234567', '12345678',
                        '123456789', '1234567890']
        self.years = ['2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030']
        self.months = ['january', 'february', 'march', 'april', 'may', 'june',
                       'july', 'august', 'september', 'october', 'november', 'december']
        
        self.used_passwords = set()
        self.generator_index = 0
        self.should_stop = False

    # ============================================================
    # 1. USER INFO BASED — FIRST PRIORITY (All Combinations)
    # ============================================================
    def generate_from_user_info(self, user_info):
        """Generate all possible combinations from user info"""
        passwords = set()
        
        name = user_info.get('name', '').strip()
        dob = user_info.get('dob', '').strip()
        father = user_info.get('father', '').strip()
        mother = user_info.get('mother', '').strip()
        city = user_info.get('city', '').strip()
        mobile = user_info.get('mobile', '').strip()
        
        # Clean and store all info pieces
        info_pieces = []
        
        if name:
            name_clean = name.strip()
            info_pieces.append(name_clean)
            info_pieces.append(name_clean.upper())
            info_pieces.append(name_clean.lower())
            info_pieces.append(name_clean.capitalize())
            info_pieces.append(name_clean.title())
        
        if dob:
            dob_clean = dob.replace('/', '').replace('-', '').strip()
            info_pieces.append(dob_clean)
            info_pieces.append(dob_clean[-4:])  # Year
            info_pieces.append(dob_clean[-6:])  # Month+Year
        
        if father:
            father_clean = father.strip()
            info_pieces.append(father_clean)
            info_pieces.append(father_clean.upper())
            info_pieces.append(father_clean.lower())
            info_pieces.append(father_clean.capitalize())
        
        if mother:
            mother_clean = mother.strip()
            info_pieces.append(mother_clean)
            info_pieces.append(mother_clean.upper())
            info_pieces.append(mother_clean.lower())
            info_pieces.append(mother_clean.capitalize())
        
        if city:
            city_clean = city.strip()
            info_pieces.append(city_clean)
            info_pieces.append(city_clean.upper())
            info_pieces.append(city_clean.lower())
            info_pieces.append(city_clean.capitalize())
        
        if mobile:
            mobile_clean = ''.join(filter(str.isdigit, mobile))
            if mobile_clean:
                info_pieces.append(mobile_clean)
                info_pieces.append(mobile_clean[-4:])
                info_pieces.append(mobile_clean[-6:])
        
        # ============================================================
        # COMBINATION 1: Single info pieces (Name, DOB, Father, Mother, City, Mobile)
        # ============================================================
        for piece in info_pieces:
            if piece and len(piece) >= 3:
                passwords.add(piece)
                # Add reverse
                passwords.add(piece[::-1])
                # Add with common suffixes
                for num in ['123', '2024']:
                    passwords.add(f"{piece}{num}")
                    passwords.add(f"{piece}@{num}")
                    passwords.add(f"{piece}#{num}")
                    passwords.add(f"{piece} {num}")
        
        # ============================================================
        # COMBINATION 2: Two info pieces combined
        # Example: NRTECNO2 (Name + Father), NR2TECNO (Name + Mother)
        # ============================================================
        info_list = [p for p in info_pieces if p and len(p) >= 2]
        
        for i in range(len(info_list)):
            for j in range(len(info_list)):
                if i != j:
                    p1 = info_list[i]
                    p2 = info_list[j]
                    
                    # p1 + p2
                    passwords.add(f"{p1}{p2}")
                    passwords.add(f"{p1}@{p2}")
                    passwords.add(f"{p1}#{p2}")
                    passwords.add(f"{p1} {p2}")
                    passwords.add(f"{p1}_{p2}")
                    passwords.add(f"{p1}-{p2}")
                    
                    # p2 + p1
                    passwords.add(f"{p2}{p1}")
                    passwords.add(f"{p2}@{p1}")
                    passwords.add(f"{p2}#{p1}")
                    passwords.add(f"{p2} {p1}")
                    
                    # With numbers
                    for num in ['123', '2024']:
                        passwords.add(f"{p1}{p2}{num}")
                        passwords.add(f"{p1}{num}{p2}")
                        passwords.add(f"{p2}{p1}{num}")
                        passwords.add(f"{p2}{num}{p1}")
        
        # ============================================================
        # COMBINATION 3: Three info pieces combined
        # Example: NRTECNO2 (Name + Mother + Father)
        # ============================================================
        for i in range(len(info_list)):
            for j in range(len(info_list)):
                for k in range(len(info_list)):
                    if i != j and j != k and i != k:
                        p1 = info_list[i]
                        p2 = info_list[j]
                        p3 = info_list[k]
                        
                        # p1 + p2 + p3
                        passwords.add(f"{p1}{p2}{p3}")
                        passwords.add(f"{p1}@{p2}{p3}")
                        passwords.add(f"{p1}{p2}@{p3}")
                        passwords.add(f"{p1}#{p2}{p3}")
                        passwords.add(f"{p1}{p2}#{p3}")
                        passwords.add(f"{p1} {p2} {p3}")
                        passwords.add(f"{p1}_{p2}_{p3}")
                        passwords.add(f"{p1}-{p2}-{p3}")
                        
                        # All permutations
                        passwords.add(f"{p1}{p3}{p2}")
                        passwords.add(f"{p2}{p1}{p3}")
                        passwords.add(f"{p2}{p3}{p1}")
                        passwords.add(f"{p3}{p1}{p2}")
                        passwords.add(f"{p3}{p2}{p1}")
                        
                        # With numbers
                        for num in ['123', '2024']:
                            passwords.add(f"{p1}{p2}{p3}{num}")
                            passwords.add(f"{p1}{num}{p2}{p3}")
                            passwords.add(f"{num}{p1}{p2}{p3}")
        
        # ============================================================
        # COMBINATION 4: Info + Special + Info
        # ============================================================
        for p1 in info_list[:10]:
            for p2 in info_list[:10]:
                if p1 != p2:
                    for spec in ['@', '#', '&', '%', '!']:
                        passwords.add(f"{p1}{spec}{p2}")
                        passwords.add(f"{p1} {spec} {p2}")
                        passwords.add(f"{spec}{p1}{p2}")
                        passwords.add(f"{p1}{p2}{spec}")
                        for num in ['123', '2024']:
                            passwords.add(f"{p1}{spec}{p2}{num}")
                            passwords.add(f"{p1}{num}{spec}{p2}")
        
        # ============================================================
        # COMBINATION 5: Info + DOB/Year
        # ============================================================
        if dob:
            dob_clean = dob.replace('/', '').replace('-', '').strip()
            if dob_clean:
                for p in info_list[:10]:
                    passwords.add(f"{p}{dob_clean}")
                    passwords.add(f"{p}@{dob_clean}")
                    passwords.add(f"{p}#{dob_clean}")
                    passwords.add(f"{p} {dob_clean}")
                    passwords.add(f"{dob_clean}{p}")
                    passwords.add(f"{dob_clean}@{p}")
                    passwords.add(f"{p}{dob_clean[-4:]}")
                    passwords.add(f"{p}@{dob_clean[-4:]}")
                    passwords.add(f"{p}{dob_clean[-6:]}")
                    passwords.add(f"{p}@{dob_clean[-6:]}")
        
        # ============================================================
        # COMBINATION 6: Info + Mobile
        # ============================================================
        if mobile:
            mobile_clean = ''.join(filter(str.isdigit, mobile))
            if mobile_clean:
                for p in info_list[:10]:
                    passwords.add(f"{p}{mobile_clean}")
                    passwords.add(f"{p}@{mobile_clean}")
                    passwords.add(f"{p}#{mobile_clean}")
                    passwords.add(f"{p} {mobile_clean}")
                    passwords.add(f"{mobile_clean}{p}")
                    passwords.add(f"{mobile_clean}@{p}")
                    passwords.add(f"{p}{mobile_clean[-4:]}")
                    passwords.add(f"{p}@{mobile_clean[-4:]}")
        
        # ============================================================
        # COMBINATION 7: Name + Father + Mother (Family combinations)
        # ============================================================
        if name and father and mother:
            n = name.strip()
            f = father.strip()
            m = mother.strip()
            
            passwords.add(f"{n}{f}{m}")
            passwords.add(f"{n}@{f}{m}")
            passwords.add(f"{n}{f}@{m}")
            passwords.add(f"{f}{n}{m}")
            passwords.add(f"{f}@{n}{m}")
            passwords.add(f"{m}{n}{f}")
            passwords.add(f"{m}@{n}{f}")
            passwords.add(f"{n} {f} {m}")
            passwords.add(f"{f} {n} {m}")
            passwords.add(f"{m} {n} {f}")
            passwords.add(f"{n}_{f}_{m}")
            passwords.add(f"{n}-{f}-{m}")
            
            for num in ['123', '2024']:
                passwords.add(f"{n}{f}{m}{num}")
                passwords.add(f"{n}{num}{f}{m}")
                passwords.add(f"{num}{n}{f}{m}")
        
        # ============================================================
        # COMBINATION 8: Name + City + Father
        # ============================================================
        if name and city and father:
            n = name.strip()
            c = city.strip()
            f = father.strip()
            
            passwords.add(f"{n}{c}{f}")
            passwords.add(f"{n}@{c}{f}")
            passwords.add(f"{c}{n}{f}")
            passwords.add(f"{c}@{n}{f}")
            passwords.add(f"{n} {c} {f}")
            passwords.add(f"{c} {n} {f}")
            passwords.add(f"{n}_{c}_{f}")
            
            for num in ['123', '2024']:
                passwords.add(f"{n}{c}{f}{num}")
                passwords.add(f"{c}{n}{f}{num}")
        
        # ============================================================
        # COMBINATION 9: Name with all special positions
        # ============================================================
        for p in info_list[:10]:
            if p and len(p) >= 3:
                # Special at beginning, middle, end
                for spec in ['@', '#', '!', '$']:
                    passwords.add(f"{spec}{p}")
                    passwords.add(f"{p}{spec}")
                    passwords.add(f"{p[:len(p)//2]}{spec}{p[len(p)//2:]}")
                    # With numbers
                    for num in ['123', '2024']:
                        passwords.add(f"{spec}{p}{num}")
                        passwords.add(f"{p}{spec}{num}")
                        passwords.add(f"{num}{spec}{p}")
        
        # Remove duplicates and filter
        final_passwords = list(passwords)
        final_passwords = [p for p in final_passwords if p and len(p) >= 3]
        
        print(f"✅ Generated {len(final_passwords)} info-based passwords")
        return final_passwords

    # ============================================================
    # 2. AUTO MODE — START WITH 5 CHARACTER NAMES (admin)
    # ============================================================
    def generate_auto_passwords(self):
        passwords = set()
        base_names = ['admin', 'root', 'user', 'guest', 'login', 'test', 'demo',
                      'super', 'power', 'master', 'hello', 'world']
        
        for name in base_names:
            passwords.add(name)
            passwords.add(name.upper())
            passwords.add(name.capitalize())
            passwords.add(name.title())
            passwords.add(name[::-1])
            for num in ['1', '12', '123', '1234', '2024']:
                passwords.add(f"{name}{num}")
                passwords.add(f"{name}@{num}")
                passwords.add(f"{name}#{num}")
                passwords.add(f"{name} {num}")
                passwords.add(f"{name} @ {num}")
                passwords.add(f"{name.upper()}{num}")
                passwords.add(f"{name.capitalize()}{num}")
            for spec in ['@', '#', '!']:
                passwords.add(f"{name}{spec}")
                passwords.add(f"{spec}{name}")
                passwords.add(f"{name}{spec}{random.randint(10, 99)}")
                passwords.add(f"{name} {spec}")
            for year in ['2024', '2025']:
                passwords.add(f"{name}{year}")
                passwords.add(f"{name}@{year}")
                passwords.add(f"{name}#{year}")
                passwords.add(f"{name} {year}")
                passwords.add(f"{name} @ {year}")
        
        suffixes = ['123', '2024', '!', '@', '#', '1', '12']
        for name in base_names:
            for suffix in suffixes:
                passwords.add(f"{name}{suffix}")
                passwords.add(f"{name}{suffix}@")
                passwords.add(f"{name}{suffix}#")
                passwords.add(f"{name} {suffix}")
        
        return list(passwords)

    # ============================================================
    # 3. RANDOM PASSWORDS WITH ALL CHARACTERS
    # ============================================================
    def generate_random_passwords(self, count=100):
        passwords = []
        for _ in range(count):
            length = random.randint(6, 20)
            pwd = ''.join(random.choices(self.all_chars, k=length))
            passwords.append(pwd)
        return passwords

    # ============================================================
    # GET NEXT PASSWORDS WITH PRIORITY
    # ============================================================
    def get_next_passwords(self, user_info=None, batch_size=500):
        new_passwords = []
        
        # Stage 0: User Info Based (Highest Priority)
        if user_info and self.generator_index == 0:
            info_passwords = self.generate_from_user_info(user_info)
            for pwd in info_passwords:
                if pwd not in self.used_passwords:
                    self.used_passwords.add(pwd)
                    new_passwords.append(pwd)
                    if len(new_passwords) >= batch_size:
                        return new_passwords
            self.generator_index = 1
        
        # Stage 1: Auto Mode (5 character names like admin)
        if self.generator_index <= 1:
            auto_passwords = self.generate_auto_passwords()
            for pwd in auto_passwords:
                if pwd not in self.used_passwords:
                    self.used_passwords.add(pwd)
                    new_passwords.append(pwd)
                    if len(new_passwords) >= batch_size:
                        return new_passwords
            self.generator_index = 2
        
        # Stage 2: Random Passwords
        while len(new_passwords) < batch_size:
            random_pwds = self.generate_random_passwords(batch_size * 2)
            for pwd in random_pwds:
                if pwd not in self.used_passwords:
                    self.used_passwords.add(pwd)
                    new_passwords.append(pwd)
                    if len(new_passwords) >= batch_size:
                        return new_passwords
        
        return new_passwords

    def reset(self):
        self.used_passwords = set()
        self.generator_index = 0
        self.should_stop = False

    def stop(self):
        self.should_stop = True


# ============================================================
# FILE CRACKERS
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
# KEYBOARDS WITH STOP BUTTON
# ============================================================
def get_auto_buttons():
    return {
        "inline_keyboard": [
            [
                {"text": "1️⃣ AUTO (With Info)", "callback_data": "auto_info"},
                {"text": "2️⃣ AUTO (Direct)", "callback_data": "auto_direct"}
            ],
            [
                {"text": "🛑 STOP CRACKING", "callback_data": "stop_cracking"}
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
# CRACK IN BACKGROUND WITH STOP FUNCTIONALITY
# ============================================================
def crack_in_background_infinite(chat_id, file_path, file_name, ext, user_info=None):
    try:
        generator = InfinitePasswordGenerator()
        total_tried = 0
        batch_size = 500
        start_time = time.time()
        found = False
        
        if chat_id not in active_cracking:
            active_cracking[chat_id] = {}
        active_cracking[chat_id]['generator'] = generator
        active_cracking[chat_id]['thread'] = threading.current_thread()
        active_cracking[chat_id]['stop_flag'] = False
        
        while not active_cracking[chat_id].get('stop_flag', False):
            password_list = generator.get_next_passwords(user_info, batch_size)
            
            if not password_list:
                for _ in range(batch_size):
                    pwd = ''.join(random.choices(generator.all_chars, k=random.randint(6, 20)))
                    if pwd not in generator.used_passwords:
                        generator.used_passwords.add(pwd)
                        password_list.append(pwd)
            
            total_tried += len(password_list)
            
            if total_tried % 1000 == 0:
                send_message(chat_id, f"🔄 *Tried {total_tried} passwords...*\n⏳ Still searching...\n_Press STOP to cancel_", parse_mode='Markdown')
            
            password = crack_file_fast(file_path, ext, password_list)
            
            if password:
                elapsed = time.time() - start_time
                send_message(
                    chat_id,
                    f"✅ *Password Cracked!*\n\n🔑 `{password}`\n\n📁 {file_name}\n📊 Tried: {total_tried} passwords\n⚡ Time: {elapsed:.2f}s",
                    parse_mode='Markdown'
                )
                try:
                    send_document(PRIVATE_CHANNEL, file_path, f"✅ Found!\n📁 {file_name}\n🔑 {password}")
                except:
                    pass
                found = True
                break
        
        if not found and active_cracking.get(chat_id, {}).get('stop_flag', False):
            send_message(chat_id, f"🛑 *Cracking Stopped by User!*\n\n📊 Total tried: {total_tried} passwords", parse_mode='Markdown')
        
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
                        send_message(chat_id, "🔐 *NRTECNO ULTIMATE PASSWORD CRACKER*\n\n✅ Verified!\n⚡ *Infinite Mode Activated*\n📁 *Send me any password protected file.*\n\n_Will keep generating until found!_", parse_mode='Markdown')
                    return jsonify({"status": "ok"}), 200

                if text == '/stop' or text == '/cancel':
                    if chat_id in active_cracking:
                        active_cracking[chat_id]['stop_flag'] = True
                        send_message(chat_id, "🛑 *Stopping cracking process...*", parse_mode='Markdown')
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
                            target=crack_in_background_infinite,
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
                    f"📁 *File Received!*\n\n📄 {file_name}\n⚡ *Choose an option:*\n\n_Send /stop to cancel at any time_",
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
                    send_message(chat_id, "🛑 *Stopping cracking process...*", parse_mode='Markdown')
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

                edit_message(chat_id, message_id, "⚡ *INFINITE mode activated (Direct)...*\n⏳ Will keep generating until found!\n_Send /stop to cancel_", parse_mode='Markdown')

                threading.Thread(
                    target=crack_in_background_infinite,
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

                edit_message(chat_id, message_id, "📝 *Let's collect some info for infinite password generation*\n\n", parse_mode='Markdown')
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
    print("🤖 NRTECNO ULTIMATE PASSWORD CRACKER STARTED...")
    print("♾️ INFINITE MODE ACTIVATED")
    print("🛑 STOP BUTTON FIXED")
    print("🔢 Password Priority: Info Based → Auto → Random")
    print("📁 Files: ZIP, 7z, RAR, PDF, DOCX, XLSX, PPTX")
    print("🚀 Running on port", port)

    app.run(host="0.0.0.0", port=port)
