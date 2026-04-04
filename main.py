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
RSI_REFRESH_TIME = 45
MIN_VOLUME_USDT = 1_000_000


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


def get_change_color(change):
    try:
        value = float(change)
        if value >= 50:
            return "00ff66"
        elif value >= 0:
            return "ffd54a"
        else:
            return "ff4d4d"
    except:
        return "ffffff"


def get_funding_color(funding):
    try:
        value = float(funding)
        if value < 0:
            return "ff4d4d"
        else:
            return "00ff66"
    except:
        return "ffffff"


def get_rsi_color(rsi):
    try:
        value = float(rsi)
        if value >= 80:
            return "ff4d4d"
        elif value >= 70:
            return "ffd54a"
        else:
            return "00ff66"
    except:
        return "ffffff"


def parse_candle_close(candle):
    try:
        if isinstance(candle, dict):
            if "c" in candle:
                return float(candle["c"])
            if "close" in candle:
                return float(candle["close"])
            return None

        if isinstance(candle, (list, tuple)):
            # Gate futures tipik sıra: [t, v, c, h, l, o, sum]
            if len(candle) >= 3:
                return float(candle[2])

        return None
    except:
        return None


def parse_candle_open_close(candle):
    try:
        if isinstance(candle, dict):
            if "o" in candle and "c" in candle:
                return float(candle["o"]), float(candle["c"])
            if "open" in candle and "close" in candle:
                return float(candle["open"]), float(candle["close"])
            return None, None

        if isinstance(candle, (list, tuple)):
            # Gate futures tipik sıra: [t, v, c, h, l, o, sum]
            if len(candle) >= 6:
                open_price = float(candle[5])
                close_price = float(candle[2])
                return open_price, close_price

        return None, None
    except:
        return None, None


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
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        })

        self.update_event = None
        self.is_updating = False
        self.rsi_cache = {}
        self.rsi_last_update = 0

        self.scroll = ScrollView(size_hint=(1, 1))
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

        self.short_box = GridLayout(
            cols=1,
            spacing=dp(6),
            size_hint_y=None
        )
        self.short_box.bind(minimum_height=self.short_box.setter("height"))
        self.content.add_widget(self.short_box)

        self.movers_title_label = LeftLabel(
            text="Gate.io Vadeli En Çok Yükselenler",
            font_size="22sp",
            bold=True,
            size_hint_y=None,
            height=dp(42)
        )
        self.content.add_widget(self.movers_title_label)

        self.movers_labels = []
        for _ in range(10):
            lbl = LeftLabel(
                text="Yükleniyor...",
                font_size="18sp",
                size_hint_y=None,
                height=dp(180),
                markup=True
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

        Clock.schedule_once(self.update_data, 1)
        self.update_event = Clock.schedule_interval(self.update_data, REFRESH_TIME)

    def fetch_candles(self, contract, limit=30):
        try:
            params = {
                "contract": contract,
                "interval": "1h",
                "limit": limit
            }
            response = self.session.get(KLINE_URL, params=params, timeout=6)
            data = response.json()

            if isinstance(data, list):
                return data

            return []
        except:
            return []

    def get_rsi(self, contract):
        candles = self.fetch_candles(contract, limit=30)
        if not candles:
            return None

        closes = []
        for candle in candles:
            close_price = parse_candle_close(candle)
            if close_price is not None:
                closes.append(close_price)

        if len(closes) < 15:
            return None

        return calculate_rsi(closes)

    def is_last_candle_red(self, contract):
        candles = self.fetch_candles(contract, limit=2)
        if not candles:
            return False

        last = candles[-1]
        open_price, close_price = parse_candle_open_close(last)

        if open_price is None or close_price is None:
            return False

        return close_price < open_price

    def refresh_rsi_cache_if_needed(self, top_coins, now_ts):
        if (now_ts - self.rsi_last_update) < RSI_REFRESH_TIME and self.rsi_cache:
            return

        new_cache = {}
        for coin in top_coins:
            new_cache[coin["c"]] = self.get_rsi(coin["c"])

        self.rsi_cache = new_cache
        self.rsi_last_update = now_ts

    def update_data(self, dt):
        if self.is_updating:
            return

        self.is_updating = True

        try:
            now_ts = Clock.get_boottime()

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
            top = coins[:10]

            self.refresh_rsi_cache_if_needed(top, now_ts)

            for i, lbl in enumerate(self.movers_labels):
                if i < len(top):
                    coin = top[i]
                    change_color = get_change_color(coin["ch"])
                    funding_color = get_funding_color(coin["f"])

                    rsi_value = self.rsi_cache.get(coin["c"])
                    if rsi_value is None:
                        rsi_text = "-"
                        rsi_color = "ffffff"
                    else:
                        rsi_text = f"{rsi_value:.1f}"
                        rsi_color = get_rsi_color(rsi_value)

                    lbl.text = (
                        f"[b][color=ffffff]{i+1}. {coin['c']}[/color][/b]\n"
                        f"[color=cccccc]Fiyat: {format_price(coin['p'])}[/color]\n"
                        f"[color={change_color}]Değişim: %{coin['ch']:.2f}[/color]\n"
                        f"[color=cccccc]Hacim: {format_volume(coin['v'])}[/color]\n"
                        f"[color={funding_color}]Funding: {format_funding(coin['f'])}[/color]\n"
                        f"[color={rsi_color}]RSI (1s): {rsi_text}[/color]"
                    )
                else:
                    lbl.text = "-"

            shorts = []
            for coin in top[:3]:
                rsi = self.rsi_cache.get(coin["c"])
                red = self.is_last_candle_red(coin["c"])

                if rsi is not None and rsi >= 80 and red:
                    shorts.append((coin, rsi))

            self.short_box.clear_widgets()

            if shorts:
                self.short_status_label.text = f"{len(shorts)} SHORT BAŞLANGICI 🔥"

                for coin, rsi in shorts:
                    lbl = LeftLabel(
                        text=(
                            f"{coin['c']}\n"
                            f"RSI: {rsi:.1f}\n"
                            f"Funding: {format_funding(coin['f'])}"
                        ),
                        font_size="18sp",
                        size_hint_y=None,
                        height=dp(70)
                    )
                    self.short_box.add_widget(lbl)
            else:
                self.short_status_label.text = "Şu an short başlangıcı yok"

            self.footer_label.text = (
                f"Son güncelleme: {datetime.now().strftime('%H:%M:%S')} | "
                f"RSI yenileme: {RSI_REFRESH_TIME}s"
            )

        except:
            self.short_status_label.text = "Veri çekme hatası"
            self.short_box.clear_widgets()
            for lbl in self.movers_labels:
                lbl.text = "HATA"

        finally:
            self.is_updating = False


class MyApp(App):
    def build(self):
        return MainLayout()


MyApp().run()
