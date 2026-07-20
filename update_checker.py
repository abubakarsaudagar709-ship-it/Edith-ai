import json
import ssl
import threading
import urllib.request

try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CONTEXT = ssl.create_default_context()

REPO = "abubakarsaudagar709-ship-it/Edith-ai"
CURRENT_VERSION = "1.0.0"


def check_for_update(callback):
    """
    Runs the check in a background thread so it never blocks the UI.
    callback(message_or_none) is called on the main thread via Clock
    by the caller — this function itself just calls callback(...) directly,
    so the caller should wrap it with Clock.schedule_once if needed.
    """

    def worker():
        try:
            url = f"https://api.github.com/repos/{REPO}/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "EdithApp"})
            with urllib.request.urlopen(req, timeout=10, context=SSL_CONTEXT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            latest_tag = data.get("tag_name", "").lstrip("v")
            if latest_tag and latest_tag != CURRENT_VERSION:
                url_page = f"https://github.com/{REPO}/releases/latest"
                callback(f"A new version ({latest_tag}) is available.\n{url_page}")
        except Exception:
            pass

    threading.Thread(target=worker, daemon=True).start()
