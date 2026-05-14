import os, requests, random

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID        = os.environ["CHAT_ID"]
GEMINI_KEY     = os.environ["GEMINI_KEY"]

HISTORY_FILE  = "used_words.txt"
LEARNED_FILE  = "learned_words.txt"


def load_words(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        return [line.strip().lower() for line in f if line.strip()]


def generate_review(word):
    prompt = f"""You are an English teacher helping a Spanish speaker memorize vocabulary through spaced review.

The student already saw this word/phrase once before: "{word}"

Your job is to create a memorable, engaging review session. The student may not remember it perfectly — that's okay.

Use EXACTLY this format, no extra text, no intro:

REPASO — {word}
¿Lo recuerdas? Intenta recordar qué significa antes de ver abajo...
Significa: [traducción natural al español, no literal]
Pronunciation: /[phonetic]/

Example 1: [everyday sentence using the word naturally]
Example 2: [a different everyday sentence showing another context or nuance]

Por qué es útil: [1 sentence in Spanish explaining when/why a native speaker uses this]

Tip para no olvidarlo: [a short memorable trick, analogy, or story in Spanish]"""

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}",
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    r = requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=15)
    r.raise_for_status()
    print(f"Enviado. Status: {r.status_code}")


if __name__ == "__main__":
    all_words  = load_words(HISTORY_FILE)
    learned    = load_words(LEARNED_FILE)

    # excluir las ya aprendidas
    to_review = [w for w in all_words if w not in learned]

    if not to_review:
        send_telegram("¡Ya repasaste todas las palabras! Agrega más con el bot principal.")
        print("No hay palabras para repasar.")
    else:
        word = random.choice(to_review)
        print(f"Repasando: {word}")
        review = generate_review(word)
        print(review)
        send_telegram(review)