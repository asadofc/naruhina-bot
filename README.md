# 💞 Naruto & Hinata Duet Chat Bot Duo  
[![Telegram Bots](https://img.shields.io/badge/Launch%20NarutoBot-@PervyNarutoBot-2CA5E0?logo=telegram&style=for-the-badge)](https://t.me/PervyNarutoBot)  
[![Telegram Bots](https://img.shields.io/badge/Launch%20HinataBot-@HornyHinataBot-2CA5E0?logo=telegram&style=for-the-badge)](https://t.me/HornyHinataBot)

> **Together. In sync. Forever.**  
> Two bots—Naruto and Hinata—team up to reenact their sweet chat story in your group. Start, pause, resume, or stop their romantic banter at will!

---

## ✨ Key Features

- 🤖 **Dual-Bot Duo** — Runs two separate bot tokens (Naruto & Hinata)  
- 🎭 **Story Replay** — Sequentially posts predefined “Story” lines as Naruto & Hinata  
- ⏸️ **Pause/Resume** — Control flow with `/kiss` (pause) & `/rub` (resume)  
- 🛑 **Stop** — End the duet with `/cum` and clear state  
- 🔐 **Admin-Only Controls** — Only chat admins can start/stop/pause/resume  

---

## 📜 Commands Overview

| Command      | Scope        | Description                                              |
|--------------|--------------|----------------------------------------------------------|
| `/fuck`      | Group only   | Start the Naruto💬Hinata duet chat loop                  |
| `/kiss`      | Group only   | Pause the duet—Naruto & Hinata stop messaging           |
| `/rub`       | Group only   | Resume the paused duet                                  |
| `/cum`       | Group only   | Stop and clear the duet session                         |
| `/start`     | Private chat | Bot intros & invite links for Naruto or Hinata           |

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+  
- **Framework:** [python-telegram-bot v20+](https://github.com/python-telegram-bot/python-telegram-bot)  
- **Concurrency:** `asyncio` for parallel bot loops  
- **Hosting:** Any Python-friendly host (Heroku, Railway, VPS, etc.)  
- **Logging:** Python’s `logging` module for introspection  

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/asadofc/naruhina-bot.git
cd naruhina-bot

# 2. Set up Python environment
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Export both bot tokens
export BOT1_TOKEN="123456789:ABCDEF-NarutoToken"
export BOT2_TOKEN="987654321:UVWXYZ-HinataToken"

# 5. Run the duo
python naruhina-bot.py
