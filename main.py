import threading
import requests

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, DictProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager, Screen


TICKERS_URL = "https://fx-api.gateio.ws/api/v4/futures/usdt/tickers"
KLINE_URL = "https://fx-api.gateio.ws/api/v4/futures/usdt/candlesticks"

REFRESH_TIME = 10
RSI_REFRESH_TIME = 45
MIN_VOLUME_USDT = 1_000_000


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


<MainScreen>:
    name: "main"

    BoxLayout:
        orientation: "vertical"
        padding: dp(14)
        spacing: dp(14)

        Label:
            text: "SHORT RADAR"
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


<DetailScreen>:
    name: "detail"

    ScrollView:
        do_scroll_x: False

        GridLayout:
            cols: 1
            padding: dp(14)
            spacing: dp(14)
            size_hint_y: None
            height: self.minimum_height

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
                height: dp(230)
                padding: dp(16)
                spacing: dp(14)

                canvas.before:
                    Color:
                        rgba: 0.08, 0.09, 0.14, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [22, 22, 22, 22]

                BoxLayout:
                    size_hint_x: None
                    width: dp(132)
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

                GridLayout:
                    cols: 1
                    spacing: dp(4)

                    Label:
                        text: "COIN DETAYI"
                        font_size: "17sp"
                        bold: True
                        color: 1, 1, 1, 1
                        size_hint_y: None
                        height: dp(24)
                        halign: "left"
                        valign: "middle"
                        text_size: self.size

                    Label:
                        text: root.info_text
                        markup: True
                        font_size: "17sp"
                        color: 1, 1, 1, 1
                        halign: "left"
                        valign: "top"
                        text_size: self.width, None
                        size_hint_y: None
                        height: self.texture_size[1]

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

            BoxLayout:
                size_hint_y: None
                height: max(dp(180), analysis_label.texture_size[1] + dp(32))
                padding: dp(16)

                canvas.before:
                    Color:
                        rgba: 0.08, 0.09, 0.14, 1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [22, 22, 22, 22]

                Label:
                    id: analysis_label
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


def parse_candle_close(candle):
    try:
        if isinstance(candle, dict):
            if "c" in candle:
                return float(candle["c"])
            if "close" in candle:
                return float(candle["close"])
        elif isinstance(candle, (list, tuple)) and len(candle) >= 3:
            return float(candle[2])
    except:
        pass
    return None


def parse_candle_open_close(candle):
    try:
        if isinstance(candle, dict):
            if "o" in candle and "c" in candle:
                return float(candle["o"]), float(candle["c"])
            if "open" in candle and "close" in candle:
                return float(candle["open"]), float(candle["close"])
        elif isinstance(candle, (list, tuple)) and len(candle) >= 6:
            return float(candle[5]), float(candle[2])
    except:
        pass
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
            notes.append("RSI asiri sisme bolgesinde.")
        elif rsi >= 85:
            notes.append("RSI cok yuksek, agresif short adayi olabilir.")
        elif rsi >= 80:
            notes.append("RSI yuksek, donus riski artiyor.")
        elif rsi >= 70:
            notes.append("RSI guclu ama henuz daha erken olabilir.")
        else:
            notes.append("RSI short icin asiri bolgede degil.")

    if change_pct >= 200:
        notes.append("Pump cok sert, sisme seviyesi yuksek.")
    elif change_pct >= 100:
        notes.append("Pump guclu, geri cekilme ihtimali izlenmeli.")
    elif change_pct >= 50:
        notes.append("Yukselis dikkat cekici seviyede.")
    else:
        notes.append("Yukselis var ama asiri degil.")

    if funding_pct > 0.3:
        notes.append("Funding pozitif ve kalabalik long riski var.")
    elif funding_pct > 0:
        notes.append("Funding pozitif, short icin destekleyici olabilir.")
    elif funding_pct < -0.5:
        notes.append("Funding negatif, kalabalik short ihtimali var.")
    else:
        notes.append("Funding tarafi notr'e yakin.")

    if red:
        notes.append("Son mum kirmizi, donus baslangici olabilir.")
    else:
        notes.append("Son mum kirmizi degil, giriste acele etmemek daha guvenli olabilir.")

    if score >= 90:
        notes.append("Genel gorunum cok guclu agresif short adayi.")
    elif score >= 70:
        notes.append("Genel gorunum guclu short adayi.")
    elif score >= 50:
        notes.append("Izlemeye deger ama teyit gerekebilir.")
    else:
        notes.append("Su an icin net short teyidi zayif.")

    return "\\n".join(notes)


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


class MainScreen(Screen):
    hero_coin = StringProperty("Yukleniyor...")
    hero_score = StringProperty("0")
    hero_info = StringProperty("")
    hero_glow_r = NumericProperty(0.18)
    hero_glow_g = NumericProperty(0.95)
    hero_glow_b = NumericProperty(0.65)


class DetailScreen(Screen):
    coin_name = StringProperty("-")
    score_text = StringProperty("0")
    info_text = StringProperty("")
    analysis_text = StringProperty("")
    glow_r = NumericProperty(0.18)
    glow_g = NumericProperty(0.95)
    glow_b = NumericProperty(0.65)


class RadarKVApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        Window.bind(on_keyboard=self.on_android_back)

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

        self.sm = Builder.load_string(KV)

        Clock.schedule_once(lambda dt: self.request_update(), 0.2)
        Clock.schedule_interval(lambda dt: self.request_update(), REFRESH_TIME)

        return self.sm

    def on_android_back(self, window, key, *args):
        if key == 27 and self.sm.current == "detail":
            self.back_to_main()
            return True
        return False

    def get_glow(self, score):
        if score >= 35:
            return 1.0, 0.35, 0.25
        return 0.18, 0.95, 0.65

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
        except:
            pass
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

        except:
            Clock.schedule_once(lambda dt: self.apply_error(), 0)

    def apply_update(self, top_coins, coin_map, rsi_cache, red_cache, rsi_last_update, candidates):
        self.top_coins = top_coins
        self.coin_map = coin_map
        self.rsi_cache = rsi_cache
        self.red_cache = red_cache
        self.rsi_last_update = rsi_last_update
        self.short_candidates = candidates

        self.populate_main()

        if self.sm.current == "detail" and self.selected_coin:
            self.load_detail(self.selected_coin)

        self.worker_running = False

    def apply_error(self):
        main = self.sm.get_screen("main")
        main.hero_coin = "Veri cekme hatasi"
        main.hero_score = "0"
        main.hero_info = "[color=ff6666]Sunucudan veri alinamadi.[/color]"
        self.worker_running = False

    def populate_main(self):
        main = self.sm.get_screen("main")

        if self.short_candidates:
            best = self.short_candidates[0]
            best_coin = best["coin"]
            red_text = "Evet" if best["red"] else "Hayir"

            r, g, b = self.get_glow(best["score"])
            main.hero_coin = best_coin["c"]
            main.hero_score = str(best["score"])
            main.hero_glow_r = r
            main.hero_glow_g = g
            main.hero_glow_b = b
            main.hero_info = (
                f"[color=ffffff]Puan:[/color] [color=ffb347]{best['score']}[/color]\\n"
                f"[color=ffffff]RSI:[/color] [color=ff8888]{best['rsi']:.1f}[/color]\\n"
                f"[color=ffffff]Funding:[/color] [color=ffffff]{format_funding(best_coin['f'])}[/color]\\n"
                f"[color=ffffff]Degisim:[/color] [color=00ff88]%{best_coin['ch']:.2f}[/color]\\n"
                f"[color=ffffff]Kirmizi mum:[/color] [color=ffffff]{red_text}[/color]"
            )
        else:
            main.hero_coin = "Sinyal yok"
            main.hero_score = "0"
            main.hero_glow_r, main.hero_glow_g, main.hero_glow_b = self.get_glow(0)
            main.hero_info = "[color=cccccc]Su an guclu short adayi bulunamadi.[/color]"

        container = main.ids.coin_list
        container.clear_widgets()

        for i, coin in enumerate(self.top_coins):
            rsi = self.rsi_cache.get(coin["c"])
            red = self.red_cache.get(coin["c"], False)
            score = calculate_short_score(coin, rsi, red) if rsi is not None else 0

            r, g, b = self.get_glow(score)
            card = ClickCard()
            card.coin_data = coin
            card.rank_text = str(i + 1)
            card.coin_text = coin["c"]
            card.change_text = f"+{coin['ch']:.2f}%"
            card.score_text = str(score)
            card.glow_r = r
            card.glow_g = g
            card.glow_b = b
            container.add_widget(card)

    def open_detail(self, coin_data):
        coin_name = coin_data.get("c")
        if not coin_name:
            return
        self.selected_coin = coin_name
        self.load_detail(coin_name)
        self.sm.current = "detail"

    def load_detail(self, coin_name):
        detail = self.sm.get_screen("detail")
        coin = self.coin_map.get(coin_name)

        if not coin:
            detail.coin_name = coin_name
            detail.score_text = "0"
            detail.info_text = "Veri bulunamadi"
            detail.analysis_text = "Bu coin icin veri henuz yuklenmedi."
            return

        rsi = self.rsi_cache.get(coin_name)
        red = self.red_cache.get(coin_name, False)
        mum_text = "Evet" if red else "Hayir"

        if rsi is None:
            rsi_text = "-"
            score = 0
        else:
            rsi_text = f"{rsi:.1f}"
            score = calculate_short_score(coin, rsi, red)

        r, g, b = self.get_glow(score)
        detail.coin_name = coin_name
        detail.score_text = str(score)
        detail.glow_r = r
        detail.glow_g = g
        detail.glow_b = b
        detail.info_text = (
            f"[color=cccccc]Fiyat:[/color] [color=ffffff]{format_price(coin['p'])}[/color]\\n"
            f"[color=cccccc]Degisim:[/color] [color=00ff88]%{coin['ch']:.2f}[/color]\\n"
            f"[color=cccccc]Hacim:[/color] [color=ffffff]{format_volume(coin['v'])}[/color]\\n"
            f"[color=cccccc]Funding:[/color] [color=ffffff]{format_funding(coin['f'])}[/color]\\n"
            f"[color=cccccc]RSI (1s):[/color] [color=ffffff]{rsi_text}[/color]\\n"
            f"[color=cccccc]Short Puani:[/color] [color=ffffff]{score}[/color]\\n"
            f"[color=cccccc]Kirmizi Mum:[/color] [color=ffffff]{mum_text}[/color]"
        )
        detail.analysis_text = build_mini_analysis(coin, rsi, red, score)

    def back_to_main(self):
        self.sm.current = "main"


if __name__ == "__main__":
    RadarKVApp().run()
