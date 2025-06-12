def caesar_cipher_decode(target_text):
    """
    카이사르 암호를 해독하는 함수
    모든 가능한 시프트 값(0-25)에 대해 해독 결과를 출력
    """
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    results = {}
    
    print('=== 카이사르 암호 해독 결과 ===')
    print(f'원본 텍스트: {target_text}')
    print('-' * 50)
    
    # 모든 가능한 시프트 값에 대해 해독 시도
    for shift in range(26):
        decoded_text = ''
        
        for char in target_text.upper():
            if char in alphabet:
                # 현재 문자의 알파벳 위치 찾기
                current_pos = alphabet.index(char)
                # 시프트만큼 뒤로 이동 (해독이므로 음수)
                new_pos = (current_pos - shift) % 26
                decoded_text += alphabet[new_pos]
            else:
                # 알파벳이 아닌 문자는 그대로 유지
                decoded_text += char
        
        results[shift] = decoded_text
        print(f'시프트 {shift:2d}: {decoded_text}')
    
    print('-' * 50)
    return results


def save_result_to_file(text, shift_number):
    """
    해독된 결과를 result.txt 파일로 저장
    """
    try:
        with open('result.txt', 'w', encoding='utf-8') as file:
            file.write(f'카이사르 암호 해독 결과\n')
            file.write(f'시프트 번호: {shift_number}\n')
            file.write(f'해독된 텍스트: {text}\n')
        print(f'결과가 result.txt 파일로 저장되었습니다.')
    except Exception as e:
        print(f'파일 저장 중 오류가 발생했습니다: {e}')


def check_meaningful_words(text):
    """
    보너스: 의미있는 단어가 포함되어 있는지 확인
    간단한 영어 단어 사전 사용
    """
    common_words = [
        'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER',
        'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW',
        'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WHO', 'BOY', 'DID',
        'CAR', 'EAT', 'FAR', 'FUN', 'GOT', 'LET', 'MAN', 'PUT', 'RUN', 'SAY',
        'SHE', 'TOO', 'USE', 'WAY', 'WIN', 'YES', 'DOOR', 'EMERGENCY', 'STORAGE',
        'KEY', 'MARS', 'BASE', 'STATION', 'UNLOCK', 'ACCESS', 'CODE', 'PASSWORD'
    ]
    
    # 텍스트를 단어로 분리
    words = text.replace(',', ' ').replace('.', ' ').split()
    found_words = []
    
    for word in words:
        if word.upper() in common_words:
            found_words.append(word)
    
    return found_words


def main():
    """
    메인 실행 함수
    """
    try:
        # password.txt 파일 읽기
        with open('password.txt', 'r', encoding='utf-8') as file:
            encrypted_text = file.read().strip()
        
        print(f'password.txt 파일을 성공적으로 읽었습니다.')
        print(f'암호화된 텍스트: {encrypted_text}')
        print()
        
        # 카이사르 암호 해독
        decode_results = caesar_cipher_decode(encrypted_text)
        
        # 보너스: 의미있는 단어 검색
        print('\n=== 의미있는 단어 검색 결과 ===')
        potential_solutions = []
        
        for shift, decoded_text in decode_results.items():
            found_words = check_meaningful_words(decoded_text)
            if found_words:
                potential_solutions.append((shift, decoded_text, found_words))
                print(f'시프트 {shift}: {len(found_words)}개 단어 발견 - {found_words}')
        
        if potential_solutions:
            print(f'\n가능한 해독 결과가 {len(potential_solutions)}개 발견되었습니다!')
            for shift, text, words in potential_solutions:
                print(f'  시프트 {shift}: {text} (단어: {words})')
        
        # 사용자 입력을 통한 최종 선택
        print('\n' + '=' * 50)
        print('위의 결과를 확인하고 올바른 해독 결과의 시프트 번호를 입력하세요.')
        
        while True:
            try:
                shift_choice = int(input('시프트 번호 (0-25): '))
                if 0 <= shift_choice <= 25:
                    selected_result = decode_results[shift_choice]
                    print(f'\n선택된 결과: {selected_result}')
                    
                    # 결과 파일로 저장
                    save_result_to_file(selected_result, shift_choice)
                    break
                else:
                    print('0부터 25 사이의 숫자를 입력해주세요.')
            except ValueError:
                print('올바른 숫자를 입력해주세요.')
            except KeyboardInterrupt:
                print('\n프로그램이 중단되었습니다.')
                break
    
    except FileNotFoundError:
        print('password.txt 파일을 찾을 수 없습니다.')
        print('현재 디렉토리에 password.txt 파일이 있는지 확인해주세요.')
    except Exception as e:
        print(f'파일을 읽는 중 오류가 발생했습니다: {e}')


if __name__ == '__main__':
    main()