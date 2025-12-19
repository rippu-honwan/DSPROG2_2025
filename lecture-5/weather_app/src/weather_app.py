import flet as ft
import requests
from datetime import datetime


class WeatherApp(ft.Row):
    """気象庁APIを使用した天気予報アプリケーション"""
    
    # 🔧 氣象廳 API 支持嘅地區代碼白名單
    VALID_AREA_CODES = {
        # 北海道
        "011000", "012000", "013000", "014030", "014100", "015000", "016000", "017000",
        # 東北
        "020000", "030000", "040000", "050000", "060000", "070000",
        # 關東甲信
        "080000", "090000", "100000", "110000", "120000", "130000", "140000", "190000", "200000",
        # 東海
        "210000", "220000", "230000", "240000",
        # 北陸
        "150000", "160000", "170000", "180000",
        # 近畿
        "250000", "260000", "270000", "280000", "290000", "300000",
        # 中國
        "310000", "320000", "330000", "340000",
        # 四國
        "360000", "370000", "380000", "390000",
        # 九州（含山口）
        "350000", "400000", "410000", "420000", "430000", "440000",
        # 九州南部・奄美
        "450000", "460040", "460100",
        # 沖繩
        "471000", "472000", "473000", "474000"
    }
    
    def __init__(self):
        super().__init__()
        self.expand = True
        self.spacing = 0
        
        self.area_data = {}
        self.selected_area_code = None
        
        self.init_ui()
    
    def init_ui(self):
        """UIコンポーネントの初期化"""
        
        # 左側のサイドバー
        self.sidebar = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.WB_SUNNY, color=ft.Colors.WHITE, size=28),
                                ft.Text(
                                    "天気予報",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                ),
                            ],
                            spacing=10,
                        ),
                        padding=20,
                        bgcolor=ft.Colors.INDIGO_900,
                    ),
                    ft.Divider(height=1, color=ft.Colors.WHITE24),
                    ft.Container(
                        content=ft.Text(
                            "地域を選択",
                            size=16,
                            color=ft.Colors.WHITE70,
                        ),
                        padding=ft.padding.only(left=20, top=15, bottom=5),
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[],
                            spacing=0,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        expand=True,
                    ),
                ],
                spacing=0,
            ),
            width=300,
            bgcolor=ft.Colors.BLUE_GREY_800,
        )
        
        # 右側のメインコンテンツ
        self.main_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "地域を選択してください",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_700,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
            expand=True,
            padding=30,
            bgcolor=ft.Colors.BLUE_GREY_100,
        )
        
        self.controls = [
            self.sidebar,
            ft.VerticalDivider(width=1, color=ft.Colors.TRANSPARENT),
            self.main_content,
        ]
    
    def load_area_data(self):
        """気象庁APIから地域データを取得"""
        try:
            url = "http://www.jma.go.jp/bosai/common/const/area.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            centers = data.get("centers", {})
            offices = data.get("offices", {})
            
            # サイドバーに地域を追加
            expansion_tiles = []
            self.area_data = {}
            
            for center_code, center_info in centers.items():
                center_name = center_info.get("name", "")
                office_codes = center_info.get("children", [])
                office_list = []
                
                for office_code in office_codes:
                    # 🔧 只顯示白名單內的地區代碼
                    if office_code in offices and office_code in self.VALID_AREA_CODES:
                        office_name = offices[office_code].get("name", "")
                        office_list.append({
                            "code": office_code,
                            "name": office_name
                        })
                
                # 如果該 center 沒有有效的 office，跳過
                if not office_list:
                    continue
                
                self.area_data[center_code] = {
                    "name": center_name,
                    "offices": office_list
                }
                
                # 地域リストを作成
                office_tiles = []
                for office in office_list:
                    tile = ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    office["name"],
                                    size=15,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.W_400,
                                ),
                                ft.Text(
                                    office["code"],
                                    size=12,
                                    color=ft.Colors.WHITE54,
                                ),
                            ],
                            spacing=3,
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                        ),
                        padding=ft.padding.only(left=20, top=10, bottom=10, right=20),
                        bgcolor=ft.Colors.BLUE_GREY_700,
                        alignment=ft.alignment.center_left,
                        on_click=lambda e, code=office["code"]: self.show_weather_forecast(code),
                    )
                    office_tiles.append(tile)
                
                # ExpansionTile を作成
                expansion = ft.ExpansionTile(
                    title=ft.Column(
                        controls=[
                            ft.Text(
                                center_name,
                                size=15,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                center_code,
                                size=12,
                                color=ft.Colors.WHITE54,
                            ),
                        ],
                        spacing=3,
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                    ),
                    initially_expanded=False,
                    controls=office_tiles,
                    bgcolor=ft.Colors.BLUE_GREY_800,
                    collapsed_bgcolor=ft.Colors.BLUE_GREY_800,
                    text_color=ft.Colors.WHITE,
                    icon_color=ft.Colors.WHITE70,
                    controls_padding=ft.padding.all(0),
                )
                expansion_tiles.append(expansion)
            
            # サイドバーを更新
            sidebar_column = self.sidebar.content.controls[3].content
            sidebar_column.controls = expansion_tiles
            self.update()
            
        except Exception as e:
            print(f"地域データの取得に失敗しました: {e}")
            self.show_error("地域データの取得に失敗しました")
    
    def show_weather_forecast(self, area_code):
        """選択された地域の天気予報を表示"""
        try:
            url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or len(data) < 2:
                self.show_error("天気予報データが見つかりませんでした")
                return
            
            # 📦 第一個物件：短期預報
            short_term = data[0]
            publishing_office = short_term.get("publishingOffice", "")
            
            # 📦 第二個物件：一週預報
            weekly = data[1]
            
            # 🔧 從第一個物件取得天氣描述（前3日）
            weather_dict = {}
            if short_term.get("timeSeries"):
                series = short_term["timeSeries"][0]  # 天氣描述
                dates = series.get("timeDefines", [])
                if series.get("areas"):
                    weathers = series["areas"][0].get("weathers", [])
                    weather_codes = series["areas"][0].get("weatherCodes", [])
                    
                    for i, date_str in enumerate(dates[:3]):
                        date_only = date_str[:10]
                        weather = weathers[i] if i < len(weathers) else ""
                        w_code = weather_codes[i] if i < len(weather_codes) else ""
                        
                        weather_dict[date_only] = {
                            "weather": weather,
                            "weather_code": w_code
                        }
            
            # 🔧 從第一個物件取得前3日的溫度（如果有）
            if short_term.get("timeSeries") and len(short_term["timeSeries"]) > 2:
                temp_series = short_term["timeSeries"][2]  # 短期溫度
                dates = temp_series.get("timeDefines", [])
                if temp_series.get("areas"):
                    area = temp_series["areas"][0]
                    temps = area.get("temps", [])
                    
                    for i, date_str in enumerate(dates):
                        date_only = date_str[:10]
                        if date_only not in weather_dict:
                            weather_dict[date_only] = {}
                        
                        # 判斷是最低溫還是最高溫（根據順序）
                        if i < len(temps) and temps[i] and temps[i].strip():
                            # 偶數索引為最低溫，奇數索引為最高溫
                            if i % 2 == 0:
                                weather_dict[date_only]["temp_min"] = temps[i]
                            else:
                                weather_dict[date_only]["temp_max"] = temps[i]
            
            # 🔧 從第二個物件取得一週天氣代碼（補充後面日子）
            if weekly.get("timeSeries"):
                w_series = weekly["timeSeries"][0]  # 一週天氣
                w_dates = w_series.get("timeDefines", [])
                if w_series.get("areas"):
                    w_area = w_series["areas"][0]
                    weather_codes = w_area.get("weatherCodes", [])
                    
                    for i, date_str in enumerate(w_dates):
                        date_only = date_str[:10]
                        if date_only not in weather_dict:
                            weather_dict[date_only] = {}
                        
                        # 補充天氣代碼（用於後面日子）
                        if i < len(weather_codes) and weather_codes[i]:
                            weather_dict[date_only]["weather_code"] = weather_codes[i]
            
            # 🔧 從第二個物件取得一週溫度（補充或覆蓋）
            if weekly.get("timeSeries") and len(weekly["timeSeries"]) > 1:
                temp_series = weekly["timeSeries"][1]  # 一週溫度
                dates = temp_series.get("timeDefines", [])
                if temp_series.get("areas"):
                    area = temp_series["areas"][0]
                    temps_min = area.get("tempsMin", [])
                    temps_max = area.get("tempsMax", [])
                    
                    for i, date_str in enumerate(dates):
                        date_only = date_str[:10]
                        if date_only not in weather_dict:
                            weather_dict[date_only] = {}
                        
                        # 🔧 檢查溫度是否為空字串，並且不覆蓋已有的短期溫度
                        if i < len(temps_min) and temps_min[i] and temps_min[i].strip():
                            if "temp_min" not in weather_dict[date_only]:
                                weather_dict[date_only]["temp_min"] = temps_min[i]
                        
                        if i < len(temps_max) and temps_max[i] and temps_max[i].strip():
                            if "temp_max" not in weather_dict[date_only]:
                                weather_dict[date_only]["temp_max"] = temps_max[i]
            
            # 轉換為列表並排序
            weather_list = []
            for date_str in sorted(weather_dict.keys())[:7]:
                item = weather_dict[date_str]
                
                # 🔧 天氣描述優先顯示，否則用天氣代碼判斷
                weather_text = item.get("weather", "")
                if not weather_text:
                    # 根據天氣代碼顯示簡化描述
                    w_code = item.get("weather_code", "")
                    if w_code.startswith("1"):
                        weather_text = "晴れ"
                    elif w_code.startswith("2"):
                        weather_text = "くもり"
                    elif w_code.startswith("3") or w_code.startswith("4"):
                        weather_text = "雨"
                    else:
                        weather_text = ""
                
                weather_list.append({
                    "date": date_str,
                    "weather": weather_text,
                    "temp_min": item.get("temp_min", ""),
                    "temp_max": item.get("temp_max", "")
                })
            
            # 天気予報カードを作成
            weather_cards = []
            for item in weather_list:
                date_str = item["date"]
                weather = item["weather"]
                temp_min = item["temp_min"]
                temp_max = item["temp_max"]
                
                # アイコンを選択
                icon_stack = None
                if "雨" in weather:
                    icon_stack = ft.Stack(
                        controls=[
                            ft.Icon(ft.Icons.WB_SUNNY, size=60, color=ft.Colors.ORANGE_400),
                            ft.Container(
                                content=ft.Icon(ft.Icons.UMBRELLA, size=40, color=ft.Colors.BLUE_400),
                                left=25, top=20,
                            ),
                        ],
                        width=70, height=70,
                    )
                elif "雪" in weather or "ふぶく" in weather:
                    icon_stack = ft.Icon(ft.Icons.AC_UNIT, size=60, color=ft.Colors.LIGHT_BLUE_200)
                elif "晴" in weather:
                    icon_stack = ft.Icon(ft.Icons.WB_SUNNY, size=60, color=ft.Colors.ORANGE_400)
                elif "曇" in weather or "くもり" in weather:
                    icon_stack = ft.Icon(ft.Icons.CLOUD, size=60, color=ft.Colors.GREY_400)
                else:
                    icon_stack = ft.Icon(ft.Icons.CLOUD, size=60, color=ft.Colors.GREY_400)
                
                # 🔧 温度表示（改良）
                has_min = temp_min and str(temp_min).strip()
                has_max = temp_max and str(temp_max).strip()

                temp_display = ft.Row(
                    controls=[
                        ft.Text(
                            f"{temp_min}°C" if has_min else "-",
                            size=16,
                            color=ft.Colors.BLUE_600 if has_min else ft.Colors.GREY_400,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text("/", size=14, color=ft.Colors.GREY_600),
                        ft.Text(
                            f"{temp_max}°C" if has_max else "-",
                            size=16,
                            color=ft.Colors.RED_400 if has_max else ft.Colors.GREY_400,
                            weight=ft.FontWeight.W_500,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                )
                
                card = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                date_str,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_800,
                            ),
                            ft.Container(height=10),
                            icon_stack,
                            ft.Container(height=5),
                            ft.Text(
                                weather if weather else "データなし",
                                size=14,
                                color=ft.Colors.GREY_700 if weather else ft.Colors.GREY_400,
                                text_align=ft.TextAlign.CENTER,
                                max_lines=3,
                            ),
                            ft.Container(height=10),
                            temp_display,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=15,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    width=180,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=10,
                        color=ft.Colors.BLACK12,
                    ),
                )
                weather_cards.append(card)
            
            # メインコンテンツを更新
            self.main_content.content = ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LOCATION_ON, size=32, color=ft.Colors.INDIGO_600),
                            ft.Text(
                                publishing_office,
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.INDIGO_900,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Container(height=20),
                    ft.Container(
                        content=ft.Row(
                            controls=weather_cards,
                            spacing=15,
                            scroll=ft.ScrollMode.AUTO,
                            wrap=True,
                        ),
                    ),
                ],
                spacing=0,
            )
            self.update()
            
        except Exception as e:
            print(f"天気予報の取得に失敗しました: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"天気予報の取得に失敗しました\n地域コード: {area_code}")
    
    def show_error(self, message):
        """エラーメッセージを表示"""
        self.main_content.content = ft.Column(
            controls=[
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=80, color=ft.Colors.RED_400),
                ft.Container(height=20),
                ft.Text(message, size=20, color=ft.Colors.RED_600, text_align=ft.TextAlign.CENTER),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
        self.update()


def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    app = WeatherApp()
    page.add(app)
    app.load_area_data()


if __name__ == "__main__":
    ft.app(target=main)
