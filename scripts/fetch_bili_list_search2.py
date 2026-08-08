# -*- coding: utf-8 -*-
"""半佛 B 站全量视频列表拉取（搜索接口，边抓边存，失败跳过）"""
import json, time, urllib.parse, urllib.request, re, os

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
MID = 37663924
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'corpus', 'bili', 'video_list.json')

def clean(t):
    return re.sub(r'<[^>]+>', '', t or '')

def fetch_json(url, retries=2):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Referer': 'https://www.bilibili.com/'})
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read().decode('utf-8', errors='ignore'))
        except Exception:
            time.sleep(8)
    return None

def main():
    all_videos = {}
    # 已抓到的兜底（从快照和之前响应）
    snapshot = os.path.join(BASE, 'corpus', 'bili', 'from_snapshot.json')
    if os.path.exists(snapshot):
        for v in json.load(open(snapshot, encoding='utf-8')):
            all_videos[v['bvid']] = {'bvid': v['bvid'], 'title': v['title']}
    # 从已有 search 响应兜底
    for fn in ['search_mid.json', 'search1.json']:
        p = os.path.join(BASE, 'corpus', 'bili', fn)
        if os.path.exists(p):
            try:
                d = json.load(open(p, encoding='utf-8'))
                for v in (d.get('data', {}).get('result') or []):
                    if str(v.get('mid')) == str(MID) and v.get('bvid'):
                        all_videos[v['bvid']] = {
                            'bvid': v['bvid'], 'title': clean(v.get('title', '')),
                            'length': v.get('duration', ''), 'play': v.get('play', 0),
                            'created': v.get('pubdate', 0), 'tname': v.get('typename', ''),
                        }
            except Exception:
                pass

    keywords = ['半佛', '半佛仙人']
    for kw in keywords:
        for page in range(1, 21):
            params = urllib.parse.urlencode({
                'search_type': 'video', 'keyword': kw,
                'mid': MID, 'page': page, 'page_size': 50
            })
            url = 'https://api.bilibili.com/x/web-interface/search/type?' + params
            d = fetch_json(url)
            if not d or d.get('code') != 0:
                print(f'[{kw}] p{page} 失败, 跳过', flush=True)
                continue
            res = (d.get('data') or {}).get('result') or []
            if not res:
                print(f'[{kw}] p{page} 空, 结束', flush=True)
                break
            for v in res:
                if str(v.get('mid')) != str(MID):
                    continue
                bvid = v.get('bvid')
                if bvid and bvid not in all_videos:
                    all_videos[bvid] = {
                        'bvid': bvid, 'title': clean(v.get('title', '')),
                        'length': v.get('duration', ''), 'play': v.get('play', 0),
                        'created': v.get('pubdate', 0), 'tname': v.get('typename', ''),
                    }
            print(f'[{kw}] p{page}: 累计 {len(all_videos)}', flush=True)
            # 边抓边存
            with open(OUT, 'w', encoding='utf-8') as f:
                json.dump(list(all_videos.values()), f, ensure_ascii=False, indent=1)
            time.sleep(2)

    videos = list(all_videos.values())
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(videos, f, ensure_ascii=False, indent=1)
    print(f'\n完成: {len(videos)} 条 → {OUT}')

if __name__ == '__main__':
    main()
