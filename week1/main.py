def read_log_file(file_path):
    """
    로그 파일을 읽어서 내용을 반환하는 함수
    
    Args:
        file_path (str): 로그 파일 경로
        
    Returns:
        list: 로그 파일의 각 라인을 담고 있는 리스트
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        return lines
    except FileNotFoundError:
        print(f'오류: {file_path} 파일을 찾을 수 없습니다.')
        return []
    except PermissionError:
        print(f'오류: {file_path} 파일에 접근할 권한이 없습니다.')
        return []
    except Exception as e:
        print(f'오류: 파일을 읽는 중 예상치 못한 오류가 발생했습니다. {e}')
        return []

def print_log_content(lines):
    """
    로그 내용을 출력하는 함수
    
    Args:
        lines (list): 로그 파일의 각 라인을 담고 있는 리스트
    """
    if not lines:
        print('로그 내용이 없습니다.')
        return
    
    print('=== 로그 파일 내용 ===')
    for line in lines:
        print(line.strip())  # 줄바꿈 문자 제거 후 출력
    print('=== 로그 파일 끝 ===')

def sort_logs_by_time_reversed(lines):
    """
    로그를 시간 역순으로 정렬하는 함수
    
    Args:
        lines (list): 로그 파일의 각 라인을 담고 있는 리스트
        
    Returns:
        list: 시간 역순으로 정렬된 로그 라인 리스트
    """
    # 헤더 행(첫 줄)을 제외하고 정렬
    if not lines:
        return lines
    
    header = lines[0]
    data_lines = lines[1:]
    
    # CSV 형식의 로그에서 timestamp 열을 기준으로 정렬
    sorted_lines = sorted(
        data_lines,
        key=lambda x: x.split(',')[0] if ',' in x and len(x.split(',')) > 0 else '',
        reverse=True  # 역순 정렬
    )
    
    # 헤더와 정렬된 데이터 라인을 합침
    return [header] + sorted_lines

def save_problematic_logs(lines, output_file):
    """
    문제가 되는 로그 내용만 파일로 저장하는 함수
    
    Args:
        lines (list): 로그 파일의 각 라인을 담고 있는 리스트
        output_file (str): 저장할 파일 경로
    """
    # 문제가 되는 키워드들(로그 분석 후 파악된 문제)
    problem_keywords = ['UNSTABLE', 'EXPLOSION', 'ERROR', 'CRITICAL', 'WARNING', 'FAILURE']
    
    problematic_lines = []
    
    # 헤더 행을 추가
    if lines and ',' in lines[0]:
        problematic_lines.append(lines[0])
    
    for line in lines[1:] if lines else []:
        # 대소문자 구분 없이 키워드가 포함된 라인 찾기
        if any(keyword in line.upper() for keyword in problem_keywords):
            problematic_lines.append(line)
    
    if len(problematic_lines) <= 1:  # 헤더만 있는 경우
        print('문제가 되는 로그 내용이 없습니다.')
        return
    
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.writelines(problematic_lines)
        print(f'문제가 되는 로그가 {output_file}에 저장되었습니다.')
    except Exception as e:
        print(f'오류: 파일을 저장하는 중 예상치 못한 오류가 발생했습니다. {e}')

def main():
    """
    메인 함수
    """
    log_file_path = 'mission_computer_main.log'
    problem_log_file = 'problematic_logs.log'
    
    # 로그 파일 읽기
    log_lines = read_log_file(log_file_path)
    
    if log_lines:
        # 원본 로그 내용 출력
        print('원본 로그 내용:')
        print_log_content(log_lines)
        
        # 시간 역순으로 정렬된 로그 출력
        sorted_log_lines = sort_logs_by_time_reversed(log_lines)
        print('\n시간 역순으로 정렬된 로그 내용:')
        print_log_content(sorted_log_lines)
        
        # 문제가 되는 로그만 파일로 저장
        save_problematic_logs(log_lines, problem_log_file)

if __name__ == '__main__':
    main()