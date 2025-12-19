import flet as ft
from weather_app import WeatherApp


def main(page: ft.Page):
    """アプリケーションのメインエントリーポイント"""
    page.title = "天気予報アプリ"
    page.padding = 0
    page.spacing = 0
    
    # ウィンドウサイズ設定
    page.window.width = 1000
    page.window.height = 700
    page.window.resizable = True
    
    # 天気予報アプリを作成（まだデータを読み込まない）
    app = WeatherApp()
    
    # ページに追加
    page.add(app)
    
    # ページに追加後にデータを読み込み
    app.load_area_data()


if __name__ == "__main__":
    ft.app(target=main)
