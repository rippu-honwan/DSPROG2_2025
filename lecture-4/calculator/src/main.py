import flet as ft
from calc import CalculatorApp


def main(page: ft.Page):
    """メイン関数"""
    page.title = "科学計算機"
    page.bgcolor = ft.Colors.BLACK
    page.padding = 0
    page.spacing = 0
    
    # ウィンドウサイズを固定（調整不可）
    page.window.width = 1230
    page.window.height = 500
    page.window.resizable = False  # サイズ変更禁止
    page.window.minimizable = True  # 最小化許可
    page.window.maximizable = False  # 最大化禁止
    
    calc = CalculatorApp()
    page.add(calc)


if __name__ == "__main__":
    ft.app(target=main)
