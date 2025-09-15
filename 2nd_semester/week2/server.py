#!/usr/bin/env python3
from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from http import HTTPStatus
from datetime import datetime, timezone
from urllib.request import urlopen
from urllib.error import URLError
import json
import csv
import os
import threading
from typing import Tuple

PORT = 8080
DOC_ROOT = os.path.dirname(os.path.abspath(__file__))
ANALYTICS_CSV = os.path.join(DOC_ROOT, 'analytics.csv')

# 보너스 과제: IP 주소 기반 위치 정보 조회를 사용할지 여부
GEOLOOKUP_ENABLED = False

# 스레드 세이프 카운터
_request_count_lock = threading.Lock()
_total_requests = 0
_per_ip_counts: dict[str, int] = {}


def iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')


def fetch_geo(ip: str) -> str:
    url = f'http://ip-api.com/json/{ip}?fields=status,country,regionName,city,query'
    try:
        with urlopen(url, timeout=2.5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except URLError:
        return ''
    except Exception:
        return ''
    if data.get('status') != 'success':
        return ''
    country = data.get('country') or ''
    region = data.get('regionName') or ''
    city = data.get('city') or ''
    parts = [p for p in (country, region, city) if p]
    return ' / '.join(parts)


def ensure_analytics_header() -> None:
    if not os.path.exists(ANALYTICS_CSV):
        with open(ANALYTICS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'client_ip', 'path', 'status', 'bytes', 'geo'])


class RequestHandler(SimpleHTTPRequestHandler):
    """정적 파일 서빙 + 접속 로깅 핸들러."""

    def translate_path(self, path: str) -> str:
        self.directory = DOC_ROOT
        return super().translate_path(path)

    def end_headers(self) -> None:
        super().end_headers()

    def log_request(self, code: int | str = '-', size: int | str = '-') -> None:
        ts = iso_now()
        ip = self.client_address[0] if self.client_address else '-'
        path = self.path

        with _request_count_lock:
            global _total_requests
            _total_requests += 1
            _per_ip_counts[ip] = _per_ip_counts.get(ip, 0) + 1
            total = _total_requests
            ip_count = _per_ip_counts[ip]

        geo = ''
        if GEOLOOKUP_ENABLED and ip not in ('127.0.0.1', '::1'):
            geo = fetch_geo(ip)

        size_txt = f'{size}B' if isinstance(size, int) else f'{size}'
        msg = (
            f'[{ts}] {ip} {self.command} {path} -> {code} ({size_txt}) '
            f'[# {total}, this IP: {ip_count}]'
        )
        if geo:
            msg += f' geo: {geo}'
        print(msg)

        try:
            ensure_analytics_header()
            with open(ANALYTICS_CSV, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([ts, ip, path, code, size, geo])
        except Exception as exc:
            print(f'[warn] failed to write analytics: {exc}')

    def do_GET(self) -> None:
        if self.path in ('', '/'):
            self.path = '/index.html'
        return super().do_GET()

    def do_HEAD(self) -> None:
        if self.path == '/health':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            return
        return super().do_HEAD()


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """멀티스레드 HTTP 서버."""
    daemon_threads = True


def run_server(host: str = '0.0.0.0', port: int = PORT) -> None:
    os.chdir(DOC_ROOT)
    server_address: Tuple[str, int] = (host, port)
    httpd = ThreadingHTTPServer(server_address, RequestHandler)
    print(f'[info] serving at http://{host}:{port}')
    print(f'[info] doc root: {DOC_ROOT}')
    print('[info] geolocation lookup: ENABLED' if GEOLOOKUP_ENABLED else '[info] geolocation lookup: disabled')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n[info] shutting down...')
    finally:
        httpd.server_close()


if __name__ == '__main__':
    run_server()
