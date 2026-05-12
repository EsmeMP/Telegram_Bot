import os, requests, random

# variables de entorno, config en secrets and variables del repo
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID        = os.environ["CHAT_ID"]
GEMINI_KEY     = os.environ["GEMINI_KEY"]

HISTORY_FILE = "used_words.txt"

CATEGORIES = [
    "everyday conversational English",
    "idioms and expressions",
    "phrasal verbs",
    "academic and writing vocabulary",
]

# lee las palabras ya enviadas
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return [line.strip().lower() for line in f.readlines() if line.strip()]

# guarda la palabra nueva al historial
def save_word(word):
    with open(HISTORY_FILE, "a") as f:
        f.write(word.lower() + "\n")

# funcion que arma el prompt y hace la peticion a Gemini
def generate_lesson():
    category = random.choice(CATEGORIES)
    history = load_history()
    avoid = ", ".join(history[-50:]) if history else "none yet"

    prompt = f"""You are an English teacher sending a short daily vocabulary lesson via Telegram.
Category: {category}

Your goal is to teach useful, natural English phrases and expressions that a Spanish speaker needs to actually hold a conversation in English.

Rules for choosing the word or phrase:
- Must be useful for real conversations, not basic b1 or b2(avoid: and, or, at, on, what, name, table, address)
- No cognates (words that are the same or very similar in Spanish like: information, direction, moment, natural)
- Prefer: phrasal verbs, idioms, collocations, connectors, conversational expressions
- Do NOT use any of these already sent words/phrases: {avoid}

Generate a lesson with EXACTLY this format, no extra text, no intro, no title:

Word: [word or phrase]
Meaning: [traducción corta al español]
Pronunciation: /[phonetic]/
Example: [natural sentence using the word]
Tip: [1 short trick or curiosity to remember it]
Quiz: [fill-in-the-blank sentence]
Answer: [the word]"""

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}",
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    lesson_text = data["candidates"][0]["content"]["parts"][0]["text"]

    # extrae la palabra y la guarda en el historial
    for line in lesson_text.splitlines():
        if line.lower().startswith("word:"):
            word = line.split(":", 1)[1].strip()
            save_word(word)
            break

    return lesson_text

# funcion que envia el msj a telegram
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=15)
    r.raise_for_status()
    print(f"Enviado. Status: {r.status_code}")

# solo si se corre el script directamente, no si se importa como modulo
if __name__ == "__main__":
    print("Generando lección...")
    lesson = generate_lesson()
    print(lesson)
    send_telegram(lesson)