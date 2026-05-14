import speech_recognition as sr
import io
import pygame
import serial
import time
import re
import pyaudio
import numpy as np
import struct
import subprocess
import threading
import os
from openai import OpenAI

# ================= تنظیمات GapGPT =================
client = OpenAI(
    api_key= 'api key',
    base_url="https://api.gapgpt.app/v1"
)

# ================= تنظیمات بلوتوث =================
def setup_bluetooth():
    try:
        bt_serial = serial.Serial('/dev/rfcomm0', baudrate=9600, timeout=1)
        print("✅ اتصال به smart_room برقرار شد")
        return bt_serial
    except Exception as e:
        print(f"❌ خطا: {e}")
        print("⚠️ اول دستور sudo rfcomm connect رو بزن")
        return None

def send_command(serial_conn, command_code):
    if serial_conn is None:
        print("⚠️ اتصال بلوتوث وجود ندارد")
        return
    try:
        serial_conn.write(bytes([command_code]))
        serial_conn.flush()
        print(f"📤 دستور {command_code} ارسال شد")
    except Exception as e:
        print(f"❌ خطا در ارسال: {e}")

# ================= اجرای دستورات ترمینال =================
terminal_counter = 1

def get_real_user():
    username = os.popen('who am i | awk "{print $1}"').read().strip()
    if not username:
        username = os.environ.get('SUDO_USER', os.environ.get('USER', 'amiraligrr'))
    return username

def get_available_terminal():
    if subprocess.run('which x-terminal-emulator', shell=True, capture_output=True).returncode == 0:
        return 'x-terminal-emulator'
    
    terminals = ['gnome-terminal', 'xterm', 'konsole', 'xfce4-terminal', 'mate-terminal', 'terminator']
    for term in terminals:
        if subprocess.run(f'which {term}', shell=True, capture_output=True).returncode == 0:
            return term
    return None

def run_terminal_command(command, terminal_id=None):
    global terminal_counter
    
    if terminal_id is None:
        terminal_id = terminal_counter
        terminal_counter += 1
    
    terminal = get_available_terminal()
    
    if not terminal:
        print("⚠️ هیچ ترمینالی پیدا نشد، دستور مستقیم اجرا میشه")
        return execute_system_command(command)
    
    try:
        username = get_real_user()
        
        if 'clementine' in command:
            if '--previous' in command or '-r' in command or 'previous' in command:
                clem_cmd = "clementine -r"
            elif '--next' in command or '-f' in command or 'next' in command:
                clem_cmd = "clementine -f"
            elif '--play' in command or '-p' in command or 'play' in command:
                clem_cmd = "clementine -p"
            elif '--pause' in command or '-u' in command or 'pause' in command:
                clem_cmd = "clementine -u"
            elif '--stop' in command or '-s' in command or 'stop' in command:
                clem_cmd = "clementine -s"
            elif '--volume-up' in command:
                clem_cmd = "clementine --volume-up"
            elif '--volume-down' in command:
                clem_cmd = "clementine --volume-down"
            else:
                clem_cmd = command
        else:
            clem_cmd = command
        
        env_cmd = f'export DISPLAY=:0 && export XAUTHORITY=/home/{username}/.Xauthority'
        
        if terminal == 'gnome-terminal':
            full_command = f'gnome-terminal --title="ارگوس-{terminal_id}" -- bash -c "{env_cmd} && {clem_cmd}; echo \'\'; echo \'✅ انجام شد. برای بستن Enter بزن...\'; read"'
        elif terminal == 'x-terminal-emulator':
            full_command = f'x-terminal-emulator -T "ارگوس-{terminal_id}" -e bash -c "{env_cmd} && {clem_cmd}; echo \'\'; echo \'✅ انجام شد. برای بستن Enter بزن...\'; read"'
        elif terminal == 'xterm':
            full_command = f'xterm -T "ارگوس-{terminal_id}" -e bash -c "{env_cmd} && {clem_cmd}; echo \'\'; echo \'✅ انجام شد. برای بستن Enter بزن...\'; read"'
        else:
            full_command = f'{terminal} -e bash -c "{env_cmd} && {clem_cmd}; echo \'\'; echo \'✅ انجام شد. برای بستن Enter بزن...\'; read"'
        
        subprocess.Popen(full_command, shell=True)
        print(f"🖥️ دستور در ترمینال {terminal_id} ({terminal}) اجرا شد: {clem_cmd}")
        return True
        
    except Exception as e:
        print(f"❌ خطا در اجرای ترمینال: {e}")
        return execute_system_command(clem_cmd)

def run_terminal_commands_parallel(commands):
    threads = []
    for i, cmd in enumerate(commands):
        thread = threading.Thread(target=run_terminal_command, args=(cmd, i+1))
        thread.start()
        threads.append(thread)
        time.sleep(0.3)
    
    for thread in threads:
        thread.join()
    
    return True

def execute_system_command(command):
    try:
        username = get_real_user()
        
        if 'clementine' in command:
            full_cmd = f'sudo -u {username} DISPLAY=:0 XAUTHORITY=/home/{username}/.Xauthority {command}'
        else:
            full_cmd = command
        
        subprocess.Popen(full_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ دستور اجرا شد: {command}")
        return True
    except Exception as e:
        print(f"❌ خطا: {e}")
        return None

# ================= باز کردن سایت‌ها با Brave =================
def open_website(site_key):
    sites = {
        "digikala": "https://www.digikala.com",
        "sroosh": "https://web.splus.ir",
        "rubika": "https://web.rubika.ir",
        "deepseek": "https://www.deepseek.com",
        "github": "https://github.com"
    }
    
    if site_key in sites:
        url = sites[site_key]
        try:
            username = get_real_user()
            env_cmd = f'export DISPLAY=:0 && export XAUTHORITY=/home/{username}/.Xauthority'
            
            result = subprocess.run(f'which brave-browser', shell=True, capture_output=True)
            if result.returncode == 0:
                full_cmd = f'{env_cmd} && brave-browser "{url}"'
            else:
                full_cmd = f'{env_cmd} && brave "{url}"'
            
            run_terminal_command(full_cmd)
            return True
        except Exception as e:
            print(f"❌ خطا در باز کردن سایت: {e}")
            return False
    return False

# ================= تبدیل متن به صدا =================
def text_to_speech(text):
    if not text or text.strip() == "":
        return
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        pygame.mixer.init()
        pygame.mixer.music.load(io.BytesIO(response.content))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except Exception as e:
        print(f"❌ خطا در TTS: {e}")

# ================= تشخیص انرژی صدا =================
def get_rms_energy(data):
    try:
        samples = struct.unpack('<' + 'h' * (len(data) // 2), data)
        rms = np.sqrt(np.mean(np.square(samples)))
        return rms
    except:
        return 0

def listen_for_clap(wake_threshold):
    p = pyaudio.PyAudio()
    
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1024)
    
    print(f"💤 ارگوس در حالت خواب... آستانه بیداری: {wake_threshold}")
    print("👏 با دست زدن یا صدای بلند بیدارم کن")
    
    energy_buffer = []
    
    try:
        while True:
            data = stream.read(1024, exception_on_overflow=False)
            energy = get_rms_energy(data)
            
            bar_len = int(energy / 100)
            if bar_len > 50:
                bar_len = 50
            bar = "█" * bar_len
            print(f"\r📊 سطح صدا: {int(energy):5d} [{bar:<50}]", end="", flush=True)
            
            energy_buffer.append(energy)
            if len(energy_buffer) > 3:
                energy_buffer.pop(0)
            avg_energy = sum(energy_buffer) / len(energy_buffer)
            
            if avg_energy > wake_threshold:
                print("\n🔊 صدای بلند تشخیص داده شد! بیدار شدم!")
                stream.stop_stream()
                stream.close()
                p.terminate()
                return True
                
    except KeyboardInterrupt:
        print("\n👋 برنامه بسته شد")
        stream.stop_stream()
        stream.close()
        p.terminate()
        return False

# ================= تشخیص صدا =================
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 گوش می‌کنم...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            with open("temp_audio.wav", "wb") as f:
                f.write(audio.get_wav_data())
            
            with open("temp_audio.wav", "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    language="fa"
                )
            text = transcript.text
            print(f"👤 شما: {text}")
            return text
        except sr.WaitTimeoutError:
            print("⏳ هیچ صدایی دریافت نشد.")
            return ""
        except Exception as e:
            print(f"❌ خطا: {e}")
            return ""

# ================= پرامپت =================
system_prompt = """تو ارگوس هستی، مغز متفکر و دستیار هوشمند اتاق امیرعلی.

========================================
🌐 باز کردن سایت‌ها (با {web:name}):
========================================

سایت‌هایی که میتونی باز کنی:
- دیجیکالا -> {web:digikala}
- سروش پلاس -> {web:sroosh}
- روبیکا -> {web:rubika}
- دیپ سیک -> {web:deepseek}
- گیتهاب -> {web:github}

⚠️ کاربر ممکن است کلمات را غلط بگوید، تو باید بفهمی منظورش چیست.

مثال تشخیص هوشمند:
- "دیجی کالا"، "دیجیکالا"، "دیزیکالا" -> {web:digikala}
- "سورش"، "سروش پلاس" -> {web:sroosh}
- "روبیلا"، "روبیسا" -> {web:rubika}
- "دیپ سک"، "دیزیک" -> {web:deepseek}
- "گیت هاب"، "گیتاپ" -> {web:github}

========================================
🎵 دستورات موسیقی:
========================================

{terminal:clementine -r} - آهنگ قبلی
{terminal:clementine -f} - آهنگ بعدی
{terminal:clementine -p} - شروع پخش
{terminal:clementine -u} - توقف موقت
{terminal:clementine --volume-up} - بلندتر
{terminal:clementine --volume-down} - کم‌تر

========================================
💡 دستورات روشنایی:
========================================

{ans:1} - پنل RGB روشن
{ans:0} - پنل RGB خاموش
{ans:2} - نور مخفی روشن
{ans:3} - نور مخفی خاموش
{ans:1,2} - هر دو روشن
{ans:0,3} - هر دو خاموش
{ans:4} - میکس مود روشن
{ans:5} - میکس مود خاموش

========================================
🗑️ دستورات سطل زباله:
========================================

{ans:6} - سطل فعال
{ans:7} - سطل غیرفعال
{ans:8} - تعویض کیسه
{ans:9} - پاکسازی مجدد

========================================
🔊 سایر دستورات:
========================================

{ans:10} - صدای سیستم روشن
{ans:11} - صدای سیستم خاموش
{ans:12} - اسپیکر روشن
{ans:13} - اسپیکر خاموش
{ans:15} - حالت فراری دادن مهمان روشن
{ans:14} - حالت فراری دادن مهمان خاموش

========================================
⚠️ قوانین:
========================================

1. **تشخیص خاموش کردن سیستم:**
   - فقط اگه کاربر گفت "لپتاپ رو خاموش کن" یا "لپتاپم رو رو خاموش کن" از {SHUTDOWN} استفاده کن
   - اگه گفت "پنل رو خاموش کن" -> {ans:0}
   - اگه گفت "نور رو خاموش کن" -> {ans:3}

2. **جواب‌ها کوتاه باشه (حداکثر ۲ خط)**

3. **برای خداحافظی  {end} بفرست**

4. **برای باز کردن سایت  {web:name} بفرست**

========================================
📝 نمونه دیالوگ:
========================================

کاربر: دیجیکالا رو باز کن
ارگوس: {web:digikala}

کاربر: آهنگ قبلی
ارگوس: {terminal:clementine -r}

کاربر: پنل رو خاموش کن
ارگوس: {ans:0}

کاربر: خداحافظ
ارگوس: باشه داداش، هر وقت نیاز بود دست بزن بیدارم کن.{end}
کاربر :ارگوس 
ارگوس: جونم چکارم داری؟
"""

# ================= پاسخ GPT =================
def get_reply(user_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            max_tokens=350,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ خطا در LLM: {e}")
        return "متاسفم، نتونستم جواب بدم."

# ================= پردازش دستورات =================
def process_commands(reply):
    """پردازش دستورات مختلف از پاسخ GPT"""
    
    # خاموش کردن سیستم
    if "{SHUTDOWN}" in reply:
        text_to_speech("خدانگهدار، سیستم خاموش میشه.")
        time.sleep(1)
        os.system("shutdown now")
        return ""
    
    # باز کردن سایت‌ها
    web_matches = re.findall(r"{web:([^}]+)}", reply)
    for site in web_matches:
        open_website(site)
        reply = reply.replace(f"{{web:{site}}}", "")
    
    # پردازش دستورات ترکیبی بلوتوث
    bt_matches = re.findall(r"{ans:([\d,]+)}", reply)
    for match in bt_matches:
        commands = [int(x.strip()) for x in match.split(',')]
        for cmd in commands:
            if bt_conn:
                send_command(bt_conn, cmd)
                time.sleep(0.1)
    
    # پردازش دستورات ترمینال
    terminal_matches = re.findall(r"{terminal:([^}]+)}", reply)
    for match in terminal_matches:
        commands = [cmd.strip() for cmd in match.split(',')]
        if len(commands) > 1:
            run_terminal_commands_parallel(commands)
        else:
            run_terminal_command(commands[0])
    
    # پاک کردن تگ‌ها
    clean_reply = re.sub(r"{SHUTDOWN}", "", reply)
    clean_reply = re.sub(r"{web:[^}]+}", "", clean_reply)
    clean_reply = re.sub(r"{ans:[\d,]+}", "", clean_reply)
    clean_reply = re.sub(r"{terminal:[^}]+}", "", clean_reply)
    clean_reply = re.sub(r"{end}", "", clean_reply)
    
    return clean_reply.strip()

# ================= حلقه اصلی =================
WAKE_THRESHOLD = 1000

print("="*60)
print("🤖 ارگوس هوشمند - کنترل کامل سیستم")
print("="*60)
print(f"🔧 آستانه بیداری: {WAKE_THRESHOLD}")
print("💡 قابلیت‌ها:")
print("   • پخش آهنگ با Clementine")
print("   • کنترل پنل RGB و نور مخفی")
print("   • کنترل سطل زباله فانتزی")
print("   • باز کردن سایت‌ها (دیجیکالا، سروش، روبیکا، دیپ سیک، گیتهاب)")
print("="*60)
print("🎵 دستورات صوتی:")
print("   • 'آهنگ قبلی' - آهنگ قبلی")
print("   • 'آهنگ بعدی' - آهنگ بعدی")
print("   • 'دیجیکالا باز کن' - باز کردن دیجیکالا")
print("   • 'خداحافظ' - رفتن به حالت خواب")
print("="*60)

text_to_speech("ارگوس آماده است.")

bt_conn = setup_bluetooth()
is_asleep = True

while True:
    try:
        if is_asleep:
            if listen_for_clap(WAKE_THRESHOLD):
                is_asleep = False
                text_to_speech("بله، بفرمایید.")
                continue
        else:
            user_text = listen()
            
            if not user_text:
                print("⚠️ فرمانی دریافت نشد")
                text_to_speech("متوجه نشدم، دوباره بفرمایید.")
                continue
            
            # دستور خاموش کردن سیستم
            if user_text.strip() == "خاموش کن" or user_text.strip() == "سیستم رو خاموش کن" or "شات داون" in user_text:
                text_to_speech("آیا مطمئنی میخوای سیستم خاموش بشه؟ بگو بله یا نه")
                confirm = listen()
                if confirm and ("بله" in confirm or "اره" in confirm or "آره" in confirm):
                    text_to_speech("خدانگهدار، سیستم خاموش میشه.")
                    time.sleep(1)
                    os.system("shutdown now")
                    break
                else:
                    text_to_speech("خاموش کردن لغو شد.")
                    continue
            
            reply = get_reply(user_text)
            print(f"🤖 ارگوس: {reply}")
            
            clean_reply = process_commands(reply)
            
            if clean_reply:
                text_to_speech(clean_reply)
            
            if "{end}" in reply:
                is_asleep = True
                print("💤 ارگوس به حالت خواب رفت. برای بیدار کردن دست بزن.")
                continue
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\n👋 برنامه بسته شد")
        if bt_conn:
            bt_conn.close()
        break
    except Exception as e:
        print(f"❌ خطا: {e}")
        time.sleep(1)
