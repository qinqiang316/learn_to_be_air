# -*- coding: utf-8 -*-
"""访谈/演讲方向：半佛访谈、播客文字稿、现场演讲全文抓取。

已发现素材（2026-08-09 侦察）：
- 新榜大会演讲 2020《我的口水里藏着一个宇宙》→ 腾讯新闻全文
- 新榜内容节演讲 2025《那些社会毒打教我的事》→ 腾讯新闻/数英全文
- 后浪研究所深度专访 2022《骚人有骚福》→ 36氪全文（对话体）
- 播客（音频，走 notebooklm-brief 转写，不进本脚本）：
  三五环 No.1/28/41/117（4期）、知行小酒馆 E165（1h26min）

用法: python3 fetch_interview.py            # 抓内置清单
      python3 fetch_interview.py <url> <标题>
"""
import os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import extract_main_text, save_text

ARTICLES = [
    {
        "title": "半佛_访谈_骚人有骚福_后浪研究所2022",
        "url": "https://mp.weixin.qq.com/s/OX-WLKhFdO_mmfNxxR6NnA",
        "source": "微信原链（后浪研究所专访，对话体；36氪转载为JS渲染抓不到）",
        "date": "2022-06",
    },
    {
        "title": "半佛_演讲_厕所艺术家的口水2020",
        "url": "https://news.qq.com/rain/a/20200610A0MA1100",
        "source": "腾讯新闻（新榜大会演讲全文）",
        "date": "2020-06",
    },
    {
        "title": "半佛_演讲_社会毒打教我的事2025",
        "url": "https://news.qq.com/rain/a/20250411A0928K00",
        "source": "腾讯新闻（2025新榜内容节演讲全文）",
        "date": "2025-04",
    },
]


def main():
    args = sys.argv[1:]
    if len(args) >= 2:
        ARTICLES.insert(0, {"title": args[1], "url": args[0], "source": "手动指定", "date": ""})
    ok, fail = 0, 0
    for a in ARTICLES:
        print(f"[访谈] {a['title']} ← {a['url']}")
        try:
            text = extract_main_text(a['url'])
            if len(text) < 300:
                print(f'  正文过短({len(text)})，可能被反爬，跳过')
                fail += 1
                continue
            save_text('interview', a['title'], text, {
                'title': a['title'], 'source': a['source'],
                'url': a['url'], 'date': datetime.date.today().isoformat(),
            })
            ok += 1
        except Exception as e:
            print(f'  失败: {e}')
            fail += 1
    print(f'\n完成: 成功 {ok} / 失败 {fail}')


if __name__ == '__main__':
    main()
