# 🤖 aiogram-cryptobot

A Telegram bot for cryptocurrency tracking and management, built with Python and the **aiogram** framework.

---

## 📂 Project Structure

Based on the repository architecture:

*   `main.py` — The main entry point to initialize and run the Telegram bot.
*   `handlers/` — Modules containing command, text, and callback query handlers.
*   `forms/` — Finite State Machine (FSM) states and forms for user input flows.
*   `bases/` — Database modules and models (user data, settings, logs).
*   `requirements.txt` — List of project dependencies and external libraries.
*   `.gitignore` — Specifies untracked files that Git should ignore (e.g., tokens, local DBs).

---

## 🛠 Tech Stack

*   **Language:** Python 3.10+
*   **Framework:** [aiogram](https://github.com/aiogram)
*   **Database:** SQLite (implemented in the `bases` directory)

---

## 💻 Installation & Local Setup

Follow these steps to set up and run the project locally:

### 1. Clone the repository
```bash
git clone [https://github.com](https://github.com/manctel222/aiogram-cryptobot)
cd aiogram-cryptobot
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# For Windows (Command Prompt / PowerShell):
venv\Scripts\activate

# For Linux / macOS:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables Setup
Create a `.env` file in the root directory (where `main.py` is located) and add your credentials:
```env
BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ (your token from @BotFather)
```
*Note: Never commit your `.env` file to GitHub!*

### 5. Run the bot
```bash
python main.py
```

---

## 📝 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
