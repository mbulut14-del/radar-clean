import threading
import requests
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager, Screen


TICKERS_URL = "https://fx-api.gateio.ws/api/v4/futures/usdt/tickers"
KLINE_URL = "https://fx-api.gateio.ws/api/v4/futures/usdt/candlesticks"

REFRESH_TIME = 10
RSI_REFRESH_TIME = 45
MIN_VOLUME_USDT = 1_000_000


def format_price(value):
    try:
        value = float(value)
        if value >= 1000:
            return f"{value:,.2f}"
        elif value >= 1:
            return f"{value:,.4f}"
        else:
            return f"{value:.8f}".rstrip("0").rstrip(".")
    except:
        return str(value)


def format_volume(value):
    try:
        value = float(value)
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.2f}K"
        else:
            return f"{value:.2f}"
    except:
        return "0"


def format_funding(value):
    try:
        value = float(value) * 100
        return f"{value:.4f}%"
    except:
        return "-"


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


def get_change_color(change):
    try:
        value = float(change)
        if value >= 80:
            return "00ff88"
        elif value >= 30:
            return "35d07f"
        elif value >= 0:
            return "ffd54a"
        else:
            return "ff6666"
    except:
        return "ffffff"


def get_funding_color(funding):
    try:
        value = float(funding)
        if value < 0:
            return "ff6b6b"
        else:
            return "00ff88"
    except:
        return "ffffff"


def get_rsi_color(rsi):
    try:
        value = float(rsi)
        if value >= 85:
            return "ff4d4d"
        elif value >= 80:
            return "ff6a6a"
        elif value >= 70:
            return "ffd54a"
        else:
            return "00ff88"
    except:
        return "ffffff"


def get_score_circle_rgba(score):
    try:
        value = int(score)
        if value >= 70:
            return (1.0, 0.28, 0.20, 1)
        elif value >= 50:
            return (1.0, 0.72, 0.22, 1)
        else:
            return (0.18, 0.82, 0.48, 1)
    except:
        return (0.35, 0.35, 0.35, 1)


def get_score_glow_rgba(score):
    try:
        value = int(score)
        if value >= 70:
            return (1.0, 0.28, 0.20, 0.36)
        elif value >= 50:
            return (1.0, 0.72, 0.22, 0.32)
        else:
            return (0.18, 0.82, 0.48, 0.28)
    except:
        return (0.35, 0.35, 0.35, 0.22)


def parse_candle_close(candle):
    try:
        if isinstance(candle, dict):
            if "c" in candle:
                return float(candle["c"])
            if "close" in candle:
                return float(candle["close"])
            return None

        if isinstance(candle, (list, tuple)):
            if len(candle) >= 3:
                return float(candle[2])

        return None
    except:
        return None


def parse_candle_open_close(candle):
    try:
        if isinstance(candle, dict):
            if "o" in candle and "c" in candle:
                return float(candle["o"]), float(candle["c"])
            if "open" in candle and "close" in candle:
                return float(candle["open"]), float(candle["close"])
            return None, None

        if isinstance(candle, (list, tuple)):
            if len(candle) >= 6:
                open_price = float(candle[5])
                close_price = float(candle[2])
                return open_price, close_price

        return None, None
    except:
        return None, None


def calculate_short_score(coin, rsi, red):
    score = 0

    if rsi is not None:
        if rsi >= 90:
            score += 50
        elif rsi >= 85:
            score += 40
        elif rsi >= 80:
            score += 30
        elif rsi >= 75:
            score += 20
        elif rsi >= 70:
            score += 10

    funding_pct = float(coin["f"]) * 100
    if funding_pct >= 1.0:
        score += 25
    elif funding_pct >= 0.3:
        score += 18
    elif funding_pct > 0:
        score += 10
    elif funding_pct <= -0.5:
        score -= 8

    change_pct = float(coin["ch"])
    if change_pct >= 200:
        score += 25
    elif change_pct >= 120:
        score += 18
    elif change_pct >= 80:
        score += 12
    elif change_pct >= 50:
        score += 8

    if red:
        score += 20

    return score


def build_mini_analysis(coin, rsi, red, score):
    notes = []

    try:
        change_pct = float(coin["ch"])
    except:
        change_pct = 0.0

    try:
        funding_pct = float(coin["f"]) * 100
    except:
        funding_pct = 0.0

    if rsi is None:
        notes.append("RSI verisi eksik.")
    else:
        if rsi >= 90:
            notes.append("RSI aşırı şişmiş bölgede.")
        elif rsi >= 85:
            notes.append("RSI çok yüksek, agresif short adayı olabilir.")
        elif rsi >= 80:
            notes.append("RSI yüksek, dönüş riski artıyor.")
        elif rsi >= 70:
            notes.append("RSI güçlü ama henüz daha erken olabilir.")
        else:
            notes.append("RSI short için aşırı bölgede değil.")

    if change_pct >= 200:
        notes.append("Pump çok sert, şişme seviyesi yüksek.")
    elif change_pct >= 100:
        notes.append("Pump güçlü, geri çekilme ihtimali izlenmeli.")
    elif change_pct >= 50:
        notes.append("Yükseliş dikkat çekici seviyede.")
    else:
        notes.append("Yükseliş var ama aşırı değil.")

    if funding_pct > 0.3:
        notes.append("Funding pozitif ve kalabalık long riski var.")
    elif funding_pct > 0:
        notes.append("Funding pozitif, short için destekleyici olabilir.")
    elif funding_pct < -0.5:
        notes.append("Funding negatif, kalabalık short ihtimali var.")
    else:
        notes.append("Funding tarafı nötre yakın.")

    if red:
        notes.append("Son mum kırmızı, dönüş başlangıcı olabilir.")
    else:
        notes.append("Son mum kırmızı değil, girişte acele etmemek daha güvenli olabilir.")

    if score >= 90:
        notes.append("Genel görünüm çok güçlü agresif short adayı.")
    elif score >= 70:
        notes.append("Genel görünüm güçlü short adayı.")
    elif score >= 50:
        notes.append("İzlemeye değer ama teyit gerekebilir.")
    else:
        notes.append("Şu an için net short teyidi zayıf.")

    return "\n".join(notes)


class LeftLabel(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        kwargs.setdefault("color", (1, 1, 1, 1))
        super().__init__(**kwargs)
        self.bind(size=self._update_text_size)

    def _update_text_size(self, *args):
        self.text_size = (self.width, None)


class CenterLabel(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault("halign", "center")
        kwargs.setdefault("valign", "middle")
        kwargs.setdefault("color", (1, 1, 1, 1))
        super().__init__(**kwargs)
        self.bind(size=self._update_text_size)

    def _update_text_size(self, *args):
        self.text_size = self.size


class ScoreRing(BoxLayout):
    def __init__(self, ring_size=62, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("width", dp(ring_size))
        kwargs.setdefault("height", dp(ring_size))
        super().__init__(**kwargs)

        from kivy.graphics import Color, Ellipse

        self._ring_inset = dp(6)
        self._core_inset = dp(11)

        with self.canvas.before:
            self.glow_outer_color = Color(*get_score_glow_rgba(0))
            self.glow_outer = Ellipse()

            self.glow_mid_color = Color(*get_score_glow_rgba(0))
            self.glow_mid = Ellipse()

            self.ring_color = Color(*get_score_circle_rgba(0))
            self.ring = Ellipse()

            self.core_color = Color(0.08, 0.08, 0.10, 1)
            self.core = Ellipse()

        self.label = CenterLabel(
            text="0",
            bold=True,
            font_size="18sp"
        )
        self.add_widget(self.label)

        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.glow_outer.pos = (self.x - dp(10), self.y - dp(10))
        self.glow_outer.size = (self.width + dp(20), self.height + dp(20))

        self.glow_mid.pos = (self.x - dp(5), self.y - dp(5))
        self.glow_mid.size = (self.width + dp(10), self.height + dp(10))

        self.ring.pos = self.pos
        self.ring.size = self.size

        self.core.pos = (self.x + self._core_inset, self.y + self._core_inset)
        self.core.size = (
            max(0, self.width - self._core_inset * 2),
            max(0, self.height - self._core_inset * 2)
        )

        self.label.pos = self.pos
        self.label.size = self.size

    def set_score(self, score):
        try:
            value = int(score)
        except:
            value = 0

        rgba = get_score_circle_rgba(value)
        glow = get_score_glow_rgba(value)

        self.label.text = str(value)
        self.ring_color.rgba = rgba
        self.glow_outer_color.rgba = glow
        self.glow_mid_color.rgba = glow


class RankRing(BoxLayout):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint", (None, None))
        kwargs.setdefault("width", dp(48))
        kwargs.setdefault("height", dp(48))
        super().__init__(**kwargs)

        from kivy.graphics import Color, Ellipse

        with self.canvas.before:
            self.glow_color = Color(0.15, 0.65, 1.0, 0.20)
            self.glow = Ellipse()

            self.ring_color = Color(0.15, 0.65, 1.0, 0.95)
            self.ring = Ellipse()

            self.core_color = Color(0.07, 0.08, 0.12, 1)
            self.core = Ellipse()

        self.label = CenterLabel(
            text="-",
            bold=True,
            font_size="17sp"
        )
        self.add_widget(self.label)

        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.glow.pos = (self.x - dp(7), self.y - dp(7))
        self.glow.size = (self.width + dp(14), self.height + dp(14))

        self.ring.pos = self.pos
        self.ring.size = self.size

        self.core.pos = (self.x + dp(5), self.y + dp(5))
        self.core.size = (max(0, self.width - dp(10)), max(0, self.height - dp(10)))

        self.label.pos = self.pos
        self.label.size = self.size

    def set_rank(self, value):
        self.label.text = str(value)


class HeroCard(BoxLayout):
    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("spacing", dp(14))
        kwargs.setdefault("padding", [dp(18), dp(16), dp(18), dp(16)])
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(220))
        super().__init__(**kwargs)

        from kivy.graphics import Color, RoundedRectangle

        with self.canvas.before:
            self.outer_glow_color = Color(1.0, 0.25, 0.20, 0.34)
            self.outer_glow = RoundedRectangle(radius=[30])

            self.mid_glow_color = Color(1.0, 0.22, 0.18, 0.24)
            self.mid_glow = RoundedRectangle(radius=[26])

            self.bg_color = Color(0.58, 0.04, 0.06, 1)
            self.bg = RoundedRectangle(radius=[24])

            self.inner_border_color = Color(1.0, 0.46, 0.34, 0.28)
            self.inner_border = RoundedRectangle(radius=[22])

        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.outer_glow.pos = (self.x - dp(10), self.y - dp(10))
        self.outer_glow.size = (self.width + dp(20), self.height + dp(20))

        self.mid_glow.pos = (self.x - dp(5), self.y - dp(5))
        self.mid_glow.size = (self.width + dp(10), self.height + dp(10))

        self.bg.pos = self.pos
        self.bg.size = self.size

        self.inner_border.pos = (self.x + dp(2), self.y + dp(2))
        self.inner_border.size = (max(0, self.width - dp(4)), max(0, self.height - dp(4)))


class CardButton(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("spacing", dp(14))
        kwargs.setdefault("padding", [dp(14), dp(12), dp(14), dp(12)])
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(104))
        super().__init__(**kwargs)

        from kivy.graphics import Color, RoundedRectangle

        with self.canvas.before:
            self.outer_glow_color = Color(0.12, 0.60, 1.0, 0.18)
            self.outer_glow = RoundedRectangle(radius=[24])

            self.mid_glow_color = Color(0.12, 0.45, 1.0, 0.13)
            self.mid_glow = RoundedRectangle(radius=[21])

            self.bg_color = Color(0.05, 0.06, 0.10, 1)
            self.bg = RoundedRectangle(radius=[18])

            self.inner_border_color = Color(0.12, 0.48, 1.0, 0.24)
            self.inner_border = RoundedRectangle(radius=[18])

        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _update_canvas(self, *args):
        self.outer_glow.pos = (self.x - dp(6), self.y - dp(6))
        self.outer_glow.size = (self.width + dp(12), self.height + dp(12))

        self.mid_glow.pos = (self.x - dp(3), self.y - dp(3))
        self.mid_glow.size = (self.width + dp(6), self.height + dp(6))

        self.bg.pos = self.pos
        self.bg.size = self.size

        self.inner_border.pos = (self.x + dp(1), self.y + dp(1))
        self.inner_border.size = (max(0, self.width - dp(2)), max(0, self.height - dp(2)))


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical")
        self.add_widget(root)

        self.scroll = ScrollView(size_hint=(1, 1))
        root.add_widget(self.scroll)

        self.content = GridLayout(
            cols=1,
            spacing=dp(16),
            padding=[dp(14), dp(14), dp(14), dp(24)],
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        self.scroll.add_widget(self.content)

        self.header_label = LeftLabel(
            text="SHORT RADAR",
            font_size="24sp",
            bold=True,
            size_hint_y=None,
            height=dp(42)
        )
        self.content.add_widget(self.header_label)

        self.hero_title = LeftLabel(
            text="EN GÜÇLÜ SHORT ADAYI",
            font_size="20sp",
            bold=True,
            size_hint_y=None,
            height=dp(36)
        )
        self.content.add_widget(self.hero_title)

        self.hero_card = HeroCard()

        self.hero_score = ScoreRing(ring_size=120)
        self.hero_card.add_widget(self.hero_score)

        hero_right = BoxLayout(orientation="vertical", spacing=dp(6))

        self.hero_inner_title = LeftLabel(
            text="EN GÜÇLÜ SHORT ADAYI",
            font_size="17sp",
            bold=True,
            size_hint_y=None,
            height=dp(26)
        )
        hero_right.add_widget(self.hero_inner_title)

        self.hero_coin = LeftLabel(
            text="Yükleniyor...",
            font_size="27sp",
            bold=True,
            size_hint_y=None,
            height=dp(42)
        )
        hero_right.add_widget(self.hero_coin)

        self.hero_info = LeftLabel(
            text="",
            font_size="18sp",
            markup=True
        )
        hero_right.add_widget(self.hero_info)

        self.hero_card.add_widget(hero_right)
        self.content.add_widget(self.hero_card)

        self.section_title = LeftLabel(
            text="Gate.io Vadeli En Çok Yükselenler",
            font_size="22sp",
            bold=True,
            size_hint_y=None,
            height=dp(42)
        )
        self.content.add_widget(self.section_title)

        self.coin_cards = []
        for _ in range(10):
            card = CardButton()
            card.bind(on_release=self.open_detail)

            rank_badge = RankRing()
            card.add_widget(rank_badge)

            center_wrap = BoxLayout(orientation="vertical", spacing=dp(4))
            coin_label = LeftLabel(
                text="Yükleniyor...",
                font_size="20sp",
                bold=True,
                color=(1, 0.35, 0.35, 1),
                size_hint_y=None,
                height=dp(34)
            )
            change_label = LeftLabel(
                text="+0.00%",
                font_size="18sp",
                bold=True,
                color=(0.18, 0.82, 0.48, 1),
                size_hint_y=None,
                height=dp(28)
            )
            center_wrap.add_widget(coin_label)
            center_wrap.add_widget(change_label)
            card.add_widget(center_wrap)

            score_circle = ScoreRing(ring_size=72)
            card.add_widget(score_circle)

            card.rank_badge = rank_badge
            card.coin_label = coin_label
            card.change_label = change_label
            card.score_circle = score_circle

            self.coin_cards.append(card)
            self.content.add_widget(card)

        self.footer_label = LeftLabel(
            text="Son güncelleme: -",
            font_size="15sp",
            size_hint_y=None,
            height=dp(30),
            color=(0.80, 0.80, 0.80, 1)
        )
        self.content.add_widget(self.footer_label)

    def open_detail(self, button):
        app = App.get_running_app()
        coin_name = getattr(button, "coin_name", None)
        if not coin_name:
            return

        app.selected_coin = coin_name
        detail_screen = app.sm.get_screen("detail")
        detail_screen.load_coin(coin_name)
        app.sm.current = "detail"

    def update_ui(self):
        app = App.get_running_app()
        top = app.top_coins

        if app.short_candidates:
            best = app.short_candidates[0]
            best_coin = best["coin"]
            red_text = "Evet" if best["red"] else "Hayır"

            self.hero_score.set_score(best["score"])
            self.hero_coin.text = best_coin["c"]
            self.hero_info.text = (
                f"[color=ffffff]Puan:[/color] [color=ffb347]{best['score']}[/color]\n"
                f"[color=ffffff]RSI:[/color] [color={get_rsi_color(best['rsi'])}]{best['rsi']:.1f}[/color]\n"
                f"[color=ffffff]Funding:[/color] [color={get_funding_color(best_coin['f'])}]{format_funding(best_coin['f'])}[/color]\n"
                f"[color=ffffff]Değişim:[/color] [color={get_change_color(best_coin['ch'])}]%{best_coin['ch']:.2f}[/color]\n"
                f"[color=ffdddd]Kırmızı mum:[/color] [color=ffffff]{red_text}[/color]"
            )
        else:
            self.hero_score.set_score(0)
            self.hero_coin.text = "Sinyal yok"
            self.hero_info.text = "[color=cccccc]Şu an güçlü short adayı bulunamadı.[/color]"

        for i, card in enumerate(self.coin_cards):
            if i < len(top):
                coin = top[i]
                card.coin_name = coin["c"]
                card.disabled = False
                card.opacity = 1

                card.rank_badge.set_rank(i + 1)
                card.coin_label.text = coin["c"]
                card.change_label.text = f"+{coin['ch']:.2f}%"

                if coin["c"] in app.coin_map:
                    rsi = app.rsi_cache.get(coin["c"])
                    if rsi is not None:
                        score = calculate_short_score(coin, rsi, app.red_cache.get(coin["c"], False))
                    else:
                        score = 0
                else:
                    score = 0

                card.score_circle.set_score(score)
            else:
                card.coin_name = None
                card.disabled = True
                card.opacity = 0.5
                card.rank_badge.set_rank("-")
                card.coin_label.text = "-"
                card.change_label.text = "-"
                card.score_circle.set_score(0)

        app_time = datetime.now().strftime("%H:%M:%S")
        self.footer_label.text = f"Son güncelleme: {app_time} | RSI yenileme: {RSI_REFRESH_TIME}s"


class DetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical")
        self.add_widget(root)

        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            padding=dp(8),
            spacing=dp(8)
        )
        root.add_widget(top_bar)

        self.back_button = Button(
            text="< Geri",
            size_hint_x=None,
            width=dp(100),
            background_normal="",
            background_down="",
            background_color=(0.15, 0.15, 0.15, 1),
            color=(1, 1, 1, 1),
            font_size="18sp"
        )
        self.back_button.bind(on_release=self.go_back)
        top_bar.add_widget(self.back_button)

        self.top_title = LeftLabel(
            text="Coin Detayı",
            font_size="22sp",
            bold=True
        )
        top_bar.add_widget(self.top_title)

        self.scroll = ScrollView(size_hint=(1, 1))
        root.add_widget(self.scroll)

        self.content = GridLayout(
            cols=1,
            spacing=dp(12),
            padding=dp(16),
            size_hint_y=None
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        self.scroll.add_widget(self.content)

        self.coin_title = LeftLabel(
            text="-",
            font_size="28sp",
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        self.content.add_widget(self.coin_title)

        self.data_label = LeftLabel(
            text="-",
            font_size="20sp",
            size_hint_y=None,
            height=dp(240),
            markup=True
        )
        self.content.add_widget(self.data_label)

        self.analysis_title = LeftLabel(
            text="Mini Analiz",
            font_size="22sp",
            bold=True,
            size_hint_y=None,
            height=dp(38)
        )
        self.content.add_widget(self.analysis_title)

        self.analysis_label = LeftLabel(
            text="-",
            font_size="18sp",
            size_hint_y=None,
            height=dp(260)
        )
        self.content.add_widget(self.analysis_label)

    def go_back(self, *args):
        App.get_running_app().sm.current = "main"

    def load_coin(self, coin_name):
        app = App.get_running_app()
        coin = app.coin_map.get(coin_name)

        if not coin:
            self.coin_title.text = coin_name
            self.data_label.text = "Veri bulunamadı"
            self.analysis_label.text = "Bu coin için veri henüz yüklenmedi."
            return

        rsi = app.rsi_cache.get(coin_name)
        red = app.red_cache.get(coin_name, False)
        mum_text = "Evet" if red else "Hayır"

        if rsi is None:
            rsi_text = "-"
            rsi_color = "ffffff"
            score = 0
        else:
            rsi_text = f"{rsi:.1f}"
            rsi_color = get_rsi_color(rsi)
            score = calculate_short_score(coin, rsi, red)

        change_color = get_change_color(coin["ch"])
        funding_color = get_funding_color(coin["f"])

        self.coin_title.text = coin_name
        self.data_label.text = (
            f"[color=cccccc]Fiyat:[/color] [color=ffffff]{format_price(coin['p'])}[/color]\n"
            f"[color=cccccc]Değişim:[/color] [color={change_color}]%{coin['ch']:.2f}[/color]\n"
            f"[color=cccccc]Hacim:[/color] [color=ffffff]{format_volume(coin['v'])}[/color]\n"
            f"[color=cccccc]Funding:[/color] [color={funding_color}]{format_funding(coin['f'])}[/color]\n"
            f"[color=cccccc]RSI (1s):[/color] [color={rsi_color}]{rsi_text}[/color]\n"
            f"[color=cccccc]Short Puanı:[/color] [color=ffffff]{score}[/color]\n"
            f"[color=cccccc]Kırmızı Mum:[/color] [color=ffffff]{mum_text}[/color]"
        )

        self.analysis_label.text = build_mini_analysis(coin, rsi, red, score)


class RadarApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)

        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        })

        self.worker_running = False
        self.rsi_cache = {}
        self.red_cache = {}
        self.rsi_last_update = 0

        self.top_coins = []
        self.coin_map = {}
        self.short_candidates = []
        self.selected_coin = None

        self.sm = ScreenManager()
        self.main_screen = MainScreen(name="main")
        self.detail_screen = DetailScreen(name="detail")

        self.sm.add_widget(self.main_screen)
        self.sm.add_widget(self.detail_screen)
        self.sm.current = "main"

        Clock.schedule_once(lambda dt: self.request_update(), 0.2)
        Clock.schedule_interval(lambda dt: self.request_update(), REFRESH_TIME)

        return self.sm

    def fetch_candles(self, contract, limit=30):
        try:
            params = {
                "contract": contract,
                "interval": "1h",
                "limit": limit
            }
            response = self.session.get(KLINE_URL, params=params, timeout=6)
            data = response.json()

            if isinstance(data, list):
                return data

            return []
        except:
            return []

    def get_rsi(self, contract):
        candles = self.fetch_candles(contract, limit=30)
        if not candles:
            return None

        closes = []
        for candle in candles:
            close_price = parse_candle_close(candle)
            if close_price is not None:
                closes.append(close_price)

        if len(closes) < 15:
            return None

        return calculate_rsi(closes)

    def is_last_candle_red(self, contract):
        candles = self.fetch_candles(contract, limit=2)
        if not candles:
            return False

        last = candles[-1]
        open_price, close_price = parse_candle_open_close(last)

        if open_price is None or close_price is None:
            return False

        return close_price < open_price

    def refresh_rsi_cache_if_needed(self, top_coins, now_ts):
        if (now_ts - self.rsi_last_update) < RSI_REFRESH_TIME and self.rsi_cache:
            return self.rsi_cache, self.red_cache, self.rsi_last_update

        new_rsi_cache = {}
        new_red_cache = {}

        for coin in top_coins:
            contract = coin["c"]
            new_rsi_cache[contract] = self.get_rsi(contract)
            new_red_cache[contract] = self.is_last_candle_red(contract)

        return new_rsi_cache, new_red_cache, now_ts

    def request_update(self):
        if self.worker_running:
            return

        self.worker_running = True
        threading.Thread(target=self.update_data_worker, daemon=True).start()

    def update_data_worker(self):
        try:
            now_ts = Clock.get_boottime()

            response = self.session.get(TICKERS_URL, timeout=8)
            data = response.json()

            coins = []
            for item in data:
                c = item.get("contract", "")
                if not c.endswith("_USDT"):
                    continue

                try:
                    price = float(item["last"])
                    change = float(item["change_percentage"])
                    volume = float(item.get("volume_24h_quote", 0))
                    funding = float(item.get("funding_rate", 0))
                except:
                    continue

                if volume < MIN_VOLUME_USDT:
                    continue

                coins.append({
                    "c": c,
                    "p": price,
                    "ch": change,
                    "v": volume,
                    "f": funding
                })

            coins.sort(key=lambda x: x["ch"], reverse=True)
            top_coins = coins[:10]
            coin_map = {coin["c"]: coin for coin in top_coins}

            rsi_cache, red_cache, rsi_last_update = self.refresh_rsi_cache_if_needed(top_coins, now_ts)

            candidates = []
            for coin in top_coins[:5]:
                rsi = rsi_cache.get(coin["c"])
                red = red_cache.get(coin["c"], False)

                if rsi is None:
                    continue

                score = calculate_short_score(coin, rsi, red)

                if rsi >= 75 or score >= 45:
                    candidates.append({
                        "coin": coin,
                        "rsi": rsi,
                        "red": red,
                        "score": score
                    })

            candidates.sort(key=lambda x: x["score"], reverse=True)

            Clock.schedule_once(
                lambda dt: self.apply_update(
                    top_coins, coin_map, rsi_cache, red_cache, rsi_last_update, candidates
                ),
                0
            )

        except Exception:
            Clock.schedule_once(lambda dt: self.apply_error(), 0)

    def apply_update(self, top_coins, coin_map, rsi_cache, red_cache, rsi_last_update, candidates):
        self.top_coins = top_coins
        self.coin_map = coin_map
        self.rsi_cache = rsi_cache
        self.red_cache = red_cache
        self.rsi_last_update = rsi_last_update
        self.short_candidates = candidates

        self.main_screen.update_ui()

        if self.sm.current == "detail" and self.selected_coin:
            self.detail_screen.load_coin(self.selected_coin)

        self.worker_running = False

    def apply_error(self):
        self.main_screen.hero_coin.text = "Veri çekme hatası"
        self.main_screen.hero_info.text = "[color=ff6666]Sunucudan veri alınamadı.[/color]"
        self.main_screen.hero_score.set_score(0)
        self.worker_running = False


RadarApp().run()
