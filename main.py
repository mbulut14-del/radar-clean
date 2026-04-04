import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock

TICKERS_URL = "https://fx-api.gateio.ws/api/v4/futures/usdt/tickers"
KLINE_URL = "https://fx-api.gateio.ws/api/v4/futures/usdt/candlesticks"
REFRESH_TIME = 10


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


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=10, **kwargs)

        self.title_label = Label(
            text="SHORT RADAR 🚨",
            font_size=24,
            size_hint_y=None,
            height=50
        )
        self.add_widget(self.title_label)

        self.short_status_label = Label(
            text="Short adayları kontrol ediliyor...",
            font_size=16,
            size_hint_y=None,
            height=35
        )
        self.add_widget(self.short_status_label)

        self.short_labels = []
        for _ in range(3):
            lbl = Label(
                text="-",
                font_size=16,
                size_hint_y=None,
                height=35
            )
            self.short_labels.append(lbl)
            self.add_widget(lbl)

        self.movers_title_label = Label(
            text="Gate.io Vadeli En Çok Yükselenler",
            font_size=20,
            size_hint_y=None,
            height=45
        )
        self.add_widget(self.movers_title_label)

        self.movers_labels = []
        for _ in range(10):
            lbl = Label(
                text="Yükleniyor...",
                font_size=16,
                size_hint_y=None,
                height=35
            )
            self.movers_labels.append(lbl)
            self.add_widget(lbl)

        Clock.schedule_once(self.update_data, 1)
        Clock.schedule_interval(self.update_data, REFRESH_TIME)

    def get_rsi(self, contract):
        try:
            params = {
                "contract": contract,
                "interval": "1h",
                "limit": 50
            }
            res = requests.get(KLINE_URL, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()

            closes = []
            for candle in data:
                try:
                    # Gate verisinde close değeri bazı cevaplarda index 2 olarak geliyor
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
            response = requests.get(TICKERS_URL, timeout=15)
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

                movers.append({
                    "contract": contract,
                    "last": last_val,
                    "change": change_val
                })

            movers.sort(key=lambda x: x["change"], reverse=True)
            top_10 = movers[:10]

            # ANA LİSTEYİ HER ZAMAN GÖSTER
            for i, lbl in enumerate(self.movers_labels):
                if i < len(top_10):
                    coin = top_10[i]
                    lbl.text = f"{coin['contract']} | Fiyat: {coin['last']} | % {coin['change']:.2f}"
                else:
                    lbl.text = "-"

            # SHORT ADAYLARI = TOP MOVER'LAR İÇİNDEN RSI 80+
            short_candidates = []
            scan_list = movers[:8]

            for coin in scan_list:
                rsi = self.get_rsi(coin["contract"])
                if rsi is None:
                    continue

                if rsi >= 80:
                    short_candidates.append({
                        "contract": coin["contract"],
                        "last": coin["last"],
                        "change": coin["change"],
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
                            f"{coin['contract']} | Fiyat: {coin['last']} | "
                            f"% {coin['change']:.2f} | RSI {coin['rsi']:.1f}"
                        )
                    else:
                        lbl.text = "-"
            else:
                self.short_status_label.text = "Şu an short adayı yok"
                self.short_labels[0].text = "-"
                self.short_labels[1].text = "-"
                self.short_labels[2].text = "-"

        except Exception:
            self.short_status_label.text = "Veri çekme hatası"
            for lbl in self.short_labels:
                lbl.text = "HATA"
            for lbl in self.movers_labels:
                lbl.text = "HATA"


class MyApp(App):
    def build(self):
        return MainLayout()


MyApp().run()
