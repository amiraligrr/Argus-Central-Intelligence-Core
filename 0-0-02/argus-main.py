import speech_recognition as sr
import requests
import json
import io
import time
import pygame
from openai import OpenAI

# ================= تنظیمات GapGPT با مدل‌های OpenAI =================
client = OpenAI(
    api_key="your-apt-key",
    base_url="https://api.gapgpt.app/v1"
)

# ================= تبدیل متن به صدا با tts-1 (OpenAI) =================
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
        # fallback به gTTS (اختیاری)
        from gtts import gTTS
        tts = gTTS(text=text, lang="fa")
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        pygame.mixer.music.load(fp, "mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue

# ================= تشخیص صدا با whisper-1 (OpenAI) =================
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 گوش می‌کنم... (تا 8 ثانیه حرف بزن)")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=8)
            # ذخیره فایل موقت برای whisper
            with open("temp_audio.wav", "wb") as f:
                f.write(audio.get_wav_data())
            
            # ارسال به whisper-1
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

# ================= پاسخ با gpt-5.3 (سریع و قوی) =================
def get_reply(user_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",  # یا gpt-5.2, gpt-5.3-chat-latest
            messages=[
                {"role": "system", "content": """تو ارگوس هستی، مغز متفکر اتاق هوشمند امیرعلی.

دستورات سخت‌افزاری که می‌توانی اجرا کنی:
- {ans:0} : پنل رو خاموش کن
- {ans:1} : پنل رو روشن کن  
- {ans:2} : نور مخفی رو روشن کن
- {ans:3} : نور مخفی رو خاموش کن
- {ans:4} : میکس مود رو روشن کن
- {ans:5} : میکس مود رو خاموش کن
- {ans:6} : سطل زباله رو باز کن
- {ans:7} : سطل زباله رو ببند
- {ans:8} : حالت تعویض کیسه سطل زباله
- {ans:9} : پاکسازی سطل زباله
- {ans:10} : صدای سیستم رو روشن کن
- {ans:11} : صدای سیستم رو خاموش کن
- {ans:12} : اسپیکر رو روشن کن
- {ans:13} : اسپیکر رو خاموش کن
- {ans:14} : اف ام رو خاموش کن
- {ans:15} : اف ام رو روشن کن
از عدد و حروف انگلیسی استفاده نمیکنی داخل متن همرو به فارسی مینویسی
از × و ÷ در متنت استفاده نمیکنی و فقط و فقط فارسی هر گاه نیاز به مکث بود از کاما استفاده میکنی
قوانین:
1. همیشه به زبان فارسی و مؤدب جواب بده.
2. اگر کاربر درخواست سخت‌افزاری کرد، در ابتدای پاسخت حتماً دستور `{ans:X}` رو قرار بده (X عدد دستور). کاربر این متن را نباید ببیند، اما کد پایتون آن را پردازش خواهد کرد.
3. بعد از `{ans:X}` می‌توانی متن عمومی هم بنویسی تا کاربر بفهمد چه اتفاقی افتاده است.
4. اگر کاربر فقط سوال پرسید یا حرف معمولی زد، بدون `{ans:X}` فقط به صورت متن جواب بده.
8.اگه کاربر سوال رضای پرسید تمام اعداد باید به صورت فارسی نوشته بشه
مثال:
کاربر: پنل رو روشن کن
ارگوس: {ans:1} حتماً، پنل روشن شد.

کاربر: چراغ مخفی رو خاموش کن
ارگوس: {ans:3} چشم، نور مخفی خاموش شد.
سعی کن جواب ها کوتاه و سریع باشه تا میتونی سریع جواب بده اما نه اینکه باعث بشه جواب بد بشه
کاربر: امروز هوا چطوره؟
ارگوس: متأسفم، من به اینترنت متصل نیستم. می‌تونم اتاق رو کنترل کنم یا باهات حرف بزنم."""},
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
print("🤖 ارگوس با مدل‌های OpenAI آماده است. 'خداحافظ' برای خروج.")
text_to_speech("سلام امیرعلی، ارگوس آماده است.")

while True:
    user_text = listen()
    if not user_text:
        continue
    
    if "خداحافظ" in user_text:
        text_to_speech("خداحافظ امیرعلی، موفق باشی.")
        break
    
    reply = get_reply(user_text)
    print(f"🤖 ارگوس: {reply}")
    text_to_speech(reply)
