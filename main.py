from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class MainApp(App):
    def build(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        title = Label(text="Hype Short Radar", font_size=28)
        coin1 = Label(text="BTC/USDT   Fiyat: yükleniyor...   RSI: yükleniyor...")
        coin2 = Label(text="ETH/USDT   Fiyat: yükleniyor...   RSI: yükleniyor...")
        coin3 = Label(text="ARB/USDT   Fiyat: yükleniyor...   RSI: yükleniyor...")

        layout.add_widget(title)
        layout.add_widget(coin1)
        layout.add_widget(coin2)
        layout.add_widget(coin3)

        return layout


if __name__ == "__main__":
    MainApp().run()
