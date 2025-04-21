#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QColor


class CustomButton(QPushButton):
    """버튼 클릭 효과를 위한 커스텀 버튼 클래스"""
    
    def __init__(self, text, parent=None, bg_color="#333333", text_color="white"):
        super().__init__(text, parent)
        self.bg_color = bg_color
        self.text_color = text_color
        self.is_pressed = False
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(100)  # 100ms 애니메이션
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.setStyleSheet(self.get_style_sheet())
    
    def get_style_sheet(self):
        """버튼 스타일시트 생성"""
        opacity = 0.7 if self.is_pressed else 1.0
        border_style = "1px solid #555" if self.is_pressed else "none"
        return (
            f"QPushButton {{"
            f"    background-color: {self.bg_color}; "
            f"    color: {self.text_color}; "
            f"    border-radius: 35px; "  # 더 둥근 버튼
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
        """마우스 버튼 누름 이벤트"""
        self.is_pressed = True
        self.setStyleSheet(self.get_style_sheet())
        
        # 버튼이 약간 축소되는 애니메이션
        rect = self.geometry()
        target = QRect(rect.x() + 2, rect.y() + 2, rect.width() - 4, rect.height() - 4)
        self.animation.setStartValue(rect)
        self.animation.setEndValue(target)
        self.animation.start()
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """마우스 버튼 놓음 이벤트"""
        self.is_pressed = False
        self.setStyleSheet(self.get_style_sheet())
        
        # 버튼이 원래 크기로 돌아오는 애니메이션
        rect = self.geometry()
        target = QRect(rect.x() - 2, rect.y() - 2, rect.width() + 4, rect.height() + 4)
        self.animation.setStartValue(rect)
        self.animation.setEndValue(target)
        self.animation.start()
        
        super().mouseReleaseEvent(event)


class CalculatorApp(QMainWindow):
    """iPhone 스타일 계산기 애플리케이션"""
    
    def __init__(self):
        """계산기 초기화"""
        super().__init__()
        
        # 계산기 상태
        self.current_number = '0'
        self.stored_number = None
        self.last_operation = None
        self.reset_next_input = False
        
        # UI 설정
        self.setWindowTitle('아이폰 계산기')
        self.setFixedSize(350, 600)
        self.setStyleSheet("background-color: black;")
        
        # 중앙 위젯 생성
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # 결과 표시 영역을 위한 여백 추가
        main_layout.addStretch(1)
        
        # 결과 표시 라벨
        self.result_display = QLabel('0')
        self.result_display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.result_display.setFont(QFont('Arial', 60))
        self.result_display.setStyleSheet('color: white; background-color: transparent; padding: 10px;')
        self.result_display.setMinimumHeight(100)
        main_layout.addWidget(self.result_display)
        
        # 버튼 그리드 레이아웃
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(10)
        main_layout.addLayout(buttons_layout)
        
        # 버튼 설정
        # [AC, +/-, %, ÷]
        # [7, 8, 9, ×]
        # [4, 5, 6, -]
        # [1, 2, 3, +]
        # [0, ., =]
        
        # 첫 번째 행
        self.create_button('AC', buttons_layout, 0, 0, self.clear_all, '#a5a5a5', 'black')
        self.create_button('+/-', buttons_layout, 0, 1, self.negate, '#a5a5a5', 'black')
        self.create_button('%', buttons_layout, 0, 2, self.percentage, '#a5a5a5', 'black')
        self.create_button('÷', buttons_layout, 0, 3, lambda: self.operation_pressed('÷'), '#ff9500', 'white')
        
        # 두 번째 행
        self.create_button('7', buttons_layout, 1, 0, lambda: self.number_pressed('7'), '#333333', 'white')
        self.create_button('8', buttons_layout, 1, 1, lambda: self.number_pressed('8'), '#333333', 'white')
        self.create_button('9', buttons_layout, 1, 2, lambda: self.number_pressed('9'), '#333333', 'white')
        self.create_button('×', buttons_layout, 1, 3, lambda: self.operation_pressed('×'), '#ff9500', 'white')
        
        # 세 번째 행
        self.create_button('4', buttons_layout, 2, 0, lambda: self.number_pressed('4'), '#333333', 'white')
        self.create_button('5', buttons_layout, 2, 1, lambda: self.number_pressed('5'), '#333333', 'white')
        self.create_button('6', buttons_layout, 2, 2, lambda: self.number_pressed('6'), '#333333', 'white')
        self.create_button('-', buttons_layout, 2, 3, lambda: self.operation_pressed('-'), '#ff9500', 'white')
        
        # 네 번째 행
        self.create_button('1', buttons_layout, 3, 0, lambda: self.number_pressed('1'), '#333333', 'white')
        self.create_button('2', buttons_layout, 3, 1, lambda: self.number_pressed('2'), '#333333', 'white')
        self.create_button('3', buttons_layout, 3, 2, lambda: self.number_pressed('3'), '#333333', 'white')
        self.create_button('+', buttons_layout, 3, 3, lambda: self.operation_pressed('+'), '#ff9500', 'white')
        
        # 다섯 번째 행
        self.create_button('0', buttons_layout, 4, 0, lambda: self.number_pressed('0'), '#333333', 'white', 2)
        self.create_button('.', buttons_layout, 4, 2, self.decimal_pressed, '#333333', 'white')
        self.create_button('=', buttons_layout, 4, 3, self.equals_pressed, '#ff9500', 'white')
    
    def create_button(self, text, layout, row, col, callback, bg_color, text_color, col_span=1):
        """버튼 생성 헬퍼 함수"""
        button = CustomButton(text, bg_color=bg_color, text_color=text_color)
        button.setMinimumSize(70, 70)
        button.clicked.connect(callback)
        layout.addWidget(button, row, col, 1, col_span)
        return button
    
    def number_pressed(self, number):
        """숫자 버튼 누를 때 호출"""
        if self.reset_next_input:
            self.current_number = number
            self.reset_next_input = False
        elif self.current_number == '0':
            self.current_number = number
        else:
            # 숫자가 너무 길어지지 않도록 제한
            if len(self.current_number) < 9:
                self.current_number += number
        
        self.update_display()
    
    def decimal_pressed(self):
        """소수점 버튼 누를 때 호출"""
        if self.reset_next_input:
            self.current_number = '0.'
            self.reset_next_input = False
        elif '.' not in self.current_number:
            self.current_number += '.'
        
        self.update_display()
    
    def operation_pressed(self, operation):
        """연산 버튼(+, -, ×, ÷) 누를 때 호출"""
        if self.stored_number is not None and not self.reset_next_input:
            self.calculate()
        
        self.last_operation = operation
        self.stored_number = self.current_number
        self.reset_next_input = True
    
    def equals_pressed(self):
        """등호(=) 버튼 누를 때 호출"""
        self.calculate()
    
    def clear_all(self):
        """AC 버튼 누를 때 호출"""
        self.current_number = '0'
        self.stored_number = None
        self.last_operation = None
        self.reset_next_input = False
        self.update_display()
    
    def negate(self):
        """+/- 버튼 누를 때 호출"""
        if self.current_number != '0':
            if self.current_number.startswith('-'):
                self.current_number = self.current_number[1:]
            else:
                self.current_number = '-' + self.current_number
            self.update_display()
    
    def percentage(self):
        """% 버튼 누를 때 호출"""
        try:
            value = float(self.current_number)
            value = value / 100.0
            self.current_number = str(value)
            self.update_display()
        except:
            self.current_number = 'Error'
            self.update_display()
    
    def update_display(self):
        """계산기 디스플레이 업데이트"""
        # 숫자를 적절한 형식으로 표시
        try:
            value = float(self.current_number)
            # 정수인 경우 소수점 제거
            if value.is_integer():
                display_text = str(int(value))
            else:
                display_text = self.current_number
                
            # 너무 큰 숫자는 지수 표기법으로 변환
            if len(display_text) > 9 and '.' in display_text:
                value = float(self.current_number)
                display_text = '{:.6g}'.format(value)
                
        except ValueError:
            display_text = self.current_number
            
        # 글꼴 크기 조정
        if len(display_text) > 9:
            self.result_display.setFont(QFont('Arial', 40))
        elif len(display_text) > 6:
            self.result_display.setFont(QFont('Arial', 50))
        else:
            self.result_display.setFont(QFont('Arial', 60))
            
        self.result_display.setText(display_text)
    
    def calculate(self):
        """
        사칙연산 구현
        """
        if self.last_operation is None or self.stored_number is None:
            return
        
        try:
            num1 = float(self.stored_number)
            num2 = float(self.current_number)
            
            if self.last_operation == '+':
                result = num1 + num2
            elif self.last_operation == '-':
                result = num1 - num2
            elif self.last_operation == '×':
                result = num1 * num2
            elif self.last_operation == '÷':
                if num2 == 0:
                    self.current_number = 'Error'
                    self.update_display()
                    return
                result = num1 / num2
            
            # 결과가 정수면 소수점 제거
            if result == int(result):
                result = int(result)
            
            self.current_number = str(result)
            self.stored_number = self.current_number
            self.last_operation = None
            self.update_display()
            self.reset_next_input = True
            
        except ValueError:
            self.current_number = 'Error'
            self.update_display()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calculator = CalculatorApp()
    calculator.show()
    sys.exit(app.exec_())