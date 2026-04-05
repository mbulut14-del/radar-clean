import threading
import requests
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager, Screen

TICKERS_URL = "https://fx-api.gateio.ws/api/v4/futures/usdt/tickers"
KLINE_URL = "https://fx-api.gateio.ws/api/v4/futures/usdt/candlesticks"

REFRESH_TIME = 10
RSI_REFRESH_TIME = 45
MIN_VOLUME_USDT = 1_000_000


# ---------- helpers ----------

def format_price(value):
    try:
        value = float(value)
        if value >= 1000:
            return f"{value:,.2f}"
        elif value >= 1:
            return f"{value:,.4f}"
        else:
            return f"{value:.8f}".rstrip("0").rstrip(".")
    except:
        return str(value)


def format_volume(value):
    try:
        value = float(value)
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.2f}K"
        else:
            return f"{value:.2f}"
    except:
        return "0"


def format_funding(value):
    try:
        value = float(value) * 100
        return f"{value:.4f}%"
    except:
        return "-"


def calculate_rsi(closes, period=14):
    if len(closes) < period + 1:
        return None

    gains, losses = [], []

    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        if diff >= 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def get_change_color(change):
    try:
        value = float(change)
        if value >= 80:
            return "00ff88"
        elif value >= 30:
            return "35d07f"
        elif value >= 0:
            return "ffd54a"
        else:
            return "ff6666"
    except:
        return "ffffff"


def get_funding_color(funding):
    try:
        value = float(funding)
        return "ff6b6b" if value < 0 else "00ff88"
    except:
        return "ffffff"


def get_rsi_color(rsi):
    try:
        value = float(rsi)
        if value >= 85:
            return "ff4d4d"
        elif value >= 80:
            return "ff6a6a"
        elif value >= 70:
            return "ffd54a"
        else:
            return "00ff88"
    except:
        return "ffffff"


def parse_candle_close(candle):
    try:
        if isinstance(candle, dict):
            return float(candle.get("c") or candle.get("close"))
        if isinstance(candle, (list, tuple)) and len(candle) >= 3:
            return float(candle[2])
    except:
        pass
    return None


def parse_candle_open_close(candle):
    try:
        if isinstance(candle, dict):
            return float(candle.get("o")), float(candle.get("c"))
        if isinstance(candle, (list, tuple)) and len(candle) >= 6:
            return float(candle[5]), float(candle[2])
    except:
        pass
    return None, None


def calculate_short_score(coin, rsi, red):
    score = 0

    if rsi is not None:
        if rsi >= 90: score += 50
        elif rsi >= 85: score += 40
        elif rsi >= 80: score += 30
        elif rsi >= 75: score += 20
        elif rsi >= 70: score += 10

    funding_pct = float(coin["f"]) * 100
    if funding_pct >= 1.0: score += 25
    elif funding_pct >= 0.3: score += 18
    elif funding_pct > 0: score += 10
    elif funding_pct <= -0.5: score -= 8

    change_pct = float(coin["ch"])
    if change_pct >= 200: score += 25
    elif change_pct >= 120: score += 18
    elif change_pct >= 80: score += 12
    elif change_pct >= 50: score += 8

    if red:
        score += 20

    return score


# ---------- UI helpers ----------

class LeftLabel(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        kwargs.setdefault("color", (1, 1, 1, 1))
        super().__init__(**kwargs)
        self.bind(size=self._update)

    def _update(self, *args):
        self.text_size = (self.width, None)


# 🔥 TEXT FIX burada (tek satır + taşma yok)
class CoinLabel(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault("color", (1, 0.35, 0.35, 1))
        kwargs.setdefault("bold", True)
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        kwargs.setdefault("font_size", "20sp")
        kwargs.setdefault("shorten", True)
        kwargs.setdefault("shorten_from", "right")
        super().__init__(**kwargs)
        self.bind(size=self._update)

    def _update(self, *args):
        self.text_size = (self.width, None)


# 🔥 SCORE CIRCLE
class ScoreCircle(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault("text", "0")
        kwargs.setdefault("bold", True)
        kwargs.setdefault("font_size", "18sp")
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("size", (dp(48), dp(48)))
        kwargs.setdefault("halign", "center")
        kwargs.setdefault("valign", "middle")
        super().__init__(**kwargs)

        from kivy.graphics import Color, Ellipse
        with self.canvas.before:
            Color(0.15, 0.2, 0.15, 0.4)
            self.circle = Ellipse(pos=self.pos, size=self.size)

        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.circle.pos = self.pos
        self.circle.size = self.size


class CardButton(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(98))
        kwargs.setdefault("padding", [dp(10), dp(6), dp(10), dp(6)])
        super().__init__(**kwargs)

        from kivy.graphics import Color, RoundedRectangle
        with self.canvas.before:
            Color(0.05, 0.06, 0.10, 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[18])

        self.bind(pos=self._update, size=self._update)

    def _update(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


# ---------- MAIN SCREEN ----------

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical")
        self.add_widget(root)

        scroll = ScrollView()
        root.add_widget(scroll)

        self.content = GridLayout(cols=1, spacing=dp(14), padding=dp(14), size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))
        scroll.add_widget(self.content)

        self.content.add_widget(LeftLabel(text="SHORT RADAR", font_size="24sp", bold=True, size_hint_y=None, height=dp(40)))
        self.content.add_widget(LeftLabel(text="EN GÜÇLÜ SHORT ADAYI", font_size="20sp", bold=True, size_hint_y=None, height=dp(36)))

        self.hero = LeftLabel(text="Yükleniyor...", font_size="22sp", size_hint_y=None, height=dp(120))
        self.content.add_widget(self.hero)

        self.content.add_widget(LeftLabel(text="Gate.io Vadeli En Çok Yükselenler", font_size="20sp", bold=True, size_hint_y=None, height=dp(40)))

        self.cards = []
        for _ in range(10):
            card = CardButton()
            row = BoxLayout(orientation="horizontal", spacing=dp(10))

            rank = Label(text="-", size_hint_x=None, width=dp(40))
            coin = CoinLabel(text="...")
            score = ScoreCircle(text="0")

            row.add_widget(rank)
            row.add_widget(coin)
            row.add_widget(score)

            card.add_widget(row)

            card.rank = rank
            card.coin = coin
            card.score = score

            self.cards.append(card)
            self.content.add_widget(card)

    def update_ui(self):
        app = App.get_running_app()
        for i, coin in enumerate(app.top_coins):
            c = self.cards[i]
            c.rank.text = str(i+1)
            c.coin.text = coin["c"]

            rsi = app.rsi_cache.get(coin["c"])
            score = calculate_short_score(coin, rsi, False) if rsi else 0
            c.score.text = str(score)


# ---------- APP ----------

class RadarApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)

        self.session = requests.Session()
        self.top_coins = []
        self.rsi_cache = {}

        self.sm = ScreenManager()
        self.main = MainScreen(name="main")
        self.sm.add_widget(self.main)

        Clock.schedule_interval(lambda dt: self.update_data(), 5)

        return self.sm

    def update_data(self):
        try:
            data = self.session.get(TICKERS_URL).json()
            coins = []

            for i in data[:10]:
                coins.append({
                    "c": i["contract"],
                    "ch": float(i["change_percentage"]),
                    "f": float(i.get("funding_rate", 0))
                })

            self.top_coins = coins
            self.main.update_ui()

        except:
            pass


RadarApp().run()
