import os
import re
import json
import random
from datetime import datetime

from web_search import web_search

USER_FILE = "edith_user.json"
NOTES_FILE = "edith_notes.json"

FOUNDER_REPLY = "I was created by Mr. Abubakar Saudagar, The Greatest of all time."

jokes = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "I told my computer I needed a break, now it won't stop sending me KitKats.",
    "Why do Java developers wear glasses? Because they can't C sharp.",
    "I would tell you a UDP joke, but you might not get it.",
    "Debugging: being the detective in a crime movie where you are also the murderer."
]

REPLIES = {
    "greeting": {
        "en": "Hello {name}! How can I help you today?",
        "hi": "नमस्ते {name}! मैं आपकी क्या मदद कर सकती हूँ?",
        "hinglish": "Hello {name}! Bolo, kya help chahiye?"
    },
    "how_are_you": {
        "en": "I'm doing great, thank you for asking.",
        "hi": "मैं बिल्कुल ठीक हूँ, पूछने के लिए धन्यवाद।",
        "hinglish": "Main bilkul badhiya hoon, poochne ke liye shukriya."
    },
    "thanks": {
        "en": "You're always welcome, {name}.",
        "hi": "आपका हमेशा स्वागत है, {name}।",
        "hinglish": "Koi baat nahi {name}, hamesha welcome ho."
    },
    "bye": {
        "en": "Goodbye {name}, take care.",
        "hi": "अलविदा {name}, अपना ख्याल रखिए।",
        "hinglish": "Bye {name}, apna khayal rakhna."
    },
    "help": {
        "en": "I can help with time, date, notes, calculator, opening apps, jokes, and general questions.",
        "hi": "मैं समय, तारीख, नोट्स, कैलकुलेटर, ऐप खोलने और सामान्य सवालों में मदद कर सकती हूँ।",
        "hinglish": "Main time, date, notes, calculator, apps kholna, jokes aur general sawaalon mein help kar sakti hoon."
    },
    "not_found": {
        "en": "Sorry, I couldn't find an answer to that right now.",
        "hi": "माफ़ कीजिए, अभी मुझे इसका जवाब नहीं मिल पाया।",
        "hinglish": "Sorry, abhi iska jawab nahi mil paya mujhe."
    }
}

HINGLISH_WORDS = [
    "hai", "kya", "kaise", "tum", "tumhara", "mera", "kaun", "batao",
    "kar", "krdo", "kro", "bhai", "yaar", "acha", "theek", "nahi", "haan"
]

GREETING_PHRASES = [
    "hi", "hello", "hey", "what's up", "whats up", "wassup", "sup", "yo",
    "namaste", "kya haal hai", "kya scene hai", "kya chal raha hai"
]

HOW_ARE_YOU_PHRASES = [
    "how are you", "how r u", "kaise ho", "kaisi ho", "haal chaal", "kya haal hai"
]

THANKS_PHRASES = ["thanks", "thank you", "thanku", "shukriya", "dhanyavad"]

BYE_PHRASES = ["bye", "goodbye", "see you", "alvida", "chalta hoon", "chalti hoon"]

HELP_PHRASES = ["help", "what can you do", "kya kar sakti ho", "madad"]

WHO_ARE_YOU_PHRASES = ["who are you", "tum kaun ho", "aap kaun hain"]

TIME_PHRASES = [
    "time", "what is the time", "what time is it", "current time",
    "samay kya hai", "time kya hai"
]

DATE_PHRASES = [
    "date", "what is the date", "what's the date", "today's date",
    "aaj ki tareekh", "tareekh kya hai"
]


def contains_any(cmd, phrases):
    for phrase in phrases:
        pattern = r"\b" + re.escape(phrase) + r"\b"
        if re.search(pattern, cmd):
            return True
    return False


def detect_language(text):
    if re.search(r"[\u0900-\u097F]", text):
        return "hi"
    lower = text.lower()
    if any(word in lower.split() for word in HINGLISH_WORDS):
        return "hinglish"
    return "en"


def reply_for(key, lang, **kwargs):
    variant = REPLIES.get(key, {})
    text = variant.get(lang) or variant.get("en", "")
    return text.format(**kwargs)


def load_user():
    if not os.path.exists(USER_FILE):
        return None
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def save_user(data):
    with open(USER_FILE, "w") as f:
        json.dump(data, f)


def create_user(name, lang):
    data = {"name": name.strip(), "language": lang, "message_count": 0}
    save_user(data)
    return data


def bump_message_count(user, lang):
    user["message_count"] = user.get("message_count", 0) + 1
    user["language"] = lang
    save_user(user)


def load_notes():
    if not os.path.exists(NOTES_FILE):
        return []
    try:
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_note(text):
    notes = load_notes()
    notes.append(text)
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f)


def show_notes():
    notes = load_notes()
    if not notes:
        return "You have no saved notes."
    reply = "Your Notes:\n"
    for i, n in enumerate(notes, 1):
        reply += f"\n{i}. {n}"
    return reply


def delete_notes():
    with open(NOTES_FILE, "w") as f:
        json.dump([], f)


def get_time():
    return "Current time is " + datetime.now().strftime("%I:%M %p")


def get_date():
    return "Today's date is " + datetime.now().strftime("%d %B %Y")


def calculate(expr):
    try:
        allowed = "0123456789.+-*/() "
        if not all(c in allowed for c in expr):
            return "Invalid expression."
        result = eval(expr, {"__builtins__": {}})
        return f"Result: {result}"
    except Exception:
        return "Sorry, I couldn't calculate that."


def open_app(name):
    import webbrowser
    name = name.strip()
    web_apps = {
        "chrome": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "instagram": "https://www.instagram.com",
        "whatsapp": "https://web.whatsapp.com"
    }
    if name in web_apps:
        try:
            webbrowser.open(web_apps[name])
            return f"Opening {name.title()}"
        except Exception:
            return f"Couldn't open {name.title()}"
    return f"I don't know how to open '{name}' yet."


def mood_reply(cmd):
    if "happy" in cmd:
        return "That's amazing to hear! Keep smiling."
    elif "sad" in cmd:
        return "I'm here for you. It's okay to feel low sometimes."
    elif "angry" in cmd:
        return "Take a deep breath. It'll be okay."
    elif "tired" in cmd:
        return "You should rest a bit."
    return "I hear you."


def is_founder_question(cmd):
    has_who = "who" in cmd or "kaun" in cmd
    has_founder_word = any(w in cmd for w in [
        "founder", "creator", "created you", "made you", "banaya", "nirmata"
    ])
    return has_who and has_founder_word


def truncate_result(text, max_len=280):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    result = ""
    for s in sentences:
        if result and len(result) + len(s) > max_len:
            break
        result += (" " if result else "") + s
    return result.strip()


def process_command(raw_text, user):
    cmd = raw_text.lower().strip()
    lang = detect_language(raw_text)
    name = user["name"] if user else "friend"

    if is_founder_question(cmd):
        return FOUNDER_REPLY

    if contains_any(cmd, WHO_ARE_YOU_PHRASES):
        return "I'm Edith, your personal AI assistant."

    if contains_any(cmd, TIME_PHRASES):
        return get_time()

    if contains_any(cmd, DATE_PHRASES):
        return get_date()

    if cmd.startswith("save note "):
        save_note(raw_text[10:])
        return "Note saved."

    if cmd == "show notes":
        return show_notes()

    if cmd == "delete notes":
        delete_notes()
        return "All notes deleted."

    if cmd.startswith("calculate ") or cmd.startswith("calc "):
        return calculate(cmd.split(" ", 1)[1])

    if cmd.startswith("open "):
        return open_app(cmd.replace("open ", "", 1))

    if cmd in ["joke", "tell me a joke"]:
        return random.choice(jokes)

    if cmd in ["i am happy", "i am sad", "i am angry", "i am tired"]:
        return mood_reply(cmd)

    if contains_any(cmd, HOW_ARE_YOU_PHRASES):
        return reply_for("how_are_you", lang)

    if contains_any(cmd, THANKS_PHRASES):
        return reply_for("thanks", lang, name=name)

    if contains_any(cmd, BYE_PHRASES):
        return reply_for("bye", lang, name=name)

    if contains_any(cmd, HELP_PHRASES):
        return reply_for("help", lang)

    if contains_any(cmd, GREETING_PHRASES):
        return reply_for("greeting", lang, name=name)

    result = web_search(raw_text)
    if result:
        return truncate_result(result)

    return reply_for("not_found", lang)
