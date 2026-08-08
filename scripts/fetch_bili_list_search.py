# -*- coding: utf-8 -*-
"""半佛 B 站全量视频列表拉取（搜索接口通道，防 wbi 风控）"""
import json, time, urllib.parse, urllib.request, re, os

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
MID = 37663924
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'corpus', 'bili', 'video_list.json')

def clean(t):
    return re.sub(r'<[^>]+>', '', t or '')

def fetch_json(url, retries=5):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Referer': 'https://www.bilibili.com/'})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode('utf-8', errors='ignore'))
        except urllib.error.HTTPError as e:
            wait = 15 * (i + 1)
            print(f'  HTTP {e.code}, 等 {wait}s...', flush=True)
            time.sleep(wait)
        except Exception as e:
            print(f'  err: {e}, 等 10s...', flush=True)
            time.sleep(10)
    return None

def main():
    all_videos = {}
    # 关键词列表：覆盖标题带/不带【半佛】的视频
    keywords = ['半佛', '半佛仙人', '我爱这个魔幻的世界']
    for kw in keywords:
        for page in range(1, 21):
            params = urllib.parse.urlencode({
                'search_type': 'video', 'keyword': kw,
                'mid': MID, 'page': page, 'page_size': 50
            })
            url = 'https://api.bilibili.com/x/web-interface/search/type?' + params
            print(f'[{kw}] page {page} ...', flush=True)
            d = fetch_json(url)
            if not d or d.get('code') != 0:
                print(f'  code={d.get("code") if d else "None"}', flush=True)
                break
            res = (d.get('data') or {}).get('result') or []
            if not res:
                break
            for v in res:
                if str(v.get('mid')) != str(MID):
                    continue
                bvid = v.get('bvid')
                if bvid and bvid not in all_videos:
                    all_videos[bvid] = {
                        'bvid': bvid,
                        'title': clean(v.get('title', '')),
                        'length': v.get('duration', ''),
                        'play': v.get('play', 0),
                        'created': v.get('pubdate', 0),
                        'tid': v.get('typeid', 0),
                        'tname': v.get('typename', ''),
                        'desc': clean(v.get('description', ''))[:200],
                    }
            time.sleep(2)  # 防限流
            if len(res) < 50:
                break

    videos = list(all_videos.values())
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=1)
    print(f'\n完成: {len(videos)} 条 → {OUT}')
    from collections import Counter
    tnames = Counter(v['tname'] for v in videos)
    print('分区分布:', dict(tnames.most_common(10)))

if __name__ == '__main__':
    main()
