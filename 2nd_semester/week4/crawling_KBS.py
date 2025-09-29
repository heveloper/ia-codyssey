"""
네이버 로그인 후 개인화 콘텐츠 크롤링
Selenium을 사용한 웹 자동화 및 크롤링
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


class NaverCrawler:
    """네이버 로그인 및 크롤링을 위한 클래스"""
    
    def __init__(self):
        """크롤러 초기화"""
        self.driver = None
        self.wait = None
        self.login_contents = []
        
    def setup_driver(self):
        """Selenium 드라이버 설정"""
        options = webdriver.ChromeOptions()
        # 헤드리스 모드 (필요시 주석 해제)
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def login_naver(self, user_id, user_pw):
        """
        네이버 로그인 수행
        
        Args:
            user_id (str): 네이버 아이디
            user_pw (str): 네이버 비밀번호
            
        Returns:
            bool: 로그인 성공 여부
        """
        try:
            # 네이버 접속
            self.driver.get('https://nid.naver.com/nidlogin.login')
            time.sleep(2)
            
            # JavaScript를 사용한 입력 (보안 우회)
            self.driver.execute_script(
                f"document.getElementById('id').value = '{user_id}'"
            )
            time.sleep(1)
            
            self.driver.execute_script(
                f"document.getElementById('pw').value = '{user_pw}'"
            )
            time.sleep(1)
            
            # 로그인 버튼 클릭
            login_btn = self.driver.find_element(By.ID, 'log.login')
            login_btn.click()
            
            time.sleep(3)
            
            # 로그인 성공 확인
            if 'naver.com' in self.driver.current_url:
                print('[성공] 네이버 로그인 완료')
                return True
            else:
                print('[실패] 로그인 실패 - Captcha 또는 보안 확인 필요')
                return False
                
        except Exception as e:
            print(f'[오류] 로그인 중 오류 발생: {e}')
            return False
    
    def crawl_personalized_content(self):
        """로그인 후 개인화 콘텐츠 크롤링"""
        try:
            # 네이버 메인 페이지로 이동
            self.driver.get('https://www.naver.com')
            time.sleep(2)
            
            # 로그인 상태 확인
            try:
                # 로그인 사용자명 확인
                user_area = self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'MyView-module__link_login___HpHMW'))
                )
                username = user_area.text
                self.login_contents.append(f'로그인 사용자: {username}')
                print(f'[확인] 로그인 사용자: {username}')
            except:
                print('[경고] 로그인 상태 아님')
                return
            
            # 개인화 콘텐츠 크롤링 (예: 메일 개수)
            try:
                mail_link = self.driver.find_element(By.LINK_TEXT, '메일')
                mail_text = mail_link.text
                self.login_contents.append(f'메일 서비스: {mail_text}')
            except:
                pass
            
            # 로그인 후 표시되는 다른 콘텐츠들
            try:
                # 네이버페이 정보
                npay_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    '.service_area a'
                )
                for elem in npay_elements[:3]:
                    text = elem.text.strip()
                    if text:
                        self.login_contents.append(f'서비스: {text}')
            except:
                pass
                
        except Exception as e:
            print(f'[오류] 크롤링 중 오류 발생: {e}')
    
    def crawl_mail_titles(self):
        """보너스: 네이버 메일 제목 크롤링"""
        try:
            # 메일 페이지 접속
            self.driver.get('https://mail.naver.com')
            time.sleep(3)
            
            # iframe으로 전환 (메일은 iframe 사용)
            self.driver.switch_to.frame('mainFrame')
            time.sleep(2)
            
            # 메일 제목 크롤링
            mail_titles = self.driver.find_elements(
                By.CSS_SELECTOR,
                '.mail_subject'
            )
            
            for idx, mail in enumerate(mail_titles[:5], 1):
                title = mail.text.strip()
                if title:
                    self.login_contents.append(f'메일 {idx}: {title}')
                    print(f'[메일] {idx}. {title}')
                    
        except Exception as e:
            print(f'[오류] 메일 크롤링 중 오류 발생: {e}')
    
    def get_contents(self):
        """크롤링한 콘텐츠 반환"""
        return self.login_contents
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            print('[완료] 브라우저 종료')


def main():
    """메인 실행 함수"""
    print('=' * 50)
    print('네이버 로그인 크롤링 프로그램')
    print('=' * 50)
    
    # 사용자 입력
    print('\n[주의] 실제 계정 정보를 입력하세요.')
    print('[주의] Captcha 발생 시 수동으로 해결해야 합니다.\n')
    
    user_id = input('네이버 아이디: ')
    user_pw = input('네이버 비밀번호: ')
    
    # 크롤러 생성 및 실행
    crawler = NaverCrawler()
    
    try:
        # 드라이버 설정
        print('\n[1단계] Selenium 드라이버 설정 중...')
        crawler.setup_driver()
        
        # 로그인
        print('[2단계] 네이버 로그인 시도 중...')
        login_success = crawler.login_naver(user_id, user_pw)
        
        if not login_success:
            print('\n[안내] Captcha가 표시되면 수동으로 해결해주세요.')
            input('로그인 완료 후 Enter를 눌러주세요...')
        
        # 개인화 콘텐츠 크롤링
        print('\n[3단계] 로그인 전용 콘텐츠 크롤링 중...')
        crawler.crawl_personalized_content()
        
        # 보너스: 메일 제목 크롤링
        print('\n[보너스] 메일 제목 크롤링 시도 중...')
        mail_option = input('메일 크롤링을 진행하시겠습니까? (y/n): ')
        
        if mail_option.lower() == 'y':
            crawler.crawl_mail_titles()
        
        # 결과 출력
        print('\n' + '=' * 50)
        print('크롤링 결과')
        print('=' * 50)
        
        contents = crawler.get_contents()
        if contents:
            for content in contents:
                print(f'- {content}')
        else:
            print('크롤링된 콘텐츠가 없습니다.')
        
        print('\n[완료] 모든 작업이 완료되었습니다.')
        
    except Exception as e:
        print(f'\n[오류] 프로그램 실행 중 오류 발생: {e}')
        
    finally:
        # 종료 전 대기
        input('\n브라우저를 종료하려면 Enter를 눌러주세요...')
        crawler.close()


if __name__ == '__main__':
    main()