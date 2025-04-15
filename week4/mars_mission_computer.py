#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import random
import threading  # 시스템 중지를 위한 쓰레드
import sys  # 입력 감지를 위한 모듈


class DummySensor:
    """
    화성 기지 환경 모니터링을 위한 센서 값 시뮬레이션 클래스
    """
    def __init__(self):
        # 센서 값 범위 초기화
        self.센서_범위 = {
            'mars_base_internal_temperature': (18.0, 25.0),   # 기지 내부 온도 (°C)
            'mars_base_external_temperature': (-80.0, -30.0), # 기지 외부 온도 (°C)
            'mars_base_internal_humidity': (30.0, 50.0),      # 기지 내부 습도 (%)
            'mars_base_external_illuminance': (0.0, 100000.0),# 기지 외부 광량 (lux)
            'mars_base_internal_co2': (300.0, 1200.0),        # 기지 내부 이산화탄소 농도 (ppm)
            'mars_base_internal_oxygen': (19.0, 21.0)         # 기지 내부 산소 농도 (%)
        }

    def 센서값_가져오기(self, 센서_이름):
        """
        특정 센서의 범위 내에서 무작위 값을 생성합니다.
        
        인자:
            센서_이름 (str): 읽을 센서의 이름
            
        반환:
            float: 시뮬레이션된 센서 값
        """
        if 센서_이름 in self.센서_범위:
            최소값, 최대값 = self.센서_범위[센서_이름]
            return round(random.uniform(최소값, 최대값), 2)
        else:
            raise ValueError(f'알 수 없는 센서: {센서_이름}')
            
    def 모든_센서값_가져오기(self):
        """
        모든 센서의 값을 가져옵니다.
        
        반환:
            dict: 모든 센서 값이 담긴 사전
        """
        센서_값들 = {}
        for 센서_이름 in self.센서_범위.keys():
            센서_값들[센서_이름] = self.센서값_가져오기(센서_이름)
        return 센서_값들


class MissionComputer:
    """
    화성 기지 환경 모니터링을 위한 미션 컴퓨터 클래스
    센서 데이터를 수집, 저장, 표시합니다.
    """
    def __init__(self):
        """미션 컴퓨터 초기화 및 환경 값 설정"""
        self.env_values = {
            'mars_base_internal_temperature': 0.0,  # 화성 기지 내부 온도
            'mars_base_external_temperature': 0.0,  # 화성 기지 외부 온도
            'mars_base_internal_humidity': 0.0,     # 화성 기지 내부 습도
            'mars_base_external_illuminance': 0.0,  # 화성 기지 외부 광량 
            'mars_base_internal_co2': 0.0,          # 화성 기지 내부 이산화탄소 농도
            'mars_base_internal_oxygen': 0.0        # 화성 기지 내부 산소 농도
        }
        self.ds = DummySensor()
        
        # 보너스 과제 - 5분 평균을 위한 히스토리 데이터 저장
        self.기록 = {센서: [] for 센서 in self.env_values}
        self.마지막_평균_시간 = time.time()
        
    def get_sensor_data(self):
        """
        센서의 환경 값을 지속적으로 업데이트하고 표시합니다.
        5초마다 업데이트하고 5분마다 평균을 계산합니다.
        'q'를 입력하고 Enter를 누르면 시스템이 중지됩니다.
        """
        # 시스템 중지를 위한 입력 감지 쓰레드 시작
        self.실행중 = True
        입력_쓰레드 = threading.Thread(target=self._중지_입력_확인)
        입력_쓰레드.daemon = True
        입력_쓰레드.start()
        
        try:
            while self.실행중:
                # 현재 센서 값 가져와서 env_values 업데이트
                센서_데이터 = self.ds.모든_센서값_가져오기()
                self.env_values.update(센서_데이터)
                
                # 히스토리 추적을 위한 값 저장 (보너스 과제)
                현재_시간 = time.time()
                for 센서, 값 in 센서_데이터.items():
                    self.기록[센서].append(값)
                
                # 현재 환경 값을 JSON 형태로 출력
                print(json.dumps(self.env_values, indent=4))
                
                # 5분 평균 계산 및 표시 (보너스 과제)
                if 현재_시간 - self.마지막_평균_시간 >= 300:  # 5분 = 300초
                    self._평균_계산_및_표시()
                    self.마지막_평균_시간 = 현재_시간
                
                # 다음 업데이트까지 5초 대기
                time.sleep(5)
                
        except KeyboardInterrupt:
            print('시스템이 중지되었습니다....')
            
    def _중지_입력_확인(self):
        """사용자 입력을 확인하여 시스템을 중지하는 쓰레드 함수"""
        while True:
            사용자_입력 = input("시스템을 중지하려면 'q'를 입력하세요: ")
            if 사용자_입력.lower() == 'q':
                print('시스템이 중지되었습니다....')
                self.실행중 = False
                break
        
    def _평균_계산_및_표시(self):
        """모든 센서에 대한 5분 평균을 계산하고 표시합니다."""
        평균값 = {}
        for 센서, 값_목록 in self.기록.items():
            if 값_목록:
                평균값[센서] = sum(값_목록) / len(값_목록)
            else:
                평균값[센서] = 0.0
                
        print("\n=== 5분 평균 ===")
        print(json.dumps(평균값, indent=4))
        print("==============\n")
        
        # 평균 계산 후 기록 초기화
        self.기록 = {센서: [] for 센서 in self.env_values}


# Create an instance of the MissionComputer class and start monitoring
if __name__ == '__main__':
    try:
        print("Mars Mission Computer Starting...")
        print("Enter 'q' to stop the system")
        
        run_computer = MissionComputer()
        run_computer.get_sensor_data()
    except Exception as e:
        print(f"Error: {e}")