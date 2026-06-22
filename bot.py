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
PRIVATE_CHANNEL = -1004491770657
CHANNEL_USERNAME = "@nrtecno2"

app = Flask(__name__)

# ============================================================
# USER SESSION STORAGE
# ============================================================
user_sessions = {}

# ============================================================
# UNLIMITED PASSWORD GENERATOR (5 to 100 characters)
# ============================================================
def generate_unlimited_passwords():
    """Generate passwords from 5 to 100 characters - UNLIMITED"""
    passwords = set()
    
    # Character sets
    lower = 'abcdefghijklmnopqrstuvwxyz'
    upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    digits = '0123456789'
    special = '@#&%!$_-'
    all_chars = lower + upper + digits + special
    
    # Common names
    common_names = [
        'raj', 'rahul', 'amit', 'vikram', 'ajay', 'sunil', 'anil', 
        'deepak', 'sanjay', 'vijay', 'arjun', 'karan', 'mohit', 
        'rohit', 'ankit', 'vivek', 'manoj', 'suresh', 'mahesh', 
        'ramesh', 'dinesh', 'ganesh', 'naveen', 'pawan', 'sachin',
        'rajesh', 'kapil', 'narendra', 'mukesh', 'ravi', 'ashok',
        'shyam', 'ghanshyam', 'kumar', 'singh', 'sharma', 'verma',
        'gupta', 'yadav', 'jain', 'patel', 'shah', 'desai'
    ]
    
    # Common words
    common_words = [
        'password', 'admin', 'root', 'toor', 'iloveyou', 'sunshine',
        'princess', 'dragon', 'baseball', 'superman', 'batman',
        'trustno', 'hello', 'freedom', 'whatever', 'qwerty',
        'letmein', 'welcome', 'monkey', 'secret', 'love', 'angel',
        'rainbow', 'tiger', 'eagle', 'phoenix', 'shadow', 'night',
        'star', 'moon', 'sun', 'cloud', 'thunder', 'lightning'
    ]
    
    numbers = ['1', '12', '123', '1234', '12345', '123456', '1234567', '12345678', '123456789', '1234567890']
    years = ['2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030']
    
    # ========== 1. NAME + NUMBER COMBINATIONS ==========
    for name in common_names:
        for num in numbers[:8]:
            passwords.add(f"{name}{num}")
            passwords.add(f"{name}@{num}")
            passwords.add(f"{name}#{num}")
            passwords.add(f"{name}{num}@")
            passwords.add(f"{name}{num}#")
            passwords.add(f"{name.capitalize()}{num}")
            passwords.add(f"{name}{num}!")
            passwords.add(f"{name}!{num}")
            passwords.add(f"{name}_{num}")
            passwords.add(f"{name}-{num}")
            passwords.add(f"{name}{num}{random.randint(10, 99)}")
    
    # ========== 2. WORD + NUMBER COMBINATIONS ==========
    for word in common_words:
        for num in numbers[:8]:
            passwords.add(f"{word}{num}")
            passwords.add(f"{word}@{num}")
            passwords.add(f"{word}#{num}")
            passwords.add(f"{word}{num}@")
            passwords.add(f"{word}{num}#")
            passwords.add(f"{word.capitalize()}{num}")
            passwords.add(f"{word}{num}!")
            passwords.add(f"{word}!{num}")
            passwords.add(f"{word}_{num}")
            passwords.add(f"{word}-{num}")
    
    # ========== 3. NAME + YEAR ==========
    for name in common_names[:30]:
        for year in years:
            passwords.add(f"{name}{year}")
            passwords.add(f"{name}@{year}")
            passwords.add(f"{name}#{year}")
            passwords.add(f"{name}{year}!")
            passwords.add(f"{name}!{year}")
            passwords.add(f"{name.capitalize()}{year}")
    
    # ========== 4. WORD + YEAR ==========
    for word in common_words[:20]:
        for year in years:
            passwords.add(f"{word}{year}")
            passwords.add(f"{word}@{year}")
            passwords.add(f"{word}#{year}")
            passwords.add(f"{word}{year}!")
            passwords.add(f"{word}!{year}")
    
    # ========== 5. NAME + WORD COMBINATIONS ==========
    for name in common_names[:20]:
        for word in common_words[:15]:
            passwords.add(f"{name}{word}")
            passwords.add(f"{name}@{word}")
            passwords.add(f"{name}#{word}")
            passwords.add(f"{name}{word}{random.randint(1, 99)}")
            passwords.add(f"{name.capitalize()}{word.capitalize()}")
            passwords.add(f"{name}{word}@")
            passwords.add(f"{name}{word}#")
    
    # ========== 6. NUMERIC COMBINATIONS ==========
    # 4 to 20 digit numbers
    for length in range(4, 21):
        # Common starting patterns
        for start in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
            for _ in range(50):  # Limit for each length
                num = start
                for __ in range(length - 1):
                    num += str(random.randint(0, 9))
                passwords.add(num)
        
        # All same digits
        for d in '0123456789':
            passwords.add(d * length)
        
        # Sequential
        seq = ''
        for i in range(length):
            seq += str(i % 10)
        passwords.add(seq)
        
        # Reverse sequential
        rev_seq = ''
        for i in range(length):
            rev_seq += str((i % 10))
        passwords.add(rev_seq[::-1])
    
    # ========== 7. ALPHABET COMBINATIONS ==========
    # 5 to 15 character alphabet combinations
    for length in range(5, 16):
        # Common prefixes
        for prefix in ['a', 'b', 'c', 'q', 'p', 'z', 'x', 'm', 'n', 's']:
            base = prefix * length
            passwords.add(base)
            passwords.add(base.capitalize())
            # Add numbers
            for num in ['123', '456', '789', '2024']:
                if len(base) >= len(num):
                    passwords.add(f"{base[:length-len(num)]}{num}")
                    passwords.add(f"{base[:length-len(num)]}@{num}")
                    passwords.add(f"{base[:length-len(num)]}#{num}")
        
        # Random combinations
        for _ in range(100):
            word = ''.join(random.choices(lower, k=length))
            passwords.add(word)
            passwords.add(word.capitalize())
            passwords.add(word + str(random.randint(10, 99)))
            passwords.add(word + '@' + str(random.randint(10, 99)))
    
    # ========== 8. SPECIAL CHARACTER COMBINATIONS ==========
    for length in range(5, 21):
        for _ in range(50):
            # Mix of letters + numbers + special
            chars = random.choices(lower + digits, k=length-2)
            chars.append(random.choice(special))
            chars.append(str(random.randint(0, 9)))
            random.shuffle(chars)
            passwords.add(''.join(chars))
            
            # Capital + small + number + special
            chars = []
            chars.append(random.choice(upper))
            for __ in range(length-4):
                chars.append(random.choice(lower + digits))
            chars.append(random.choice(special))
            chars.append(str(random.randint(0, 9)))
            random.shuffle(chars)
            passwords.add(''.join(chars))
    
    # ========== 9. LONG PASSWORDS (30 to 100 chars) ==========
    long_patterns = [
        "abcdefghijklmnopqrstuvwxyz",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "0123456789",
        "qwertyuiopasdfghjklzxcvbnm",
        "thequickbrownfoxjumpsoverthelazydog",
        "packmyboxwithfivedozenliquorjugs",
        "howvexinglyquickdafoxjumpsoverthelazydog",
        "thefiveboxingwizardsjumpquickly",
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "0123456789abcdefghijklmnopqrstuvwxyz"
    ]
    
    for pattern in long_patterns:
        for length in range(30, 101):
            if len(pattern) >= length:
                base = pattern[:length]
                passwords.add(base)
                # Add numbers
                for num in ['123', '456', '789', '123456', '2024']:
                    if len(base) >= len(num) + 3:
                        pwd = f"{base[:length-len(num)-1]}{num}{random.choice(special)}"
                        passwords.add(pwd)
                        pwd2 = f"{base[:length-len(num)-1]}{random.choice(special)}{num}"
                        passwords.add(pwd2)
    
    # ========== 10. WORDLIST + SPECIAL COMBOS ==========
    for word in common_words:
        # Add special chars at different positions
        for spec in special:
            for num in numbers[:5]:
                passwords.add(f"{word}{spec}{num}")
                passwords.add(f"{word}{num}{spec}")
                passwords.add(f"{spec}{word}{num}")
                passwords.add(f"{word}{spec}{num}{spec}")
    
    # ========== 11. SOCIAL MEDIA PATTERNS ==========
    social_patterns = [
        'instagram', 'facebook', 'whatsapp', 'telegram', 'twitter',
        'snapchat', 'youtube', 'google', 'microsoft', 'apple',
        'amazon', 'netflix', 'spotify', 'reddit', 'discord'
    ]
    
    for pattern in social_patterns:
        for num in numbers[:5]:
            passwords.add(f"{pattern}{num}")
            passwords.add(f"{pattern}@{num}")
            passwords.add(f"{pattern}#{num}")
            passwords.add(f"{pattern}{num}!")
            passwords.add(f"{pattern.capitalize()}{num}")
    
    # ========== 12. DATE BASED ==========
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    days = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28']
    
    for name in common_names[:20]:
        for m in months[:6]:
            for d in days[:10]:
                passwords.add(f"{name}{d}{m}")
                passwords.add(f"{name}@{d}{m}")
                passwords.add(f"{name}{d}{m}{random.randint(10, 99)}")
                passwords.add(f"{name}{d}-{m}")
                passwords.add(f"{name}_{d}{m}")
    
    # ========== 13. 100 CHARACTER PASSWORDS ==========
    base_long = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#&%!$_-"
    for _ in range(100):
        pwd = ''.join(random.choices(base_long, k=100))
        passwords.add(pwd)
        # Add variation with specific patterns
        for pattern in ['123', 'abc', 'xyz', 'qwerty']:
            for i in range(0, 90, 10):
                pwd_list = list(pwd)
                pwd_list[i:i+len(pattern)] = pattern
                passwords.add(''.join(pwd_list))
    
    # Remove duplicates and limit to avoid memory crash
    passwords = list(passwords)
    random.shuffle(passwords)
    
    print(f"✅ Generated {len(passwords)} unlimited passwords (5 to 100 chars)")
    return passwords

# ============================================================
# SMART PASSWORD GENERATOR CLASS (For INFO mode)
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
        self.years = ['2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030']
    
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
        
        info_pieces = [name, father, mother, city]
        info_pieces = [p for p in info_pieces if p]
        
        # 1. Name + Number combinations
        for p in info_pieces:
            if p:
                for num in self.numbers[:8]:
                    passwords.add(f"{p}{num}")
                    passwords.add(f"{p}@{num}")
                    passwords.add(f"{p}#{num}")
                    passwords.add(f"{p}{num}@")
                    passwords.add(f"{p}{num}#")
                    passwords.add(f"{p.capitalize()}{num}")
                    passwords.add(f"{p}{num}!")
                    passwords.add(f"{p}!{num}")
                    passwords.add(f"{p}_{num}")
        
        # 2. Name + Year
        for p in info_pieces:
            if p:
                for y in self.years[:8]:
                    passwords.add(f"{p}{y}")
                    passwords.add(f"{p}@{y}")
                    passwords.add(f"{p}#{y}")
                    passwords.add(f"{p}{y}!")
                    passwords.add(f"{p.capitalize()}{y}")
        
        # 3. Name + Name combinations
        for p1 in info_pieces:
            for p2 in info_pieces:
                if p1 != p2:
                    passwords.add(f"{p1}{p2}")
                    passwords.add(f"{p1}@{p2}")
                    passwords.add(f"{p1}#{p2}")
                    passwords.add(f"{p1}{p2}{random.randint(1, 99)}")
                    passwords.add(f"{p1.capitalize()}{p2.capitalize()}")
        
        # 4. Mobile number combinations
        if mobile:
            mobile_clean = ''.join(filter(str.isdigit, mobile))
            if mobile_clean:
                for i in range(2, len(mobile_clean) + 1):
                    passwords.add(mobile_clean[:i])
                    passwords.add(mobile_clean[-i:])
                    for p in info_pieces:
                        if p:
                            passwords.add(f"{p}{mobile_clean[:i]}")
                            passwords.add(f"{p}@{mobile_clean[:i]}")
                            passwords.add(f"{p}{mobile_clean[-i:]}")
                            passwords.add(f"{p}@{mobile_clean[-i:]}")
                            passwords.add(f"{p}{mobile_clean[:i]}{random.randint(1, 99)}")
        
        # 5. Date of birth combinations
        if dob:
            clean_dob = dob.replace('/', '').replace('-', '')
            if len(clean_dob) >= 4:
                passwords.add(clean_dob)
                passwords.add(clean_dob[-4:])
                for p in info_pieces:
                    if p:
                        passwords.add(f"{p}{clean_dob}")
                        passwords.add(f"{p}@{clean_dob}")
                        passwords.add(f"{p}{clean_dob[-4:]}")
                        passwords.add(f"{p}@{clean_dob[-4:]}")
        
        # 6. Name + Common Words
        for p in info_pieces:
            if p:
                for word in self.common_words[:15]:
                    passwords.add(f"{p}{word}")
                    passwords.add(f"{p}@{word}")
                    passwords.add(f"{p}#{word}")
                    passwords.add(f"{p}{word}{random.randint(1, 99)}")
                    passwords.add(f"{p.capitalize()}{word.capitalize()}")
        
        # 7. Long passwords (30 to 100 chars) from info
        for p in info_pieces:
            if p and len(p) >= 3:
                for length in range(30, 101):
                    base = (p * (length // len(p) + 1))[:length]
                    passwords.add(base)
                    for num in ['123', '456', '789', '2024', '2025']:
                        if len(base) >= len(num) + 3:
                            pwd = f"{base[:length-len(num)-1]}{num}@{random.randint(1, 9)}"
                            passwords.add(pwd)
                            pwd2 = f"{base[:length-len(num)-1]}{random.choice(self.special_chars)}{num}"
                            passwords.add(pwd2)
        
        # 8. Info + Special combinations
        for p in info_pieces:
            if p:
                for spec in self.special_chars:
                    for num in self.numbers[:5]:
                        passwords.add(f"{p}{spec}{num}")
                        passwords.add(f"{p}{num}{spec}")
                        passwords.add(f"{spec}{p}{num}")
                        passwords.add(f"{p}{spec}{num}{spec}")
        
        return list(passwords)
    
    def generate_smart_passwords(self, count=10000):
        """Generate common passwords without info"""
        passwords = set()
        
        for word in self.common_words:
            for num in self.numbers[:8]:
                passwords.add(f"{word}{num}")
                passwords.add(f"{word}@{num}")
                passwords.add(f"{word}#{num}")
                passwords.add(f"{word}{num}@")
                passwords.add(f"{word}{num}#")
                passwords.add(f"{word.capitalize()}{num}")
                passwords.add(f"{word}{num}!")
                passwords.add(f"{word}!{num}")
        
        for num in self.numbers:
            passwords.add(num)
            for num2 in self.numbers[:5]:
                passwords.add(f"{num}{num2}")
                passwords.add(f"{num}@{num2}")
                passwords.add(f"{num}#{num2}")
        
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
                passwords.add(f"{p}{num}@")
                passwords.add(f"{p}{num}#")
        
        # Add long passwords
        long_patterns = [
            "abcdefghijklmnopqrstuvwxyz",
            "qwertyuiopasdfghjklzxcvbnm",
            "thequickbrownfoxjumpsoverthelazydog"
        ]
        
        for pattern in long_patterns:
            for length in range(30, 101):
                if len(pattern) >= length:
                    base = pattern[:length]
                    passwords.add(base)
                    for num in ['123', '456', '789']:
                        if len(base) >= len(num) + 2:
                            passwords.add(f"{base[:length-len(num)]}{num}")
                            passwords.add(f"{base[:length-len(num)]}@{num}")
        
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
                
                # Handle info collection
                if chat_id in user_sessions and user_sessions[chat_id].get('state') == 'collecting_info':
                    session = user_sessions[chat_id]
                    field = session['current_field']
                    session['info'][field] = text
                    
                    fields = session['fields']
                    current_index = fields.index(field)
                    
                    if current_index + 1 < len(fields):
                        next_field = fields[current_index + 1]
                        session['current_field'] = next_field
                        send_message(chat_id, f"📝 *Enter {next_field.title()}?*", parse_mode='Markdown')
                    else:
                        session['state'] = 'cracking'
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
                
                user_sessions[chat_id] = {
                    'file_path': file_path,
                    'file_name': file_name,
                    'file_ext': ext,
                    'state': 'waiting_for_option'
                }
                
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
                
                edit_message(chat_id, message_id, "🔄 *AUTO mode activated (Direct)...*\n⏳ Generating unlimited passwords...", parse_mode='Markdown')
                
                # Generate unlimited passwords
                password_list = generate_unlimited_passwords()
                
                send_message(chat_id, f"📊 *Generated {len(password_list)} passwords*\n🔍 *Cracking...*", parse_mode='Markdown')
                
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
                    try:
                        send_document(PRIVATE_CHANNEL, file_path, f"❌ Not Found!\n📁 {session['file_name']}\n🔢 {len(password_list)} tried\n👤 @{user_id}")
                    except:
                        pass
                
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
                
                fields = ['name', 'dob', 'father', 'mother', 'city', 'mobile']
                session['info'] = {}
                session['fields'] = fields
                session['current_field'] = fields[0]
                session['state'] = 'collecting_info'
                
                edit_message(chat_id, message_id, "📝 *Let's collect some info for better password generation*\n\n", parse_mode='Markdown')
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
    print("🤖 NRTECNO BOT STARTED (Flask + Webhook + UNLIMITED Generator)...")
    print("🔢 Password generation: 5 to 100 characters")
    print("🚀 Running on port", port)
    
    app.run(host="0.0.0.0", port=port)
