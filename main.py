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

        self.update_event = None

        self.scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
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

        self.filter_info_label = LeftLabel(
            text=f"Filtre: Hacim >= {format_volume(MIN_VOLUME_USDT)}",
            font_size="16sp",
            size_hint_y=None,
            height=dp(30)
        )
        self.content.add_widget(self.filter_info_label)

        self.movers_labels = []
        for _ in range(10):
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

        Clock.schedule_once(self.update_data, 1)
        self.update_event = Clock.schedule_interval(self.update_data, REFRESH_TIME)

    def stop_updates(self):
        if self.update_event is not None:
            self.update_event.cancel()
            self.update_event = None

    def get_rsi(self, contract):
        try:
            params = {
                "contract": contract,
                "interval": "1h",
                "limit": 30
            }
            res = requests.get(KLINE_URL, params=params, timeout=8)
            res.raise_for_status()
            data = res.json()

            closes = []
            for candle in data:
                try:
                    closes.append(float(candle[2]))
                except:
                    continue

            if not closes:
                return None

            return calculate_rsi(closes)
        except:
            return None

    def update_data(self, dt):
        try:
            response = requests.get(TICKERS_URL, timeout=10)
            response.raise_for_status()
            data = response.json()

            movers = []
            for item in data:
                contract = item.get("contract", "")
                if not contract.endswith("_USDT"):
                    continue

                try:
                    change_val = float(item.get("change_percentage", 0))
                    last_val = float(item.get("last", 0))
                except:
                    continue

                volume_val = 0.0
                for key in ["volume_24h_quote", "volume_24h_settle", "volume_24h"]:
                    try:
                        raw = item.get(key, 0)
                        if raw is not None:
                            volume_val = float(raw)
                            if volume_val > 0:
                                break
                    except:
                        continue

                funding_val = 0.0
                try:
                    funding_val = float(item.get("funding_rate", 0))
                except:
                    funding_val = 0.0

                if volume_val < MIN_VOLUME_USDT:
                    continue

                movers.append({
                    "contract": contract,
                    "last": last_val,
                    "change": change_val,
                    "volume": volume_val,
                    "funding": funding_val
                })

            movers.sort(key=lambda x: x["change"], reverse=True)
            top_10 = movers[:10]

            if top_10:
                for i, lbl in enumerate(self.movers_labels):
                    if i < len(top_10):
                        coin = top_10[i]
                        lbl.text = (
                            f"{i + 1}. {coin['contract']}   "
                            f"Fiyat: {format_price(coin['last'])}   "
                            f"%{coin['change']:.2f}\n"
                            f"Hacim: {format_volume(coin['volume'])}   "
                            f"Funding: {format_funding(coin['funding'])}"
                        )
                    else:
                        lbl.text = "-"
            else:
                self.movers_labels[0].text = "Filtreye uyan coin bulunamadı"
                for lbl in self.movers_labels[1:]:
                    lbl.text = "-"

            short_candidates = []
            scan_list = movers[:3]

            for coin in scan_list:
                rsi = self.get_rsi(coin["contract"])
                if rsi is None:
                    continue

                if rsi >= 80:
                    short_candidates.append({
                        "contract": coin["contract"],
                        "last": coin["last"],
                        "change": coin["change"],
                        "volume": coin["volume"],
                        "funding": coin["funding"],
                        "rsi": rsi
                    })

                if len(short_candidates) >= 3:
                    break

            if short_candidates:
                self.short_status_label.text = f"{len(short_candidates)} short adayı bulundu"
                for i, lbl in enumerate(self.short_labels):
                    if i < len(short_candidates):
                        coin = short_candidates[i]
                        lbl.text = (
                            f"{i + 1}. {coin['contract']}   "
                            f"Fiyat: {format_price(coin['last'])}   "
                            f"%{coin['change']:.2f}\n"
                            f"RSI: {coin['rsi']:.1f}   "
                            f"Hacim: {format_volume(coin['volume'])}   "
                            f"Funding: {format_funding(coin['funding'])}"
                        )
                    else:
                        lbl.text = "-"
            else:
                self.short_status_label.text = "Şu an short adayı yok"
                for lbl in self.short_labels:
                    lbl.text = "-"

            self.footer_label.text = (
                f"Son güncelleme: {datetime.now().strftime('%H:%M:%S')}   "
                f"Yenileme: {REFRESH_TIME} sn"
            )

        except Exception as e:
            self.short_status_label.text = "Veri çekme hatası"
            for lbl in self.short_labels:
                lbl.text = "HATA"
            for lbl in self.movers_labels:
                lbl.text = "HATA"
            self.footer_label.text = f"Son hata: {str(e)}"


class MyApp(App):
    def build(self):
        self.root_layout = MainLayout()
        Window.bind(on_keyboard=self.on_back_button)
        return self.root_layout

    def rebuild_ui(self):
        try:
            if hasattr(self, "root_layout") and self.root_layout:
                self.root_layout.stop_updates()
        except:
            pass

        new_layout = MainLayout()

        try:
            self.root.clear_widgets()
            self.root.add_widget(new_layout)
            self.root_layout = new_layout
        except:
            self.root_layout = new_layout
            return new_layout

    def on_pause(self):
        return True

    def on_resume(self):
        Clock.schedule_once(lambda dt: self.rebuild_ui(), 0.2)
        return True

    def on_back_button(self, window, key, *args):
        if key == 27:
            self.stop()
            return True
        return False


MyApp().run()
