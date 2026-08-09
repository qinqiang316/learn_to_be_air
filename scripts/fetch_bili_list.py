# -*- coding: utf-8 -*-
"""半佛 B 站全量视频列表拉取（wbi 签名 + 慢速防限流版）"""
import json, time, urllib.parse, urllib.request, hashlib, functools, os

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
MID = 37663924
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'corpus', 'bili', 'video_list.json')

MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
    61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
    36, 20, 34, 44, 52
]

def get_mixin_key(orig: str) -> str:
    return functools.reduce(lambda s, i: s + orig[i], MIXIN_KEY_ENC_TAB, "")[:32]

def enc_wbi(params: dict, img_key: str, sub_key: str) -> dict:
    mixin_key = get_mixin_key(img_key + sub_key)
    curr_time = round(time.time())
    params['wts'] = curr_time
    params = dict(sorted(params.items()))
    params = {k: ''.join(filter(lambda c: c not in "!'()*", str(v))) for k, v in params.items()}
    query = urllib.parse.urlencode(params)
    wbi_sign = hashlib.md5((query + mixin_key).encode()).hexdigest()
    params['w_rid'] = wbi_sign
    return params

def fetch(url, headers=None, retries=5):
    last_err = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers or {'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                raw = r.read().decode('utf-8', errors='ignore')
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            last_err = f'HTTP {e.code}'
            if e.code == 412:
                wait = 20 * (i + 1)
                print(f'  412 风控，等待 {wait}s...')
                time.sleep(wait)
            else:
                time.sleep(5)
        except Exception as e:
            last_err = str(e)
            time.sleep(3)
    raise RuntimeError(f'fetch failed: {last_err}')

def get_wbi_keys():
    d = fetch('https://api.bilibili.com/x/web-interface/nav')
    img_url = d['data']['wbi_img']['img_url']
    sub_url = d['data']['wbi_img']['sub_url']
    img_key = img_url.rsplit('/', 1)[1].split('.')[0]
    sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]
    return img_key, sub_key

def main():
    img_key, sub_key = get_wbi_keys()
    print(f'wbi keys: {img_key[:8]} / {sub_key[:8]}')
    all_videos = []
    pn = 1
    total = None
    while True:
        params = {'mid': MID, 'ps': 100, 'pn': pn}
        signed = enc_wbi(params, img_key, sub_key)
        url = 'https://api.bilibili.com/x/space/wbi/arc/search?' + urllib.parse.urlencode(signed)
        print(f'page {pn} ...')
        d = fetch(url, {'User-Agent': UA})
        if d.get('code') != 0:
            code = d.get('code')
            print(f'page {pn} code={code} msg={d.get("message")} — stop')
            # 风控类错误等待冷却后重试同页，最多 3 次
            if code in (-352, -412, -799) and pn <= 2:
                for attempt in range(3):
                    print(f'  冷却 {60*(attempt+1)}s 后重试第 {pn} 页...')
                    time.sleep(60 * (attempt + 1))
                    d = fetch(url, {'User-Agent': UA})
                    if d.get('code') == 0:
                        break
            if d.get('code') != 0:
                break
        data = d.get('data') or {}
        if total is None:
            total = data.get('page', {}).get('count')
            print(f'总视频数: {total}')
        vlist = (data.get('list') or {}).get('vlist') or []
        if not vlist:
            print(f'page {pn} vlist 空，结束')
            break
        for v in vlist:
            all_videos.append({
                'bvid': v.get('bvid'), 'aid': v.get('aid'),
                'title': v.get('title'), 'length': v.get('length'),
                'play': v.get('play'), 'comment': v.get('comment'),
                'created': v.get('created'), 'tid': v.get('tid'),
                'tname': v.get('tname'), 'desc': (v.get('description') or '')[:200],
            })
        print(f'  +{len(vlist)} (累计 {len(all_videos)})')
        if len(all_videos) >= total or pn >= 15:
            break
        pn += 1
        time.sleep(12)  # 每页间隔，防限流

    if not all_videos:
        print('!! 未拉到任何视频，保留现有清单不动（防止风控失败覆盖数据）')
        return
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(all_videos, f, ensure_ascii=False, indent=1)
    print(f'\n完成: {len(all_videos)} 条 → {OUT}')
    from collections import Counter
    tnames = Counter(v['tname'] for v in all_videos)
    print('分区分布:', dict(tnames.most_common(10)))

if __name__ == '__main__':
    main()
