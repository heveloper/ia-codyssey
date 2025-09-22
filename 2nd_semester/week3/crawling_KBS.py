#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crawling_KBS.py
KBS 헤드라인 뉴스를 수집하여 리스트로 출력합니다.

요구조건 준수:
- Python 3.x
- 표준 라이브러리 + requests만 사용
- PEP 8 스타일 (가능한 한 준수)
- 문자열 기본: 작은따옴표 사용
"""

import re
import sys
import html
import time
from html.parser import HTMLParser
from typing import List, Tuple, Optional
from urllib.parse import urljoin

import requests

USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/120.0.0.0 Safari/537.36'
)


class KbsHeadlineParser(HTMLParser):
    """KBS 뉴스 <a> 태그 파싱"""

    LINK_PATTERNS = [
        re.compile(r'/news/\w*/?view\.do', re.I),
        re.compile(r'/news/view\.do', re.I),
    ]

    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self._capture = False
        self._buf: List[str] = []
        self.items: List[Tuple[str, str]] = []
        self._current_href: Optional[str] = None

    @staticmethod
    def _looks_like_article(href: Optional[str]) -> bool:
        if not href:
            return False
        return any(pat.search(href) for pat in KbsHeadlineParser.LINK_PATTERNS)

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag.lower() == 'a':
            href = dict(attrs).get('href')
            if self._looks_like_article(href):
                self._capture = True
                self._buf = []
                self._current_href = urljoin(self.base_url, href or '')

    def handle_data(self, data: str) -> None:
        if self._capture and data:
            self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == 'a' and self._capture:
            raw_text = ''.join(self._buf).strip()
            text = html.unescape(re.sub(r'\s+', ' ', raw_text))
            if text:
                self.items.append((text, self._current_href or ''))
            self._capture = False
            self._buf = []
            self._current_href = None


def fetch_html(url: str, timeout: int = 10) -> str:
    headers = {'User-Agent': USER_AGENT, 'Accept-Language': 'ko'}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def unique_keep_order(seq: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    seen = set()
    out: List[Tuple[str, str]] = []
    for title, href in seq:
        if (title, href) in seen:
            continue
        if len(title) < 6:  # 짧은 제목은 제외
            continue
        seen.add((title, href))
        out.append((title, href))
    return out


def get_kbs_headlines(max_items: int = 20) -> List[Tuple[str, str]]:
    candidates = [
        'https://news.kbs.co.kr/',
        'https://world.kbs.co.kr/service/news_main.htm?lang=k',
    ]

    for url in candidates:
        try:
            html_text = fetch_html(url)
            parser = KbsHeadlineParser(base_url=url)
            parser.feed(html_text)
            items = unique_keep_order(parser.items)
            if items:
                return items[:max_items]
        except Exception as exc:
            sys.stderr.write(f'[warn] {url} 요청 실패: {exc}\n')
            time.sleep(0.5)

    return []


def print_headlines(items: List[Tuple[str, str]]) -> None:
    print('[KBS 헤드라인]')
    if not items:
        print('- 수집된 항목이 없습니다.')
        return
    for i, (title, href) in enumerate(items, start=1):
        print(f'{i:02d}. {title}')
        print(f'    - {href}')


# --- 보너스 과제: 네이버 금융에서 KOSPI 지수 가져오기 ---
_KOSPI_URL = 'https://finance.naver.com/sise/'


def get_kospi_now() -> Optional[str]:
    try:
        html_text = fetch_html(_KOSPI_URL)
    except requests.RequestException:
        return None
    m = re.search(r'id="KOSPI_now"[^>]*>\s*([0-9,]+\.[0-9]+|[0-9,]+)\s*<', html_text)
    return m.group(1) if m else None


def main() -> None:
    items = get_kbs_headlines()
    print_headlines(items)

    kospi = get_kospi_now()
    print('\n[보너스] KOSPI 현재지수: ' + (kospi if kospi else '가져오기 실패'))


if __name__ == '__main__':
    main()
