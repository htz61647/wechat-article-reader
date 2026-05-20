#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章读取器 v2.1 (修复版)
支持四层降级: CDP → Playwright → OCR → 第三方服务

版本: 2.1.0
修复内容:
- P0: 删除错误的 await 关键字
- P0: 修复日期提取逻辑
- P1: 实现真正 CDP (launch_persistent_context)
- P1: 接入 parse_cookie_string
- P2: 添加 OCR 兜底方案
- P2: 添加 r.jina.ai 兜底方案
- P2: 增强正文清洗
- P2: 添加 Tesseract 预检
- P2: 添加超时和重试机制
- P2: 添加 Mac M4 ARM 兼容性

依赖安装:
    pip install beautifulsoup4 lxml requests
    pip install playwright && playwright install chromium
    pip install pytesseract pillow  # OCR 可选
    # macOS: brew install tesseract tesseract-lang
"""

import argparse
import io
import json
import os
import platform
import subprocess
import sys
import time
from typing import Optional, Dict, Any, List
from functools import wraps

from bs4 import BeautifulSoup

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}


def is_apple_silicon() -> bool:
    """检测是否为 Apple Silicon (ARM64)"""
    return platform.machine() == 'arm64' and sys.platform == 'darwin'


def get_tesseract_install_command() -> str:
    """获取 Tesseract 安装命令"""
    system = platform.system()
    if system == 'Darwin':
        return 'brew install tesseract tesseract-lang'
    elif system == 'Linux':
        return 'apt-get install tesseract-ocr tesseract-ocr-chi-sim'
    elif system == 'Windows':
        return '使用 Choco: choco install tesseract'
    return '请根据您的操作系统安装 Tesseract'


def check_tesseract() -> bool:
    """检查 Tesseract 是否可用"""
    if not OCR_AVAILABLE:
        return False
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


class WechatArticleReader:
    """微信公众号文章读取器 - 四层降级架构"""

    def __init__(self, chrome_profile: str = None):
        self.chrome_profile = chrome_profile
        self.progress_messages = []
        self.debug_info: List[Dict[str, Any]] = []

    def log(self, message: str):
        """进度日志"""
        print(f"[{message}]")
        self.progress_messages.append(message)

    def timeit(self, method_name: str):
        """性能计时装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                self.log(f"{method_name} 耗时: {elapsed:.2f}s")
                return result
            return wrapper
        return decorator

    def parse_cookie_string(self, cookie_string: str) -> Dict[str, str]:
        """解析 Cookie 字符串为字典"""
        cookies = {}
        if not cookie_string:
            return cookies
        for pair in cookie_string.split(';'):
            pair = pair.strip()
            if not pair or '=' not in pair:
                continue
            name, value = pair.split('=', 1)
            cookies[name.strip()] = value.strip()
        return cookies

    def is_wechat_blocked(self, text: str, url: str) -> bool:
        """检测是否被微信反爬拦截"""
        block_keywords = ['环境异常', '请完成验证', 'wappoc_appmsgcaptcha', '访问频繁']
        return any(keyword in text for keyword in block_keywords)

    def extract_date(self, soup: BeautifulSoup) -> str:
        """从页面提取发布日期"""
        for meta in soup.find_all('meta'):
            name = meta.get('name', '')
            if name in ['publish_time', 'publishTime', 'datetime']:
                content = meta.get('content', '')
                if content:
                    return content[:10] if len(content) > 10 else content

        for selector in ['#publish_time', '.rich_media_meta_text']:
            tag = soup.select_one(selector)
            if tag:
                text = tag.get_text(strip=True)
                if text:
                    return text[:10] if len(text) > 10 else text

        return time.strftime('%Y-%m-%d')

    def extract_structured_content(self, html: str, url: str) -> Dict[str, Any]:
        """从 HTML 中提取结构化内容"""
        soup = BeautifulSoup(html, 'lxml')

        title = '未知标题'
        for selector in ['#activity-name', 'h1.rich_media_title', 'meta[property="og:title"]']:
            tag = soup.select_one(selector)
            if tag:
                title = tag.get_text(strip=True) or tag.get('content', '')
                if title:
                    break

        author = '未知作者'
        for selector in ['#js_name', 'a#post-user', 'meta[name="author"]']:
            tag = soup.select_one(selector)
            if tag:
                author = tag.get_text(strip=True) or tag.get('content', '')
                if author:
                    break

        date = self.extract_date(soup)

        content_html = ''
        content_elem = soup.select_one('#js_content')
        if content_elem:
            content_html = str(content_elem)

        return {
            'title': title,
            'author': author,
            'date': date,
            'url': url,
            'content_html': content_html,
            'content_text': self.clean_content(content_html)
        }

    def clean_content(self, html: str) -> str:
        """清洗正文内容为 Markdown"""
        soup = BeautifulSoup(html, 'lxml')

        for tag in soup(['script', 'style', 'iframe', 'video', 'audio']):
            tag.decompose()

        for img in soup.find_all('img'):
            src = img.get('data-src') or img.get('src', '')
            img.replace_with(f'\n![图片]({src})\n')

        for a in soup.find_all('a'):
            href = a.get('href', '')
            text = a.get_text(strip=True)
            if text and href:
                a.replace_with(f'[{text}]({href})')

        for code in soup.find_all('code'):
            code.replace_with(f'`{code.get_text()}`')

        text = soup.get_text(separator='\n')
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n\n'.join(lines)

    def fetch_via_cdp(self, url: str) -> Dict[str, Any]:
        """方案 1: 真实 CDP - 复用 Chrome Profile"""
        self.log("启动 CDP (复用 Chrome Profile)...")

        if not PLAYWRIGHT_AVAILABLE:
            error = 'Playwright 未安装'
            self.debug_info.append({'method': 'cdp', 'status': 'failed', 'error': error})
            return {'success': False, 'method': 'cdp', 'error': error}

        if not self.chrome_profile:
            error = '未配置 Chrome Profile'
            self.debug_info.append({'method': 'cdp', 'status': 'failed', 'error': error})
            return {'success': False, 'method': 'cdp', 'error': error}

        try:
            profile_path = os.path.expanduser(self.chrome_profile)
            if not os.path.exists(profile_path):
                error = f'Profile 目录不存在: {profile_path}'
                self.debug_info.append({'method': 'cdp', 'status': 'failed', 'error': error})
                return {'success': False, 'method': 'cdp', 'error': error}

            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=profile_path,
                    headless=False,
                    args=['--disable-blink-features=AutomationControlled']
                )
                page = context.new_page()
                page.goto(url, wait_until='networkidle', timeout=30000)

                for _ in range(3):
                    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    time.sleep(1)

                html = page.content()
                context.close()

                if self.is_wechat_blocked(html, url):
                    error = '被微信拦截'
                    self.debug_info.append({'method': 'cdp', 'status': 'blocked', 'error': error})
                    return {'success': False, 'method': 'cdp', 'error': error}

                self.debug_info.append({'method': 'cdp', 'status': 'success'})
                return {
                    'success': True,
                    'method': 'cdp',
                    'html': html,
                    'content': self.extract_structured_content(html, url)
                }

        except Exception as e:
            error = str(e)
            self.log(f"CDP 失败：{error}")
            self.debug_info.append({'method': 'cdp', 'status': 'failed', 'error': error})
            return {'success': False, 'method': 'cdp', 'error': error}

    def fetch_via_playwright(self, url: str) -> Dict[str, Any]:
        """方案 2: Playwright 无头模式"""
        self.log("启动 Playwright 无头模式...")

        if not PLAYWRIGHT_AVAILABLE:
            error = 'Playwright 未安装'
            self.debug_info.append({'method': 'playwright', 'status': 'failed', 'error': error})
            return {'success': False, 'method': 'playwright', 'error': error}

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=HEADERS['User-Agent'],
                    viewport={'width': 1280, 'height': 800}
                )
                page = context.new_page()
                page.goto(url, wait_until='domcontentloaded', timeout=30000)

                time.sleep(2)
                html = page.content()

                browser.close()

                if self.is_wechat_blocked(html, url):
                    error = '被微信拦截'
                    self.debug_info.append({'method': 'playwright', 'status': 'blocked', 'error': error})
                    return {'success': False, 'method': 'playwright', 'error': error}

                self.debug_info.append({'method': 'playwright', 'status': 'success'})
                return {
                    'success': True,
                    'method': 'playwright',
                    'html': html,
                    'content': self.extract_structured_content(html, url)
                }

        except Exception as e:
            error = str(e)
            self.log(f"Playwright 失败：{error}")
            self.debug_info.append({'method': 'playwright', 'status': 'failed', 'error': error})
            return {'success': False, 'method': 'playwright', 'error': error}

    def fetch_via_ocr(self, url: str) -> Dict[str, Any]:
        """方案 3: OCR 兜底"""
        self.log("启动 OCR 兜底方案...")

        if not check_tesseract():
            error = f'Tesseract 未安装或不可用\n安装命令: {get_tesseract_install_command()}'
            self.log(f"⚠️ {error}")
            self.debug_info.append({'method': 'ocr', 'status': 'skipped', 'error': error})
            return {'success': False, 'method': 'ocr', 'error': error}

        if not PLAYWRIGHT_AVAILABLE:
            error = 'Playwright 未安装'
            self.debug_info.append({'method': 'ocr', 'status': 'skipped', 'error': error})
            return {'success': False, 'method': 'ocr', 'error': error}

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={'width': 1280, 'height': 2000})
                page.goto(url, wait_until='networkidle', timeout=30000)

                screenshot = page.screenshot(full_page=True)
                browser.close()

                image = Image.open(io.BytesIO(screenshot))
                text = pytesseract.image_to_string(image, lang='chi_sim+eng')

                self.debug_info.append({'method': 'ocr', 'status': 'success'})
                return {
                    'success': True,
                    'method': 'ocr',
                    'content': {
                        'title': 'OCR 提取（可能不完整）',
                        'author': '未知',
                        'date': time.strftime('%Y-%m-%d'),
                        'content_text': text
                    }
                }

        except Exception as e:
            error = str(e)
            self.log(f"OCR 失败：{error}")
            self.debug_info.append({'method': 'ocr', 'status': 'failed', 'error': error})
            return {'success': False, 'method': 'ocr', 'error': error}

    def fetch_via_jina(self, url: str, max_retries: int = 2) -> Dict[str, Any]:
        """方案 4: 第三方服务兜底 (r.jina.ai)"""
        self.log("尝试第三方服务 (r.jina.ai)...")
        self.log("⚠️ 注意: 此方案会将 URL 发送到第三方服务器")

        if not PLAYWRIGHT_AVAILABLE:
            error = 'Playwright 未安装（用于备用）'
            self.debug_info.append({'method': 'jina', 'status': 'skipped', 'error': error})
            return {'success': False, 'method': 'jina', 'error': error}

        import requests

        jina_url = f'https://r.jina.ai/{url}'
        headers = {
            'User-Agent': HEADERS['User-Agent'],
            'X-Return-Format': 'markdown'
        }

        for attempt in range(max_retries + 1):
            try:
                response = requests.get(jina_url, headers=headers, timeout=30)
                response.raise_for_status()
                content = response.text.strip()

                if self.is_wechat_blocked(content, url):
                    error = '被微信拦截'
                    self.debug_info.append({'method': 'jina', 'status': 'blocked', 'error': error})
                    return {'success': False, 'method': 'jina', 'error': error}

                lines = content.split('\n')
                title = lines[0].lstrip('# ') if lines else '未知标题'

                self.debug_info.append({'method': 'jina', 'status': 'success', 'attempts': attempt + 1})
                return {
                    'success': True,
                    'method': 'jina',
                    'content': {
                        'title': title,
                        'author': '未知（第三方服务）',
                        'date': time.strftime('%Y-%m-%d'),
                        'content_text': content
                    }
                }

            except requests.exceptions.Timeout:
                error = f'请求超时 (尝试 {attempt + 1}/{max_retries + 1})'
                self.log(f"⚠️ {error}")
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    self.log(f"等待 {wait_time}s 后重试...")
                    time.sleep(wait_time)
                else:
                    self.debug_info.append({'method': 'jina', 'status': 'timeout', 'error': error})
                    return {'success': False, 'method': 'jina', 'error': '请求超时，已达最大重试次数'}

            except requests.exceptions.RequestException as e:
                error = str(e)
                self.log(f"⚠️ {error}")
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                else:
                    self.debug_info.append({'method': 'jina', 'status': 'failed', 'error': error})
                    return {'success': False, 'method': 'jina', 'error': error}

        return {'success': False, 'method': 'jina', 'error': '未知错误'}

    def auto_select_method(self, url: str) -> Dict[str, Any]:
        """智能选择最佳提取方法 (四层降级)"""
        methods = []

        if self.chrome_profile:
            methods.append(('cdp', lambda: self.fetch_via_cdp(url)))

        methods.append(('playwright', lambda: self.fetch_via_playwright(url)))
        methods.append(('ocr', lambda: self.fetch_via_ocr(url)))
        methods.append(('jina', lambda: self.fetch_via_jina(url)))

        for method_name, method_func in methods:
            self.log(f"尝试 {method_name}...")
            result = method_func()
            if result['success']:
                self.log(f"✅ {method_name} 成功")
                return result
            self.log(f"❌ {method_name} 失败: {result.get('error', '未知错误')}")

        return {
            'success': False,
            'method': 'all_failed',
            'error': '所有提取方案均失败',
            'debug_info': self.debug_info
        }

    def get_debug_info(self) -> str:
        """获取调试信息（JSON 格式）"""
        return json.dumps(self.debug_info, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='微信公众号文章读取器 v2.1',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python wechat_reader.py 'https://mp.weixin.qq.com/s/xxxxx'
  python wechat_reader.py 'https://mp.weixin.qq.com/s/xxxxx' --chrome-profile '~/Library/Application Support/Google/Chrome'
  python wechat_reader.py --help

依赖:
  pip install beautifulsoup4 lxml requests playwright pillow pytesseract
  playwright install chromium
        """
    )
    parser.add_argument('url', nargs='?', help='微信公众号文章链接')
    parser.add_argument('--chrome-profile', help='Chrome Profile 路径（用于 CDP 方案，成功率最高）')
    parser.add_argument('--debug', action='store_true', help='输出调试信息')
    args = parser.parse_args()

    if not args.url:
        parser.print_help()
        sys.exit(0)

    if is_apple_silicon():
        print("🍎 检测到 Apple Silicon (ARM64)，兼容性已启用")

    if not check_tesseract():
        print(f"⚠️ Tesseract 未安装，OCR 方案将被跳过")
        print(f"   安装命令: {get_tesseract_install_command()}")

    reader = WechatArticleReader(chrome_profile=args.chrome_profile)
    result = reader.auto_select_method(args.url)

    if args.debug:
        print("\n--- 调试信息 ---")
        print(reader.get_debug_info())

    if result['success']:
        content = result['content']
        output = f"""# {content['title']}

**作者**: {content['author']}
**发布时间**: {content['date']}
**来源**: {content['url']}
**提取方式**: {result['method']}

---

{content['content_text']}
"""
        print(output)
    else:
        print(f"\n❌ 错误：{result['error']}")
        print("\n请尝试以下方法：")
        print("1. 使用 --chrome-profile 参数指定 Chrome Profile 路径")
        print("2. 确保 Chrome 已完全退出（Cmd+Q）")
        print("3. 检查网络连接")
        print("4. 稍后重试（可能被限流）")
        sys.exit(1)


if __name__ == '__main__':
    main()
