import json
import ssl
import urllib.request
import urllib.parse

try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CONTEXT = ssl.create_default_context()


def web_search(query):
    try:
        url = (
            "https://api.duckduckgo.com/?q="
            + urllib.parse.quote(query)
            + "&format=json&no_html=1&skip_disambig=1"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "EdithApp/1.0"})
        with urllib.request.urlopen(req, timeout=8, context=SSL_CONTEXT) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        abstract = data.get("AbstractText")
        if abstract:
            return abstract

        related = data.get("RelatedTopics")
        if related:
            for item in related:
                if isinstance(item, dict) and item.get("Text"):
                    return item["Text"]

    except Exception:
        pass
    return None
