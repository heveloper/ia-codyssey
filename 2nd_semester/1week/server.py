#!usrbinenv python3
# -- coding utf-8 --

import socket
import threading
from typing import Dict, Tuple


class ChatServer
    def __init__(self, host str = '0.0.0.0', port int = 5000) - None
        self.host = host
        self.port = port
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 연결된 클라이언트 conn - username
        self.clients Dict[socket.socket, str] = {}
        self.lock = threading.Lock()

    def start(self) - None
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(10)
        print(f'서버 시작 {self.host}{self.port}')

        try
            while True
                conn, addr = self.server_sock.accept()
                threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr),
                    daemon=True
                ).start()
        except KeyboardInterrupt
            print('n서버 종료 중...')
        finally
            self.shutdown()

    def handle_client(self, conn socket.socket, addr Tuple[str, int]) - None
        try
            conn.sendall('사용자 이름을 입력하세요 '.encode('utf-8'))
            username_data = conn.recv(1024)
            if not username_data
                conn.close()
                return
            username = username_data.decode('utf-8').strip()

            with self.lock
                self.clients[conn] = username

            self.broadcast(f'📢 {username}님이 입장하셨습니다.', sender=None)

            conn.sendall('안내 종료 입력 시 연결이 종료됩니다. 귓속말은 w 대상이름 내용.n'.encode('utf-8'))

            while True
                data = conn.recv(4096)
                if not data
                    break

                text = data.decode('utf-8').strip()
                if text == '종료'
                    conn.sendall('서버 연결을 종료합니다.n'.encode('utf-8'))
                    break

                if text.startswith('w ')
                    # 형식 w 대상이름 내용...
                    self.handle_whisper(username, text, conn)
                    continue

                # 일반 메시지 브로드캐스트
                self.broadcast(f'{username} {text}', sender=conn)

        except ConnectionResetError
            # 클라이언트 비정상 종료
            pass
        finally
            self.remove_client(conn)

    def handle_whisper(self, sender_name str, raw str, sender_conn socket.socket) - None
        parts = raw.split(' ', 2)
        if len(parts)  3
            sender_conn.sendall('서버 사용법 w 대상이름 내용n'.encode('utf-8'))
            return

        _, target_name, message = parts
        target_conn = self.find_conn_by_username(target_name)
        if target_conn is None
            sender_conn.sendall(f'서버 {target_name} 사용자를 찾을 수 없습니다.n'.encode('utf-8'))
            return

        # 귓속말 전송 받는 사람과 보낸 사람에게만 표시
        whisper_to_target = f'(귓속말) {sender_name} {message}n'
        whisper_to_sender = f'(귓속말 전송됨) {sender_name} - {target_name} {message}n'
        try
            target_conn.sendall(whisper_to_target.encode('utf-8'))
            sender_conn.sendall(whisper_to_sender.encode('utf-8'))
        except OSError
            sender_conn.sendall('서버 귓속말 전송에 실패했습니다.n'.encode('utf-8'))

    def find_conn_by_username(self, username str) - socket.socket  None
        with self.lock
            for conn, name in self.clients.items()
                if name == username
                    return conn
        return None

    def broadcast(self, message str, sender socket.socket  None) - None
        # sender가 None이면 시스템 공지로 간주
        data = (message + 'n').encode('utf-8')
        with self.lock
            targets = list(self.clients.keys())

        for conn in targets
            # 보낸 사람에게도 보이도록 함(요구사항은 전체 공유이므로)
            try
                conn.sendall(data)
            except OSError
                # 전송 실패 시 제거
                self.remove_client(conn)

    def remove_client(self, conn socket.socket) - None
        username = None
        with self.lock
            if conn in self.clients
                username = self.clients.pop(conn)
        try
            conn.close()
        except OSError
            pass
        if username
            self.broadcast(f'👋 {username}님이 퇴장하셨습니다.', sender=None)

    def shutdown(self) - None
        with self.lock
            conns = list(self.clients.keys())
            self.clients.clear()
        for conn in conns
            try
                conn.close()
            except OSError
                pass
        try
            self.server_sock.close()
        except OSError
            pass


def main() - None
    server = ChatServer(host='0.0.0.0', port=5000)
    server.start()


if __name__ == '__main__'
    main()
