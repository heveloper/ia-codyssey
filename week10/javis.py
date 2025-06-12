import os
import datetime
import threading
import time
try:
    import pyaudio
    import wave
except ImportError:
    print('음성 녹음을 위해 pyaudio와 wave 라이브러리가 필요합니다.')
    print('설치: pip install pyaudio')
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
    
    def list_recordings_by_date(self, start_date=None, end_date=None):
        """특정 날짜 범위의 녹음 파일 목록 조회 (보너스 기능)"""
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
    print('3. 종료')
    print('=' * 40)


def main():
    """메인 함수"""
    recorder = VoiceRecorder()
    
    print('화성 음성 일기 시스템을 시작합니다!')
    print('한송희 박사님, 오늘도 화이팅!')
    
    while True:
        show_main_menu()
        choice = input('메뉴를 선택하세요 (1-3): ').strip()
        
        if choice == '1':
            print('\n음성 녹음을 시작합니다...')
            recorder.start_recording()
        elif choice == '2':
            recorder.show_recordings_menu()
        elif choice == '3':
            print('화성 음성 일기 시스템을 종료합니다.')
            print('한송희 박사님, 좋은 하루 되세요!')
            break
        else:
            print('잘못된 선택입니다. 다시 선택해주세요.')


if __name__ == '__main__':
    main()