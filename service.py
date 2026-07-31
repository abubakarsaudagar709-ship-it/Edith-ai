# ============================================================
# WAKE WORD BACKGROUND SERVICE — EXPERIMENTAL / HIGHEST RISK
#
# Android REQUIRES a persistent notification for any service that
# uses the microphone in the background — this is not optional,
# it's an Android privacy rule, so a notification will always be
# visible while this is running.
# ============================================================

try:
    from jnius import autoclass, PythonJavaClass, java_method
    JNIUS_AVAILABLE = True
except Exception:
    JNIUS_AVAILABLE = False

COMMAND_FILE = "edith_wake_command.txt"


def handle_result(text):
    text_lower = text.lower()
    if "edith" in text_lower:
        try:
            with open(COMMAND_FILE, "w") as f:
                f.write(text_lower)
        except Exception:
            pass


if JNIUS_AVAILABLE:

    SpeechRecognizer = autoclass("android.speech.SpeechRecognizer")
    RecognizerIntent = autoclass("android.speech.RecognizerIntent")
    Intent = autoclass("android.content.Intent")
    PythonService = autoclass("org.kivy.android.PythonService")
    Looper = autoclass("android.os.Looper")
    Handler = autoclass("android.os.Handler")
    NotificationBuilder = autoclass("android.app.Notification$Builder")
    NotificationChannel = autoclass("android.app.NotificationChannel")
    NotificationManager = autoclass("android.app.NotificationManager")
    Context = autoclass("android.content.Context")
    BuildVersion = autoclass("android.os.Build$VERSION")

    class EdithRecognitionListener(PythonJavaClass):
        __javainterfaces__ = ["android/speech/RecognitionListener"]
        __javacontext__ = "app"

        def __init__(self, on_result, restart_callback):
            super().__init__()
            self.on_result = on_result
            self.restart_callback = restart_callback

        @java_method("(Landroid/os/Bundle;)V")
        def onResults(self, results):
            try:
                matches = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                if matches and matches.size() > 0:
                    self.on_result(matches.get(0))
            except Exception:
                pass
            self.restart_callback()

        @java_method("(I)V")
        def onError(self, error):
            self.restart_callback()

        @java_method("(Landroid/os/Bundle;)V")
        def onReadyForSpeech(self, params):
            pass

        @java_method("()V")
        def onBeginningOfSpeech(self):
            pass

        @java_method("(F)V")
        def onRmsChanged(self, rmsdB):
            pass

        @java_method("([B)V")
        def onBufferReceived(self, buffer):
            pass

        @java_method("()V")
        def onEndOfSpeech(self):
            pass

        @java_method("(Landroid/os/Bundle;)V")
        def onPartialResults(self, partialResults):
            pass

        @java_method("(ILandroid/os/Bundle;)V")
        def onEvent(self, eventType, params):
            pass


def show_notification(service):
    try:
        channel_id = "edith_wake_channel"
        if BuildVersion.SDK_INT >= 26:
            channel = NotificationChannel(
                channel_id, "Edith Wake Word", NotificationManager.IMPORTANCE_LOW
            )
            manager = service.getSystemService(Context.NOTIFICATION_SERVICE)
            manager.createNotificationChannel(channel)
            builder = NotificationBuilder(service, channel_id)
        else:
            builder = NotificationBuilder(service)

        builder.setContentTitle("Edith")
        builder.setContentText("Listening for wake word...")
        notification = builder.build()
        service.startForeground(1, notification)
    except Exception:
        pass


def run_service():
    if not JNIUS_AVAILABLE:
        return

    service = PythonService.mService
    show_notification(service)

    Looper.prepare()
    handler = Handler(Looper.myLooper())

    recognizer = SpeechRecognizer.createSpeechRecognizer(service)

    intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
    intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)

    def restart_listening():
        def _start():
            try:
                recognizer.startListening(intent)
            except Exception:
                pass
        handler.postDelayed(_start, 500)

    listener = EdithRecognitionListener(handle_result, restart_listening)
    recognizer.setRecognitionListener(listener)

    restart_listening()

    Looper.loop()


if __name__ == "__main__":
    run_service()
