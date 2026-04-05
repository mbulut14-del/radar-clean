from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, DictProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager

KV = """
#:import dp kivy.metrics.dp

<ClickCard>:
    size_hint_y: None
    height: dp(104)
    padding: dp(12)
    spacing: dp(12)

    canvas.before:
        Color:
            rgba: 0.07, 0.16, 0.35, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [18, 18, 18, 18]

    BoxLayout:
        size_hint_x: None
        width: dp(64)
        padding: dp(8)

        canvas.before:
            Color:
                rgba: 0.15, 0.65, 1.0, 0.25
            Ellipse:
                pos: self.x - dp(6), self.y - dp(6)
                size: self.width + dp(12), self.height + dp(12)
            Color:
                rgba: 0.15, 0.65, 1.0, 1
            Ellipse:
                pos: self.pos
                size: self.size
            Color:
                rgba: 0.05, 0.05, 0.10, 1
            Ellipse:
                pos: self.x + dp(8), self.y + dp(8)
                size: self.width - dp(16), self.height - dp(16)

        Label:
            text: root.rank_text
            bold: True
            font_size: "20sp"
            color: 1, 1, 1, 1

    BoxLayout:
        orientation: "vertical"
        spacing: dp(2)

        Label:
            text: root.coin_text
            font_size: "20sp"
            bold: True
            color: 1, 0.35, 0.35, 1
            size_hint_y: None
            height: dp(34)
            halign: "left"
            valign: "middle"
            text_size: self.size

        Label:
            text: root.change_text
            font_size: "18sp"
            bold: True
            color: 0.18, 0.95, 0.65, 1
            size_hint_y: None
            height: dp(28)
            halign: "left"
            valign: "middle"
            text_size: self.size

    BoxLayout:
        size_hint_x: None
        width: dp(88)
        padding: dp(6)

        canvas.before:
            Color:
                rgba: root.glow_r, root.glow_g, root.glow_b, 0.22
            Ellipse:
                pos: self.x - dp(8), self.y - dp(8)
                size: self.width + dp(16), self.height + dp(16)
            Color:
                rgba: root.glow_r, root.glow_g, root.glow_b, 1
            Ellipse:
                pos: self.pos
                size: self.size
            Color:
                rgba: 0.05, 0.05, 0.10, 1
            Ellipse:
                pos: self.x + dp(12), self.y + dp(12)
                size: self.width - dp(24), self.height - dp(24)

        Label:
            text: root.score_text
            bold: True
            font_size: "22sp"
            color: 1, 1, 1, 1


<MainScreen@Screen>:
    name: "main"
    hero_coin: ""
    hero_score: "0"
    hero_info: ""
    hero_glow_r: 0.18
    hero_glow_g: 0.95
    hero_glow_b: 0.65

    BoxLayout:
        orientation: "vertical"
        padding: dp(14)
        spacing: dp(14)

        Label:
            text: "SHORT RADAR - KV TEST"
            font_size: "24sp"
            bold: True
            color: 1, 1, 1, 1
            size_hint_y: None
            height: dp(42)
            halign: "left"
            valign: "middle"
            text_size: self.size

        Label:
            text: "EN GUCLU SHORT ADAYI"
            font_size: "20sp"
            bold: True
            color: 1, 1, 1, 1
            size_hint_y: None
            height: dp(34)
            halign: "left"
            valign: "middle"
            text_size: self.size

        BoxLayout:
            size_hint_y: None
            height: dp(220)
            padding: dp(16)
            spacing: dp(14)

            canvas.before:
                Color:
                    rgba: 0.75, 0.14, 0.14, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [22, 22, 22, 22]

            BoxLayout:
                size_hint_x: None
                width: dp(130)
                padding: dp(8)

                canvas.before:
                    Color:
                        rgba: root.hero_glow_r, root.hero_glow_g, root.hero_glow_b, 0.28
                    Ellipse:
                        pos: self.x - dp(10), self.y - dp(10)
                        size: self.width + dp(20), self.height + dp(20)
                    Color:
                        rgba: root.hero_glow_r, root.hero_glow_g, root.hero_glow_b, 1
                    Ellipse:
                        pos: self.pos
                        size: self.size
                    Color:
                        rgba: 0.05, 0.05, 0.10, 1
                    Ellipse:
                        pos: self.x + dp(14), self.y + dp(14)
                        size: self.width - dp(28), self.height - dp(28)

                Label:
                    text: root.hero_score
                    bold: True
                    font_size: "24sp"
                    color: 1, 1, 1, 1

            BoxLayout:
                orientation: "vertical"
                spacing: dp(4)

                Label:
                    text: "EN GUCLU SHORT\\nADAYI"
                    font_size: "17sp"
                    bold: True
                    color: 1, 1, 1, 1
                    size_hint_y: None
                    height: dp(54)
                    halign: "left"
                    valign: "middle"
                    text_size: self.size

                Label:
                    text: root.hero_coin
                    font_size: "28sp"
                    bold: True
                    color: 1, 1, 1, 1
                    size_hint_y: None
                    height: dp(42)
                    halign: "left"
                    valign: "middle"
                    text_size: self.size

                Label:
                    text: root.hero_info
                    markup: True
                    font_size: "16sp"
                    color: 1, 1, 1, 1
                    halign: "left"
                    valign: "top"
                    text_size: self.width, None

        Label:
            text: "Gate.io Vadeli En Cok Yukselenler"
            font_size: "20sp"
            bold: True
            color: 1, 1, 1, 1
            size_hint_y: None
            height: dp(36)
            halign: "left"
            valign: "middle"
            text_size: self.size

        ScrollView:
            do_scroll_x: False

            GridLayout:
                id: coin_list
                cols: 1
                spacing: dp(12)
                padding: 0, 0, 0, dp(18)
                size_hint_y: None
                height: self.minimum_height


<DetailScreen@Screen>:
    name: "detail"
    coin_name: "-"
    score_text: "0"
    info_text: ""
    analysis_text: ""
    glow_r: 0.18
    glow_g: 0.95
    glow_b: 0.65

    BoxLayout:
        orientation: "vertical"
        padding: dp(14)
        spacing: dp(14)

        Button:
            text: "< Geri"
            size_hint_y: None
            height: dp(46)
            size_hint_x: None
            width: dp(110)
            background_normal: ""
            background_down: ""
            background_color: 0.15, 0.15, 0.18, 1
            color: 1, 1, 1, 1
            on_release: app.back_to_main()

        Label:
            text: root.coin_name
            font_size: "28sp"
            bold: True
            color: 1, 1, 1, 1
            size_hint_y: None
            height: dp(44)
            halign: "left"
            valign: "middle"
            text_size: self.size

        BoxLayout:
            size_hint_y: None
            height: dp(220)
            padding: dp(16)
            spacing: dp(14)

            canvas.before:
                Color:
                    rgba: 0.10, 0.10, 0.14, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [22, 22, 22, 22]

            BoxLayout:
                size_hint_x: None
                width: dp(130)
                padding: dp(8)

                canvas.before:
                    Color:
                        rgba: root.glow_r, root.glow_g, root.glow_b, 0.28
                    Ellipse:
                        pos: self.x - dp(10), self.y - dp(10)
                        size: self.width + dp(20), self.height + dp(20)
                    Color:
                        rgba: root.glow_r, root.glow_g, root.glow_b, 1
                    Ellipse:
                        pos: self.pos
                        size: self.size
                    Color:
                        rgba: 0.05, 0.05, 0.10, 1
                    Ellipse:
                        pos: self.x + dp(14), self.y + dp(14)
                        size: self.width - dp(28), self.height - dp(28)

                Label:
                    text: root.score_text
                    bold: True
                    font_size: "24sp"
                    color: 1, 1, 1, 1

            Label:
                text: root.info_text
                markup: True
                font_size: "17sp"
                color: 1, 1, 1, 1
                halign: "left"
                valign: "top"
                text_size: self.width, None

        Label:
            text: "Mini Analiz"
            font_size: "22sp"
            bold: True
            color: 1, 1, 1, 1
            size_hint_y: None
            height: dp(36)
            halign: "left"
            valign: "middle"
            text_size: self.size

        ScrollView:
            do_scroll_x: False

            Label:
                text: root.analysis_text
                font_size: "18sp"
                color: 1, 1, 1, 1
                halign: "left"
                valign: "top"
                text_size: self.width, None
                size_hint_y: None
                height: self.texture_size[1]


ScreenManager:
    MainScreen:
    DetailScreen:
"""


class ClickCard(ButtonBehavior, BoxLayout):
    rank_text = StringProperty("-")
    coin_text = StringProperty("-")
    change_text = StringProperty("-")
    score_text = StringProperty("0")
    glow_r = NumericProperty(0.18)
    glow_g = NumericProperty(0.95)
    glow_b = NumericProperty(0.65)
    coin_data = DictProperty({})

    def on_release(self):
        App.get_running_app().open_detail(dict(self.coin_data))


class KVTestApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)

        self.coins = [
            {
                "rank": 1,
                "coin": "SIREN_USDT",
                "change": "+76.75%",
                "score": 28,
                "price": "0.53657",
                "rsi": "45.6",
                "funding": "0.0925%",
                "volume": "260.88M",
                "red": "Evet",
                "analysis": "RSI short icin asiri bolgede degil.\\nPump guclu, geri cekilme ihtimali izlenmeli.\\nFunding pozitif, short icin destekleyici olabilir.\\nSon mum kirmizi, donus baslangici olabilir.\\nSu an icin net short teyidi zayif."
            },
            {
                "rank": 2,
                "coin": "KOMA_USDT",
                "change": "+59.66%",
                "score": 38,
                "price": "0.38210",
                "rsi": "84.8",
                "funding": "0.0050%",
                "volume": "180.21M",
                "red": "Hayir",
                "analysis": "RSI yuksek bolgede.\\nMomentum guclu ama donus ihtimali artis gosteriyor.\\nFunding hafif pozitif.\\nDirekt giris yerine teyit daha saglikli olabilir."
            },
            {
                "rank": 3,
                "coin": "MMT_USDT",
                "change": "+38.57%",
                "score": 42,
                "price": "0.22541",
                "rsi": "96.2",
                "funding": "-1.8490%",
                "volume": "95.14M",
                "red": "Hayir",
                "analysis": "RSI asiri sisme bolgesinde.\\nFunding negatif, kalabalik short riski var.\\nPump var ama short acarken acele edilmemeli.\\nTeyit mumu beklemek daha guvenli olabilir."
            },
            {
                "rank": 4,
                "coin": "PTB_USDT",
                "change": "+21.43%",
                "score": 18,
                "price": "0.09811",
                "rsi": "61.2",
                "funding": "0.0140%",
                "volume": "44.03M",
                "red": "Hayir",
                "analysis": "Yukselis var ama henuz asiri degil.\\nRSI orta-ust bolgede.\\nErken short riski var."
            },
            {
                "rank": 5,
                "coin": "ARC_USDT",
                "change": "+18.12%",
                "score": 14,
                "price": "0.76420",
                "rsi": "58.9",
                "funding": "0.0210%",
                "volume": "37.88M",
                "red": "Evet",
                "analysis": "Henuz net short teyidi zayif.\\nSon mum kirmizi olsa da ekstra teyit gerekli."
            },
        ]

        self.sm = Builder.load_string(KV)
        self.populate_main()
        return self.sm

    def get_glow(self, score):
        if score >= 35:
            return 1.0, 0.35, 0.25
        return 0.18, 0.95, 0.65

    def populate_main(self):
        main = self.sm.get_screen("main")
        hero_coin = self.coins[-1]
        hr, hg, hb = self.get_glow(hero_coin["score"])

        main.hero_coin = hero_coin["coin"]
        main.hero_score = str(hero_coin["score"])
        main.hero_glow_r = hr
        main.hero_glow_g = hg
        main.hero_glow_b = hb
        main.hero_info = (
            f"[color=ffffff]Puan:[/color] [color=ffb347]{hero_coin['score']}[/color]\\n"
            f"[color=ffffff]RSI:[/color] [color=ff8888]{hero_coin['rsi']}[/color]\\n"
            f"[color=ffffff]Funding:[/color] [color=ff7777]{hero_coin['funding']}[/color]\\n"
            f"[color=ffffff]Degisim:[/color] [color=00ff88]{hero_coin['change']}[/color]\\n"
            f"[color=ffffff]Kirmizi mum:[/color] [color=ffffff]{hero_coin['red']}[/color]"
        )

        container = main.ids.coin_list
        container.clear_widgets()

        for item in self.coins:
            r, g, b = self.get_glow(item["score"])
            card = ClickCard()
            card.coin_data = item
            card.rank_text = str(item["rank"])
            card.coin_text = item["coin"]
            card.change_text = item["change"]
            card.score_text = str(item["score"])
            card.glow_r = r
            card.glow_g = g
            card.glow_b = b
            container.add_widget(card)

    def open_detail(self, coin_data):
        detail = self.sm.get_screen("detail")
        r, g, b = self.get_glow(coin_data["score"])

        detail.coin_name = coin_data["coin"]
        detail.score_text = str(coin_data["score"])
        detail.glow_r = r
        detail.glow_g = g
        detail.glow_b = b
        detail.info_text = (
            f"[color=cccccc]Fiyat:[/color] [color=ffffff]{coin_data['price']}[/color]\\n"
            f"[color=cccccc]Degisim:[/color] [color=00ff88]{coin_data['change']}[/color]\\n"
            f"[color=cccccc]Hacim:[/color] [color=ffffff]{coin_data['volume']}[/color]\\n"
            f"[color=cccccc]Funding:[/color] [color=ffffff]{coin_data['funding']}[/color]\\n"
            f"[color=cccccc]RSI (1s):[/color] [color=ffffff]{coin_data['rsi']}[/color]\\n"
            f"[color=cccccc]Short Puani:[/color] [color=ffffff]{coin_data['score']}[/color]\\n"
            f"[color=cccccc]Kirmizi Mum:[/color] [color=ffffff]{coin_data['red']}[/color]"
        )
        detail.analysis_text = coin_data["analysis"]
        self.sm.current = "detail"

    def back_to_main(self):
        self.sm.current = "main"


if __name__ == "__main__":
    KVTestApp().run()
