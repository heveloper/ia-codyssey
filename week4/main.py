#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
화성 기지 미션 컴퓨터를 위한 더미 센서 클래스 구현
"""

import random
import datetime


class DummySensor:
    """화성 기지의 환경 값을 모니터링하기 위한 더미 센서 클래스"""

    def __init__(self):
        """DummySensor 클래스 초기화"""
        self.env_values = {
            'mars_base_internal_temperature': 0,
            'mars_base_external_temperature': 0,
            'mars_base_internal_humidity': 0,
            'mars_base_external_illuminance': 0,
            'mars_base_internal_co2': 0,
            'mars_base_internal_oxygen': 0
        }

    def set_env(self):
        """
        환경 값을 임의로 생성하여 env_values 사전에 저장
        각 값은 지정된 범위 내에서 무작위로 생성됨
        """
        self.env_values['mars_base_internal_temperature'] = round(random.uniform(18, 30), 2)
        self.env_values['mars_base_external_temperature'] = round(random.uniform(0, 21), 2)
        self.env_values['mars_base_internal_humidity'] = round(random.uniform(50, 60), 2)
        self.env_values['mars_base_external_illuminance'] = round(random.uniform(500, 715), 2)
        self.env_values['mars_base_internal_co2'] = round(random.uniform(0.02, 0.1), 4)
        self.env_values['mars_base_internal_oxygen'] = round(random.uniform(4, 7), 2)

    def get_env(self):
        """
        환경 값을 담고 있는 사전을 반환하고 로그 파일에 기록
        
        Returns:
            dict: 환경 값이 저장된 사전 객체
        """
        # 현재 날짜와 시간 가져오기
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # 로그 파일에 기록
        with open('mars_base_environment.log', 'a') as log_file:
            log_file.write(f'{timestamp}, '
                          f'내부온도: {self.env_values["mars_base_internal_temperature"]}°C, '
                          f'외부온도: {self.env_values["mars_base_external_temperature"]}°C, '
                          f'내부습도: {self.env_values["mars_base_internal_humidity"]}%, '
                          f'외부광량: {self.env_values["mars_base_external_illuminance"]} W/m2, '
                          f'내부CO2: {self.env_values["mars_base_internal_co2"]}%, '
                          f'내부O2: {self.env_values["mars_base_internal_oxygen"]}%\n')
        
        return self.env_values


# DummySensor 클래스의 인스턴스 생성
ds = DummySensor()

# 환경 값 설정 및 출력
ds.set_env()
env_data = ds.get_env()

# 결과 출력
print('화성 기지 환경 데이터:')
print(f'내부 온도: {env_data["mars_base_internal_temperature"]}°C')
print(f'외부 온도: {env_data["mars_base_external_temperature"]}°C')
print(f'내부 습도: {env_data["mars_base_internal_humidity"]}%')
print(f'외부 광량: {env_data["mars_base_external_illuminance"]} W/m2')
print(f'내부 이산화탄소 농도: {env_data["mars_base_internal_co2"]}%')
print(f'내부 산소 농도: {env_data["mars_base_internal_oxygen"]}%')
print('\n환경 데이터가 mars_base_environment.log 파일에 기록되었습니다.')