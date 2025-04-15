#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import random
import threading  # 시스템 중지를 위한 쓰레드
import sys  # 입력 감지를 위한 모듈
import platform  # 시스템 정보를 가져오기 위한 모듈
import os  # 시스템 정보를 가져오기 위한 모듈


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
        
        # 보너스 과제 - 설정 파일 로드
        self.설정 = self._설정_파일_로드()
        
    def _설정_파일_로드(self):
        """설정 파일을 로드하여 출력할 정보 항목을 결정합니다."""
        기본_설정 = {
            'system_info': ['os', 'os_version', 'cpu_type', 'cpu_cores', 'memory_size'],
            'load_info': ['cpu_usage', 'memory_usage']
        }
        
        try:
            with open('setting.txt', 'r') as 파일:
                라인들 = 파일.readlines()
                설정 = {'system_info': [], 'load_info': []}
                
                현재_섹션 = None
                for 라인 in 라인들:
                    라인 = 라인.strip()
                    if not 라인 or 라인.startswith('#'):
                        continue
                    
                    if 라인 == '[system_info]':
                        현재_섹션 = 'system_info'
                    elif 라인 == '[load_info]':
                        현재_섹션 = 'load_info'
                    elif 현재_섹션:
                        설정[현재_섹션].append(라인)
                
                # 설정 파일에 항목이 없을 경우 기본값 사용
                if not 설정['system_info']:
                    설정['system_info'] = 기본_설정['system_info']
                if not 설정['load_info']:
                    설정['load_info'] = 기본_설정['load_info']
                    
                return 설정
        except FileNotFoundError:
            # 설정 파일이 없으면 기본 설정을 만들고 저장
            with open('setting.txt', 'w') as 파일:
                파일.write('# 미션 컴퓨터 정보 출력 설정\n\n')
                파일.write('[system_info]\n')
                for 항목 in 기본_설정['system_info']:
                    파일.write(f'{항목}\n')
                파일.write('\n[load_info]\n')
                for 항목 in 기본_설정['load_info']:
                    파일.write(f'{항목}\n')
            
            return 기본_설정
        except Exception as e:
            print(f'설정 파일 로드 중 오류 발생: {e}')
            return 기본_설정
        
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
        
    def get_mission_computer_info(self):
        """
        미션 컴퓨터의 시스템 정보를 가져옵니다.
        - 운영체계
        - 운영체계 버전
        - CPU 타입
        - CPU 코어 수
        - 메모리 크기
        """
        try:
            # 설정에 따라 출력할 항목 결정
            정보 = {}
            
            # 운영체계 및 버전 정보
            if 'os' in self.설정['system_info']:
                정보['운영체계'] = platform.system()
            if 'os_version' in self.설정['system_info']:
                정보['운영체계_버전'] = platform.version()
            
            # CPU 정보 (타입 및 코어 수)
            if 'cpu_type' in self.설정['system_info']:
                try:
                    if platform.system() == 'Windows':
                        정보['CPU_타입'] = platform.processor()
                    elif platform.system() == 'Darwin':  # macOS
                        import subprocess
                        cmd = 'sysctl -n machdep.cpu.brand_string'
                        정보['CPU_타입'] = subprocess.check_output(cmd, shell=True).decode().strip()
                    else:  # Linux
                        try:
                            with open('/proc/cpuinfo', 'r') as f:
                                for line in f:
                                    if line.startswith('model name'):
                                        정보['CPU_타입'] = line.split(':')[1].strip()
                                        break
                        except:
                            정보['CPU_타입'] = platform.machine()
                except Exception:
                    정보['CPU_타입'] = platform.machine()
            
            if 'cpu_cores' in self.설정['system_info']:
                정보['CPU_코어_수'] = os.cpu_count()  # 논리적 코어 수
            
            # 메모리 정보
            if 'memory_size' in self.설정['system_info']:
                try:
                    # Windows 시스템에서 메모리 정보 가져오기
                    if platform.system() == 'Windows':
                        import ctypes
                        kernel32 = ctypes.windll.kernel32
                        c_ulong = ctypes.c_ulong
                        
                        class MEMORYSTATUS(ctypes.Structure):
                            _fields_ = [
                                ('dwLength', c_ulong),
                                ('dwMemoryLoad', c_ulong),
                                ('dwTotalPhys', c_ulong),
                                ('dwAvailPhys', c_ulong),
                                ('dwTotalPageFile', c_ulong),
                                ('dwAvailPageFile', c_ulong),
                                ('dwTotalVirtual', c_ulong),
                                ('dwAvailVirtual', c_ulong)
                            ]
                            
                        memory_status = MEMORYSTATUS()
                        memory_status.dwLength = ctypes.sizeof(MEMORYSTATUS)
                        kernel32.GlobalMemoryStatus(ctypes.byref(memory_status))
                        
                        # 메모리 크기를 GB로 변환
                        메모리_GB = memory_status.dwTotalPhys / (1024**3)
                        정보['메모리_크기_GB'] = round(메모리_GB, 2)
                        
                    # Linux 시스템에서 메모리 정보 가져오기
                    elif platform.system() == 'Linux':
                        try:
                            with open('/proc/meminfo', 'r') as f:
                                for line in f:
                                    if line.startswith('MemTotal'):
                                        # MemTotal 형식: "MemTotal:       16384516 kB"
                                        메모리_KB = int(line.split()[1])
                                        메모리_GB = 메모리_KB / (1024**2)  # KB -> GB
                                        정보['메모리_크기_GB'] = round(메모리_GB, 2)
                                        break
                        except:
                            정보['메모리_크기_GB'] = '알 수 없음 (Linux)'
                            
                    # macOS 시스템에서 메모리 정보 가져오기
                    elif platform.system() == 'Darwin':  # macOS
                        import subprocess
                        cmd = 'sysctl -n hw.memsize'
                        메모리_바이트 = int(subprocess.check_output(cmd, shell=True).decode().strip())
                        메모리_GB = 메모리_바이트 / (1024**3)
                        정보['메모리_크기_GB'] = round(메모리_GB, 2)
                        
                    else:
                        정보['메모리_크기_GB'] = '알 수 없음 (지원되지 않는 OS)'
                        
                except Exception as e:
                    정보['메모리_크기_GB'] = f'알 수 없음 (오류: {str(e)})'
            
            # JSON 형식으로 출력
            print("\n=== 미션 컴퓨터 정보 ===")
            print(json.dumps(정보, indent=4, ensure_ascii=False))
            print("=====================\n")
            
            return 정보
            
        except Exception as e:
            print(f"시스템 정보 가져오기 실패: {e}")
            return {'오류': str(e)}
    
    def get_mission_computer_load(self):
        """
        미션 컴퓨터의 실시간 부하 정보를 가져옵니다.
        - CPU 실시간 사용량
        - 메모리 실시간 사용량
        """
        try:
            # 설정에 따라 출력할 항목 결정
            부하_정보 = {}
            
            # CPU 사용량 (기본 라이브러리만으로 추정)
            if 'cpu_usage' in self.설정['load_info']:
                try:
                    # 간단한 CPU 부하 추정 (더 정확한 방법은 psutil 라이브러리 필요)
                    import threading
                    
                    # CPU 사용 시간 측정을 위한 함수
                    def 계산_작업():
                        시작_시간 = time.time()
                        while time.time() - 시작_시간 < 0.5:
                            # CPU를 사용하는 작업 수행
                            _ = [i * i for i in range(10000)]
                    
                    # CPU 사용량 측정 시작
                    시작_시간 = time.time()
                    계산_스레드 = threading.Thread(target=계산_작업)
                    계산_스레드.start()
                    계산_스레드.join()
                    걸린_시간 = time.time() - 시작_시간
                    
                    # CPU 사용량 추정 (간단한 방법)
                    # 0.5초의 작업을 수행하는 데 걸린 실제 시간에 따라 사용량 추정
                    # CPU가 100% 사용되면 이론적으로 0.5초가 걸림
                    # CPU가 50% 사용되면 약 1초가 걸림 (다른 작업과 공유)
                    사용량_추정 = min(100, (0.5 / 걸린_시간) * 100) if 걸린_시간 > 0 else 0
                    부하_정보['CPU_사용량_%'] = round(사용량_추정, 1)
                    
                except Exception as e:
                    부하_정보['CPU_사용량_%'] = f'측정 불가 (오류: {str(e)})'
            
            # 메모리 사용량 (간단한 추정)
            if 'memory_usage' in self.설정['load_info']:
                try:
                    if platform.system() == 'Windows':
                        import ctypes
                        kernel32 = ctypes.windll.kernel32
                        c_ulong = ctypes.c_ulong
                        
                        class MEMORYSTATUS(ctypes.Structure):
                            _fields_ = [
                                ('dwLength', c_ulong),
                                ('dwMemoryLoad', c_ulong),  # 메모리 사용 비율
                                ('dwTotalPhys', c_ulong),
                                ('dwAvailPhys', c_ulong),
                                ('dwTotalPageFile', c_ulong),
                                ('dwAvailPageFile', c_ulong),
                                ('dwTotalVirtual', c_ulong),
                                ('dwAvailVirtual', c_ulong)
                            ]
                            
                        memory_status = MEMORYSTATUS()
                        memory_status.dwLength = ctypes.sizeof(MEMORYSTATUS)
                        kernel32.GlobalMemoryStatus(ctypes.byref(memory_status))
                        
                        부하_정보['메모리_사용량_%'] = memory_status.dwMemoryLoad
                        부하_정보['메모리_사용량_GB'] = round((memory_status.dwTotalPhys - memory_status.dwAvailPhys) / (1024**3), 2)
                        부하_정보['메모리_여유_GB'] = round(memory_status.dwAvailPhys / (1024**3), 2)
                        
                    elif platform.system() == 'Linux':
                        try:
                            메모리_총량 = 0
                            메모리_여유량 = 0
                            
                            with open('/proc/meminfo', 'r') as f:
                                for line in f:
                                    if line.startswith('MemTotal'):
                                        메모리_총량 = int(line.split()[1])
                                    elif line.startswith('MemAvailable') or line.startswith('MemFree'):
                                        # MemAvailable가 있으면 사용, 없으면 MemFree 사용
                                        if line.startswith('MemAvailable') or 메모리_여유량 == 0:
                                            메모리_여유량 = int(line.split()[1])
                                
                            if 메모리_총량 > 0:
                                메모리_사용_비율 = ((메모리_총량 - 메모리_여유량) / 메모리_총량) * 100
                                부하_정보['메모리_사용량_%'] = round(메모리_사용_비율, 1)
                                부하_정보['메모리_사용량_GB'] = round((메모리_총량 - 메모리_여유량) / (1024**2), 2)
                                부하_정보['메모리_여유_GB'] = round(메모리_여유량 / (1024**2), 2)
                            else:
                                부하_정보['메모리_사용량_%'] = '측정 불가 (Linux)'
                        except:
                            부하_정보['메모리_사용량_%'] = '측정 불가 (Linux)'
                            
                    elif platform.system() == 'Darwin':  # macOS
                        try:
                            import subprocess
                            # 총 메모리 크기
                            cmd_total = 'sysctl -n hw.memsize'
                            메모리_총_바이트 = int(subprocess.check_output(cmd_total, shell=True).decode().strip())
                            
                            # vm_stat으로 메모리 사용량 확인
                            cmd_usage = 'vm_stat'
                            vm_stat_출력 = subprocess.check_output(cmd_usage, shell=True).decode().strip()
                            lines = vm_stat_출력.split('\n')
                            
                            # 페이지 크기와 여유 페이지 수 추출
                            page_size = 4096  # 기본값, 변경될 수 있음
                            free_pages = 0
                            
                            for line in lines:
                                if 'page size of' in line:
                                    try:
                                        page_size = int(line.split()[-1])
                                    except:
                                        pass
                                elif 'Pages free' in line:
                                    try:
                                        free_pages = int(line.split(':')[1].strip().replace('.', ''))
                                    except:
                                        pass
                            
                            메모리_여유_바이트 = free_pages * page_size
                            메모리_사용_바이트 = 메모리_총_바이트 - 메모리_여유_바이트
                            
                            부하_정보['메모리_사용량_%'] = round((메모리_사용_바이트 / 메모리_총_바이트) * 100, 1)
                            부하_정보['메모리_사용량_GB'] = round(메모리_사용_바이트 / (1024**3), 2)
                            부하_정보['메모리_여유_GB'] = round(메모리_여유_바이트 / (1024**3), 2)
                        except:
                            부하_정보['메모리_사용량_%'] = '측정 불가 (macOS)'
                    else:
                        부하_정보['메모리_사용량_%'] = '측정 불가 (지원되지 않는 OS)'
                        
                except Exception as e:
                    부하_정보['메모리_사용량_%'] = f'측정 불가 (오류: {str(e)})'
            
            # JSON 형식으로 출력
            print("\n=== 미션 컴퓨터 부하 ===")
            print(json.dumps(부하_정보, indent=4, ensure_ascii=False))
            print("=====================\n")
            
            return 부하_정보
            
        except Exception as e:
            print(f"시스템 부하 정보 가져오기 실패: {e}")
            return {'오류': str(e)}


# MissionComputer 클래스의 인스턴스를 생성하고 모니터링 시작
if __name__ == '__main__':
    try:
        print("화성 미션 컴퓨터 시작 중...")
        
        # 미션 컴퓨터 인스턴스 생성
        실행_컴퓨터 = MissionComputer()
        
        # 시스템 정보 및 부하 정보 출력
        실행_컴퓨터.get_mission_computer_info()
        실행_컴퓨터.get_mission_computer_load()
        
        print("\n환경 모니터링 시작...")
        print("시스템을 중지하려면 'q'를 입력하세요")
        
        # 센서 데이터 모니터링 시작
        실행_컴퓨터.get_sensor_data()
    except Exception as e:
        print(f"오류 발생: {e}")