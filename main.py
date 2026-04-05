from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window

KV = """
#:import dp kivy.metrics.dp

BoxLayout:
    orientation: "vertical"
    padding: dp(16)
    spacing: dp(16)
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size

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
        orientation: "horizontal"
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
                    rgba: 0.18, 0.95, 0.65, 0.35
                Ellipse:
                    pos: self.x - dp(10), self.y - dp(10)
                    size: self.width + dp(20), self.height + dp(20)
                Color:
                    rgba: 0.18, 0.95, 0.65, 1
                Ellipse:
                    pos: self.pos
                    size: self.size
                Color:
                    rgba: 0.05, 0.05, 0.10, 1
                Ellipse:
                    pos: self.x + dp(14), self.y + dp(14)
                    size: self.width - dp(28), self.height - dp(28)

            Label:
                text: "42"
                bold: True
                font_size: "24sp"
                color: 1, 1, 1, 1

        BoxLayout:
            orientation: "vertical"
            spacing: dp(4)

            Label:
                text: "EN GUCLU SHORT\\nADAYI"
                markup: False
                font_size: "17sp"
                bold: True
                color: 1, 1, 1, 1
                size_hint_y: None
                height: dp(54)
                halign: "left"
                valign: "middle"
                text_size: self.size

            Label:
                text: "MMT_USDT"
                font_size: "28sp"
                bold: True
                color: 1, 1, 1, 1
                size_hint_y: None
                height: dp(42)
                halign: "left"
                valign: "middle"
                text_size: self.size

            Label:
                text: "[color=ffffff]Puan:[/color] [color=ffb347]42[/color]\\n[color=ffffff]RSI:[/color] [color=ff8888]96.2[/color]\\n[color=ffffff]Funding:[/color] [color=ff7777]-1.8490%[/color]\\n[color=ffffff]Degisim:[/color] [color=00ff88]%38.57[/color]\\n[color=ffffff]Kirmizi mum:[/color] [color=ffffff]Hayir[/color]"
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

    BoxLayout:
        orientation: "vertical"
        spacing: dp(12)

        BoxLayout:
            size_hint_y: None
            height: dp(96)
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
                    text: "1"
                    bold: True
                    font_size: "20sp"
                    color: 1, 1, 1, 1

            BoxLayout:
                orientation: "vertical"
                spacing: dp(2)

                Label:
                    text: "SIREN_USDT"
                    font_size: "20sp"
                    bold: True
                    color: 1, 0.35, 0.35, 1
                    size_hint_y: None
                    height: dp(34)
                    halign: "left"
                    valign: "middle"
                    text_size: self.size

                Label:
                    text: "+76.75%"
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
                        rgba: 0.18, 0.95, 0.65, 0.20
                    Ellipse:
                        pos: self.x - dp(8), self.y - dp(8)
                        size: self.width + dp(16), self.height + dp(16)
                    Color:
                        rgba: 0.18, 0.95, 0.65, 1
                    Ellipse:
                        pos: self.pos
                        size: self.size
                    Color:
                        rgba: 0.05, 0.05, 0.10, 1
                    Ellipse:
                        pos: self.x + dp(12), self.y + dp(12)
                        size: self.width - dp(24), self.height - dp(24)

                Label:
                    text: "28"
                    bold: True
                    font_size: "22sp"
                    color: 1, 1, 1, 1

        BoxLayout:
            size_hint_y: None
            height: dp(96)
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
                    text: "2"
                    bold: True
                    font_size: "20sp"
                    color: 1, 1, 1, 1

            BoxLayout:
                orientation: "vertical"
                spacing: dp(2)

                Label:
                    text: "KOMA_USDT"
                    font_size: "20sp"
                    bold: True
                    color: 1, 0.35, 0.35, 1
                    size_hint_y: None
                    height: dp(34)
                    halign: "left"
                    valign: "middle"
                    text_size: self.size

                Label:
                    text: "+59.66%"
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
                        rgba: 1.0, 0.35, 0.25, 0.22
                    Ellipse:
                        pos: self.x - dp(8), self.y - dp(8)
                        size: self.width + dp(16), self.height + dp(16)
                    Color:
                        rgba: 1.0, 0.35, 0.25, 1
                    Ellipse:
                        pos: self.pos
                        size: self.size
                    Color:
                        rgba: 0.05, 0.05, 0.10, 1
                    Ellipse:
                        pos: self.x + dp(12), self.y + dp(12)
                        size: self.width - dp(24), self.height - dp(24)

                Label:
                    text: "38"
                    bold: True
                    font_size: "22sp"
                    color: 1, 1, 1, 1
"""

class KVTestApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        return Builder.load_string(KV)

if __name__ == "__main__":
    KVTestApp().run()
