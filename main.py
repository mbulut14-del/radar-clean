import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock

API_URL = "https://fx-api.gateio.ws/api/v4/futures/usdt/tickers"


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=20, **kwargs)

        self.status_label = Label(
            text="Vadeli coinler yükleniyor...",
            font_size=22
        )
        self.add_widget(self.status_label)

        self.coin_labels = []
        for _ in range(10):
            lbl = Label(
                text="",
                font_size=18
            )
            self.coin_labels.append(lbl)
            self.add_widget(lbl)

        Clock.schedule_once(self.fetch_data, 1)

    def fetch_data(self, dt):
        try:
            response = requests.get(API_URL, timeout=15)
            response.raise_for_status()
            data = response.json()

            filtered = []
            for item in data:
                contract = item.get("contract", "")

                if not contract.endswith("_USDT"):
                    continue

                change_raw = item.get("change_percentage", "0")
                last_raw = item.get("last", "0")

                try:
                    change_val = float(change_raw)
                    last_val = float(last_raw)
                except:
                    continue

                filtered.append({
                    "contract": contract,
                    "last": last_val,
                    "change": change_val
                })

            filtered.sort(key=lambda x: x["change"], reverse=True)
            top_10 = filtered[:10]

            self.status_label.text = "Gate.io Vadeli En Çok Yükselenler"

            for i, lbl in enumerate(self.coin_labels):
                if i < len(top_10):
                    coin = top_10[i]
                    lbl.text = f"{coin['contract']} | Fiyat: {coin['last']} | % {coin['change']:.2f}"
                else:
                    lbl.text = ""

        except Exception as e:
            self.status_label.text = "Veri çekme hatası"
            for lbl in self.coin_labels:
                lbl.text = "HATA"


class MyApp(App):
    def build(self):
        return MainLayout()


MyApp().run()
