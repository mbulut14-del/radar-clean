import threading
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
import requests


API_BASE = "https://api.gateio.ws/api/v4"


def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def calculate_rsi(closes, period=14):
    if len(closes) < period + 1:
        return None

    gains = []
    losses = []

    for i in range(1, period + 1):
        diff = closes[i] - closes[i - 1]
        if diff >= 0:
            gains.append(diff)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(abs(diff))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    if avg_loss == 0:
        return 100.0

    for i in range(period + 1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gain = max(diff, 0.0)
        loss = abs(min(diff, 0.0))

        avg_gain = ((avg_gain * (period - 1)) + gain) / period
        avg_loss = ((avg_loss * (period - 1)) + loss) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def extract_close(item):
    if isinstance(item, dict):
        for key in ["c", "close", "last"]:
            if key in item:
                return safe_float(item[key])
    if isinstance(item, list) and len(item) >= 6:
        return safe_float(item[5])
    return None


class MainApp(App):
    def build(self):
        self.root_layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        self.title = Label(
            text="Hype Short Radar",
            font_size=28,
            size_hint=(1, 0.15),
        )

        self.status = Label(
            text="Gate futures hype coinleri yükleniyor...",
            font_size=16,
            size_hint=(1, 0.1),
        )

        self.coin_labels = [
            Label(text="1. veri bekleniyor...", font_size=20),
            Label(text="2. veri bekleniyor...", font_size=20),
            Label(text="3. veri bekleniyor...", font_size=20),
        ]

        self.root_layout.add_widget(self.title)
        self.root_layout.add_widget(self.status)

        for label in self.coin_labels:
            self.root_layout.add_widget(label)

        threading.Thread(target=self.load_data, daemon=True).start()
        return self.root_layout

    def load_data(self):
        try:
            tickers = self.fetch_hype_futures()
            results = []

            for ticker in tickers[:3]:
                contract = ticker["contract"]
                price = ticker["price"]
                change = ticker["change"]
                rsi = self.fetch_rsi(contract)

                if rsi is None:
                    rsi_text = "RSI: hesaplanamadı"
                else:
                    rsi_text = f"RSI: {rsi:.1f}"

                line = f"{contract}   Fiyat: {price:.6f}   24s: {change:.2f}%   {rsi_text}"
                results.append(line)

            Clock.schedule_once(lambda dt: self.update_ui(results, None), 0)

        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_ui([], str(e)), 0)

    def fetch_hype_futures(self):
        url = f"{API_BASE}/futures/usdt/tickers"
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()

        filtered = []
        excluded = {"BTC_USDT", "ETH_USDT"}

        for item in data:
            contract = item.get("contract", "")
            if not contract.endswith("_USDT"):
                continue
            if contract in excluded:
                continue

            quote_volume = safe_float(
                item.get("volume_24h_quote", item.get("volume_24h_usdt", item.get("volume_24h", 0)))
            )
            if quote_volume < 1000000:
                continue

            change = safe_float(item.get("change_percentage", item.get("change_24h", 0)))
            last_price = safe_float(item.get("last", 0))

            filtered.append(
                {
                    "contract": contract,
                    "price": last_price,
                    "change": change,
                    "quote_volume": quote_volume,
                }
            )

        filtered.sort(key=lambda x: (abs(x["change"]), x["quote_volume"]), reverse=True)
        return filtered

    def fetch_rsi(self, contract):
        url = f"{API_BASE}/futures/usdt/candlesticks"
        params = {
            "contract": contract,
            "interval": "1h",
            "limit": 100,
        }

        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        candles = response.json()

        closes = []
        for candle in candles:
            close_value = extract_close(candle)
            if close_value is not None:
                closes.append(close_value)

        if len(closes) < 20:
            return None

        return calculate_rsi(closes, period=14)

    def update_ui(self, lines, error_text):
        if error_text:
            self.status.text = f"Hata: {error_text}"
            return

        self.status.text = "Gate futures hype coinleri yüklendi"

        for i, label in enumerate(self.coin_labels):
            if i < len(lines):
                label.text = lines[i]
            else:
                label.text = "-"


if __name__ == "__main__":
    MainApp().run()
