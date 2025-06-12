import csv
import datetime
try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    print('MySQL 연결을 위해 mysql-connector-python이 필요합니다.')
    print('설치: pip install mysql-connector-python')
    exit(1)


class MySQLHelper:
    """MySQL 데이터베이스 연결 및 쿼리를 위한 헬퍼 클래스"""
    
    def __init__(self, host='localhost', database='mars_mission', 
                 user='root', password=''):
        """MySQL 연결 초기화"""
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """데이터베이스 연결"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                print(f'MySQL 데이터베이스 "{self.database}"에 성공적으로 연결되었습니다.')
                return True
        
        except Error as e:
            print(f'MySQL 연결 오류: {e}')
            return False
    
    def create_database_if_not_exists(self):
        """데이터베이스가 없으면 생성"""
        try:
            # 데이터베이스 없이 연결
            temp_connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            temp_cursor = temp_connection.cursor()
            
            # 데이터베이스 생성
            temp_cursor.execute(f'CREATE DATABASE IF NOT EXISTS {self.database}')
            print(f'데이터베이스 "{self.database}"를 생성했습니다.')
            
            temp_cursor.close()
            temp_connection.close()
            
        except Error as e:
            print(f'데이터베이스 생성 오류: {e}')
    
    def execute_query(self, query, params=None):
        """쿼리 실행 (INSERT, UPDATE, DELETE 등)"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        
        except Error as e:
            print(f'쿼리 실행 오류: {e}')
            self.connection.rollback()
            return False
    
    def fetch_all(self, query, params=None):
        """SELECT 쿼리 실행 후 모든 결과 반환"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        
        except Error as e:
            print(f'데이터 조회 오류: {e}')
            return None
    
    def fetch_one(self, query, params=None):
        """SELECT 쿼리 실행 후 하나의 결과 반환"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchone()
        
        except Error as e:
            print(f'데이터 조회 오류: {e}')
            return None
    
    def close(self):
        """데이터베이스 연결 종료"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print('MySQL 연결이 종료되었습니다.')


class MarsWeatherManager:
    """화성 날씨 데이터 관리 클래스"""
    
    def __init__(self, db_helper):
        self.db = db_helper
    
    def create_weather_table(self):
        """mars_weather 테이블 생성"""
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS mars_weather (
            weather_id INT AUTO_INCREMENT PRIMARY KEY,
            mars_date DATETIME NOT NULL,
            temp INT,
            storm INT
        )
        '''
        
        if self.db.execute_query(create_table_query):
            print('mars_weather 테이블이 생성되었습니다.')
            return True
        return False
    
    def load_csv_data(self, csv_filename):
        """CSV 파일에서 날씨 데이터 로드"""
        weather_data = []
        
        try:
            with open(csv_filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                print(f'CSV 파일 "{csv_filename}"을 읽는 중...')
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # 날짜 파싱
                        mars_date = self._parse_date(row.get('mars_date', ''))
                        temp = int(row.get('temp', 0))
                        storm = int(row.get('storm', 0))
                        
                        weather_data.append({
                            'mars_date': mars_date,
                            'temp': temp,
                            'storm': storm
                        })
                    
                    except (ValueError, TypeError) as e:
                        print(f'행 {row_num} 데이터 파싱 오류: {e}')
                        continue
                
                print(f'총 {len(weather_data)}개의 날씨 데이터를 로드했습니다.')
                return weather_data
        
        except FileNotFoundError:
            print(f'파일을 찾을 수 없습니다: {csv_filename}')
            return []
        except Exception as e:
            print(f'CSV 파일 읽기 오류: {e}')
            return []
    
    def _parse_date(self, date_string):
        """날짜 문자열을 datetime 객체로 변환"""
        # 다양한 날짜 형식 지원
        date_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%m/%d/%Y',
            '%d/%m/%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.datetime.strptime(date_string.strip(), fmt)
            except ValueError:
                continue
        
        # 파싱 실패시 현재 날짜 반환
        print(f'날짜 파싱 실패: {date_string}')
        return datetime.datetime.now()
    
    def insert_weather_data(self, weather_data):
        """날씨 데이터를 데이터베이스에 삽입"""
        if not weather_data:
            print('삽입할 데이터가 없습니다.')
            return False
        
        # 기존 데이터 삭제 (새로 입력하기 위해)
        self.clear_weather_data()
        
        insert_query = '''
        INSERT INTO mars_weather (mars_date, temp, storm)
        VALUES (%s, %s, %s)
        '''
        
        success_count = 0
        
        for data in weather_data:
            params = (
                data['mars_date'],
                data['temp'],
                data['storm']
            )
            
            if self.db.execute_query(insert_query, params):
                success_count += 1
        
        print(f'{success_count}개의 날씨 데이터가 성공적으로 삽입되었습니다.')
        return success_count > 0
    
    def clear_weather_data(self):
        """기존 날씨 데이터 삭제"""
        delete_query = 'DELETE FROM mars_weather'
        self.db.execute_query(delete_query)
        print('기존 날씨 데이터를 삭제했습니다.')
    
    def get_weather_summary(self):
        """날씨 데이터 요약 조회"""
        queries = {
            'total_records': 'SELECT COUNT(*) FROM mars_weather',
            'storm_days': 'SELECT COUNT(*) FROM mars_weather WHERE storm = 1',
            'avg_temp': 'SELECT AVG(temp) FROM mars_weather',
            'min_temp': 'SELECT MIN(temp) FROM mars_weather',
            'max_temp': 'SELECT MAX(temp) FROM mars_weather'
        }
        
        summary = {}
        
        for key, query in queries.items():
            result = self.db.fetch_one(query)
            summary[key] = result[0] if result else 0
        
        return summary
    
    def check_storm_on_date(self, target_date):
        """특정 날짜에 모래 폭풍이 있는지 확인"""
        query = 'SELECT storm FROM mars_weather WHERE DATE(mars_date) = %s'
        result = self.db.fetch_one(query, (target_date,))
        
        if result:
            return result[0] == 1
        return False
    
    def get_safe_travel_days(self, start_date, end_date):
        """특정 기간 중 안전한 이동 가능 날짜 조회"""
        query = '''
        SELECT DATE(mars_date) as travel_date, temp, storm 
        FROM mars_weather 
        WHERE DATE(mars_date) BETWEEN %s AND %s 
        AND storm = 0
        ORDER BY mars_date
        '''
        
        results = self.db.fetch_all(query, (start_date, end_date))
        return results if results else []
    
    def display_weather_summary(self):
        """날씨 데이터 요약 출력"""
        summary = self.get_weather_summary()
        
        print('\n=== 화성 날씨 데이터 요약 ===')
        print(f'전체 기록 수: {summary["total_records"]:,}개')
        print(f'모래 폭풍 발생일: {summary["storm_days"]:,}개')
        print(f'평균 온도: {summary["avg_temp"]:.1f}°C')
        print(f'최저 온도: {summary["min_temp"]}°C')
        print(f'최고 온도: {summary["max_temp"]}°C')
        
        if summary["total_records"] > 0:
            storm_percentage = (summary["storm_days"] / summary["total_records"]) * 100
            print(f'모래 폭풍 발생률: {storm_percentage:.1f}%')
        
        print('=' * 30)


def create_sample_csv_data():
    """샘플 CSV 데이터 생성 (실제 파일이 없을 경우)"""
    import random
    
    filename = 'mars_weathers_data.csv'
    
    try:
        # 파일이 이미 존재하는지 확인
        with open(filename, 'r'):
            print(f'기존 {filename} 파일을 사용합니다.')
            return filename
    except FileNotFoundError:
        pass
    
    print(f'샘플 데이터로 {filename} 파일을 생성합니다...')
    
    # 30일간의 샘플 데이터 생성
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['mars_date', 'temp', 'storm'])
        
        base_date = datetime.datetime(2024, 3, 1)
        
        for i in range(30):
            current_date = base_date + datetime.timedelta(days=i)
            temp = random.randint(-80, -10)  # 화성의 일반적인 온도 범위
            storm = random.choice([0, 0, 0, 0, 1])  # 20% 확률로 모래 폭풍
            
            writer.writerow([
                current_date.strftime('%Y-%m-%d %H:%M:%S'),
                temp,
                storm
            ])
    
    print(f'{filename} 파일이 생성되었습니다.')
    return filename


def main():
    """메인 함수"""
    print('화성 날씨 데이터베이스 시스템을 시작합니다!')
    print('한송희 박사님의 안전한 이동을 위한 날씨 분석 시스템입니다.')
    
    # MySQL 헬퍼 초기화
    db_helper = MySQLHelper()
    
    # 데이터베이스 생성 (없을 경우)
    db_helper.create_database_if_not_exists()
    
    # 데이터베이스 연결
    if not db_helper.connect():
        print('데이터베이스 연결에 실패했습니다.')
        return
    
    try:
        # 날씨 관리자 초기화
        weather_manager = MarsWeatherManager(db_helper)
        
        # 테이블 생성
        weather_manager.create_weather_table()
        
        # CSV 파일 확인 및 생성
        csv_filename = 'mars_weathers_data.csv'
        try:
            with open(csv_filename, 'r'):
                print(f'{csv_filename} 파일을 찾았습니다.')
        except FileNotFoundError:
            print(f'{csv_filename} 파일이 없어 샘플 데이터를 생성합니다.')
            csv_filename = create_sample_csv_data()
        
        # CSV 데이터 로드
        weather_data = weather_manager.load_csv_data(csv_filename)
        
        if weather_data:
            # 데이터베이스에 삽입
            weather_manager.insert_weather_data(weather_data)
            
            # 요약 정보 출력
            weather_manager.display_weather_summary()
            
            # 안전한 이동 날짜 확인 예시
            print('\n=== 이동 계획 도우미 ===')
            start_date = '2024-03-01'
            end_date = '2024-03-07'
            
            safe_days = weather_manager.get_safe_travel_days(start_date, end_date)
            
            if safe_days:
                print(f'{start_date}부터 {end_date}까지 안전한 이동 가능일:')
                for day_info in safe_days:
                    date_str = day_info[0].strftime('%Y-%m-%d')
                    temp = day_info[1]
                    print(f'  - {date_str} (온도: {temp}°C)')
            else:
                print(f'{start_date}부터 {end_date}까지 안전한 이동 가능일이 없습니다.')
        
        else:
            print('날씨 데이터 로드에 실패했습니다.')
    
    finally:
        # 데이터베이스 연결 종료
        db_helper.close()
    
    print('\n화성 날씨 분석이 완료되었습니다!')
    print('한송희 박사님, 안전한 여행 되세요!')


if __name__ == '__main__':
    main()