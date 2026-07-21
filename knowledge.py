import os
import json

KNOWLEDGE_FILE = "edith_knowledge.json"


def load_knowledge():
    if not os.path.exists(KNOWLEDGE_FILE):
        return {}
    try:
        with open(KNOWLEDGE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_knowledge(data):
    with open(KNOWLEDGE_FILE, "w") as f:
        json.dump(data, f)


def teach(topic, explanation):
    data = load_knowledge()
    data[topic.strip().lower()] = explanation.strip()
    save_knowledge(data)


def forget(topic):
    data = load_knowledge()
    key = topic.strip().lower()
    if key in data:
        del data[key]
        save_knowledge(data)
        return True
    return False


def find_knowledge(query):
    data = load_knowledge()
    query_lower = query.lower()

    if query_lower in data:
        return data[query_lower]

    for topic, explanation in data.items():
        if topic and topic in query_lower:
            return explanation

    return None
