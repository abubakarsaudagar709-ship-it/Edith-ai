import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle

from edith_core import process_command, load_user, create_user, bump_message_count, detect_language
from voice_utils import listen_once, speak
from update_checker import check_for_update

try:
    from jnius import autoclass
    JNIUS_AVAILABLE = True
except Exception:
    JNIUS_AVAILABLE = False

Window.softinput_mode = "below_target"

BLACK = (0.05, 0.05, 0.05, 1)
DARK_GRAY = (0.13, 0.13, 0.13, 1)
RED = (0.85, 0.1, 0.15, 1)
WHITE = (1, 1, 1, 1)

WAKE_COMMAND_FILE = "edith_wake_command.txt"


class ChatBubble(AnchorLayout):
    def __init__(self, text, is_user, **kwargs):
        anchor = "right" if is_user else "left"
        super().__init__(anchor_x=anchor, size_hint_y=None, padding=(10, 4), **kwargs)

        bubble_color = RED if is_user else DARK_GRAY

        self.label = Label(
            text=text,
            color=WHITE,
            font_size=23,
            halign="left",
            valign="top",
            size_hint=(None, None),
            padding=(14, 10)
        )
        self.label.bind(texture_size=self._resize)
        self.add_widget(self.label)

        with self.label.canvas.before:
            Color(*bubble_color)
            self.bg = RoundedRectangle(radius=[16])
        self.label.bind(pos=self._update_bg, size=self._update_bg)

    def _resize(self, instance, value):
        max_width = Window.width * 0.72
        w = min(value[0] + 28, max_width)
        self.label.text_size = (max_width - 28, None)
        self.label.size = (w, value[1] + 20)
        self.height = self.label.height + 8

    def _update_bg(self, *args):
        self.bg.pos = self.label.pos
        self.bg.size = self.label.size


class EdithUI(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.voice_enabled = False
        self.wake_word_enabled = False
        self.user = load_user()
        self.awaiting_name = self.user is None

        top_bar = BoxLayout(size_hint=(1, 0.09), padding=(15, 8))
        with top_bar.canvas.before:
            Color(*BLACK)
            self.topbar_bg = RoundedRectangle(radius=[0])
        top_bar.bind(pos=self._update_topbar_bg, size=self._update_topbar_bg)

        title = Label(text="EDITH", font_size=24, bold=True, color=RED, halign="left")
        top_bar.add_widget(title)

        self.voice_btn = Button(
            text="Voice: OFF",
            size_hint=(0.3, 1),
            background_color=DARK_GRAY,
            color=WHITE,
            font_size=12
        )
        self.voice_btn.bind(on_press=self.toggle_voice)
        top_bar.add_widget(self.voice_btn)

        self.wake_btn = Button(
            text="Wake: OFF",
            size_hint=(0.3, 1),
            background_color=DARK_GRAY,
            color=WHITE,
            font_size=12
        )
        self.wake_btn.bind(on_press=self.toggle_wake_word)
        top_bar.add_widget(self.wake_btn)

        self.add_widget(top_bar)

        self.scroll = ScrollView(size_hint=(1, 0.68))
        self.chat_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=8, padding=(10, 10))
        self.chat_box.bind(minimum_height=self.chat_box.setter("height"))
        self.scroll.add_widget(self.chat_box)
        self.add_widget(self.scroll)

        input_row = BoxLayout(size_hint=(1, 0.1), padding=(10, 6), spacing=6)

        self.entry = TextInput(
            multiline=False,
            font_size=18,
            background_color=DARK_GRAY,
            foreground_color=WHITE,
            cursor_color=WHITE
        )
        self.entry.bind(on_text_validate=self.on_send)
        input_row.add_widget(self.entry)

        mic_btn = Button(text="Mic", size_hint=(0.16, 1), background_color=DARK_GRAY, color=WHITE)
        mic_btn.bind(on_press=self.on_mic)
        input_row.add_widget(mic_btn)

        paste_btn = Button(text="Paste", size_hint=(0.18, 1), background_color=DARK_GRAY, color=WHITE, font_size=13)
        paste_btn.bind(on_press=self.on_paste)
        input_row.add_widget(paste_btn)

        send_btn = Button(text="SEND", size_hint=(0.22, 1), background_color=RED, color=WHITE, bold=True)
        send_btn.bind(on_press=self.on_send)
        input_row.add_widget(send_btn)

        self.add_widget(input_row)

        Window.clearcolor = BLACK

        Clock.schedule_once(self._startup, 0.4)
        Clock.schedule_interval(self._poll_wake_command, 2)

    def _update_topbar_bg(self, *args):
        self.topbar_bg.pos = args[0].pos
        self.topbar_bg.size = args[0].size

    def _startup(self, dt):
        if self.awaiting_name:
            self.add_bubble("Hi! I'm Edith. What's your name?", is_user=False)
        else:
            self.add_bubble(f"Welcome back, {self.user['name']}!", is_user=False)
            check_for_update(lambda msg: Clock.schedule_once(lambda dt2: self.add_bubble(msg, is_user=False)))

    def add_bubble(self, text, is_user):
        bubble = ChatBubble(text, is_user)
        self.chat_box.add_widget(bubble)
        Clock.schedule_once(lambda dt: setattr(self.scroll, "scroll_y", 0), 0.05)

        if not is_user and self.voice_enabled:
            speak(text)

    def on_send(self, *args):
        text = self.entry.text.strip()
        self.entry.text = ""
        if text == "":
            return
        self.handle_input(text)

    def handle_input(self, text):
        self.add_bubble(text, is_user=True)

        if self.awaiting_name:
            lang = detect_language(text)
            self.user = create_user(text, lang)
            self.awaiting_name = False
            self.add_bubble(f"Nice to meet you, {self.user['name']}! How can I help you today?", is_user=False)
            return

        lang = detect_language(text)
        bump_message_count(self.user, lang)

        reply = process_command(text, self.user)
        self.add_bubble(reply, is_user=False)

    def on_mic(self, *args):
        def got_text(text):
            if text:
                Clock.schedule_once(lambda dt: self.handle_input(text))
            else:
                Clock.schedule_once(lambda dt: self.add_bubble("Couldn't hear that clearly.", is_user=False))
        listen_once(got_text)

    def on_paste(self, *args):
        try:
            pasted = Clipboard.paste()
            if pasted:
                self.entry.text += pasted
        except Exception:
            pass

    def toggle_voice(self, *args):
        self.voice_enabled = not self.voice_enabled
        self.voice_btn.text = "Voice: ON" if self.voice_enabled else "Voice: OFF"

    def toggle_wake_word(self, *args):
        self.wake_word_enabled = not self.wake_word_enabled
        self.wake_btn.text = "Wake: ON" if self.wake_word_enabled else "Wake: OFF"

        if not JNIUS_AVAILABLE:
            self.add_bubble("Wake word only works in the installed Android app.", is_user=False)
            return

        try:
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            service_class_name = "org.abubakarsaudagar.edith.ServiceWakeword"
            ServiceClass = autoclass(service_class_name)
            intent = Intent(PythonActivity.mActivity, ServiceClass)
            if self.wake_word_enabled:
                PythonActivity.mActivity.startService(intent)
                self.add_bubble("Wake word listening started.", is_user=False)
            else:
                PythonActivity.mActivity.stopService(intent)
                self.add_bubble("Wake word listening stopped.", is_user=False)
        except Exception:
            self.add_bubble("Couldn't toggle the wake word service.", is_user=False)

    def _poll_wake_command(self, dt):
        if not self.wake_word_enabled:
            return
        if not os.path.exists(WAKE_COMMAND_FILE):
            return
        try:
            with open(WAKE_COMMAND_FILE, "r") as f:
                text = f.read().strip()
            os.remove(WAKE_COMMAND_FILE)
            if text:
                self.handle_input(text)
        except Exception:
            pass


class EdithApp(App):
    def build(self):
        return EdithUI()


if __name__ == "__main__":
    EdithApp().run()
