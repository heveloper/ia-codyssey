#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont

# 계산기 핵심 코어 클래스
class Calculator:
    def __init__(self):
        self.reset()

    def reset(self):
        self.current_number = '0'
        self.stored_number = None
        self.last_operation = None
        self.reset_next_input = False

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ZeroDivisionError('0으로 나눌 수 없습니다')
        return a / b

    def toggle_sign(self):
        if self.current_number.startswith('-'):
            self.current_number = self.current_number[1:]
        elif self.current_number != '0':
            self.current_number = '-' + self.current_number

    def percent(self):
        try:
            value = float(self.current_number)
            self.current_number = str(value / 100.0)
        except ValueError:
            self.current_number = 'Error'

    def input_number(self, number):
        if self.reset_next_input:
            self.current_number = number
            self.reset_next_input = False
        elif self.current_number == '0':
            self.current_number = number
        else:
            if len(self.current_number) < 9:
                self.current_number += number

    def input_decimal(self):
        if self.reset_next_input:
            self.current_number = '0.'
            self.reset_next_input = False
        elif '.' not in self.current_number:
            self.current_number += '.'

    def set_operation(self, operation):
        if self.stored_number is not None and not self.reset_next_input:
            self.equal()
        self.last_operation = operation
        self.stored_number = self.current_number
        self.reset_next_input = True

    def equal(self):
        if self.last_operation is None or self.stored_number is None:
            return

        try:
            num1 = float(self.stored_number)
            num2 = float(self.current_number)

            if self.last_operation == '+':
                result = self.add(num1, num2)
            elif self.last_operation == '-':
                result = self.subtract(num1, num2)
            elif self.last_operation == '×':
                result = self.multiply(num1, num2)
            elif self.last_operation == '÷':
                result = self.divide(num1, num2)
            else:
                result = num2

            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 6)

            self.current_number = str(result)
            self.stored_number = self.current_number
            self.last_operation = None
            self.reset_next_input = True

        except Exception:
            self.current_number = 'Error'

    def get_display(self):
        try:
            value = float(self.current_number)
            if value.is_integer():
                return str(int(value))
            else:
                return str(value)
        except ValueError:
            return self.current_number

# UI용 커스텀 버튼
class CustomButton(QPushButton):
    def __init__(self, text, parent=None, bg_color="#333333", text_color="white"):
        super().__init__(text, parent)
        self.bg_color = bg_color
        self.text_color = text_color
        self.is_pressed = False
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(100)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.setStyleSheet(self.get_style_sheet())

    def get_style_sheet(self):
        opacity = 0.7 if self.is_pressed else 1.0
        border_style = "1px solid #555" if self.is_pressed else "none"
        return (
            f"QPushButton {{"
            f"    background-color: {self.bg_color}; "
            f"    color: {self.text_color}; "
            f"    border-radius: 35px; "
            f"    border: {border_style}; "
            f"    font-family: Arial; "
            f"    font-weight: bold; "
            f"    font-size: 20px; "
            f"    opacity: {opacity}; "
            f"}}"
            f"QPushButton:pressed {{"
            f"    background-color: {'#555555' if self.bg_color == '#333333' else '#ffb340'}; "
            f"}}"
        )

    def mousePressEvent(self, event):
        self.is_pressed = True
        self.setStyleSheet(self.get_style_sheet())
        rect = self.geometry()
        target = QRect(rect.x() + 2, rect.y() + 2, rect.width() - 4, rect.height() - 4)
        self.animation.setStartValue(rect)
        self.animation.setEndValue(target)
        self.animation.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.is_pressed = False
        self.setStyleSheet(self.get_style_sheet())
        rect = self.geometry()
        target = QRect(rect.x() - 2, rect.y() - 2, rect.width() + 4, rect.height() + 4)
        self.animation.setStartValue(rect)
        self.animation.setEndValue(target)
        self.animation.start()
        super().mouseReleaseEvent(event)

# 전체 앱 클래스
class CalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.calc = Calculator()

        self.setWindowTitle('아이폰 계산기')
        self.setFixedSize(350, 600)
        self.setStyleSheet("background-color: black;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        main_layout.addStretch(1)

        self.result_display = QLabel('0')
        self.result_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.result_display.setFont(QFont('Arial', 60))
        self.result_display.setStyleSheet('color: white; background-color: transparent; padding: 10px;')
        self.result_display.setMinimumHeight(100)
        main_layout.addWidget(self.result_display)

        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(10)
        main_layout.addLayout(buttons_layout)

        # 버튼 배치
        self.create_button('AC', buttons_layout, 0, 0, self.clear_all, '#a5a5a5', 'black')
        self.create_button('+/-', buttons_layout, 0, 1, self.negate, '#a5a5a5', 'black')
        self.create_button('%', buttons_layout, 0, 2, self.percentage, '#a5a5a5', 'black')
        self.create_button('÷', buttons_layout, 0, 3, lambda: self.operation_pressed('÷'), '#ff9500', 'white')
        self.create_button('7', buttons_layout, 1, 0, lambda: self.number_pressed('7'), '#333333', 'white')
        self.create_button('8', buttons_layout, 1, 1, lambda: self.number_pressed('8'), '#333333', 'white')
        self.create_button('9', buttons_layout, 1, 2, lambda: self.number_pressed('9'), '#333333', 'white')
        self.create_button('×', buttons_layout, 1, 3, lambda: self.operation_pressed('×'), '#ff9500', 'white')
        self.create_button('4', buttons_layout, 2, 0, lambda: self.number_pressed('4'), '#333333', 'white')
        self.create_button('5', buttons_layout, 2, 1, lambda: self.number_pressed('5'), '#333333', 'white')
        self.create_button('6', buttons_layout, 2, 2, lambda: self.number_pressed('6'), '#333333', 'white')
        self.create_button('-', buttons_layout, 2, 3, lambda: self.operation_pressed('-'), '#ff9500', 'white')
        self.create_button('1', buttons_layout, 3, 0, lambda: self.number_pressed('1'), '#333333', 'white')
        self.create_button('2', buttons_layout, 3, 1, lambda: self.number_pressed('2'), '#333333', 'white')
        self.create_button('3', buttons_layout, 3, 2, lambda: self.number_pressed('3'), '#333333', 'white')
        self.create_button('+', buttons_layout, 3, 3, lambda: self.operation_pressed('+'), '#ff9500', 'white')
        self.create_button('0', buttons_layout, 4, 0, lambda: self.number_pressed('0'), '#333333', 'white', 2)
        self.create_button('.', buttons_layout, 4, 2, self.decimal_pressed, '#333333', 'white')
        self.create_button('=', buttons_layout, 4, 3, self.equals_pressed, '#ff9500', 'white')

    def create_button(self, text, layout, row, col, callback, bg_color, text_color, col_span=1):
        button = CustomButton(text, bg_color=bg_color, text_color=text_color)
        button.setMinimumSize(70, 70)
        button.clicked.connect(callback)
        layout.addWidget(button, row, col, 1, col_span)
        return button

    def update_display(self):
        display_text = self.calc.get_display()
        length = len(display_text)
        if length > 9:
            self.result_display.setFont(QFont('Arial', 40))
        elif length > 6:
            self.result_display.setFont(QFont('Arial', 50))
        else:
            self.result_display.setFont(QFont('Arial', 60))
        self.result_display.setText(display_text)

    def number_pressed(self, number):
        self.calc.input_number(number)
        self.update_display()

    def decimal_pressed(self):
        self.calc.input_decimal()
        self.update_display()

    def operation_pressed(self, op):
        self.calc.set_operation(op)
        self.update_display()

    def equals_pressed(self):
        self.calc.equal()
        self.update_display()

    def clear_all(self):
        self.calc.reset()
        self.update_display()

    def negate(self):
        self.calc.toggle_sign()
        self.update_display()

    def percentage(self):
        self.calc.percent()
        self.update_display()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalculatorApp()
    window.show()
    sys.exit(app.exec_())
