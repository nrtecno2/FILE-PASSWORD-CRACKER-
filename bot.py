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
from itertools import product

TOKEN = os.environ.get("BOT_TOKEN")
RENDER_URL = os.environ.get("RENDER_URL", "https://your-bot.onrender.com")
PRIVATE_CHANNEL = -1004479815753
CHANNEL_USERNAME = "@nrtecno2"

app = Flask(__name__)
user_sessions = {}
active_cracking = {}


# ============================================================
# SEQUENTIAL PASSWORD GENERATOR — 5 TO 100 CHARS
# ============================================================
class SequentialPasswordGenerator:
    def __init__(self):
        # Character sets for sequential generation
        self.lowercase = 'abcdefghijklmnopqrstuvwxyz'
        self.uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.digits = '0123456789'
        self.symbols = '!@#$%^&*()_+-='
        self.all_chars = self.lowercase + self.uppercase + self.digits + self.symbols
        
        # Smart passwords for initial quick hits
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
        self.current_length = 5
        self.generator_mode = 0
        self.char_index = 0
        self.should_stop = False

    # ============================================================
    # 1. USER INFO BASED — FIRST PRIORITY
    # ============================================================
    def generate_from_user_info(self, user_info):
        passwords = set()
        name = user_info.get('name', '').strip()
        dob = user_info.get('dob', '').strip()
        father = user_info.get('father', '').strip()
        mother = user_info.get('mother', '').strip()
        city = user_info.get('city', '').strip()
        mobile = user_info.get('mobile', '').strip()
        
        info_pieces = []
        if name:
            info_pieces.extend([name, name.upper(), name.lower(), name.capitalize()])
        if dob:
            dob_clean = dob.replace('/', '').replace('-', '').strip()
            info_pieces.extend([dob_clean, dob_clean[-4:], dob_clean[-6:]])
        if father:
            info_pieces.extend([father, father.upper(), father.lower(), father.capitalize()])
        if mother:
            info_pieces.extend([mother, mother.upper(), mother.lower(), mother.capitalize()])
        if city:
            info_pieces.extend([city, city.upper(), city.lower(), city.capitalize()])
        if mobile:
            mobile_clean = ''.join(filter(str.isdigit, mobile))
            if mobile_clean:
                info_pieces.extend([mobile_clean, mobile_clean[-4:], mobile_clean[-6:]])
        
        # Single pieces
        for p in info_pieces:
            if p and len(p) >= 4:
                passwords.add(p)
                passwords.add(p[::-1])
                for num in ['123', '2024']:
                    passwords.add(f"{p}{num}")
                    passwords.add(f"{p}@{num}")
                    passwords.add(f"{p}#{num}")
                    passwords.add(f"{p}{num}@")
        
        # Two pieces
        for i in range(len(info_pieces)):
            for j in range(len(info_pieces)):
                if i != j and info_pieces[i] and info_pieces[j]:
                    p1 = info_pieces[i]
                    p2 = info_pieces[j]
                    passwords.add(f"{p1}{p2}")
                    passwords.add(f"{p1}@{p2}")
                    passwords.add(f"{p1}#{p2}")
                    passwords.add(f"{p2}{p1}")
                    passwords.add(f"{p1}{p2}{random.randint(10, 99)}")
        
        # Three pieces
        for i in range(min(5, len(info_pieces))):
            for j in range(min(5, len(info_pieces))):
                for k in range(min(5, len(info_pieces))):
                    if i != j and j != k and i != k:
                        p1 = info_pieces[i]
                        p2 = info_pieces[j]
                        p3 = info_pieces[k]
                        if p1 and p2 and p3:
                            passwords.add(f"{p1}{p2}{p3}")
                            passwords.add(f"{p1}@{p2}{p3}")
                            passwords.add(f"{p1}{p2}@{p3}")
        
        return list(passwords)

    # ============================================================
    # 2. SMART PASSWORDS (Names, Common Words)
    # ============================================================
    def generate_smart_passwords(self):
        passwords = set()
        
        # Names + Numbers
        for name in self.names[:20]:
            for num in ['123', '2024', '1', '12']:
                passwords.add(f"{name}{num}")
                passwords.add(f"{name}@{num}")
                passwords.add(f"{name}#{num}")
                passwords.add(f"{name}{num}@")
                passwords.add(f"{name.capitalize()}{num}")
                passwords.add(f"{name.upper()}{num}")
                passwords.add(f"{name}{num}!")
        
        # Common Words + Numbers
        for word in self.common_words[:15]:
            for num in ['123', '2024']:
                passwords.add(f"{word}{num}")
                passwords.add(f"{word}@{num}")
                passwords.add(f"{word}#{num}")
                passwords.add(f"{word}{num}@")
                passwords.add(f"{word.capitalize()}{num}")
                passwords.add(f"{word.upper()}{num}")
        
        # Name + Name
        for n1 in self.names[:10]:
            for n2 in self.names[:8]:
                if n1 != n2:
                    passwords.add(f"{n1}{n2}")
                    passwords.add(f"{n1}@{n2}")
                    passwords.add(f"{n1}{n2}{random.randint(10, 99)}")
                    passwords.add(f"{n1}{n2}@")
        
        # Common Word + Common Word
        for w1 in self.common_words[:8]:
            for w2 in self.common_words[:6]:
                if w1 != w2:
                    passwords.add(f"{w1}{w2}")
                    passwords.add(f"{w1}@{w2}")
                    passwords.add(f"{w1}{w2}{random.randint(10, 99)}")
        
        return list(passwords)

    # ============================================================
    # 3. SEQUENTIAL PASSWORDS (5 to 100 chars) - FAST
    # ============================================================
    def generate_sequential_passwords(self, length, batch_size=1000):
        """Generate sequential passwords of specific length - OPTIMIZED for speed"""
        passwords = []
        chars = self.all_chars
        total_combinations = len(chars) ** length
        
        # Start from where we left off
        start_index = self.char_index
        end_index = min(start_index + batch_size, total_combinations)
        
        # Fast generation using numeric conversion
        for idx in range(start_index, end_index):
            pwd = ''
            temp = idx
            for _ in range(length):
                pwd = chars[temp % len(chars)] + pwd
                temp //= len(chars)
            passwords.append(pwd)
            self.char_index += 1
        
        # If we've exhausted this length, move to next
        if self.char_index >= total_combinations:
            self.current_length += 1
            self.char_index = 0
        
        return passwords

    # ============================================================
    # GET NEXT PASSWORDS WITH PRIORITY
    # ============================================================
    def get_next_passwords(self, user_info=None, batch_size=1000):
        new_passwords = []
        
        # Stage 0: User Info Based (Highest Priority)
        if user_info and self.generator_mode == 0:
            info_passwords = self.generate_from_user_info(user_info)
            for pwd in info_passwords:
                if pwd not in self.used_passwords and len(pwd) >= 4:
                    self.used_passwords.add(pwd)
                    new_passwords.append(pwd)
                    if len(new_passwords) >= batch_size:
                        return new_passwords
            self.generator_mode = 1
            self.current_length = 5
        
        # Stage 1: Smart Passwords (5+ characters)
        if self.generator_mode == 1:
            smart_passwords = self.generate_smart_passwords()
            for pwd in smart_passwords:
                if pwd not in self.used_passwords and len(pwd) >= 5:
                    self.used_passwords.add(pwd)
                    new_passwords.append(pwd)
                    if len(new_passwords) >= batch_size:
                        return new_passwords
            self.generator_mode = 2
            self.current_length = 5
            self.char_index = 0
        
        # Stage 2: Sequential Passwords (5 to 100 chars)
        while len(new_passwords) < batch_size:
            if self.current_length > 100:
                break
            
            # Generate sequential passwords of current length
            seq_passwords = self.generate_sequential_passwords(
                self.current_length, 
                batch_size - len(new_passwords)
            )
            
            for pwd in seq_passwords:
                if pwd not in self.used_passwords:
                    self.used_passwords.add(pwd)
                    new_passwords.append(pwd)
        
        return new_passwords

    def reset(self):
        self.used_passwords = set()
        self.current_length = 5
        self.generator_mode = 0
        self.char_index = 0
        self.should_stop = False


# ============================================================
# FAST FILE CRACKERS (Optimized)
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
                {"text": "🛑 /stop", "callback_data": "stop_cracking"}
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
# CRACK IN BACKGROUND — SEQUENTIAL 5 TO 100 CHARS (10000/sec)
# ============================================================
def crack_in_background_sequential(chat_id, file_path, file_name, ext, user_info=None):
    try:
        generator = SequentialPasswordGenerator()
        total_tried = 0
        batch_size = 2000  # Increased for 10000/sec speed
        start_time = time.time()
        found = False
        current_length = 5
        last_progress_time = time.time()
        
        if chat_id not in active_cracking:
            active_cracking[chat_id] = {}
        active_cracking[chat_id]['generator'] = generator
        active_cracking[chat_id]['thread'] = threading.current_thread()
        active_cracking[chat_id]['stop_flag'] = False
        
        send_message(chat_id, f"⚡ *Sequential Brute-Force Started*\n\n📊 Starting from {current_length} characters\n⏳ Target: Up to 100 characters\n🚀 Speed: ~10,000 passwords/sec\n\n_Type /stop to cancel_", parse_mode='Markdown')
        
        while not active_cracking[chat_id].get('stop_flag', False):
            # Get next batch of passwords
            password_list = generator.get_next_passwords(user_info, batch_size)
            
            if not password_list:
                if generator.current_length > 100:
                    break
                continue
            
            total_tried += len(password_list)
            current_length = generator.current_length
            
            # Send progress update every 5000 passwords or every 0.5 seconds
            current_time = time.time()
            if total_tried % 5000 == 0 or (current_time - last_progress_time) > 0.5:
                elapsed = current_time - start_time
                speed = int(total_tried / elapsed) if elapsed > 0 else 0
                send_message(
                    chat_id, 
                    f"🔄 *Tried {total_tried:,} passwords...*\n"
                    f"📊 Current length: {current_length} chars\n"
                    f"🚀 Speed: {speed:,} passwords/sec\n"
                    f"⏳ Still searching...\n"
                    f"_Type /stop to cancel_", 
                    parse_mode='Markdown'
                )
                last_progress_time = current_time
            
            # Try to crack (try in chunks for speed)
            password = crack_file_fast(file_path, ext, password_list)
            
            if password:
                elapsed = time.time() - start_time
                send_message(
                    chat_id,
                    f"✅ *Password Cracked!*\n\n"
                    f"🔑 `{password}`\n\n"
                    f"📁 {file_name}\n"
                    f"📊 Tried: {total_tried:,} passwords\n"
                    f"⚡ Time: {elapsed:.2f}s\n"
                    f"🚀 Avg Speed: {int(total_tried/elapsed):,}/s\n"
                    f"🔢 Password length: {len(password)} chars",
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
                    f"📊 Total tried: {total_tried:,} passwords\n"
                    f"⏳ Last length: {current_length} chars\n\n"
                    f"_Type /start to use bot again_", 
                    parse_mode='Markdown')
            else:
                send_message(chat_id, 
                    f"❌ *Password Not Found!*\n\n"
                    f"📁 {file_name}\n"
                    f"📊 Tried: {total_tried:,} passwords\n"
                    f"🔢 Up to {current_length} characters\n"
                    f"⚡ Time: {time.time() - start_time:.2f}s\n\n"
                    f"_All combinations exhausted._", 
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
                        send_message(chat_id, "🔐 *NRTECNO ULTIMATE PASSWORD CRACKER*\n\n✅ Verified!\n⚡ *Sequential Mode: 5 → 100 chars*\n🚀 *Speed: 10,000+ passwords/sec*\n📁 *Send me any password protected file.*\n\n_Will keep generating until found!_", parse_mode='Markdown')
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
                            target=crack_in_background_sequential,
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

                edit_message(chat_id, message_id, "⚡ *Sequential mode activated (Direct)...*\n📊 5 → 100 characters\n🚀 10,000+ passwords/sec\n⏳ Will keep generating until found!\n_Type /stop to cancel_", parse_mode='Markdown')

                threading.Thread(
                    target=crack_in_background_sequential,
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

                edit_message(chat_id, message_id, "📝 *Let's collect some info for sequential password generation*\n\n", parse_mode='Markdown')
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
    print("🤖 NRTECNO SEQUENTIAL PASSWORD CRACKER STARTED...")
    print("♾️ SEQUENTIAL MODE: 5 → 100 characters")
    print("🚀 SPEED: 10,000+ passwords/sec")
    print("🛑 STOP BUTTON: /stop")
    print("📁 Files: ZIP, 7z, RAR, PDF, DOCX, XLSX, PPTX")
    print("🚀 Running on port", port)

    app.run(host="0.0.0.0", port=port)
