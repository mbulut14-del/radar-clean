from kivy.app import App
from kivy.lang import Builder

KV = '''
BoxLayout:
    orientation: "vertical"
    padding: 20
    spacing: 20

    Label:
        text: "SHORT RADAR - KV TEST"
        font_size: "26sp"
        bold: True

    Label:
        text: "EN GÜÇLÜ SHORT ADAYI"
        font_size: "20sp"

    BoxLayout:
        size_hint_y: None
        height: 200
        padding: 20

        canvas.before:
            Color:
                rgba: (1, 0.2, 0.2, 1)
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [20]

        Label:
            text: "KOMA_USDT\\nPuan: 72\\nRSI: 84.8"
            halign: "center"
            valign: "middle"

    Label:
        text: "LISTE TEST"
        font_size: "18sp"

    BoxLayout:
        size_hint_y: None
        height: 80

        canvas.before:
            Color:
                rgba: (0.1, 0.2, 0.4, 1)
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [15]

        Label:
            text: "SIREN_USDT  (+102%)"
'''

class TestApp(App):
    def build(self):
        return Builder.load_string(KV)

if __name__ == "__main__":
    TestApp().run()
