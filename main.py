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

TICKERS_URL = "https://fx-api.gateio.ws/api/v4/futures/usdt/tickers"
KLINE_URL = "https://fx-api.gateio.ws/api/v4/futures/usdt/candlesticks"

REFRESH_TIME = 10
MIN_VOLUME_USDT = 1_000_000


def format_price(value):
    try:
        value = float(value)
        if value >= 1:
            return f"{value:.4f}"
        else:
            return f"{value:.8f}".rstrip("0").rstrip(".")
    except:
        return str(value)


def format_volume(value):
    try:
        value = float(value)
        if value >= 1_000_000:
            return f"{value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"{value/1_000:.2f}K"
        else:
            return f"{value:.2f}"
    except:
        return "0"


def calculate_rsi(closes, period=14):
    if len(closes) < period + 1:
        return None

    gains, losses = [], []

    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


class LeftLabel(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault("halign", "left")
        super().__init__(**kwargs)
        self.bind(size=self.update)

    def update(self, *args):
        self.text_size = (self.width, None)


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        Window.clearcolor = (0, 0, 0, 1)

        scroll = ScrollView()
        self.add_widget(scroll)

        self.content = GridLayout(cols=1, spacing=dp(10), padding=dp(15), size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))
        scroll.add_widget(self.content)

        self.title = LeftLabel(text="SHORT RADAR", font_size="26sp", size_hint_y=None, height=dp(50))
        self.content.add_widget(self.title)

        self.status = LeftLabel(text="Yükleniyor...", font_size="18sp", size_hint_y=None, height=dp(40))
        self.content.add_widget(self.status)

        self.short_labels = []
        for _ in range(3):
            lbl = LeftLabel(text="-", font_size="18sp", size_hint_y=None, height=dp(50))
            self.short_labels.append(lbl)
            self.content.add_widget(lbl)

        self.title2 = LeftLabel(text="Gate.io Vadeli En Çok Yükselenler", font_size="22sp",
                                size_hint_y=None, height=dp(50))
        self.content.add_widget(self.title2)

        self.movers = []
        for _ in range(10):
            lbl = LeftLabel(text="...", font_size="18sp", size_hint_y=None, height=dp(60))
            self.movers.append(lbl)
            self.content.add_widget(lbl)

        self.footer = LeftLabel(text="", font_size="16sp", size_hint_y=None, height=dp(40))
        self.content.add_widget(self.footer)

        Clock.schedule_once(self.update_data, 1)
        Clock.schedule_interval(self.update_data, REFRESH_TIME)

    def get_rsi(self, contract):
        try:
            params = {"contract": contract, "interval": "1h", "limit": 30}
            data = requests.get(KLINE_URL, params=params, timeout=8).json()
            closes = [float(x[2]) for x in data]
            return calculate_rsi(closes)
        except:
            return None

    def update_data(self, dt):
        try:
            data = requests.get(TICKERS_URL, timeout=10).json()

            coins = []
            for item in data:
                c = item.get("contract", "")
                if not c.endswith("_USDT"):
                    continue

                try:
                    price = float(item["last"])
                    change = float(item["change_percentage"])
                except:
                    continue

                volume = float(item.get("volume_24h_quote", 0))

                if volume < MIN_VOLUME_USDT:
                    continue

                coins.append({
                    "c": c,
                    "p": price,
                    "ch": change,
                    "v": volume
                })

            coins.sort(key=lambda x: x["ch"], reverse=True)
            top = coins[:10]

            # movers
            for i, lbl in enumerate(self.movers):
                if i < len(top):
                    coin = top[i]
                    lbl.text = f"{i+1}. {coin['c']}  {format_price(coin['p'])}  %{coin['ch']:.2f}\nHacim: {format_volume(coin['v'])}"
                else:
                    lbl.text = "-"

            # SHORT (çok hafif)
            shorts = []
            for coin in top[:3]:
                rsi = self.get_rsi(coin["c"])
                if rsi and rsi >= 80:
                    shorts.append((coin, rsi))

            if shorts:
                self.status.text = f"{len(shorts)} short adayı"
                for i, lbl in enumerate(self.short_labels):
                    if i < len(shorts):
                        coin, rsi = shorts[i]
                        lbl.text = f"{coin['c']}  RSI:{rsi:.1f}"
                    else:
                        lbl.text = "-"
            else:
                self.status.text = "Şu an short adayı yok"
                for lbl in self.short_labels:
                    lbl.text = "-"

            self.footer.text = datetime.now().strftime("%H:%M:%S")

        except:
            self.status.text = "Veri çekme hatası"
            for lbl in self.movers:
                lbl.text = "HATA"


class MyApp(App):
    def build(self):
        return MainLayout()


MyApp().run()
