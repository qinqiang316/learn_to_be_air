# -*- coding: utf-8 -*-
"""多方向调研通用工具：fetch + 正文提取 + 落盘。"""
import json, os, re, sys, time, urllib.request, urllib.error

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # be_air/
CORPUS = os.path.join(BASE, 'corpus')


def fetch(url, retries=4, timeout=30):
    """GET 页面原始字节，自动跟随重定向。返回 bytes。"""
    last_err = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': UA,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            })
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last_err = f'HTTP {e.code}'
            if e.code in (403, 412):
                print(f'  {e.code} 风控，等待 {10*(i+1)}s...')
                time.sleep(10 * (i + 1))
            else:
                time.sleep(3)
        except Exception as e:
            last_err = str(e)
            time.sleep(3)
    raise RuntimeError(f'fetch failed: {url} → {last_err}')


def decode(raw: bytes):
    """按 BOM/meta/charset 猜测编码解码成 str。"""
    if raw.startswith(b'\xef\xbb\xbf'):
        return raw.decode('utf-8-sig', errors='replace')
    for enc in ('utf-8', 'gb18030', 'big5'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    # meta charset 探测
    m = re.search(rb'charset=["\']?([\w-]+)', raw[:4096], re.I)
    if m:
        try:
            return raw.decode(m.group(1).decode(), errors='replace')
        except LookupError:
            pass
    return raw.decode('utf-8', errors='replace')


def strip_tags(html: str) -> str:
    """去 script/style/nav/header/footer，提取正文文本。"""
    html = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', html)
    html = re.sub(r'(?is)<(nav|header|footer|aside)[^>]*>.*?</\1>', ' ', html)
    html = re.sub(r'(?is)<!--.*?-->', ' ', html)
    # 段落/换行标签 → 换行
    html = re.sub(r'(?i)</(p|div|h[1-6]|li|br|tr)>', '\n', html)
    html = re.sub(r'(?i)<br\s*/?>', '\n', html)
    # 其余标签删除
    html = re.sub(r'<[^>]+>', '', html)
    # 实体
    html = html.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    # 压缩空白：保留段落，去每行首尾空格
    lines = [ln.strip() for ln in html.split('\n')]
    lines = [ln for ln in lines if ln]
    return '\n'.join(lines)


def extract_main_text(url: str) -> str:
    """抓取并提取正文。返回清洗后的纯文本。"""
    raw = fetch(url)
    html = decode(raw)
    return strip_tags(html)


def save_text(direction: str, fname: str, text: str, meta: dict = None):
    """落盘 corpus/<direction>/<fname>.txt，附带元数据头。"""
    d = os.path.join(CORPUS, direction)
    os.makedirs(d, exist_ok=True)
    if meta:
        lines = [f'# {meta.get("title", fname)}',
                 f'- 来源: {meta.get("source", "")}',
                 f'- 链接: {meta.get("url", "")}',
                 f'- 抓取日期: {meta.get("date", "")}',
                 '']
        text = '\n'.join(lines) + text
    path = os.path.join(d, fname)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'  已保存 {path} ({len(text)} 字符)')
    return path


def load_json(path, default=None):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
