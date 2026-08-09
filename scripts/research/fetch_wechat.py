# -*- coding: utf-8 -*-
"""公众号方向：转载站全文抓取（数英/36氪/腾讯新闻/知乎等）。

用法: python3 fetch_wechat.py            # 抓取内置清单全部
      python3 fetch_wechat.py <url> <标题>  # 追加抓取单篇
"""
import os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import extract_main_text, save_text

# 半佛公众号（半佛仙人 + 仙人JUMP）授权转载/镜像全文，按发布时间
ARTICLES = [
    {
        "title": "半佛_公众号写作秘诀_新榜大会2020",
        "url": "https://www.digitaling.com/articles/248485.html",
        "source": "数英（新榜大会分享转载）",
        "date": "2020-01",
        "note": "半佛本人分享公众号写作方法论，含自述风格",
    },
    {
        "title": "半佛_深扒半佛仙人_韭菜局终结者",
        "url": "https://zhuanlan.zhihu.com/p/98354030",
        "source": "知乎专栏·新榜（二手拆解，仅作参考）",
        "date": "2019-12",
        "note": "二手拆解：他的推文不遵循公众号爆款规律，超长文无图不排版",
    },
]


def main():
    args = sys.argv[1:]
    if len(args) >= 2:
        ARTICLES.insert(0, {"title": args[1], "url": args[0], "source": "手动指定", "date": ""})
    ok, fail = 0, 0
    for a in ARTICLES:
        print(f"[公众号] {a['title']} ← {a['url']}")
        try:
            text = extract_main_text(a['url'])
            if len(text) < 300:
                print(f'  正文过短({len(text)})，可能被反爬，跳过')
                fail += 1
                continue
            save_text('wechat', a['title'], text, {
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
