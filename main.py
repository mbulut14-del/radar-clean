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
MAX_MOVERS = 10
MAX_SHORT_SCAN = 5


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

    gains = []
    losses = []

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


class LeftLabel(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        super().__init__(**kwargs)
        self.bind(size=self._update_text_size)

    def _update_text_size(self, *args):
        self.text_size = (self.width, None)


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        Window.clearcolor = (0, 0, 0, 1)

        self.session = requests.Session()
        self.update_event = None
        self.is_updating = False

        self.scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(6),
            scroll_type=["bars", "content"]
        )
        self.add_widget(self.scroll)

        self.content = GridLayout(
            cols=1,
            spacing=dp(12),
            padding=dp(16),
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        self.scroll.add_widget(self.content)

        self.title_label = LeftLabel(
            text="SHORT RADAR",
            font_size="26sp",
            bold=True,
            size_hint_y=None,
            height=dp(46)
        )
        self.content.add_widget(self.title_label)

        self.short_status_label = LeftLabel(
            text="Yükleniyor...",
            font_size="18sp",
            size_hint_y=None,
            height=dp(34)
        )
        self.content.add_widget(self.short_status_label)

        self.short_labels = []
        for _ in range(3):
            lbl = LeftLabel(
                text="-",
                font_size="18sp",
                size_hint_y=None,
                height=dp(62)
            )
            self.short_labels.append(lbl)
            self.content.add_widget(lbl)

        self.movers_title_label = LeftLabel(
            text="Gate.io Vadeli En Çok Yükselenler",
            font_size="22sp",
            bold=True,
            size_hint_y=None,
            height=dp(42)
        )
        self.content.add_widget(self.movers_title_label)

        self.movers_labels = []
        for _ in range(MAX_MOVERS):
            lbl = LeftLabel(
                text="Yükleniyor...",
                font_size="18sp",
                size_hint_y=None,
                height=dp(72)
            )
            self.movers_labels.append(lbl)
            self.content.add_widget(lbl)

        self.footer_label = LeftLabel(
            text="Son güncelleme: -",
            font_size="16sp",
            size_hint_y=None,
            height=dp(34)
        )
        self.content.add_widget(self.footer_label)

        Clock.schedule_once(self.first_load, 0.3)
        self.update_event = Clock.schedule_interval(self.update_data, REFRESH_TIME)

    def first_load(self, dt):
        self.short_status_label.text = "Veriler yükleniyor..."
        self.footer_label.text = "Son güncelleme: yükleniyor..."
        self.update_data(0)

    def on_parent(self, *args):
        Clock.schedule_once(lambda dt: self.scroll.scroll_y.__class__, 0)

    def get_rsi(self, contract):
        try:
            params = {
                "contract": contract,
                "interval": "1h",
                "limit": 30
            }
            response = self.session.get(KLINE_URL, params=params, timeout=6)
            data = response.json()

            if not isinstance(data, list) or len(data) < 15:
                return None

            closes = [float(x[2]) for x in data]
            return calculate_rsi(closes)
        except:
            return None

    def is_last_candle_red(self, contract):
        try:
            params = {
                "contract": contract,
                "interval": "1h",
                "limit": 2
            }
            response = self.session.get(KLINE_URL, params=params, timeout=6)
            data = response.json()

            if not isinstance(data, list) or len(data) < 1:
                return False

            last = data[-1]
            open_price = float(last[1])
            close_price = float(last[2])

            return close_price < open_price
        except:
            return False

    def scan_short_candidates(self, top_coins):
        shorts = []

        # Önce daha mantıklı adayları tara:
        # güçlü yükseliş + pozitif funding öncelikli
        candidates = sorted(
            top_coins[:MAX_SHORT_SCAN],
            key=lambda x: (x["ch"], x["f"]),
            reverse=True
        )

        for coin in candidates:
            rsi = self.get_rsi(coin["c"])
            red = self.is_last_candle_red(coin["c"])

            if rsi is not None and rsi >= 80 and red:
                shorts.append((coin, rsi))

            if len(shorts) >= 3:
                break

        return shorts

    def update_data(self, dt):
        if self.is_updating:
            return

        self.is_updating = True

        try:
            response = self.session.get(TICKERS_URL, timeout=8)
            data = response.json()

            coins = []
            for item in data:
                c = item.get("contract", "")
                if not c.endswith("_USDT"):
                    continue

                try:
                    price = float(item["last"])
                    change = float(item["change_percentage"])
                    volume = float(item.get("volume_24h_quote", 0))
                    funding = float(item.get("funding_rate", 0))
                except:
                    continue

                if volume < MIN_VOLUME_USDT:
                    continue

                coins.append({
                    "c": c,
                    "p": price,
                    "ch": change,
                    "v": volume,
                    "f": funding
                })

            coins.sort(key=lambda x: x["ch"], reverse=True)
            top = coins[:MAX_MOVERS]

            for i, lbl in enumerate(self.movers_labels):
                if i < len(top):
                    coin = top[i]
                    lbl.text = (
                        f"{i + 1}. {coin['c']}  {format_price(coin['p'])}  %{coin['ch']:.2f}\n"
                        f"Hacim: {format_volume(coin['v'])}  Funding: {format_funding(coin['f'])}"
                    )
                else:
                    lbl.text = "-"

            shorts = self.scan_short_candidates(top)

            if shorts:
                self.short_status_label.text = f"{len(shorts)} SHORT BAŞLANGICI 🔥"
                for i, lbl in enumerate(self.short_labels):
                    if i < len(shorts):
                        coin, rsi = shorts[i]
                        lbl.text = (
                            f"{coin['c']}  RSI: {rsi:.1f}\n"
                            f"Funding: {format_funding(coin['f'])}"
                        )
                    else:
                        lbl.text = "-"
            else:
                self.short_status_label.text = "Şu an short başlangıcı yok"
                for lbl in self.short_labels:
                    lbl.text = "-"

            self.footer_label.text = f"Son güncelleme: {datetime.now().strftime('%H:%M:%S')}"

            # içerik boyu güncellensin, scroll düzgün çalışsın
            self.content.do_layout()
            self.scroll.do_layout()

        except:
            self.short_status_label.text = "Veri çekme hatası"
            for lbl in self.movers_labels:
                lbl.text = "HATA"
            self.footer_label.text = f"Son güncelleme: {datetime.now().strftime('%H:%M:%S')}"

        finally:
            self.is_updating = False


class MyApp(App):
    def build(self):
        return MainLayout()


MyApp().run()
