#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
import sys


def recv_loop(sock: socket.socket) -> None:
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                print('서버와의 연결이 종료되었습니다.')
                break
            print(data.decode('utf-8'), end='')
    except OSError:
        pass
    finally:
        try:
            sock.close()
        except OSError:
            pass


def main() -> None:
    host = '127.0.0.1'
    port = 5000

    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print('포트는 정수여야 합니다.')
            return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # 수신 스레드 시작
    threading.Thread(target=recv_loop, args=(sock,), daemon=True).start()

    try:
        # 서버가 먼저 사용자 이름을 요청함
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            text = line.rstrip('\n')
            sock.sendall((text + '\n').encode('utf-8'))

            if text == '/종료':
                break
    except KeyboardInterrupt:
        try:
            sock.sendall('/종료\n'.encode('utf-8'))
        except OSError:
            pass
    finally:
        try:
            sock.close()
        except OSError:
            pass


if __name__ == '__main__':
    main()
