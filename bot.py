import os, requests, random
from datetime import datetime

# variables de entorno, config en secrets and variables del repo
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID        = os.environ["CHAT_ID"]
GEMINI_KEY     = os.environ["GEMINI_KEY"]   

# lista de categorias, se elige una al azar
CATEGORIES = [
    "everyday conversational English",
    # "business and professional English",
    "idioms and expressions",
    "phrasal verbs",
    "academic and writing vocabulary",
    # "travel and social situations",
]

# funcion que arma el prompt, """ -> string multilinea, hace la peticion a Gemini, devuelve el texto de la respuesta"
def generate_lesson():
    category = random.choice(CATEGORIES)
    prompt = f"""You are an English teacher sending a short daily vocabulary lesson via Telegram.
Category: {category}

Generate a lesson with EXACTLY this format, no extra text, no intro, no title:

*Word:* [word or phrase]
*Meaning:* [traducción corta al español]
*Pronunciation:* /[phonetic]/
*Example:* [natural sentence using the word]
*Tip:* [1 short trick or curiosity to remember it]
*Quiz:* [fill-in-the-blank sentence]
Answer: ||[the word]||"""

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}",
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

# funcion que envia el msj a telegram, 
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=15)
    r.raise_for_status()
    print(f"Enviado. Status: {r.status_code}")


# solo si se corre el script directamente, no si se importa como modulo
if __name__ == "__main__":
    print("Generando lección...")
    lesson = generate_lesson()
    print(lesson)
    send_telegram(lesson)