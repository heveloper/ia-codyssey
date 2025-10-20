#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail SMTP를 사용한 이메일 발송 프로그램
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


class GmailSender:
    """Gmail SMTP를 사용하여 이메일을 발송하는 클래스"""
    
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    
    def __init__(self, sender_email, sender_password):
        """
        GmailSender 초기화
        
        Args:
            sender_email (str): 발신자 Gmail 주소
            sender_password (str): Gmail 앱 비밀번호
        """
        self.sender_email = sender_email
        self.sender_password = sender_password
    
    def send_email(self, receiver_email, subject, body, attachments=None):
        """
        이메일 발송 메서드
        
        Args:
            receiver_email (str): 수신자 이메일 주소
            subject (str): 이메일 제목
            body (str): 이메일 본문
            attachments (list): 첨부파일 경로 리스트 (선택사항)
        
        Returns:
            bool: 발송 성공 여부
        """
        try:
            # MIME 메시지 생성
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = receiver_email
            message['Subject'] = subject
            
            # 본문 추가
            message.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 첨부파일 추가
            if attachments:
                for file_path in attachments:
                    if not self._attach_file(message, file_path):
                        print(f'경고: 파일 {file_path}를 첨부할 수 없습니다.')
            
            # SMTP 서버 연결 및 메일 발송
            return self._send_via_smtp(message, receiver_email)
            
        except Exception as e:
            print(f'이메일 발송 중 오류 발생: {str(e)}')
            return False
    
    def _attach_file(self, message, file_path):
        """
        파일을 메시지에 첨부
        
        Args:
            message (MIMEMultipart): MIME 메시지 객체
            file_path (str): 첨부할 파일 경로
        
        Returns:
            bool: 첨부 성공 여부
        """
        try:
            if not os.path.exists(file_path):
                print(f'파일을 찾을 수 없습니다: {file_path}')
                return False
            
            # 파일 읽기
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            # 파일 인코딩
            encoders.encode_base64(part)
            
            # 헤더 추가
            filename = os.path.basename(file_path)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            message.attach(part)
            return True
            
        except IOError as e:
            print(f'파일 읽기 오류: {str(e)}')
            return False
        except Exception as e:
            print(f'파일 첨부 중 오류 발생: {str(e)}')
            return False
    
    def _send_via_smtp(self, message, receiver_email):
        """
        SMTP 서버를 통해 메일 발송
        
        Args:
            message (MIMEMultipart): 발송할 메시지
            receiver_email (str): 수신자 이메일
        
        Returns:
            bool: 발송 성공 여부
        """
        server = None
        try:
            # SMTP 서버 연결
            server = smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT)
            server.set_debuglevel(0)
            server.ehlo()
            
            # TLS 보안 연결 시작
            server.starttls()
            server.ehlo()
            
            # 로그인
            server.login(self.sender_email, self.sender_password)
            
            # 메일 발송
            text = message.as_string()
            server.sendmail(self.sender_email, receiver_email, text)
            
            print('이메일이 성공적으로 발송되었습니다.')
            return True
            
        except smtplib.SMTPAuthenticationError:
            print('인증 실패: 이메일 또는 비밀번호를 확인하세요.')
            print('Gmail의 경우 앱 비밀번호를 사용해야 합니다.')
            return False
        except smtplib.SMTPConnectError:
            print('SMTP 서버 연결 실패: 네트워크 연결을 확인하세요.')
            return False
        except smtplib.SMTPException as e:
            print(f'SMTP 오류 발생: {str(e)}')
            return False
        except Exception as e:
            print(f'예상치 못한 오류 발생: {str(e)}')
            return False
        finally:
            if server:
                try:
                    server.quit()
                except Exception:
                    pass


def main():
    """메인 실행 함수"""
    
    # 설정 정보
    sender_email = 'your_email@gmail.com'  # 발신자 Gmail 주소
    sender_password = 'your_app_password'  # Gmail 앱 비밀번호
    receiver_email = 'receiver@example.com'  # 수신자 이메일 주소
    
    # 이메일 내용
    subject = '테스트 메일입니다'
    body = '''안녕하세요.
    
이것은 Python으로 발송한 테스트 메일입니다.
    
감사합니다.'''
    
    # 첨부파일 리스트 (선택사항)
    attachments = [
        # 'path/to/file1.pdf',
        # 'path/to/file2.txt',
    ]
    
    # GmailSender 인스턴스 생성
    gmail_sender = GmailSender(sender_email, sender_password)
    
    # 이메일 발송
    if attachments:
        success = gmail_sender.send_email(
            receiver_email,
            subject,
            body,
            attachments
        )
    else:
        success = gmail_sender.send_email(
            receiver_email,
            subject,
            body
        )
    
    if success:
        print('프로그램이 정상적으로 종료되었습니다.')
    else:
        print('이메일 발송에 실패했습니다.')


if __name__ == '__main__':
    main()