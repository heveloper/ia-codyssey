import os
import datetime
import threading
import time
import csv
try:
    import pyaudio
    import wave
    import speech_recognition as sr
except ImportError:
    print('음성 녹음 및 텍스트 변환을 위해 다음 라이브러리가 필요합니다:')
    print('설치: pip install pyaudio SpeechRecognition')
    exit(1)


class VoiceRecorder:
    """화성에서의 음성 일기 녹음을 위한 클래스"""
    
    def __init__(self):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.recording = False
        self.frames = []
        self.audio = None
        self.stream = None
        self.records_dir = 'records'
        self.recognizer = sr.Recognizer()
        self._ensure_records_directory()
    
    def _ensure_records_directory(self):
        """records 디렉토리가 없으면 생성"""
        if not os.path.exists(self.records_dir):
            os.makedirs(self.records_dir)
            print(f'{self.records_dir} 폴더를 생성했습니다.')
    
    def _get_filename(self):
        """현재 날짜와 시간을 기반으로 파일명 생성"""
        now = datetime.datetime.now()
        filename = now.strftime('%Y%m%d-%H%M%S.wav')
        return os.path.join(self.records_dir, filename)
    
    def _initialize_audio(self):
        """오디오 시스템 초기화"""
        try:
            self.audio = pyaudio.PyAudio()
            return True
        except Exception as e:
            print(f'오디오 시스템 초기화 실패: {e}')
            return False
    
    def _start_recording_stream(self):
        """녹음 스트림 시작"""
        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            return True
        except Exception as e:
            print(f'마이크 접근 실패: {e}')
            return False
    
    def _record_audio_data(self):
        """실제 오디오 데이터 녹음"""
        self.frames = []
        print('녹음 중... (Enter를 눌러 중지)')
        
        while self.recording:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f'녹음 중 오류 발생: {e}')
                break
    
    def _save_recording(self, filename):
        """녹음 데이터를 파일로 저장"""
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.frames))
            return True
        except Exception as e:
            print(f'파일 저장 실패: {e}')
            return False
    
    def _cleanup_audio(self):
        """오디오 리소스 정리"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
    
    def start_recording(self):
        """녹음 시작"""
        if not self._initialize_audio():
            return False
        
        if not self._start_recording_stream():
            self._cleanup_audio()
            return False
        
        self.recording = True
        filename = self._get_filename()
        
        # 별도 스레드에서 녹음 진행
        recording_thread = threading.Thread(target=self._record_audio_data)
        recording_thread.start()
        
        # 사용자 입력 대기
        input()
        
        # 녹음 중지
        self.recording = False
        recording_thread.join()
        
        # 스트림 정리
        self._cleanup_audio()
        
        # 파일 저장
        if self.frames and self._save_recording(filename):
            print(f'녹음이 완료되었습니다: {filename}')
            return True
        else:
            print('녹음 저장에 실패했습니다.')
            return False
    
    def convert_audio_to_text(self, audio_file_path):
        """음성 파일을 텍스트로 변환하는 STT 기능"""
        print(f'음성을 텍스트로 변환 중: {audio_file_path}')
        
        try:
            # 음성 파일 읽기
            with sr.AudioFile(audio_file_path) as source:
                # 배경 소음 조정
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = self.recognizer.record(source)
            
            # 음성을 텍스트로 변환 (Google Web Speech API 사용)
            try:
                text = self.recognizer.recognize_google(audio_data, language='ko-KR')
                return text
            except sr.UnknownValueError:
                return '[음성을 인식할 수 없습니다]'
            except sr.RequestError as e:
                return f'[음성 인식 서비스 오류: {e}]'
        
        except Exception as e:
            print(f'음성 파일 처리 중 오류: {e}')
            return f'[파일 처리 오류: {e}]'
    
    def convert_audio_to_text_with_timestamps(self, audio_file_path):
        """음성 파일을 시간대별 텍스트로 변환"""
        print(f'시간대별 음성 변환 중: {audio_file_path}')
        
        try:
            results = []
            
            # 파일을 작은 청크로 나누어 처리
            with sr.AudioFile(audio_file_path) as source:
                audio_duration = source.DURATION
                chunk_duration = 10  # 10초 단위로 처리
                
                for start_time in range(0, int(audio_duration), chunk_duration):
                    end_time = min(start_time + chunk_duration, audio_duration)
                    
                    # 해당 시간 구간의 오디오 추출
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    audio_chunk = self.recognizer.record(source, 
                                                       offset=start_time, 
                                                       duration=min(chunk_duration, 
                                                                  audio_duration - start_time))
                    
                    # 텍스트 변환
                    try:
                        text = self.recognizer.recognize_google(audio_chunk, language='ko-KR')
                        if text.strip():  # 빈 텍스트가 아닌 경우만 저장
                            timestamp = f'{start_time:02d}:{start_time%60:02d}-{end_time:02d}:{end_time%60:02d}'
                            results.append((timestamp, text))
                    except sr.UnknownValueError:
                        # 인식되지 않은 구간은 건너뛰기
                        continue
                    except sr.RequestError as e:
                        timestamp = f'{start_time:02d}:{start_time%60:02d}-{end_time:02d}:{end_time%60:02d}'
                        results.append((timestamp, f'[음성 인식 서비스 오류: {e}]'))
            
            return results
        
        except Exception as e:
            print(f'시간대별 음성 변환 중 오류: {e}')
            return [('00:00-00:00', f'[파일 처리 오류: {e}]')]
    
    def save_text_to_csv(self, audio_filename, text_data):
        """텍스트 데이터를 CSV 파일로 저장"""
        # 확장자를 .csv로 변경
        csv_filename = audio_filename.replace('.wav', '.csv')
        
        try:
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # 헤더 작성
                writer.writerow(['시간', '인식된 텍스트'])
                
                # 데이터가 리스트인 경우 (시간대별)
                if isinstance(text_data, list):
                    for timestamp, text in text_data:
                        writer.writerow([timestamp, text])
                else:
                    # 단일 텍스트인 경우
                    writer.writerow(['전체', text_data])
            
            print(f'텍스트가 CSV로 저장되었습니다: {csv_filename}')
            return True
        
        except Exception as e:
            print(f'CSV 저장 실패: {e}')
            return False
    
    def process_audio_files(self):
        """모든 음성 파일을 텍스트로 변환"""
        audio_files = self.get_audio_files()
        
        if not audio_files:
            print('변환할 음성 파일이 없습니다.')
            return
        
        print(f'총 {len(audio_files)}개의 음성 파일을 변환합니다...')
        
        for i, audio_file in enumerate(audio_files, 1):
            print(f'\n[{i}/{len(audio_files)}] 처리 중: {audio_file}')
            
            # CSV 파일이 이미 존재하는지 확인
            csv_file = audio_file.replace('.wav', '.csv')
            if os.path.exists(csv_file):
                print(f'이미 변환된 파일입니다: {csv_file}')
                continue
            
            # 시간대별 텍스트 변환
            text_results = self.convert_audio_to_text_with_timestamps(audio_file)
            
            # CSV로 저장
            if text_results:
                self.save_text_to_csv(audio_file, text_results)
            
            # 처리 간 잠시 대기 (API 제한 고려)
            time.sleep(1)
        
        print('\n모든 음성 파일 변환이 완료되었습니다!')
    
    def get_audio_files(self):
        """records 폴더의 모든 wav 파일 목록 반환"""
        if not os.path.exists(self.records_dir):
            return []
        
        audio_files = []
        for filename in os.listdir(self.records_dir):
            if filename.endswith('.wav'):
                audio_files.append(os.path.join(self.records_dir, filename))
        
        return sorted(audio_files)
    
    def search_keyword_in_csv_files(self, keyword):
        """CSV 파일에서 키워드 검색 (보너스 기능)"""
        if not keyword.strip():
            print('검색할 키워드를 입력해주세요.')
            return
        
        print(f'\n키워드 "{keyword}" 검색 결과:')
        print('=' * 60)
        
        csv_files = self.get_csv_files()
        found_results = []
        
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader)  # 헤더 스킵
                    
                    for row_num, row in enumerate(reader, 2):  # 1은 헤더, 2부터 데이터
                        if len(row) >= 2 and keyword.lower() in row[1].lower():
                            file_date = self._extract_date_from_filename(csv_file)
                            found_results.append({
                                'file': os.path.basename(csv_file),
                                'date': file_date,
                                'time': row[0],
                                'text': row[1]
                            })
            
            except Exception as e:
                print(f'파일 읽기 오류 ({csv_file}): {e}')
        
        if found_results:
            # 날짜순 정렬
            found_results.sort(key=lambda x: x['date'])
            
            for i, result in enumerate(found_results, 1):
                print(f'{i:2d}. [{result["date"]}] {result["time"]}')
                print(f'    파일: {result["file"]}')
                print(f'    내용: {result["text"]}')
                print('-' * 60)
            
            print(f'\n총 {len(found_results)}개의 결과를 찾았습니다.')
        else:
            print('검색 결과가 없습니다.')
    
    def get_csv_files(self):
        """records 폴더의 모든 csv 파일 목록 반환"""
        if not os.path.exists(self.records_dir):
            return []
        
        csv_files = []
        for filename in os.listdir(self.records_dir):
            if filename.endswith('.csv'):
                csv_files.append(os.path.join(self.records_dir, filename))
        
        return sorted(csv_files)
    
    def _extract_date_from_filename(self, filename):
        """파일명에서 날짜 추출"""
        try:
            basename = os.path.basename(filename)
            date_str = basename.split('-')[0]
            return datetime.datetime.strptime(date_str, '%Y%m%d').date()
        except:
            return datetime.date.min
    
    def show_stt_menu(self):
        """STT 관련 메뉴"""
        print('\n=== 음성-텍스트 변환 ===')
        print('1. 모든 음성 파일을 텍스트로 변환')
        print('2. 특정 음성 파일 변환')
        print('3. 키워드 검색')
        print('4. 변환된 텍스트 파일 목록')
        print('5. 돌아가기')
        
        choice = input('선택하세요 (1-5): ').strip()
        
        if choice == '1':
            self.process_audio_files()
        elif choice == '2':
            self._convert_single_file()
        elif choice == '3':
            keyword = input('검색할 키워드를 입력하세요: ').strip()
            self.search_keyword_in_csv_files(keyword)
        elif choice == '4':
            self._show_csv_files()
        elif choice == '5':
            return
        else:
            print('잘못된 선택입니다.')
    
    def _convert_single_file(self):
        """특정 음성 파일 변환"""
        audio_files = self.get_audio_files()
        
        if not audio_files:
            print('변환할 음성 파일이 없습니다.')
            return
        
        print('\n음성 파일 목록:')
        for i, file_path in enumerate(audio_files, 1):
            filename = os.path.basename(file_path)
            print(f'{i:2d}. {filename}')
        
        try:
            choice = int(input('\n변환할 파일 번호를 선택하세요: ')) - 1
            if 0 <= choice < len(audio_files):
                selected_file = audio_files[choice]
                print(f'\n선택된 파일: {os.path.basename(selected_file)}')
                
                text_results = self.convert_audio_to_text_with_timestamps(selected_file)
                if text_results:
                    self.save_text_to_csv(selected_file, text_results)
            else:
                print('잘못된 번호입니다.')
        except ValueError:
            print('올바른 숫자를 입력해주세요.')
    
    def _show_csv_files(self):
        """변환된 CSV 파일 목록 출력"""
        csv_files = self.get_csv_files()
        
        if not csv_files:
            print('변환된 텍스트 파일이 없습니다.')
            return
        
        print(f'\n총 {len(csv_files)}개의 텍스트 파일이 있습니다:')
        print('-' * 50)
        for i, file_path in enumerate(csv_files, 1):
            filename = os.path.basename(file_path)
            file_date = self._extract_date_from_filename(file_path)
            print(f'{i:2d}. {filename} ({file_date})')
        print('-' * 50)
    
    def list_recordings_by_date(self, start_date=None, end_date=None):
        """특정 날짜 범위의 녹음 파일 목록 조회"""
        if not os.path.exists(self.records_dir):
            print('녹음 파일이 없습니다.')
            return []
        
        files = []
        for filename in os.listdir(self.records_dir):
            if filename.endswith('.wav'):
                try:
                    # 파일명에서 날짜 추출 (YYYYMMDD-HHMMSS.wav)
                    date_str = filename.split('-')[0]
                    file_date = datetime.datetime.strptime(date_str, '%Y%m%d').date()
                    
                    # 날짜 범위 필터링
                    if start_date and file_date < start_date:
                        continue
                    if end_date and file_date > end_date:
                        continue
                    
                    files.append({
                        'filename': filename,
                        'date': file_date,
                        'path': os.path.join(self.records_dir, filename)
                    })
                except ValueError:
                    # 날짜 형식이 맞지 않는 파일은 무시
                    continue
        
        # 날짜순 정렬
        files.sort(key=lambda x: x['date'])
        return files
    
    def show_recordings_menu(self):
        """녹음 파일 조회 메뉴"""
        print('\n=== 녹음 파일 조회 ===')
        print('1. 모든 녹음 파일 보기')
        print('2. 특정 날짜 범위 녹음 파일 보기')
        print('3. 돌아가기')
        
        choice = input('선택하세요 (1-3): ').strip()
        
        if choice == '1':
            files = self.list_recordings_by_date()
            self._display_recordings(files)
        elif choice == '2':
            self._show_date_range_recordings()
        elif choice == '3':
            return
        else:
            print('잘못된 선택입니다.')
    
    def _show_date_range_recordings(self):
        """날짜 범위 지정 녹음 파일 조회"""
        try:
            print('날짜 형식: YYYY-MM-DD (예: 2024-03-15)')
            start_input = input('시작 날짜 (엔터시 전체): ').strip()
            end_input = input('종료 날짜 (엔터시 전체): ').strip()
            
            start_date = None
            end_date = None
            
            if start_input:
                start_date = datetime.datetime.strptime(start_input, '%Y-%m-%d').date()
            if end_input:
                end_date = datetime.datetime.strptime(end_input, '%Y-%m-%d').date()
            
            files = self.list_recordings_by_date(start_date, end_date)
            self._display_recordings(files)
            
        except ValueError:
            print('날짜 형식이 올바르지 않습니다.')
    
    def _display_recordings(self, files):
        """녹음 파일 목록 출력"""
        if not files:
            print('해당 조건의 녹음 파일이 없습니다.')
            return
        
        print(f'\n총 {len(files)}개의 녹음 파일을 찾았습니다:')
        print('-' * 50)
        for i, file_info in enumerate(files, 1):
            print(f'{i:2d}. {file_info["filename"]} ({file_info["date"]})')
        print('-' * 50)


def show_main_menu():
    """메인 메뉴 출력"""
    print('\n=== 화성 음성 일기 시스템 (JAVIS) ===')
    print('1. 음성 녹음 시작')
    print('2. 녹음 파일 조회')
    print('3. 음성-텍스트 변환 및 검색')
    print('4. 종료')
    print('=' * 40)


def main():
    """메인 함수"""
    recorder = VoiceRecorder()
    
    print('화성 음성 일기 시스템을 시작합니다!')
    print('한송희 박사님, 이제 음성을 텍스트로 변환하여 검색할 수 있습니다!')
    
    while True:
        show_main_menu()
        choice = input('메뉴를 선택하세요 (1-4): ').strip()
        
        if choice == '1':
            print('\n음성 녹음을 시작합니다...')
            recorder.start_recording()
        elif choice == '2':
            recorder.show_recordings_menu()
        elif choice == '3':
            recorder.show_stt_menu()
        elif choice == '4':
            print('화성 음성 일기 시스템을 종료합니다.')
            print('한송희 박사님, 좋은 하루 되세요!')
            break
        else:
            print('잘못된 선택입니다. 다시 선택해주세요.')


if __name__ == '__main__':
    main()