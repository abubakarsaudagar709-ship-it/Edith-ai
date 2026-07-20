try:
    from jnius import autoclass
    from android import activity as android_activity
    JNIUS_AVAILABLE = True
except Exception:
    JNIUS_AVAILABLE = False

try:
    from plyer import tts
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False


def speak(text):
    if not TTS_AVAILABLE:
        return
    try:
        tts.speak(text)
    except Exception:
        pass


def listen_once(on_result):
    """
    Starts Android's native speech recognizer (tap-to-talk).
    on_result(text_or_none) is called with the recognized text,
    or None if it failed / isn't available (e.g. running off-device).
    """
    if not JNIUS_AVAILABLE:
        on_result(None)
        return

    try:
        Intent = autoclass("android.content.Intent")
        RecognizerIntent = autoclass("android.speech.RecognizerIntent")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")

        intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
        intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Speak now...")

        request_code = 1001

        def on_activity_result(request_code_in, result_code, intent_data):
            if request_code_in != request_code:
                return
            text = None
            try:
                results = intent_data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
                if results and results.size() > 0:
                    text = results.get(0)
            except Exception:
                text = None
            android_activity.unbind(on_activity_result=on_activity_result)
            on_result(text)

        android_activity.bind(on_activity_result=on_activity_result)
        PythonActivity.mActivity.startActivityForResult(intent, request_code)
    except Exception:
        on_result(None)
