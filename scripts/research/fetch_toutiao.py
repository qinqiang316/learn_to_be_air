# -*- coding: utf-8 -*-
"""微博/头条方向：半佛社交账号探测与抓取。

已知账号（2026-08-09 侦察）：
- 今日头条「半佛仙人本仙人」：认证头条精选作者/优质财经领域创作者
  https://www.toutiao.com/c/user/token/MS4wLjABAAAA5X0VBPDBZMEMapObds7t3Z_5K6V61i3zNDYgSd6uPlM/
- 微博：账号名待确认（半佛官方表态不重微博运营，以头条/公众号为主）
- 数英主页: https://www.digitaling.com/people/10696083（认证作者，文章聚合）

用法: python3 fetch_toutiao.py              # 探测头条主页
"""
import os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import fetch, decode, strip_tags, save_text

TOUTIAO_HOME = "https://www.toutiao.com/c/user/token/MS4wLjABAAAA5X0VBPDBZMEMapObds7t3Z_5K6V61i3zNDYgSd6uPlM/"


def probe_toutiao():
    print("[头条] 探测主页:", TOUTIAO_HOME)
    try:
        raw = fetch(TOUTIAO_HOME)
        html = decode(raw)
        text = strip_tags(html)
        # 只留前 2000 字符看账号信息
        print("  ===== 主页可见内容(前2000字) =====")
        print(text[:2000])
        print("  =================================")
        save_text('weibo', 'toutiao_主页探测', text, {
            'title': '半佛仙人本仙人·头条主页',
            'source': '今日头条',
            'url': TOUTIAO_HOME, 'date': datetime.date.today().isoformat(),
        })
    except Exception as e:
        print(f"  失败: {e}")


if __name__ == '__main__':
    probe_toutiao()
