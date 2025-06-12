import zipfile
import time
import itertools
import string


def unlock_zip():
    """
    emergency_storage_key.zip 파일의 암호를 찾는 함수
    암호는 숫자와 소문자 알파벳으로 구성된 6자리 문자
    """
    zip_filename = 'emergency_storage_key.zip'
    password_file = 'password.txt'
    
    # 가능한 문자 집합 (숫자 + 소문자)
    characters = string.digits + string.ascii_lowercase
    password_length = 6
    
    print('=== 화성 기지 Emergency Storage 해킹 시작 ===')
    print(f'대상 파일: {zip_filename}')
    print(f'암호 길이: {password_length}자리')
    print(f'사용 문자: {characters}')
    print(f'총 가능한 조합 수: {len(characters)**password_length:,}개')
    print()
    
    start_time = time.time()
    attempt_count = 0
    
    try:
        # ZIP 파일 열기
        with zipfile.ZipFile(zip_filename, 'r') as zip_file:
            print('ZIP 파일을 성공적으로 열었습니다.')
            print('암호 해독을 시작합니다...')
            print()
            
            # 모든 가능한 조합 시도
            for password_tuple in itertools.product(characters, repeat=password_length):
                password = ''.join(password_tuple)
                attempt_count += 1
                
                # 진행상황 출력 (1000번마다)
                if attempt_count % 1000 == 0:
                    elapsed_time = time.time() - start_time
                    print(f'시도 횟수: {attempt_count:,} | '
                          f'현재 암호: {password} | '
                          f'경과 시간: {elapsed_time:.2f}초')
                
                try:
                    # 암호 시도
                    zip_file.setpassword(password.encode('utf-8'))
                    
                    # 첫 번째 파일을 읽어보기 시도
                    file_list = zip_file.namelist()
                    if file_list:
                        zip_file.read(file_list[0])
                    
                    # 성공한 경우
                    end_time = time.time()
                    total_time = end_time - start_time
                    
                    print()
                    print('=' * 50)
                    print('🎉 암호 해독 성공! 🎉')
                    print(f'발견된 암호: {password}')
                    print(f'총 시도 횟수: {attempt_count:,}회')
                    print(f'총 소요 시간: {total_time:.2f}초')
                    print(f'초당 시도 횟수: {attempt_count/total_time:.0f}회/초')
                    print('=' * 50)
                    
                    # 암호를 파일에 저장
                    try:
                        with open(password_file, 'w', encoding='utf-8') as f:
                            f.write(password)
                        print(f'암호가 {password_file} 파일에 저장되었습니다.')
                        
                        # ZIP 파일 내용 확인
                        print()
                        print('ZIP 파일 내용:')
                        for file_info in zip_file.filelist:
                            print(f'  - {file_info.filename} ({file_info.file_size} bytes)')
                        
                    except IOError as e:
                        print(f'암호 파일 저장 중 오류 발생: {e}')
                    
                    return password
                    
                except (RuntimeError, zipfile.BadZipFile):
                    # 잘못된 암호인 경우 계속 진행
                    continue
                except Exception as e:
                    print(f'예상치 못한 오류 발생: {e}')
                    continue
            
            # 모든 조합을 시도했지만 암호를 찾지 못한 경우
            print('모든 가능한 조합을 시도했지만 암호를 찾을 수 없습니다.')
            return None
            
    except FileNotFoundError:
        print(f'오류: {zip_filename} 파일을 찾을 수 없습니다.')
        print('emergency_storage_key.zip 파일이 현재 디렉토리에 있는지 확인해주세요.')
        return None
    except zipfile.BadZipFile:
        print(f'오류: {zip_filename}이 유효한 ZIP 파일이 아닙니다.')
        return None
    except Exception as e:
        print(f'예상치 못한 오류 발생: {e}')
        return None


def unlock_zip_optimized():
    """
    보너스 - 최적화된 암호 해독 함수
    일반적으로 많이 사용되는 패턴부터 시도하여 속도를 향상시킴
    """
    zip_filename = 'emergency_storage_key.zip'
    password_file = 'password_optimized.txt'
    
    print('=== 최적화된 암호 해독 시작 ===')
    
    # 일반적인 패턴들을 우선 시도
    common_patterns = [
        # 숫자만
        ['123456', '000000', '111111', '987654', '654321'],
        # 일반적인 패턴
        ['abc123', 'pass12', '123abc', 'admin1'],
        # 년도 관련
        ['2024ab', '2025ab', '2023ab'],
    ]
    
    start_time = time.time()
    attempt_count = 0
    
    try:
        with zipfile.ZipFile(zip_filename, 'r') as zip_file:
            # 1단계: 일반적인 패턴 먼저 시도
            print('1단계: 일반적인 패턴 시도 중...')
            for pattern_group in common_patterns:
                for password in pattern_group:
                    if len(password) == 6:
                        attempt_count += 1
                        try:
                            zip_file.setpassword(password.encode('utf-8'))
                            file_list = zip_file.namelist()
                            if file_list:
                                zip_file.read(file_list[0])
                            
                            # 성공
                            end_time = time.time()
                            print(f'🎉 최적화 방법으로 빠르게 발견! 암호: {password}')
                            print(f'시도 횟수: {attempt_count}회, 소요 시간: {end_time - start_time:.2f}초')
                            
                            with open(password_file, 'w') as f:
                                f.write(password)
                            return password
                            
                        except (RuntimeError, zipfile.BadZipFile):
                            continue
            
            # 2단계: 일반적인 brute force 진행
            print('2단계: 전체 조합 시도 중...')
            return unlock_zip()  # 기본 방법으로 진행
            
    except Exception as e:
        print(f'최적화된 방법 실행 중 오류: {e}')
        return unlock_zip()  # 기본 방법으로 fallback


if __name__ == '__main__':
    print('화성 기지 Emergency Storage 해킹 프로그램')
    print('=' * 60)
    
    # 기본 해킹 시도
    result = unlock_zip()
    
    if result:
        print(f'\n✅ 미션 완료! Emergency Storage의 암호는 "{result}"입니다.')
        print('이제 화성 기지의 비상 저장고에 접근할 수 있습니다!')
    else:
        print('\n❌ 미션 실패. 암호를 찾을 수 없습니다.')
        
    print('\n보너스 최적화 방법도 시도해보시겠습니까? (y/n): ', end='')
    
    # 간단한 입력 대기 (실제 실행 시에는 input() 사용)
    # choice = input().lower()
    # if choice == 'y':
    #     print('\n=== 보너스: 최적화된 방법 시도 ===')
    #     unlock_zip_optimized()