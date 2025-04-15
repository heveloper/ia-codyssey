#!/usr/bin/env python3
"""
화성 기지 인벤토리 관리자

이 스크립트는 인벤토리 목록을 읽고, 인화성 순으로 정렬하며,
위험 물질을 식별하고 결과를 내보냅니다.
"""

import csv
import os
import struct


def read_csv_file(file_path):
    """
    CSV 파일을 읽고 그 내용을 딕셔너리 리스트로 반환합니다.
    
    Args:
        file_path (str): CSV 파일 경로
        
    Returns:
        list: CSV 데이터를 포함하는 딕셔너리 리스트
    
    Raises:
        FileNotFoundError: 지정된 파일이 존재하지 않는 경우
        Exception: 파일 읽기 중 발생하는 다른 모든 오류
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            # 각 행을 딕셔너리로 변환하고 리스트에 저장
            data = []
            for row in reader:
                # 올바른 정렬을 위해 인화성을 float로 변환
                row['Flammability'] = float(row['Flammability'])
                data.append(row)
            return data
    except FileNotFoundError:
        print(f'오류: 파일 {file_path}을(를) 찾을 수 없습니다.')
        return []
    except Exception as e:
        print(f'파일 읽기 오류: {str(e)}')
        return []


def sort_by_flammability(inventory_list):
    """
    인벤토리 목록을 인화성 순으로 내림차순 정렬합니다.
    
    Args:
        inventory_list (list): 인벤토리 데이터를 포함하는 딕셔너리 리스트
        
    Returns:
        list: 정렬된 딕셔너리 리스트
    """
    return sorted(inventory_list, key=lambda x: x['Flammability'], reverse=True)


def filter_dangerous_items(inventory_list, threshold=0.7):
    """
    인화성이 임계값 이상인 항목을 필터링합니다.
    
    Args:
        inventory_list (list): 인벤토리 데이터를 포함하는 딕셔너리 리스트
        threshold (float): 인화성 임계값 (기본값 0.7)
        
    Returns:
        list: 필터링된 딕셔너리 리스트
    """
    return [item for item in inventory_list if item['Flammability'] >= threshold]


def write_csv_file(data, file_path, fieldnames=None):
    """
    데이터를 CSV 파일에 씁니다.
    
    Args:
        data (list): CSV에 쓸 딕셔너리 리스트
        file_path (str): 출력 파일 경로
        fieldnames (list): CSV 헤더의 필드 이름 리스트 (선택 사항)
        
    Returns:
        bool: 쓰기 성공 시 True, 그렇지 않으면 False
    """
    try:
        if not fieldnames and data:
            fieldnames = data[0].keys()
            
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception as e:
        print(f'파일 {file_path}에 쓰기 오류: {str(e)}')
        return False


def write_binary_file(data, file_path):
    """
    인벤토리 데이터를 이진 파일에 씁니다.
    
    Args:
        data (list): 인벤토리 데이터를 포함하는 딕셔너리 리스트
        file_path (str): 출력 이진 파일 경로
        
    Returns:
        bool: 쓰기 성공 시 True, 그렇지 않으면 False
    """
    try:
        with open(file_path, 'wb') as file:
            # 레코드 수 쓰기
            file.write(struct.pack('I', len(data)))
            
            for item in data:
                # 물질 이름 쓰기 (길이 접두사 포함)
                substance = item['Substance'].encode('utf-8')
                file.write(struct.pack('I', len(substance)))
                file.write(substance)
                
                # 무게를 문자열로 쓰기 (길이 접두사 포함)
                weight = item['Weight (g/cm³)'].encode('utf-8')
                file.write(struct.pack('I', len(weight)))
                file.write(weight)
                
                # 비중을 문자열로 쓰기 (길이 접두사 포함)
                gravity = item['Specific Gravity'].encode('utf-8')
                file.write(struct.pack('I', len(gravity)))
                file.write(gravity)
                
                # 강도를 문자열로 쓰기 (길이 접두사 포함)
                strength = item['Strength'].encode('utf-8')
                file.write(struct.pack('I', len(strength)))
                file.write(strength)
                
                # 인화성을 float로 쓰기
                file.write(struct.pack('f', item['Flammability']))
        return True
    except Exception as e:
        print(f'이진 파일 {file_path}에 쓰기 오류: {str(e)}')
        return False


def read_binary_file(file_path):
    """
    이진 파일에서 인벤토리 데이터를 읽습니다.
    
    Args:
        file_path (str): 이진 파일 경로
        
    Returns:
        list: 인벤토리 데이터를 포함하는 딕셔너리 리스트
    """
    data = []
    try:
        with open(file_path, 'rb') as file:
            # 레코드 수 읽기
            num_records = struct.unpack('I', file.read(4))[0]
            
            for _ in range(num_records):
                item = {}
                
                # 물질 읽기
                str_len = struct.unpack('I', file.read(4))[0]
                item['Substance'] = file.read(str_len).decode('utf-8')
                
                # 무게 읽기
                str_len = struct.unpack('I', file.read(4))[0]
                item['Weight (g/cm³)'] = file.read(str_len).decode('utf-8')
                
                # 비중 읽기
                str_len = struct.unpack('I', file.read(4))[0]
                item['Specific Gravity'] = file.read(str_len).decode('utf-8')
                
                # 강도 읽기
                str_len = struct.unpack('I', file.read(4))[0]
                item['Strength'] = file.read(str_len).decode('utf-8')
                
                # 인화성 읽기
                item['Flammability'] = struct.unpack('f', file.read(4))[0]
                
                data.append(item)
        return data
    except FileNotFoundError:
        print(f'오류: 이진 파일 {file_path}을(를) 찾을 수 없습니다.')
        return []
    except Exception as e:
        print(f'이진 파일 읽기 오류: {str(e)}')
        return []


def print_inventory(inventory_list):
    """
    인벤토리 항목을 형식에 맞게 출력합니다.
    
    Args:
        inventory_list (list): 인벤토리 데이터를 포함하는 딕셔너리 리스트
    """
    if not inventory_list:
        print('표시할 인벤토리 항목이 없습니다.')
        return
    
    # 더 나은 형식을 위한 열 너비 정의
    col_widths = {
        'Substance': 25,
        'Weight (g/cm³)': 15,
        'Specific Gravity': 18,
        'Strength': 15,
        'Flammability': 12
    }
    
    # 헤더 출력
    header = '|'.join(
        f' {name:<{col_widths[name]}} '
        for name in col_widths.keys()
    )
    separator = '+'.join(
        '-' * (col_widths[name] + 2)
        for name in col_widths.keys()
    )
    
    print(separator)
    print(header)
    print(separator)
    
    # 각 항목 출력
    for item in inventory_list:
        row = '|'.join(
            f' {str(item[name]):<{col_widths[name]}} '
            for name in col_widths.keys()
        )
        print(row)
    
    print(separator)
    print(f'총 항목 수: {len(inventory_list)}')


def main():
    """스크립트를 실행하는 메인 함수입니다."""
    input_file = 'Mars_Base_Inventory_List.csv'
    dangerous_output_file = 'Mars_Base_Inventory_danger.csv'
    binary_output_file = 'Mars_Base_Inventory_List.bin'
    
    print('화성 기지 인벤토리 목록을 읽는 중...')
    inventory_list = read_csv_file(input_file)
    
    if not inventory_list:
        print('인벤토리 데이터가 없습니다. 종료합니다.')
        return
    
    print('\n원본 인벤토리 목록:')
    print_inventory(inventory_list)
    
    # 인화성으로 정렬
    sorted_inventory = sort_by_flammability(inventory_list)
    print('\n인화성 순으로 정렬된 인벤토리 (높은 순에서 낮은 순):')
    print_inventory(sorted_inventory)
    
    # 위험 항목 필터링
    dangerous_items = filter_dangerous_items(sorted_inventory)
    print('\n위험 항목 (인화성 >= 0.7):')
    print_inventory(dangerous_items)
    
    # 위험 항목을 CSV에 쓰기
    if write_csv_file(dangerous_items, dangerous_output_file):
        print(f'\n위험 항목이 {dangerous_output_file}에 저장되었습니다')
    
    # 보너스 작업
    if write_binary_file(sorted_inventory, binary_output_file):
        print(f'\n정렬된 인벤토리가 이진 파일 {binary_output_file}에 저장되었습니다')
    
    print('\n이진 파일에서 데이터 읽는 중:')
    binary_data = read_binary_file(binary_output_file)
    print_inventory(binary_data)
    
    print('\n텍스트 vs 이진 파일 비교:')
    print('''
    텍스트 파일 (CSV):
    - 장점:
      * 사람이 읽을 수 있고 텍스트 편집기로 편집 가능
      * 다른 시스템 간에 이식성이 좋음
      * 표준 라이브러리로 쉽게 파싱 가능
      * 스프레드시트 프로그램으로 쉽게 가져올 수 있음
    
    - 단점:
      * 저장 효율성이 낮음 (특히 숫자 데이터의 경우)
      * 대용량 데이터셋의 경우 읽기/쓰기가 느림
      * 숫자 값의 파싱/변환이 필요함
      * 특수 문자와 인코딩에 문제가 있을 수 있음
    
    이진 파일:
    - 장점:
      * 더 컴팩트한 저장
      * 더 빠른 읽기/쓰기 작업
      * 정확한 숫자 표현을 보존
      * 복잡한 데이터 구조를 효율적으로 저장 가능
    
    - 단점:
      * 특수 도구 없이는 사람이 읽을 수 없음
      * 이식성이 낮음 (엔디안에 영향을 받을 수 있음)
      * 읽기/쓰기에 사용자 정의 코드 필요
      * 수동으로 디버깅하고 수정하기 어려움
    
    화성 기지 인벤토리의 경우, 이진 형식은 기계 처리에 더 효율적이고,
    CSV는 사람의 검사와 다른 시스템이나 팀원과의 공유에 더 좋습니다.
    ''')


if __name__ == '__main__':
    main()