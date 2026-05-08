import os
import requests
import json
import random
from datetime import datetime

# ─── CONFIG ──────────────────────────────────────────────
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]   
CHAT_ID        = os.environ["CHAT_ID"]          
ANTHROPIC_KEY  = os.environ["ANTHROPIC_KEY"]    

# ─── CATEGORÍAS ──────────────────────────────────────────
CATEGORIES = [
    "everyday conversational English",
    "business and professional English",
    "idioms and expressions",
    "phrasal verbs",
    "academic and writing vocabulary",
    "travel and social situations",
]

# ─── GENERAR LECCIÓN ──────────────────────────
def generate_lesson():
    category = random.choice(CATEGORIES)
    today = datetime.now().strftime("%A, %B %d")

    prompt = f"""You are an English teacher sending a daily vocabulary lesson via Telegram.

Today is {today}. Category: {category}

Generate a lesson with EXACTLY this format (use these exact emoji and labels):

📚 *Daily English* — {category}

─────────────────
🔤 *Word:* [word or phrase]
🗣 *Pronunciation:* /[phonetic]/
📖 *Meaning:* [clear, simple definition in 1 sentence]
─────────────────

💬 *Example 1:*
[natural sentence using the word]

💬 *Example 2:*
[another sentence in a different context]

─────────────────
🧠 *Memory tip:*
[a short mnemonic or trick to remember it]

❓ *Quick quiz:*
[a fill-in-the-blank sentence where the answer is the word]
Answer: ||[the word]||

─────────────────
#EnglishDaily #{category.replace(' ', '')}

Keep it practical and useful for a Spanish-speaking learner. Be concise."""

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 600,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["content"][0]["text"]

# ─── ENVIAR A TELEGRAM ────────────────────────────────────
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()
    print(f"✅ Mensaje enviado. Status: {r.status_code}")

# ─── MAIN ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("🤖 Generando lección...")
    lesson = generate_lesson()
    print(lesson)
    print("\n📤 Enviando a Telegram...")
    send_telegram(lesson)