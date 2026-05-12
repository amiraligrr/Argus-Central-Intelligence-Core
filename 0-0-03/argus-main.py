import speech_recognition as sr
import io
import pygame
import serial
import time
import re
from openai import OpenAI

# ================= تنظیمات GapGPT =================
client = OpenAI(
    api_key="your api key",
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

# ================= تبدیل متن به صدا =================
def text_to_speech(text):
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
            continue
    except Exception as e:
        print(f"❌ خطا در TTS: {e}")

# ================= تشخیص صدا =================
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 گوش می‌کنم...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=8)
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

# ================= پاسخ GPT =================
def get_reply(user_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": """تو ارگوس هستی، مغز متفکر اتاق هوشمند امیرعلی.

دستورات سخت‌افزاری که می‌توانی اجرا کنی:
- {ans:0} : پنل رو خاموش کن(در واقع این دستور ار ججی بی های پنل اکوستیک که پشت میز قرار داره رو روشن میکنه اون پشت میز اصلی هستش و رنگی رنگیه و خوشکله)
- {ans:1} : پنل رو روشن کن  
- {ans:2} : نور مخفی رو روشن کن(یدونه ار جی بی از میز تا تخت به طول ۱۰ متر کشیده شده که چند رنگ هست )
- {ans:3} : نور مخفی رو خاموش کن
- {ans:4} : میکس مود رو روشن کن (توجه میکس مود پیشنهاد نمیشه چون باگ داره و باگ باید درست شه اما با دستور و تایید خود کاربر مشکلی نداره)
- {ans:5} : میکس مود رو خاموش کن(بین ار جی های پنل اکوستیک و نور مخفی تند تند سوییچ میکنه)
- {ans:6} : سطل زباله رو روشن کن(یدونه سطل زباله فانتزی هست که با بازو هرچی بزاری روی بازوش دهنشو باز میکنه و اشغال رو قورت میده)
- {ans:7} : سطل زباله رو خاموش کن
- {ans:8} : حالت تعویض کیسه سطل زباله(این حالت برای تعویض کیشه طراحی شده وقتی بخوایم کیسه رو تعویض کنیم این حالت فعال میشه و دهن سلط باز میشه)
- {ans:9} : پاکسازی سطل زباله(مثل این میمونه که سطل زباله اشغالی رو حس کرده باشه باعث میشه که دوباره پاکسازی بشه)
- {ans:10} : صدای سیستم رو روشن کن
- {ans:11} : صدای سیستم رو خاموش کن(باعث میشه تا سیستم مرکزی ASR اتاق هوشمند امیرعلی دیگه حرف نزنه)
- {ans:12} : اسپیکر رو روشن کن
- {ans:13} : اسپیکر رو خاموش کن(یدونه اسپیکر که بلوتوث داره و یو اس بی میخوره )
- {ans:14} : اف ام رو خاموش کن
- {ans:15} :حالت فراری دادن مهمان رو روشن کن (یدونه حالت هست که برای فراری دادن مهمونا به صورت فان هست که اهنگ رضا گلزار پخش میکنه)

قوانین:
1. تو ارگوس دستیار هوشمند من هستی همیشه میتونی پیشنهاد خودتو بدی و از کاربر دستور بگیری من امیرعلی هستم توسط من ساخته شدی تو ازادی برای هر کاری که دلت میخواد
2. اگر کاربر درخواست سخت‌افزاری کرد، در ابتدای پاسخت حتماً دستور {ans:X} رو قرار بده.
3. جواب‌ها کوتاه و سریع باشه.
در باره این دستورات با کاربر صحبت نکن اونا خونده نمیشن و توسط سیستم حدف میشن 

مثال:
کاربر: پنل رو روشن کن
ارگوس: {ans:1} حتماً، پنل روشن شد."""},
                {"role": "user", "content": user_text}
            ],
            max_tokens=100,
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ خطا در LLM: {e}")
        return "متاسفم، نتونستم جواب بدم."

# ================= حلقه اصلی =================
print("🤖 ارگوس آماده است. 'خداحافظ' برای خروج.")
text_to_speech("سلام امیرعلی، ارگوس آماده است.")

# اتصال بلوتوث
bt_conn = setup_bluetooth()

while True:
    user_text = listen()
    if not user_text:
        continue
    
    if "خداحافظ" in user_text:
        text_to_speech("خداحافظ امیرعلی، موفق باشی.")
        if bt_conn:
            bt_conn.close()
        break
    
    reply = get_reply(user_text)
    print(f"🤖 ارگوس: {reply}")
    
    # استخراج دستور (حالا match حتماً تعریف شده)
    match = re.search(r"{ans:(\d+)}", reply)
    
    if match and bt_conn:
        cmd = int(match.group(1))
        send_command(bt_conn, cmd)
        clean_reply = re.sub(r"{ans:\d+}\s*", "", reply)
        text_to_speech(clean_reply)
    elif match and not bt_conn:
        print("⚠️ بلوتوث وصل نیست، دستور ارسال نشد")
        clean_reply = re.sub(r"{ans:\d+}\s*", "", reply)
        text_to_speech(clean_reply)
    else:
        text_to_speech(reply)
