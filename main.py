import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
import threading

COINS = ["BTCUSDT", "ETHUSDT", "ARBUSDT"]

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.labels = {}

        for coin in COINS:
            lbl = Label(text=f"{coin} yükleniyor...")
            self.labels[coin] = lbl
            self.add_widget(lbl)

        threading.Thread(target=self.update_data).start()

    def update_data(self):
        try:
            url = "https://api.binance.com/api/v3/ticker/price"
            data = requests.get(url, timeout=10).json()

            prices = {item["symbol"]: item["price"] for item in data}

            for coin in COINS:
                price = prices.get(coin, "yok")

                Clock.schedule_once(lambda dt, c=coin, p=price: self.update_label(c, p))

        except Exception as e:
            print("HATA:", e)

    def update_label(self, coin, price):
        self.labels[coin].text = f"{coin} Fiyat: {price}"

class MyApp(App):
    def build(self):
        return MainLayout()

MyApp().run()
