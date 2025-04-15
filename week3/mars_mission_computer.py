#!/usr/bin/env python3
"""
화성 기지 미션 컴퓨터 - 더미 센서 모듈

화성 기지의 환경 센서 값을 시뮬레이션하기 위한 더미 센서 클래스를 제공합니다.
"""

import random
import datetime


class DummySensor:
    """
    화성 기지의 환경 데이터를 시뮬레이션하는 더미 센서 클래스
    
    랜덤으로 생성된 환경 값을 저장하고 반환하는 기능을 제공합니다.
    """
    
    def __init__(self):
        """
        DummySensor 클래스 초기화
        
        환경 값을 저장할 사전(env_values)을 초기화합니다.
        """
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
        환경 값을 랜덤으로 생성하여 env_values에 설정합니다.
        
        각 환경 값은 지정된 범위 내에서 랜덤하게 생성됩니다.
        """
        # 화성 기지 내부 온도 (18~30도)
        self.env_values['mars_base_internal_temperature'] = round(random.uniform(18, 30), 2)
        
        # 화성 기지 외부 온도 (0~21도)
        self.env_values['mars_base_external_temperature'] = round(random.uniform(0, 21), 2)
        
        # 화성 기지 내부 습도 (50~60%)
        self.env_values['mars_base_internal_humidity'] = round(random.uniform(50, 60), 2)
        
        # 화성 기지 외부 광량 (500~715 W/m2)
        self.env_values['mars_base_external_illuminance'] = round(random.uniform(500, 715), 2)
        
        # 화성 기지 내부 이산화탄소 농도 (0.02~0.1%)
        self.env_values['mars_base_internal_co2'] = round(random.uniform(0.02, 0.1), 4)
        
        # 화성 기지 내부 산소 농도 (4%~7%)
        self.env_values['mars_base_internal_oxygen'] = round(random.uniform(4, 7), 2)
    
    def get_env(self):
        """
        현재 설정된 환경 값을 반환하고, 로그 파일에 기록합니다.
        
        Returns:
            dict: 환경 값이 저장된 사전 객체
        """
        # 현재 날짜와 시간 가져오기
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 로그 파일에 데이터 기록
        try:
            with open('mars_base_sensor_log.txt', 'a') as log_file:
                log_entry = (
                    f"{current_time}, "
                    f"{self.env_values['mars_base_internal_temperature']}°C, "
                    f"{self.env_values['mars_base_external_temperature']}°C, "
                    f"{self.env_values['mars_base_internal_humidity']}%, "
                    f"{self.env_values['mars_base_external_illuminance']} W/m2, "
                    f"{self.env_values['mars_base_internal_co2']}%, "
                    f"{self.env_values['mars_base_internal_oxygen']}%\n"
                )
                log_file.write(log_entry)
        except Exception as e:
            print(f'로그 파일 기록 중 오류 발생: {e}')
        
        return self.env_values


def print_env_values(values):
    """
    환경 값을 보기 좋게 출력합니다.
    
    Args:
        values (dict): 출력할 환경 값이 저장된 사전 객체
    """
    print('\n화성 기지 환경 센서 데이터')
    print('=' * 50)
    print(f"내부 온도: {values['mars_base_internal_temperature']}°C")
    print(f"외부 온도: {values['mars_base_external_temperature']}°C")
    print(f"내부 습도: {values['mars_base_internal_humidity']}%")
    print(f"외부 광량: {values['mars_base_external_illuminance']} W/m2")
    print(f"내부 CO2 농도: {values['mars_base_internal_co2']}%")
    print(f"내부 산소 농도: {values['mars_base_internal_oxygen']}%")
    print('=' * 50)


def main():
    """
    메인 함수: DummySensor 인스턴스를 생성하고 테스트합니다.
    """
    print('화성 기지 미션 컴퓨터 - 환경 센서 테스트')
    
    # DummySensor 인스턴스 생성
    ds = DummySensor()
    
    # 환경 값 설정
    ds.set_env()
    
    # 환경 값 가져오기 및 출력
    env_data = ds.get_env()
    print_env_values(env_data)
    
    print('\n로그 파일이 mars_base_sensor_log.txt에 기록되었습니다.')


if __name__ == '__main__':
    main()