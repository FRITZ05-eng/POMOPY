import kivy
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from datetime import datetime, timedelta
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.audio import SoundLoader
from kivy.animation import Animation
from kivy.uix.anchorlayout import AnchorLayout
import sqlite3
from collections import defaultdict
from kivy.uix.boxlayout import BoxLayout
import matplotlib.pyplot as plt
from kivy.metrics import dp
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.widget import Widget
from kivy.properties import (
    ListProperty,
    NumericProperty,
    BooleanProperty,
    StringProperty,
    ObjectProperty,
)
from kivy.uix.progressbar import ProgressBar as KivyProgressBar
from datetime import datetime
from kivy.uix.screenmanager import (
    SlideTransition,
    FadeTransition,
    SwapTransition,
    WipeTransition,
    FallOutTransition,
    RiseInTransition
)


import os

kivy.require("2.3.0")  # Using 2.3.0 is fine


Window.clearcolor = (0.1176, 0.4510, 0.7451, 1)  # white background for light theme





class RoundedButton(Button):
    bg_color = ListProperty([0.2, 0.6, 0.8, 1])
    text_color = ListProperty([1, 1, 1, 1])
    radius = ListProperty([15])

    def __init__(self, **kwargs):
        bg_color = kwargs.pop("background_color", None)
        if bg_color:
            self.bg_color = bg_color
        text_color = kwargs.pop("color", None)
        if text_color:
            self.text_color = text_color
        radius = kwargs.pop("radius", None)
        if radius:
            self.radius = radius
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)  # transparent, we paint bg ourselves
        self.color = self.text_color
        self.size_hint = kwargs.get("size_hint", (1, None))
        self.height = kwargs.get("height", 50)
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(radius=self.radius)
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(bg_color=self.update_bg_color)
        self.bind(state=self.on_state_change)
        if Window.width < dp(400):
            self.logo.font_size = '20sp'
            for btn in [self.btn_home, self.btn_timer, self.btn_history, self.btn_goals]:
                btn.width = dp(80)

    def update_rect(self, *args): # Added *args here
        self.rect.pos = self.pos
        self.rect.size = self.size

    def update_bg_color(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)

    def on_state_change(self, instance, value):
        if value == "down":  # darken background color slightly on press
            darkened = [max(0, c - 0.1) for c in self.bg_color[:3]] + [self.bg_color[3]]
            self.canvas.before.clear()
            with self.canvas.before:
                Color(*darkened)
                self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)
        else:
            self.update_bg_color(self, self.bg_color)


class IconButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = True


def make_back_icon(callback):
    icon = IconButton(source="back_icon.png", size_hint=(None, None), size=(40, 40))
    icon.bind(on_press=callback)
    return icon


class HomeButton(RoundedButton):
    def __init__(self, **kwargs):
        super().__init__(
            text="Home",
            size_hint_x=None,
            width=dp(100),
            background_color=(0.2, 0.6, 0.8, 0),
            color=(0.2, 0.6, 0.8, 1),
            **kwargs
        )

    def on_press(self):
        App.get_running_app().root.current = "main"


class TimerButton(RoundedButton):
    def __init__(self, **kwargs):
        super().__init__(
            text="Timer",
            size_hint_x=None,
            width=dp(100),
            background_color=(0.2, 0.6, 0.8, 0),
            color=(0.2, 0.6, 0.8, 1),
            **kwargs
        )

    def on_press(self):
        App.get_running_app().root.current = "timer"


class HistoryButton(RoundedButton):
    def __init__(self, **kwargs):
        super().__init__(
            text="History",
            size_hint_x=None,
            width=dp(100),
            background_color=(0.2, 0.6, 0.8, 0),
            color=(0.2, 0.6, 0.8, 1),
            **kwargs
        )

    def on_press(self):
        app = App.get_running_app()
        sm = app.root
        if sm.has_screen("history"):
            sm.get_screen("history").load_history()
        sm.transition = SlideTransition(direction="left", duration=0.3)
        sm.current = "history"


class GoalsButton(RoundedButton):
    def __init__(self, **kwargs):
        super().__init__(
            text="Goals",
            size_hint_x=None,
            width=dp(100),
            background_color=(0.2, 0.6, 0.8, 0),
            color=(0.2, 0.6, 0.8, 1),
            **kwargs
        )

    def on_press(self):
        App.get_running_app().root.current = "dailygoals"


class BackIcon(ButtonBehavior, Image):
    def __init__(self, callback, **kwargs):
        super().__init__(
            source='back_icon.png',
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            allow_stretch=True,
            keep_ratio=True,
            **kwargs
        )
        self.callback = callback

    def on_press(self):
        if callable(self.callback):
            self.callback()


class NavigationBar(BoxLayout):
    def __init__(self, back_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = dp(15)
        self.spacing = dp(20)

        if back_callback is None:
            back_callback = self.go_back

        self.back_icon = BackIcon(back_callback)
        self.add_widget(self.back_icon)

        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(pos=self.update_rect, size=self.update_rect)

        self.logo = Label(
            text="Pomopy",
            font_size='24sp',
            bold=True,
            color=(0.2, 0.6, 0.8, 1),
            size_hint_x=None,
            width=150,
        )
        self.add_widget(self.logo)

        # Add polymorphic buttons directly
        self.add_widget(HomeButton())
        self.add_widget(TimerButton())
        self.add_widget(HistoryButton())
        self.add_widget(GoalsButton())

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def go_back(self):
        app = App.get_running_app()
        sm = app.root
        if hasattr(sm, 'screen_names') and sm.screen_names:
            current = sm.current
            current_index = sm.screen_names.index(current)
            if current_index > 0:
                sm.transition = SlideTransition(direction="right", duration=0.3)
                sm.current = sm.screen_names[current_index - 1]



class Card(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.height = dp(60)
        self.padding = dp(15)
        self.spacing = dp(20)
        self.width = dp(100)
        self.size_hint_y = None
        self.height = kwargs.get("height", 150)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = RoundedRectangle(radius=[15])
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._layout = BoxLayout(orientation="vertical", spacing=30, padding=60)
        self._setup_ui()
        self.add_widget(self._layout)

    def _setup_ui(self):
        self._layout.add_widget(Image(source="pomopy_logo.png", size_hint=(1, 0.6)))

        title = Label(
            text="Welcome to Pomopy",
            font_size=48,
            bold=True,
            color=(1, 1, 1, 1),
        )
        self._layout.add_widget(title)

        subtitle = Label(
            text="Your elegant Pomodoro timer",
            font_size=20,
            color=(1, 1, 1, 1),
        )
        self._layout.add_widget(subtitle)

        self._name_input = TextInput(
            hint_text="Enter your name",
            size_hint=(1, None),
            height=50,
            multiline=False,
            foreground_color=(0, 0, 0, 1),
            background_color=(0.9, 0.9, 0.9, 1),
        )
        self._layout.add_widget(self._name_input)

        self._layout.add_widget(
            RoundedButton(
                text="ENTER YOUR NAME",
                background_color=(0.2, 0.6, 0.8, 1),
                on_press=self._go_to_main,
            )
        )
        self._layout.add_widget(
            RoundedButton(
                text="EXIT",
                background_color=(0.2, 0.6, 0.8, 1),
                on_press=App.get_running_app().stop,
            )
        )

    def get_name_input(self):
        return self._name_input.text

    def _go_to_main(self, instance):
        print(f"User entered name: {self.get_name_input()}")
        self.manager.current = "main"


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation="vertical")
        self.navbar = NavigationBar()
        main_layout.add_widget(self.navbar)
        content = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(20))

        content_wrapper = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            spacing=dp(20),
            padding=[dp(20)] * 4
        )

        content_wrapper.padding = (20, 20, 20, 20)
        content_wrapper.spacing = 20
        content_wrapper.add_widget(Image(source="pomopy_logo.png", size_hint=(1, 0.5)))

        self.user_name_label = Label(
            text="Welcome!",
            font_size='28sp',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50),
        )
        content_wrapper.add_widget(self.user_name_label)

        headline = Label(
            text="Ready to focus?",
            font_size='32sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(70),
        )
        content_wrapper.add_widget(headline)

        timer_card = Card(height=180)
        self.timer_label = Label(
            text="25:00",
            font_size='64sp',
            color=(0.2, 0.6, 0.8, 1),
            size_hint_y=None,
            height=dp(100),
        )
        timer_card.add_widget(self.timer_label)
        content_wrapper.add_widget(timer_card)

        buttons_layout = BoxLayout(
            orientation="horizontal", spacing=20, size_hint_y=None, height=60
        )
        start_btn = RoundedButton(
            text="START SESSION",
            background_color=(0.2, 0.6, 0.8, 1),
            on_press=self.start_timer,
        )
        history_btn = RoundedButton(
            text="HISTORY",
            background_color=(0.6, 0.3, 1, 1),
            on_press=self.show_history,
        )
        buttons_layout.add_widget(start_btn)
        buttons_layout.add_widget(history_btn)
        content_wrapper.add_widget(buttons_layout)

        quote_label = Label(
            text="Crush it now, chill later",
            font_size='32sp',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=30,
        )
        content_wrapper.add_widget(quote_label)
        content.add_widget(content_wrapper)
        main_layout.add_widget(content)
        self.add_widget(main_layout)
        SlideTransition(direction="left", duration=0.3)

    def on_pre_enter(self):
        welcome_screen = self.manager.get_screen("welcome")
        name = welcome_screen.get_name_input()
        self.user_name_label.text = f"Welcome, {name}!"

    def start_timer(self, instance):
        self.manager.get_screen("timer").start_session()
        self.manager.current = "timer"

    def show_history(self, instance):
        self.manager.get_screen("history").load_history()
        self.manager.current = "history"



class TimerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_db()

    def _init_db(self):
        """Creates the sessions table if it doesn't exist."""
        conn = sqlite3.connect("pomopy.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                start_time TEXT,
                end_time TEXT,
                duration INTEGER
            )
        """)
        conn.commit()
        conn.close()
        self.pomodoro_count = 0
        self.is_running = False
        self.pomodoro_duration = 25
        self.time_left = self.pomodoro_duration * 60
        self.break_duration = 5
        self.long_break_duration = 15
        self.session_type = "pomodoro"
        self.alarm = SoundLoader.load("ringtone.mp3")
        self.timer_event = None
        self.start_time = None
        main_layout = BoxLayout(orientation="vertical")
        self.navbar = NavigationBar()
        main_layout.add_widget(self.navbar)
        content = BoxLayout(orientation="vertical", padding=40, spacing=30)
        content_wrapper = BoxLayout(orientation="vertical", size_hint=(1, None),
                                    width=Window.width, spacing=dp(20))

        content_wrapper.add_widget(Image(source="pomopy_logo.png", size_hint=(1, 0.3)))

        timer_card = Card(height=200, orientation="vertical")

        # Wrap label in anchor layout
        anchor = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, 1))

        self.timer_label = Label(
            text="25:00",
            font_size=dp(100),
            color=(0.15, 0.4, 0.7, 1),
            size_hint=(1, 1),
            halign="center",
            valign="middle"
        )
        self.timer_label.bind(size=self._update_timer_text_size)

        anchor.add_widget(self.timer_label)
        timer_card.add_widget(anchor)

        content_wrapper.add_widget(timer_card)
        self.start_button = RoundedButton(
            text="START TIMER",
            background_color=(0.2, 0.6, 0.8, 1),
            size_hint=(1, None),
            height=50,
            on_press=self.start_timer,
        )
        content_wrapper.add_widget(self.start_button)
        time_control = BoxLayout(
            orientation="horizontal", spacing=10, size_hint_y=None, height=50
        )
        add_min_btn = RoundedButton(
            text="+ 1 MIN", background_color=(0.4, 0.4, 1, 1), on_press=self.add_minute
        )
        sub_min_btn = RoundedButton(
            text="- 1 MIN", background_color=(0.4, 0.4, 1, 1), on_press=self.subtract_minute
        )
        time_control.add_widget(add_min_btn)
        time_control.add_widget(sub_min_btn)
        content_wrapper.add_widget(time_control)
        quote = Label(
            text="Crush it now, chill later", font_size=20, color=(0.5, 0.5, 0.5, 1)
        )
        content_wrapper.add_widget(quote)
        content.add_widget(content_wrapper)
        main_layout.add_widget(content)
        self.add_widget(main_layout)
        FadeTransition(duration=0.3)
        self.navbar = NavigationBar(back_callback=self.go_back)

        Clock.schedule_once(self.stop_alarm, 10)


    def _update_timer_text_size(self, instance, value):
        instance.text_size = value

    def start_session(self, session_type="pomodoro"):
        self.session_type = session_type
        if session_type == "pomodoro":
            self.time_left = self.pomodoro_duration * 60
        elif session_type == "break":
            self.time_left = self.break_duration * 60
        elif session_type == "long_break":
            self.time_left = self.long_break_duration * 60
        self.timer_label.text = f"{self.time_left // 60:02}:{self.time_left % 60:02}"
        self.is_running = False

    def go_back(self, *args):
        if self.manager:
            self.manager.transition = FadeTransition(duration=0.3)
            self.manager.current = "MainScreen                                                   "

    def start_timer(self, instance):
        if not self.is_running:
            self.start_time = datetime.now()
            self.is_running = True
            Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        if self.is_running:
            if self.time_left > 0:
                self.time_left -= 1
                minutes, seconds = divmod(self.time_left, 60)
                self.timer_label.text = f"{minutes:02}:{seconds:02}"
            else:
                self.is_running = False
                self.timer_label.text = "Time's up!"
                self.on_timer_complete()

    def stop_alarm(self, instance):

        if self.alarm:
            self.alarm.stop()

    def add_minute(self, instance):
        self.time_left += 60
        minutes, seconds = divmod(self.time_left, 60)
        self.timer_label.text = f"{minutes:02}:{seconds:02}"

    def subtract_minute(self, instance):
        self.time_left = max(0, self.time_left - 60)
        minutes, seconds = divmod(self.time_left, 60)
        self.timer_label.text = f"{minutes:02}:{seconds:02}"

    def save_session(self):
        if not self.start_time:
            print("Skipping save: No start time recorded")
            return

        end_time = datetime.now()
        duration = int((end_time - self.start_time).total_seconds() // 60)

        print(f"Attempting to save: {self.start_time}, {end_time}, {duration} min")  # Debug output

        conn = sqlite3.connect("pomopy.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (date, start_time, end_time, duration)
            VALUES (?, ?, ?, ?)
        """, (self.start_time.strftime("%Y-%m-%d"),
              self.start_time.strftime("%H:%M"),
              end_time.strftime("%H:%M"),
              duration))

        conn.commit()
        conn.close()

        print("Session saved successfully!")  # Confirmation debug

    def on_timer_complete(self):
        """Handles actions after the timer completes."""
        now = datetime.now()
        start = now.strftime("%H:%M")
        end = (now + timedelta(minutes=25)).strftime("%H:%M")  # assuming 25 min
        duration = 25

        self.save_session()  # Store session details in SQLite

        # Navigate to history screen
        self.manager.current = "history"


class HistoryDB:
    def __init__(self, db_path=None):
        if not db_path:
            db_path = os.path.join(os.getcwd(), "history.db")
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                start TEXT,
                end TEXT,
                duration TEXT
            )
        """)
        self.conn.commit()

    def add_entry(self, date, start, end, duration):
        self.conn.execute(
            "INSERT INTO history (date, start, end, duration) VALUES (?, ?, ?, ?)",
            (date, start, end, duration)
        )
        self.conn.commit()

    def get_all_entries(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT date, start, end, duration FROM history ORDER BY id ASC")
        return cursor.fetchall()

    def close(self):
        self.conn.close()


class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = BoxLayout(orientation="vertical")
        self.navbar = NavigationBar()
        main_layout.add_widget(self.navbar)

        content = BoxLayout(orientation="vertical", padding=40, spacing=20)
        self.scroll = ScrollView()
        self.history_layout = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.history_layout.bind(minimum_height=self.history_layout.setter("height"))
        self.scroll.add_widget(self.history_layout)
        content.add_widget(self.scroll)
        btn = Button(text="Load History", size_hint_y=None, height=50)
        btn.bind(on_release=lambda x: self.load_history())
        content.add_widget(btn)

        main_layout.add_widget(content)
        self.add_widget(main_layout)
        Clock.schedule_once(self._inject_dummy_history, 1)

        content = BoxLayout(orientation="vertical", padding=40, spacing=20)

        # Delay history loading
        Clock.schedule_once(lambda dt: self.load_history(), 0.5)


    def load_history(self):
        self.history_layout.clear_widgets()

        db = HistoryDB()
        entries = db.get_all_entries()
        db.close()

        if not entries:
            return

        total_sessions = len(entries)
        total_minutes = sum(int(e[3].split()[0]) for e in entries)
        summary_text = f"Total Sessions: {total_sessions} | Total Time: {total_minutes} min"
        summary_label = Label(
            text=summary_text,
            color=(0.2, 0.4, 0.7, 1),
            size_hint_y=None,
            height=50,
            halign="left",
            valign="middle",
        )
        summary_label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        card_summary = Card(height=50)
        card_summary.add_widget(summary_label)
        self.history_layout.add_widget(card_summary)

        minutes_per_day = defaultdict(int)
        for e in entries:
            minutes_per_day[e[0]] += int(e[3].split()[0])

        if minutes_per_day:
            sorted_dates = sorted(minutes_per_day)
            minutes = [minutes_per_day[d] for d in sorted_dates]
            fig, ax = plt.subplots(figsize=(6, 2))
            ax.bar(sorted_dates, minutes, color="#3498db")
            ax.set_title("Minutes Done Per Day")
            ax.set_xlabel("Date")
            ax.set_ylabel("Minutes")
            ax.tick_params(axis='x', rotation=45)
            fig.tight_layout()
            canvas = FigureCanvasKivyAgg(fig)
            canvas.size_hint_y = None
            canvas.height = 300
            self.history_layout.add_widget(canvas)

        for date, start, end, duration in reversed(entries):
            text = f"{date} {start} - {end} ({duration})"
            card = Card(height=60)
            label = Label(
                text=text,
                color=(0.3, 0.3, 0.3, 1),
                halign="left",
                valign="middle",
                size_hint_y=None,
                height=60,
            )
            label.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
            card.add_widget(label)
            self.history_layout.add_widget(card)

    def save_session_to_history(self, start_time, end_time, duration_min):
        if not (start_time and end_time and duration_min):
            print("Missing session values")
            return

        db = HistoryDB()
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        db.add_entry(date, start_time, end_time, f"{duration_min} min")

    def _inject_dummy_history(self, *args):
        from datetime import datetime
        db = HistoryDB()
        now = datetime.now().strftime("%Y-%m-%d")
        db.add_entry(now, "09:00", "09:25", "25 min")
        db.add_entry(now, "10:00", "10:25", "25 min")
        db.close()
        self.load_history()

        db.close()

        Clock.schedule_once(lambda dt: self.load_history(), 0.1)


class PlayButton(ButtonBehavior, FloatLayout):
    bg_color = ListProperty([0, 0.72, 0.54, 1])
    icon_color = ListProperty([1, 1, 1, 1])
    is_playing = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (48, 48)

        with self.canvas.before:
            self.color_instruction = Color(*self.bg_color) # Store a reference to the Color instruction
            self.bg_circle = RoundedRectangle(pos=self.pos, size=self.size, radius=[24])
        self.bind(pos=self.update_bg, size=self.update_bg, bg_color=self.update_bg_color)
        self.icon = Label(
            text="▶",
            font_size=24,
            color=self.icon_color,
            bold=True,
            size_hint=(None, None),
            size=(24, 24),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.bind(icon_color=self.update_icon_color)
        self.add_widget(self.icon)

    def update_icon_color(self, instance, value):
        self.icon.color = value

    def update_bg(self, *args):
        self.bg_circle.pos = self.pos
        self.bg_circle.size = self.size

    def update_bg_color(self, instance, value):
        self.color_instruction.rgb = value[:3] # Update the existing Color instruction's RGB
        self.color_instruction.a = value[3]    # Update the existing Color instruction's alpha (if needed)

    def on_press(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.bg_color = [0, 0.72, 0.54, 1]
            self.icon.text = "❚❚"  # Change icon to pause
        else:
            self.bg_color = [0, 0.72, 0.54, 1]
            self.icon.text = "▶"  # Change icon to play


class ProgressBar(KivyProgressBar):
    bar_color = ListProperty([0, 0.72, 0.54, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._color_instruction = Color(*self.bar_color)
            self._rect = RoundedRectangle(pos=self.pos, size=(self.width * (self.value / 100.0),
                                                              self.height), radius=[8])

        self.bind(value=self._update_rect)
        self.bind(pos=self._update_rect)
        self.bind(size=self._update_rect)
        self.bind(bar_color=self._update_color_graphics)

        Clock.schedule_once(lambda dt: self._update_rect())

    def _update_color_graphics(self, instance, value):
        self._color_instruction.rgba = value

    def _update_rect(self, *args):
        self._rect.pos = self.pos
        self._rect.size = (self.width * (self.value / 100.0), self.height)



class DailyGoalItem(BoxLayout):
    title = StringProperty("")
    time_done = NumericProperty(0)  # in minutes
    time_goal = NumericProperty(0)  # in minutes
    color = ListProperty([0, 0.72, 0.54, 1])
    percent = NumericProperty(0)
    is_playing = BooleanProperty(False)
    editing = BooleanProperty(False)

    def __init__(self, title, time_done, time_goal, color, update_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(72)
        self.padding = [dp(20), dp(12), dp(20), dp(12)]
        self.spacing = dp(20)

        self.color = color
        self.title = title
        self.time_done = time_done
        self.time_goal = time_goal
        self.percent = min(self.time_done / self.time_goal * 100, 100) if self.time_goal > 0 else 0

        self.update_callback = update_callback
        self.editing = False


        with self.canvas.before:
            Color(0.74, 0.89, 0.78, 1)
            self.bg_rect = RoundedRectangle(radius=[16])
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Left side layout
        self.left = BoxLayout(orientation="horizontal", size_hint_x=0.7, spacing=16)
        self.play_btn = PlayButton(bg_color=self.color)
        self.play_btn.size_hint = (None, None)
        self.play_btn.size = (48, 48)
        self.play_btn.bind(on_press=self.toggle_play)
        self.left.add_widget(self.play_btn)

        self.text_layout = BoxLayout(orientation="vertical", spacing=4)
        self.title_label = Label(
            text=self.title,
            color=self.color,
            font_size='14sp',
            bold=True,
            size_hint_y=None,
            height=20,
            halign="left",
            valign="middle",
        )
        self.title_label.bind(size=self.title_label.setter("text_size"))
        self.text_layout.add_widget(self.title_label)
        self.title_label.color = self.color

        time_text = f"{self.format_time(self.time_done)} / {self.format_time(self.time_goal)}" if self.time_goal > 0 else f"{self.format_time(self.time_done)}"
        self.time_label = Label(
            text=time_text,
            color=(1, 1, 1, 1),
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=28,
            halign="left",
            valign="middle",
        )
        self.time_label.bind(size=self.time_label.setter("text_size"))
        self.text_layout.add_widget(self.time_label)
        self.left.add_widget(self.text_layout)
        self.add_widget(self.left)

        self.progress_row = BoxLayout(
            orientation="horizontal",
            spacing=6,
            size_hint_y=None,
            height=dp(16),
        )

        self.right_layout = BoxLayout(
            orientation="vertical",
            size_hint_x=0.3,
            spacing=dp(6),
            padding=[0, dp(4), 0, dp(4)]
        )

        # Move it where you want it:
        self.text_layout.add_widget(self.progress_row)  # Instead of right_layout

        self.progress_bar = ProgressBar(value=self.percent, bar_color=self.color, size_hint_x=0.75, height=12)
        self.percent_label = Label(
            text=f"{int(self.percent)} %",
            color=(1, 1, 1, 1),
            font_size='14sp',
            size_hint_x=0.25,
            halign="right",
            valign="middle"
        )

        self.percent_label.bind(size=self.percent_label.setter("text_size"))
        self.progress_row.add_widget(self.progress_bar)
        self.progress_row.add_widget(self.percent_label)


        # Edit + Delete buttons
        self.buttons_layout = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=30)
        self.btn_edit = RoundedButton(
            text="Edit", background_color=(0.4, 0.4, 1, 1),
            size_hint_x=0.5, height=28,
            on_press=self.start_edit,
        )
        self.btn_delete = RoundedButton(
            text="Delete", background_color=(0.9, 0.1, 0.1, 1),
            size_hint_x=0.5, height=28,
            on_press=self.delete_item,
        )
        self.buttons_layout.add_widget(self.btn_edit)
        self.buttons_layout.add_widget(self.btn_delete)
        self.right_layout.add_widget(self.buttons_layout)

        self.edit_layout = BoxLayout(orientation="horizontal", spacing=8, size_hint_y=None, height=30)
        self.edit_title_input = TextInput(text=self.title, multiline=False, size_hint_x=0.5, font_size=14, height=28)
        self.edit_time_input = TextInput(text=str(self.time_goal), multiline=False, size_hint_x=0.3, font_size=14, height=28, input_filter="int")
        self.btn_save_edit = RoundedButton(
            text="Save",
            background_color=(0.2, 0.6, 0.8, 1),
            size_hint_x=0.2,
            height=28,
            on_press=self.save_edit,
        )
        self.edit_layout.add_widget(self.edit_title_input)
        self.edit_layout.add_widget(self.edit_time_input)
        self.edit_layout.add_widget(self.btn_save_edit)
        self.edit_layout.opacity = 0
        self.edit_layout.disabled = True
        self.right_layout.add_widget(self.edit_layout)

        self.add_widget(self.right_layout)
        self.play_timer = None



    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def toggle_play(self, instance):
        if self.editing:
            return
        self.is_playing = not self.is_playing
        self.play_btn.is_playing = self.is_playing
        if self.is_playing:
            self.start_increment_timer()
        else:
            self.stop_increment_timer()

    def start_increment_timer(self):
        if not self.play_timer:
            self.play_timer = Clock.schedule_interval(self.increment_time, 60)

    def stop_increment_timer(self):
        if self.play_timer:
            self.play_timer.cancel()
            self.play_timer = None
        self.is_playing = False
        self.play_btn.is_playing = False

    def increment_time(self, dt):
        if self.time_goal > 0 and self.time_done >= self.time_goal:
            self.stop_increment_timer()
            return
        self.time_done += 1
        self.percent = (self.time_done / self.time_goal * 100) if self.time_goal > 0 else 0
        self._update_progress_bar(self, self.percent)
        self.percent_label.text = f"{int(self.percent)} %"
        time_text = f"{self.format_time(self.time_done)} / {self.format_time(self.time_goal)}" if self.time_goal > 0 else f"{self.format_time(self.time_done)}"
        self.time_label.text = time_text
        self.update_callback()
        print(f"{self.title}: {self.percent}% done")

    def _update_progress_bar(self, instance, value):
        self.progress_bar.value = value

    def start_edit(self, instance):
        if self.is_playing:
            self.toggle_play(None)
        self.editing = True
        self.title_label.opacity = 0
        self.time_label.opacity = 0
        self.play_btn.opacity = 0
        self.buttons_layout.opacity = 0
        self.edit_layout.opacity = 1
        self.edit_layout.disabled = False

    def save_edit(self, instance):
        new_title = self.edit_title_input.text.strip()
        new_time_goal_str = self.edit_time_input.text.strip()

        if new_title:
            self.title = new_title
        try:
            new_time_goal = int(new_time_goal_str)
            if new_time_goal < 0:
                new_time_goal = 0
        except ValueError:
            new_time_goal = 0

        self.time_goal = new_time_goal
        if self.time_goal > 0 and self.time_done > self.time_goal:
            self.time_done = self.time_goal

        self.percent = (self.time_done / self.time_goal * 100) if self.time_goal > 0 else 0
        self.title_label.text = self.title
        time_text = f"{self.format_time(self.time_done)} / {self.format_time(self.time_goal)}" if self.time_goal > 0 else f"{self.format_time(self.time_done)}"
        self.time_label.text = time_text
        self.progress_bar.value = self.percent
        self.percent_label.text = f"{int(self.percent)} %"

        self.editing = False
        self.title_label.opacity = 1
        self.time_label.opacity = 1
        self.play_btn.opacity = 1
        self.buttons_layout.opacity = 1
        self.edit_layout.opacity = 0
        self.edit_layout.disabled = True
        self.update_callback()

    def delete_item(self, instance):
        self.stop_increment_timer()
        parent = self.parent
        if parent:
            parent.remove_widget(self)
        self.update_callback()

    def format_time(self, minutes):
        h = minutes // 60
        m = minutes % 60
        return f"{h}h {m:02}m"


class DailyGoalsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_db()
        main_layout = BoxLayout(orientation="vertical")
        self.navbar = NavigationBar()
        main_layout.add_widget(self.navbar)
        content = BoxLayout(orientation="vertical", padding=[dp(20)] * 4, spacing=dp(20))
        title_layout = BoxLayout(orientation="vertical", size_hint_y=None, height=120)
        title_label = Label(
            text="Beat Procrastination\nWith Daily Goals",
            font_size='34sp',
            bold=True,
            color=(1, 1, 1, 1),
            halign="center",
            valign="middle",
        )
        if not title_label:
            self.new_goal_title_input.background_color = (1, 0.3, 0.3, 1)  # Light red
            return

        title_label.bind(size=title_label.setter("text_size"))
        subtitle_label = Label(
            text="Set goals and put in the hours",
            font_size='18sp',
            bold=True,
            color=(1, 1, 1, 1),
            halign="center",
            valign="middle",
        )
        title_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))


        subtitle_label.bind(size=subtitle_label.setter("text_size"))
        title_layout.add_widget(title_label)
        title_layout.add_widget(subtitle_label)
        content.add_widget(title_layout)

        # Area for adding new goal
        self.add_goal_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(10))
        self.new_goal_title_input = TextInput(
            hint_text="New goal title",
            multiline=False,
            font_size='16sp',
            size_hint_x=0.6,
        )
        self.new_goal_time_input = TextInput(
            hint_text="Goal time (min)",
            multiline=False,
            font_size='16sp',
            size_hint_x=0.3,
            input_filter="int",
        )
        self.btn_add_goal = RoundedButton(
            text="Add Goal",
            background_color=(0.2, 0.6, 0.8, 1),
            size_hint_x=0.1,
            on_press=self.add_new_goal,
            height=dp(40),
        )
        self.add_goal_layout.add_widget(self.new_goal_title_input)
        self.add_goal_layout.add_widget(self.new_goal_time_input)
        self.add_goal_layout.add_widget(self.btn_add_goal)
        content.add_widget(self.add_goal_layout)

        # Scroll area for goals
        scroll = ScrollView()
        self.goals_layout = BoxLayout(orientation="vertical", spacing=12, size_hint_y=None)
        self.goals_layout.bind(minimum_height=self.goals_layout.setter("height"))
        scroll.add_widget(self.goals_layout)
        content.add_widget(scroll)

        main_layout.add_widget(content)
        self.add_widget(main_layout)
        self.goal_items = []
        self.goals_data = self.load_goals()
        self.goals_data.sort(key=lambda g: g["time_done"] / g["time_goal"] if g["time_goal"] > 0 else 0, reverse=True)
        self.load_goals_to_ui()

        self.goal_items = []
        # Load goals data from file or start with defaults
        self.goals_data = self.load_goals()
        self.goals_data.sort(key=lambda g: g["time_done"] / g["time_goal"] if g["time_goal"] > 0 else 0, reverse=True)

        self.load_goals_to_ui()

    def _init_db(self):
        """Creates the goals table if it doesn't exist."""
        conn = sqlite3.connect("pomopy.db")
        cursor = conn.cursor()
        cursor.execute("\n"
                       "            CREATE TABLE IF NOT EXISTS daily_goals (\n"
                       "                id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
                       "                title TEXT UNIQUE,\n"
                       "                time_done INTEGER DEFAULT 0,\n"
                       "                time_goal INTEGER,\n"
                       "                color TEXT\n"
                       "            )\n"
                       "        ")
        conn.commit()
        conn.close()

    def load_goals(self):
        conn = sqlite3.connect("pomopy.db")
        cursor = conn.cursor()
        cursor.execute("SELECT title, time_done, time_goal, color FROM daily_goals")
        goals = [{"title": row[0], "time_done": row[1], "time_goal": row[2], "color": eval(row[3])} for row in
                 cursor.fetchall()]
        conn.close()
        return goals

    def save_goals(self):
        conn = sqlite3.connect("pomopy.db")
        cursor = conn.cursor()
        for goal in self.goals_data:
            cursor.execute("""
                INSERT INTO daily_goals (title, time_done, time_goal, color) 
                VALUES (?, ?, ?, ?) 
                ON CONFLICT(title) DO UPDATE SET time_done = excluded.time_done, time_goal = excluded.time_goal, color = excluded.color
            """, (goal["title"], goal["time_done"], goal["time_goal"], str(goal["color"])))
        conn.commit()
        conn.close()

    def load_goals_to_ui(self):
        self.goals_layout.clear_widgets()
        self.goal_items = []
        for goal in self.goals_data:
            item = DailyGoalItem(
                title=goal["title"],
                time_done=goal["time_done"],
                time_goal=goal["time_goal"],
                color=goal.get("color", [0.4667, 0.8667, 0.4667, 1]),  # Default color if not present
                update_callback=self.update_goal_data,
            )
            self.goals_layout.add_widget(item)
            self.goal_items.append(item)

    def add_new_goal(self, instance):
        title = self.new_goal_title_input.text.strip()
        time_goal_str = self.new_goal_time_input.text.strip()

        if not title:
            print("Goal title cannot be empty!")
            return

        try:
            time_goal = int(time_goal_str)
            if time_goal < 0:
                time_goal = 0
        except ValueError:
            print("Invalid time goal input. Setting to 0.")
            time_goal = 0

        conn = sqlite3.connect("pomopy.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO daily_goals (title, time_done, time_goal, color)
            VALUES (?, ?, ?, ?)
        """, (title, 0, time_goal, str([0.4667, 0.8667, 0.4667, 1])))

        conn.commit()
        conn.close()

        self.goals_data = self.load_goals()
        self.load_goals_to_ui()  # Refresh the UI
        self.new_goal_title_input.text = ""
        self.new_goal_time_input.text = ""

    def update_goal_data(self):
        # This method is called by DailyGoalItem when its data changes (e.g., time_done, title, goal)
        updated_goals_data = []
        for item in self.goal_items:
            if item.parent:
                updated_goals_data.append(
                    {
                        "title": item.title,
                        "time_done": item.time_done,
                        "time_goal": item.time_goal,
                        "color": item.color,
                    }
                )
        self.goals_data = updated_goals_data
        self.save_goals()

    def on_timer_complete(self):
        print("Timer completed. Saving session...")
        self.save_session()
        self.manager.current = "history"


class PomopyApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(WelcomeScreen(name="welcome"))
        self.sm.add_widget(MainScreen(name="main"))
        self.sm.add_widget(TimerScreen(name="timer"))
        self.sm.add_widget(HistoryScreen(name="history"))
        self.sm.add_widget(DailyGoalsScreen(name="dailygoals"))
        return self.sm


if __name__ == "__main__":


    PomopyApp().run()