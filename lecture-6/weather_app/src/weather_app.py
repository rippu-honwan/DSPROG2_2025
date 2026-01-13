import flet as ft
import requests
import sqlite3
from datetime import datetime

class WeatherDatabase:
    """SQLite データベース管理クラス"""
    
    def __init__(self, db_path="weather_forecast.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベーステーブルの作成"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. 地域情報テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS areas (
                area_code TEXT PRIMARY KEY,
                area_name TEXT NOT NULL,
                center_code TEXT,
                center_name TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        # 2. 予報情報テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forecasts (
                forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_code TEXT NOT NULL,
                publishing_office TEXT,
                report_datetime TEXT NOT NULL,
                fetched_at TEXT NOT NULL
            )
        """)
        
        # 3. 予報詳細テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forecast_details (
                detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
                forecast_id INTEGER NOT NULL,
                forecast_date TEXT NOT NULL,
                weather_text TEXT,
                weather_code TEXT,
                temp_min TEXT,
                temp_max TEXT,
                FOREIGN KEY (forecast_id) REFERENCES forecasts(forecast_id),
                UNIQUE(forecast_id, forecast_date)
            )
        """)
        
        # インデックスの作成
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_area_code 
            ON forecasts(area_code)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_forecast_date 
            ON forecast_details(forecast_date)
        """)
        
        conn.commit()
        conn.close()
    
    def save_area(self, area_code, area_name, center_code=None, center_name=None):
        """地域情報をデータベースに保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO areas 
                (area_code, area_name, center_code, center_name, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (area_code, area_name, center_code, center_name, 
                  datetime.now().isoformat()))
            conn.commit()
        finally:
            conn.close()
    
    def save_forecast(self, area_code, publishing_office, weather_list):
        """天気予報をデータベースに保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            fetched_at = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO forecasts 
                (area_code, publishing_office, report_datetime, fetched_at)
                VALUES (?, ?, ?, ?)
            """, (area_code, publishing_office, fetched_at, fetched_at))
            
            forecast_id = cursor.lastrowid
            
            for item in weather_list:
                cursor.execute("""
                    INSERT INTO forecast_details
                    (forecast_id, forecast_date, weather_text, weather_code, temp_min, temp_max)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    forecast_id,
                    item["date"],
                    item["weather"],
                    item.get("weather_code", ""),
                    item["temp_min"],
                    item["temp_max"]
                ))
            
            conn.commit()
            return forecast_id
        finally:
            conn.close()
    
    def get_latest_forecast(self, area_code):
        """最新の天気予報をデータベースから取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT forecast_id, publishing_office, fetched_at
                FROM forecasts
                WHERE area_code = ?
                ORDER BY fetched_at DESC
                LIMIT 1
            """, (area_code,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            forecast_id, publishing_office, fetched_at = result
            
            cursor.execute("""
                SELECT forecast_date, weather_text, weather_code, temp_min, temp_max
                FROM forecast_details
                WHERE forecast_id = ?
                ORDER BY forecast_date
            """, (forecast_id,))
            
            details = cursor.fetchall()
            
            weather_list = []
            for row in details:
                weather_list.append({
                    "date": row[0],
                    "weather": row[1],
                    "weather_code": row[2],
                    "temp_min": row[3],
                    "temp_max": row[4]
                })
            
            return {
                "forecast_id": forecast_id,
                "publishing_office": publishing_office,
                "fetched_at": fetched_at,
                "weather_list": weather_list
            }
        finally:
            conn.close()
    
    def get_forecast_history(self, area_code):
        """過去の予報履歴を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT forecast_id, fetched_at, publishing_office
                FROM forecasts
                WHERE area_code = ?
                ORDER BY fetched_at DESC
                LIMIT 10
            """, (area_code,))
            
            return cursor.fetchall()
        finally:
            conn.close()
    
    def get_forecast_by_id(self, forecast_id):
        """指定されたforecast_idの予報を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT publishing_office, fetched_at
                FROM forecasts
                WHERE forecast_id = ?
            """, (forecast_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            publishing_office, fetched_at = result
            
            cursor.execute("""
                SELECT forecast_date, weather_text, weather_code, temp_min, temp_max
                FROM forecast_details
                WHERE forecast_id = ?
                ORDER BY forecast_date
            """, (forecast_id,))
            
            details = cursor.fetchall()
            
            weather_list = []
            for row in details:
                weather_list.append({
                    "date": row[0],
                    "weather": row[1],
                    "weather_code": row[2],
                    "temp_min": row[3],
                    "temp_max": row[4]
                })
            
            return {
                "forecast_id": forecast_id,
                "publishing_office": publishing_office,
                "fetched_at": fetched_at,
                "weather_list": weather_list
            }
        finally:
            conn.close()


class WeatherApp(ft.Row):
    """気象庁APIを使用した天気予報アプリケーション（データベース対応版）"""
    
    VALID_AREA_CODES = {
        "011000", "012000", "013000", "014030", "014100", "015000", "016000", "017000",
        "020000", "030000", "040000", "050000", "060000", "070000",
        "080000", "090000", "100000", "110000", "120000", "130000", "140000", "190000", "200000",
        "210000", "220000", "230000", "240000",
        "150000", "160000", "170000", "180000",
        "250000", "260000", "270000", "280000", "290000", "300000",
        "310000", "320000", "330000", "340000",
        "360000", "370000", "380000", "390000",
        "350000", "400000", "410000", "420000", "430000", "440000",
        "450000", "460040", "460100",
        "471000", "472000", "473000", "474000"
    }
    
    def __init__(self):
        super().__init__()
        self.expand = True
        self.spacing = 0
        
        self.area_data = {}
        self.selected_area_code = None
        self.current_forecast_id = None
        
        self.db = WeatherDatabase()
        
        self.init_ui()
    
    def init_ui(self):
        """UIコンポーネントの初期化"""
        
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
            
            expansion_tiles = []
            self.area_data = {}
            
            for center_code, center_info in centers.items():
                center_name = center_info.get("name", "")
                office_codes = center_info.get("children", [])
                office_list = []
                
                for office_code in office_codes:
                    if office_code in offices and office_code in self.VALID_AREA_CODES:
                        office_name = offices[office_code].get("name", "")
                        office_list.append({
                            "code": office_code,
                            "name": office_name
                        })
                        
                        self.db.save_area(office_code, office_name, center_code, center_name)
                
                if not office_list:
                    continue
                
                self.area_data[center_code] = {
                    "name": center_name,
                    "offices": office_list
                }
                
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
            
            sidebar_column = self.sidebar.content.controls[3].content
            sidebar_column.controls = expansion_tiles
            self.update()
            
        except Exception as e:
            print(f"地域データの取得に失敗しました: {e}")
            self.show_error("地域データの取得に失敗しました")
    
    def show_weather_forecast(self, area_code):
        """選択された地域の天気予報を表示"""
        try:
            self.selected_area_code = area_code
            
            db_data = self.db.get_latest_forecast(area_code)
            
            if db_data:
                fetched_time = datetime.fromisoformat(db_data["fetched_at"])
                age = (datetime.now() - fetched_time).total_seconds() / 3600
                
                if age < 1:
                    print(f"データベースからデータを取得しました（{age:.1f}時間前）")
                    self.current_forecast_id = db_data["forecast_id"]
                    self.display_weather(
                        db_data["publishing_office"],
                        db_data["weather_list"],
                        db_data["fetched_at"]
                    )
                    return
            
            print("気象庁APIからデータを取得しています")
            url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or len(data) < 2:
                self.show_error("天気予報データが見つかりませんでした")
                return
            
            short_term = data[0]
            publishing_office = short_term.get("publishingOffice", "")
            weekly = data[1]
            
            weather_dict = {}
            if short_term.get("timeSeries"):
                series = short_term["timeSeries"][0]
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
            
            if short_term.get("timeSeries") and len(short_term["timeSeries"]) > 2:
                temp_series = short_term["timeSeries"][2]
                dates = temp_series.get("timeDefines", [])
                if temp_series.get("areas"):
                    area = temp_series["areas"][0]
                    temps = area.get("temps", [])
                    
                    for i, date_str in enumerate(dates):
                        date_only = date_str[:10]
                        if date_only not in weather_dict:
                            weather_dict[date_only] = {}
                        
                        if i < len(temps) and temps[i] and temps[i].strip():
                            if i % 2 == 0:
                                weather_dict[date_only]["temp_min"] = temps[i]
                            else:
                                weather_dict[date_only]["temp_max"] = temps[i]
            
            if weekly.get("timeSeries"):
                w_series = weekly["timeSeries"][0]
                w_dates = w_series.get("timeDefines", [])
                if w_series.get("areas"):
                    w_area = w_series["areas"][0]
                    weather_codes = w_area.get("weatherCodes", [])
                    
                    for i, date_str in enumerate(w_dates):
                        date_only = date_str[:10]
                        if date_only not in weather_dict:
                            weather_dict[date_only] = {}
                        
                        if i < len(weather_codes) and weather_codes[i]:
                            weather_dict[date_only]["weather_code"] = weather_codes[i]
            
            if weekly.get("timeSeries") and len(weekly["timeSeries"]) > 1:
                temp_series = weekly["timeSeries"][1]
                dates = temp_series.get("timeDefines", [])
                if temp_series.get("areas"):
                    area = temp_series["areas"][0]
                    temps_min = area.get("tempsMin", [])
                    temps_max = area.get("tempsMax", [])
                    
                    for i, date_str in enumerate(dates):
                        date_only = date_str[:10]
                        if date_only not in weather_dict:
                            weather_dict[date_only] = {}
                        
                        if i < len(temps_min) and temps_min[i] and temps_min[i].strip():
                            if "temp_min" not in weather_dict[date_only]:
                                weather_dict[date_only]["temp_min"] = temps_min[i]
                        
                        if i < len(temps_max) and temps_max[i] and temps_max[i].strip():
                            if "temp_max" not in weather_dict[date_only]:
                                weather_dict[date_only]["temp_max"] = temps_max[i]
            
            weather_list = []
            for date_str in sorted(weather_dict.keys())[:7]:
                item = weather_dict[date_str]
                
                weather_text = item.get("weather", "")
                if not weather_text:
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
                    "weather_code": item.get("weather_code", ""),
                    "temp_min": item.get("temp_min", ""),
                    "temp_max": item.get("temp_max", "")
                })
            
            forecast_id = self.db.save_forecast(area_code, publishing_office, weather_list)
            self.current_forecast_id = forecast_id
            print("データをデータベースに保存しました")
            
            self.display_weather(publishing_office, weather_list, datetime.now().isoformat())
            
        except Exception as e:
            print(f"天気予報の取得に失敗しました: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"天気予報の取得に失敗しました\n地域コード: {area_code}")
    
    def display_weather(self, publishing_office, weather_list, fetched_at):
        """天気予報を表示"""
        
        history_dropdown = None
        if self.selected_area_code:
            history = self.db.get_forecast_history(self.selected_area_code)
            
            if len(history) > 1:
                dropdown_options = []
                for forecast_id, fetch_time, office in history:
                    dt = datetime.fromisoformat(fetch_time)
                    time_str = dt.strftime("%Y年%m月%d日 %H時%M分")
                    
                    # 現在表示中の予報に印を付ける
                    if forecast_id == self.current_forecast_id:
                        label = f"[現在表示] {time_str}"
                    else:
                        label = time_str
                    
                    dropdown_options.append(
                        ft.dropdown.Option(key=str(forecast_id), text=label)
                    )
                
                history_dropdown = ft.Dropdown(
                    label="過去の予報を選択",
                    options=dropdown_options,
                    value=str(self.current_forecast_id),
                    width=350,
                    on_change=self.on_history_selected,
                    bgcolor=ft.Colors.WHITE,
                    border_color=ft.Colors.INDIGO_200,
                )
        
        weather_cards = []
        for item in weather_list:
            date_str = item["date"]
            weather = item["weather"]
            temp_min = item["temp_min"]
            temp_max = item["temp_max"]
            
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
        
        fetch_dt = datetime.fromisoformat(fetched_at)
        fetch_time_str = fetch_dt.strftime("%Y年%m月%d日 %H時%M分")
        
        content_controls = [
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
            ft.Text(
                f"取得時刻: {fetch_time_str}",
                size=12,
                color=ft.Colors.GREY_600,
                italic=True,
            ),
        ]
        
        if history_dropdown:
            content_controls.append(ft.Container(height=10))
            content_controls.append(history_dropdown)
        
        content_controls.append(ft.Container(height=20))
        content_controls.append(
            ft.Container(
                content=ft.Row(
                    controls=weather_cards,
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                    wrap=True,
                ),
            )
        )
        
        self.main_content.content = ft.Column(
            controls=content_controls,
            spacing=0,
        )
        self.update()
    
    def on_history_selected(self, e):
        """過去の予報選択時の処理"""
        selected_forecast_id = int(e.control.value)
        
        forecast_data = self.db.get_forecast_by_id(selected_forecast_id)
        
        if forecast_data:
            self.current_forecast_id = selected_forecast_id
            self.display_weather(
                forecast_data["publishing_office"],
                forecast_data["weather_list"],
                forecast_data["fetched_at"]
            )
            print(f"過去の予報を表示しました（予報ID: {selected_forecast_id}）")
    
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
    page.title = "天気予報アプリ（データベース版）"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    app = WeatherApp()
    page.add(app)
    app.load_area_data()


if __name__ == "__main__":
    ft.app(target=main)
