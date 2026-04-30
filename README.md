# Argus – Central Intelligence Core

**The brain behind ASR v3. Local LLM + memory + TTS + command execution.**

---

## 🧠 What is Argus?

Argus is the central AI system for my smart room ecosystem.  
It *thinks*, *decides*, *speaks*, and *commands* – but never touches hardware directly.

- **Can speak** using `{say:'...'}` (text‑to‑speech)  
- **Can execute hardware commands** using `{ans:...}` (sent to ASR v3)  
- **Decides whether to respond or stay silent** – no hardcoded rules  

ASR v3 (the hardware layer) only executes `{ans:...}` commands and has **no voice, no decision, no memory**.

This separation is the core of version 3.

---

## 📦 Current Status

**Argus is currently under active development.**  
I am building it *at the same time* as [ASR v3](https://github.com/amiraligrr/ASR-v3) – the hardware execution layer.

✅ Argus can generate `{say:'...'}` to speak  
✅ Argus can generate `{ans:...}` to control hardware  
✅ Decision of *what* to say and *whether* to respond is made by Argus itself (not hardcoded)  
🔄 Local LLM integration (in progress)  
🔄 Speech‑to‑text (wake word "Argus" planned)  
⬜ Long‑term memory (MongoDB)  
⬜ Computer vision (Mamad)  
⬜ Turret control (security system)

---

## 🏛️ Architecture
┌─────────────────────────────────────────┐
│ ARGUS (this repo) │
│ - Local LLM (decides what to do) │
│ - TTS {say:'...'} (speaks) │
│ - Command generator {ans:...} │
│ - Memory (planned) │
│ - Voice wake (future) │
└───────────────┬─────────────────────────┘
│
┌───────┴───────┐
▼ ▼
┌──────────────┐ ┌──────────────┐
│ Speaker │ │ ASR v3 │
│ (plays voice)│ │ (executes │
│ │ │ hardware) │
└──────────────┘ └──────────────┘

---

## 🎙️ Example Flow

1. User says: *"Argus, turn off the hidden light"*  
2. Argus (LLM) processes → decides to respond  
3. Argus sends `{say:'OK, turning off the hidden light'}` to speaker  
4. Argus sends `{ans:3}` to ASR v3  
5. ASR v3 turns off the relay  
6. Argus decides to stay silent afterward (no extra voice)

Argus can also decide to **not respond** at all – for example, if the command is invalid or if it's a simple hardware toggle with no need for voice feedback.

---

## 🔧 Command Reference

| Command | Target | Example |
|---------|--------|---------|
| `{say:'text'}` | Speaker | `{say:'Hello, room'}` |
| `{ans:code}` | ASR v3 | `{ans:3}` (code 3 = hidden light off) |
| `{rd}` | Memory (future) | Retrieve data from long‑term memory |

---

## 🔗 Related Repositories

- [ASR v3](https://github.com/amiraligrr/ASR-v3) – Hardware execution layer (lights, trash can, turrets) – **being built simultaneously**  
- [ZP-lang-Framework](https://github.com/amiraligrr/ZP-lang-Framework) – Code in your mother tongue  
- [Smart Trash Can](https://github.com/amiraligrr/smart-trash-can) – Servo‑controlled bin  
- [Manual-7Segment](https://github.com/amiraligrr/Manual-7Segment) – No‑library 7‑segment driver  

---

## 🚀 Roadmap (Argus + ASR v3)

### Phase 1 (now – in progress)
- [x] Define Argus command format (`{say:...}`, `{ans:...}`)  
- [x] Argus can speak via TTS  
- [x] Argus decides when to speak or stay silent  
- [ ] Basic local LLM integration (text in → command out)  
- [ ] Connect Argus to ASR v3 via local API  

### Phase 2 (coming soon)
- [ ] Wake word detection ("Argus")  
- [ ] Speech‑to‑text (Whisper / Vosk)  
- [ ] Short‑term conversation memory  
- [ ] Full command set for ASR v3 (lights, fan, trash can, turrets)  

### Phase 3 (future)
- [ ] Long‑term memory (MongoDB)  
- [ ] Computer vision (Mamad) for robot (Akbar)  
- [ ] Turret security system  
- [ ] Remote access (cloud server)  

---

## 💬 Why Argus?

Because a smart room shouldn't just *obey* – it should *understand*.  
And the one who understands should be central, separate, upgradeable, and **able to speak or stay silent as it decides**.

Argus is that center.  
Not tied to a single room. Not tied to a single robot.  
Just the brain. Pure logic. With a voice.

---

## 👤 Author

**Amirali** – 16 years old, Iran.  
This is the third generation of my smart room.  
ASR v1 (joystick) → ASR v2 (voice) → ASR v3 + Argus (decoupled brain and body).

---

**My Room , my Code, my Rules**

*Argus – thinking, speaking, commanding. ASR v3 – silent, fast, obedient.*
