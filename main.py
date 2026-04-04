import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock

TICKERS_URL = "https://fx-api.gateio.ws/api/v4/futures/usdt/tickers"
KLINE_URL = "https://fx-api.gateio.ws/api/v4/futures/usdt/candlesticks"

REFRESH_TIME = 10  # saniye


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
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=15, **kwargs)

        self.title = Label(text="SHORT RADAR 🚨", font_size=24)
        self.add_widget(self.title)

        self.labels = []
        for _ in range(10):
            lbl = Label(text="", font_size=18)
            self.labels.append(lbl)
            self.add_widget(lbl)

        Clock.schedule_interval(self.update_data, REFRESH_TIME)

    def get_rsi(self, contract):
        try:
            params = {
                "contract": contract,
                "interval": "1h",
                "limit": 50
            }
            res = requests.get(KLINE_URL, params=params, timeout=10)
            data = res.json()

            closes = [float(candle[2]) for candle in data]  # close price
            return calculate_rsi(closes)

        except:
            return None

    def update_data(self, dt):
        try:
            res = requests.get(TICKERS_URL, timeout=10)
            data = res.json()

            coins = []
            for item in data:
                contract = item.get("contract", "")
                if not contract.endswith("_USDT"):
                    continue

                try:
                    change = float(item.get("change_percentage", 0))
                    last = float(item.get("last", 0))
                except:
                    continue

                coins.append({
                    "contract": contract,
                    "change": change,
                    "last": last
                })

            # en çok yükselenleri al
            coins.sort(key=lambda x: x["change"], reverse=True)
            top = coins[:15]

            results = []

            for coin in top:
                rsi = self.get_rsi(coin["contract"])

                if rsi is None:
                    continue

                if rsi >= 80:
                    results.append({
                        "contract": coin["contract"],
                        "price": coin["last"],
                        "change": coin["change"],
                        "rsi": rsi
                    })

                if len(results) >= 10:
                    break

            # ekrana yaz
            if not results:
                self.title.text = "SHORT YOK ❌"
                for lbl in self.labels:
                    lbl.text = ""
                return

            self.title.text = "SHORT ADAYLARI 🚨"

            for i, lbl in enumerate(self.labels):
                if i < len(results):
                    c = results[i]
                    lbl.text = f"{c['contract']} | {c['price']} | %{c['change']:.2f} | RSI {c['rsi']:.1f}"
                else:
                    lbl.text = ""

        except:
            self.title.text = "HATA ❌"
            for lbl in self.labels:
                lbl.text = ""


class MyApp(App):
    def build(self):
        return MainLayout()


MyApp().run()
