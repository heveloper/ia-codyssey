"""
네이버 로그인 후 개인화 콘텐츠 크롤링 (수정판)
- 두 번째(동작 확인된) 코드의 안정적인 방식으로 1번째 클래스를 전면 개선
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import os
import time


class NaverCrawler:
    """네이버 로그인 및 크롤링을 위한 클래스 (개선판)"""
    
    def __init__(self, headless=False, driver_path=None, timeout=15):
        """크롤러 초기화"""
        self.driver = None
        self.wait = None
        self.login_contents = []
        self.headless = headless
        self.driver_path = driver_path
        self.timeout = timeout
        
    def setup_driver(self):
        """Selenium 드라이버 설정"""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # 가끔 자동화 차단 회피에 도움이 되는 UA 지정 (선택)
        # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        if self.driver_path:
            self.driver = webdriver.Chrome(self.driver_path, options=options)
        else:
            self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, self.timeout)
        
    def login_naver(self, user_id, user_pw):
        """
        네이버 로그인 수행
        Returns:
            bool: 로그인 성공 여부
        """
        try:
            self.driver.get('https://nid.naver.com/nidlogin.login')
            # 아이디/비번 입력은 JS로 arguments 주입 (따옴표/이스케이프 문제 방지)
            # Naver는 name='id', name='pw'가 안정적임
            self.wait.until(EC.presence_of_element_located((By.NAME, 'id')))
            self.driver.execute_script(
                "document.getElementsByName('id')[0].value = arguments[0];",
                user_id
            )
            time.sleep(0.3)
            self.wait.until(EC.presence_of_element_located((By.NAME, 'pw')))
            self.driver.execute_script(
                "document.getElementsByName('pw')[0].value = arguments[0];",
                user_pw
            )

            # 로그인 버튼 대기 후 클릭
            login_btn = self.wait.until(EC.element_to_be_clickable((By.ID, 'log.login')))
            login_btn.click()

            # 전환/보안 확인 대기
            time.sleep(2)
            # 메인으로 튕기거나 보안 페이지일 수 있음 → 두 경우 모두 처리
            # 성공 신호 1: www.naver.com로 이동
            # 성공 신호 2: 상단에 '메일' 링크 노출
            try:
                self.wait.until(
                    EC.any_of(
                        EC.url_contains('www.naver.com'),
                        EC.presence_of_element_located((By.LINK_TEXT, '메일'))
                    )
                )
            except Exception:
                # Captcha/2차 인증 등
                print('[안내] 추가 인증(캡차/2차인증) 발생 가능. 수동으로 완료 후 Enter.')
                input('로그인이 완료되면 Enter를 누르세요...')

            # 최종 확인: 메인 이동 or 로그인 상태 요소 확인
            current = self.driver.current_url
            if 'naver.com' in current:
                print('[성공] 네이버 로그인 완료')
                return True

            print('[실패] 로그인 미확인 (추가 인증 또는 페이지 구조 변경 가능)')
            return False

        except Exception as e:
            print(f'[오류] 로그인 중 오류 발생: {e}')
            return False
    
    def crawl_personalized_content(self):
        """로그인 후 개인화 콘텐츠 크롤링(가벼운 예시)"""
        try:
            # 메인으로 이동
            self.driver.get('https://www.naver.com')
            time.sleep(1.5)

            # 로그인 상태 간단 확인: '메일' 링크 탐색
            try:
                mail_link = self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '메일')))
                self.login_contents.append('로그인 상태 확인: 메일 링크 노출됨')
            except Exception:
                print('[경고] 메일 링크가 보이지 않습니다. 비로그인 상태이거나 레이아웃 변경일 수 있습니다.')
                return

            # 메인에서 보이는 서비스 영역 일부 텍스트 수집(존재 시)
            try:
                # 너무 구체적인(해시된) 클래스는 피하고, 비교적 안정적인 링크 텍스트/role 위주로
                service_candidates = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="pay.naver"], a[href*="order.pay.naver"], a[href*="shopping.naver"]')
                grabbed = 0
                for a in service_candidates:
                    txt = a.text.strip()
                    if txt:
                        self.login_contents.append(f'서비스: {txt}')
                        grabbed += 1
                        if grabbed >= 3:
                            break
            except Exception:
                pass
                
        except Exception as e:
            print(f'[오류] 크롤링 중 오류 발생: {e}')
    
    def crawl_mail_titles(self, max_items=10):
        """네이버 메일 제목 크롤링 (신규 UI v2 기준, iframe 미사용)"""
        try:
            self.driver.get('https://mail.naver.com/v2/folders/0/all')
            # 목록 렌더 대기
            selector = 'div.mail_title a.mail_title_link span.text'
            try:
                elems = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
            except Exception:
                elems = []

            if not elems:
                print('[경고] 메일 제목 요소를 찾지 못했습니다. 레이아웃 변경/권한 문제 가능.')
                print(f'[디버그] 현재 URL: {self.driver.current_url}')
                return

            count = 0
            for i, el in enumerate(elems, start=1):
                title = (el.text or '').strip()
                if title:
                    self.login_contents.append(f'메일 {i}: {title}')
                    print(f'[메일] {i}. {title}')
                    count += 1
                    if count >= max_items:
                        break

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
    print('네이버 로그인 크롤링 프로그램 (개선판)')
    print('=' * 50)
    
    # 환경변수 우선 사용, 없으면 입력
    env_id = os.environ.get('NAVER_ID')
    env_pw = os.environ.get('NAVER_PW')
    if env_id and env_pw:
        user_id = env_id
        user_pw = env_pw
        print('[안내] 환경변수 NAVER_ID/PW 사용')
    else:
        print('\n[주의] 실제 계정 정보를 입력하세요. (환경변수 NAVER_ID/NAVER_PW 권장)')
        user_id = input('네이버 아이디: ').strip()
        user_pw = input('네이버 비밀번호: ').strip()
    
    crawler = NaverCrawler(headless=False, timeout=20)
    
    try:
        print('\n[1단계] Selenium 드라이버 설정 중...')
        crawler.setup_driver()
        
        print('[2단계] 네이버 로그인 시도 중...')
        login_success = crawler.login_naver(user_id, user_pw)
        
        if not login_success:
            print('\n[안내] 추가 인증(캡차/2차인증) 후 Enter를 눌러 계속 진행할 수 있습니다.')
            input('로그인이 완료되면 Enter를 누르세요...')
        
        print('\n[3단계] 로그인 전용 콘텐츠 크롤링 중...')
        crawler.crawl_personalized_content()
        
        print('\n[보너스] 메일 제목 크롤링 시도 중...')
        do_mail = input('메일 크롤링을 진행하시겠습니까? (y/n): ').strip().lower()
        if do_mail == 'y':
            crawler.crawl_mail_titles(max_items=10)
        
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
        input('\n브라우저를 종료하려면 Enter를 누르세요...')
        crawler.close()


if __name__ == '__main__':
    main()
