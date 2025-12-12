import flet as ft
import math


class CalcButton(ft.ElevatedButton):
    """計算機ボタンの基底クラス"""
    def __init__(self, text, button_clicked, expand=1, bgcolor=None, color=None):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text
        self.bgcolor = bgcolor or ft.Colors.with_opacity(0.2, ft.Colors.WHITE)
        self.color = color or ft.Colors.WHITE
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=50),
            padding=ft.padding.all(18),
        )


class CalculatorApp(ft.Container):
    """科学計算機アプリケーション（iPhone風デザイン）"""
    def __init__(self):
        super().__init__()
        self.reset()
        
        # 角度モード表示（ラジアン/度）
        self.angle_mode = "Rad"
        self.angle_mode_text = ft.Text(
            value=self.angle_mode, 
            color=ft.Colors.ORANGE, 
            size=20,
            weight=ft.FontWeight.BOLD
        )

        # 計算結果表示用テキスト
        self.result = ft.Text(
            value="0", 
            color=ft.Colors.WHITE, 
            size=52,
            weight=ft.FontWeight.W_300,
            text_align=ft.TextAlign.RIGHT
        )
        
        # 画面全体の設定
        self.bgcolor = ft.Colors.BLACK
        self.padding = ft.padding.symmetric(horizontal=20, vertical=10)
        self.expand = True
        
        # メニューアイコン
        menu_icon = ft.IconButton(
            icon=ft.Icons.MENU,
            icon_color=ft.Colors.ORANGE,
            icon_size=30
        )
        
        self.content = ft.Column(
            controls=[
                # ヘッダー行（メニューアイコン - 左寄せ）
                ft.Row(
                    controls=[
                        menu_icon,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                
                # 計算結果表示（右寄せ）
                ft.Row(
                    controls=[self.result], 
                    alignment=ft.MainAxisAlignment.END,
                    expand=1,
                ),
                
                # Rad表示行（左寄せ、ボタンの直前）
                ft.Row(
                    controls=[self.angle_mode_text],
                    alignment=ft.MainAxisAlignment.START,
                ),
                
                # ボタン行1：括弧、メモリ機能、基本操作
                ft.Row(
                    controls=[
                        CalcButton("(", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton(")", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("mc", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("m+", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("m-", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("mr", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("AC", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.WHITE70), color=ft.Colors.BLACK),
                        CalcButton("+/-", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.WHITE70), color=ft.Colors.BLACK),
                        CalcButton("%", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.WHITE70), color=ft.Colors.BLACK),
                        CalcButton("÷", self.button_clicked, bgcolor=ft.Colors.ORANGE),
                    ],
                    spacing=8,
                ),
                
                # ボタン行2：指数関数と数字7-9
                ft.Row(
                    controls=[
                        CalcButton("2nd", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("x²", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("x³", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("xʸ", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("eˣ", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("10ˣ", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("7", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                        CalcButton("8", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                        CalcButton("9", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                        CalcButton("×", self.button_clicked, bgcolor=ft.Colors.ORANGE),
                    ],
                    spacing=8,
                ),
                
                # ボタン行3：根と対数、数字4-6
                ft.Row(
                    controls=[
                        CalcButton("¹/x", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("²√x", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("³√x", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("ʸ√x", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("ln", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("log₁₀", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("4", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                        CalcButton("5", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                        CalcButton("6", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                        CalcButton("-", self.button_clicked, bgcolor=ft.Colors.ORANGE),
                    ],
                    spacing=8,
                ),
                
                # ボタン行4：三角関数、定数、数字1-3
                ft.Row(
                    controls=[
                        CalcButton("x!", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("sin", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("cos", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("tan", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("e", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("EE", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("1", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                        CalcButton("2", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                        CalcButton("3", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                        CalcButton("+", self.button_clicked, bgcolor=ft.Colors.ORANGE),
                    ],
                    spacing=8,
                ),
                
                # ボタン行5：双曲線関数、特殊機能、数字0と小数点
                ft.Row(
                    controls=[
                        CalcButton("🔢", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("sinh", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("cosh", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("tanh", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("π", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("Deg", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("Rand", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                        CalcButton("0", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                        CalcButton(".", self.button_clicked, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                        CalcButton("=", self.button_clicked, bgcolor=ft.Colors.ORANGE),
                    ],
                    spacing=8,
                ),
            ],
            spacing=10,
            expand=True,
        )

    def button_clicked(self, e):
        """ボタンクリック時の処理"""
        data = e.control.data
        print(f"ボタンがクリックされました: {data}")
        
        try:
            # オールクリアまたはエラー状態のリセット
            if self.result.value == "Error" or data == "AC":
                self.result.value = "0"
                self.reset()

            # 数字と小数点の入力処理
            elif data in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."):
                if self.result.value == "0" or self.new_operand:
                    self.result.value = data
                    self.new_operand = False
                else:
                    self.result.value = str(self.result.value) + str(data)

            # 四則演算子の処理
            elif data in ("+", "-", "×", "÷"):
                operator_map = {"×": "*", "÷": "/"}
                actual_operator = operator_map.get(data, data)
                
                self.result.value = str(self.calculate(
                    self.operand1,
                    float(str(self.result.value)),
                    self.operator
                ))
                self.operator = actual_operator
                self.operand1 = float(self.result.value) if self.result.value != "Error" else 0
                self.new_operand = True

            # イコール（計算実行）
            elif data == "=":
                self.result.value = str(self.calculate(
                    self.operand1,
                    float(str(self.result.value)),
                    self.operator
                ))
                self.reset()

            # パーセント計算
            elif data == "%":
                self.result.value = str(float(str(self.result.value)) / 100)
                self.reset()

            # 符号反転
            elif data == "+/-":
                current = float(str(self.result.value))
                self.result.value = str(self.format_number(-current))

            # 正弦（サイン）
            elif data == "sin":
                value = float(str(self.result.value))
                if self.angle_mode == "Rad":
                    self.result.value = str(self.format_number(math.sin(value)))
                else:
                    self.result.value = str(self.format_number(math.sin(math.radians(value))))
                self.reset()

            # 余弦（コサイン）
            elif data == "cos":
                value = float(str(self.result.value))
                if self.angle_mode == "Rad":
                    self.result.value = str(self.format_number(math.cos(value)))
                else:
                    self.result.value = str(self.format_number(math.cos(math.radians(value))))
                self.reset()

            # 正接（タンジェント）
            elif data == "tan":
                value = float(str(self.result.value))
                if self.angle_mode == "Rad":
                    self.result.value = str(self.format_number(math.tan(value)))
                else:
                    self.result.value = str(self.format_number(math.tan(math.radians(value))))
                self.reset()

            # 平方根
            elif data == "²√x":
                value = float(str(self.result.value))
                if value < 0:
                    self.result.value = "Error"
                else:
                    self.result.value = str(self.format_number(math.sqrt(value)))
                self.reset()

            # 二乗
            elif data == "x²":
                value = float(str(self.result.value))
                self.result.value = str(self.format_number(value ** 2))
                self.reset()

            # 三乗
            elif data == "x³":
                value = float(str(self.result.value))
                self.result.value = str(self.format_number(value ** 3))
                self.reset()

            # 自然対数
            elif data == "ln":
                value = float(str(self.result.value))
                if value <= 0:
                    self.result.value = "Error"
                else:
                    self.result.value = str(self.format_number(math.log(value)))
                self.reset()

            # 常用対数
            elif data == "log₁₀":
                value = float(str(self.result.value))
                if value <= 0:
                    self.result.value = "Error"
                else:
                    self.result.value = str(self.format_number(math.log10(value)))
                self.reset()

            # 円周率π
            elif data == "π":
                self.result.value = str(math.pi)
                self.new_operand = True

            # 自然対数の底e
            elif data == "e":
                self.result.value = str(math.e)
                self.new_operand = True

            # 逆数
            elif data == "¹/x":
                value = float(str(self.result.value))
                if value == 0:
                    self.result.value = "Error"
                else:
                    self.result.value = str(self.format_number(1 / value))
                self.reset()

            # 階乗
            elif data == "x!":
                value = int(float(str(self.result.value)))
                if value < 0:
                    self.result.value = "Error"
                else:
                    self.result.value = str(self.format_number(math.factorial(value)))
                self.reset()

            # 角度モード切り替え（Deg/Rad）
            elif data == "Deg":
                self.angle_mode = "Deg" if self.angle_mode == "Rad" else "Rad"
                self.angle_mode_text.value = self.angle_mode
                self.angle_mode_text.update()

        except Exception as ex:
            print(f"エラーが発生しました: {ex}")
            self.result.value = "Error"
            self.reset()

        self.update()

    def format_number(self, num):
        """数値を適切な形式にフォーマット"""
        if num % 1 == 0:
            return int(num)
        else:
            return round(num, 10)

    def calculate(self, operand1, operand2, operator):
        """四則演算を実行"""
        if operator == "+":
            return self.format_number(operand1 + operand2)
        elif operator == "-":
            return self.format_number(operand1 - operand2)
        elif operator == "*":
            return self.format_number(operand1 * operand2)
        elif operator == "/":
            if operand2 == 0:
                return "Error"
            else:
                return self.format_number(operand1 / operand2)

    def reset(self):
        """計算状態をリセット"""
        self.operator = "+"
        self.operand1 = 0
        self.new_operand = True


def main(page: ft.Page):
    """メイン関数（単体実行用）"""
    page.title = "科学計算機"
    page.bgcolor = ft.Colors.BLACK
    page.padding = 0
    page.spacing = 0
    
    # ウィンドウサイズを固定
    page.window.width = 1230
    page.window.height = 500
    page.window.resizable = False
    page.window.minimizable = True
    page.window.maximizable = False
    
    calc = CalculatorApp()
    page.add(calc)


if __name__ == "__main__":
    ft.app(target=main)
