import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock

COINS = ["BTCUSDT", "ETHUSDT", "ARBUSDT"]

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.labels = {}

        for coin in COINS:
            lbl = Label(text=f"{coin} yükleniyor...")
            self.labels[coin] = lbl
            self.add_widget(lbl)

        # Direkt ana threadde çalıştır
        Clock.schedule_once(self.fetch_data, 1)

    def fetch_data(self, dt):
        try:
            url = "https://api.binance.com/api/v3/ticker/price"
            data = requests.get(url, timeout=10).json()

            prices = {item["symbol"]: item["price"] for item in data}

            for coin in COINS:
                price = prices.get(coin, "yok")
                self.labels[coin].text = f"{coin} Fiyat: {price}"

        except Exception as e:
            for coin in COINS:
                self.labels[coin].text = f"{coin} HATA"

class MyApp(App):
    def build(self):
        return MainLayout()

MyApp().run()
