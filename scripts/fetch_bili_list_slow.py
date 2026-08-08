# -*- coding: utf-8 -*-
"""半佛 B 站全量视频列表拉取（极慢速版：每页间隔 30s，容忍 412/-799 重试）"""
import json, time, urllib.parse, urllib.request, hashlib, functools, os, sys

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

def fetch(url, headers=None, retries=8):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers or {'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                raw = r.read().decode('utf-8', errors='ignore')
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            code = e.code
            print(f'  HTTP {code}, 第{i+1}次重试, 等待 {30*(i+1)}s...', flush=True)
            time.sleep(30 * (i + 1))
        except Exception as e:
            print(f'  err: {e}, 第{i+1}次重试', flush=True)
            time.sleep(15)
    return None

def get_wbi_keys():
    d = fetch('https://api.bilibili.com/x/web-interface/nav')
    if not d or not d.get('data') or not d['data'].get('wbi_img'):
        return None, None
    img_url = d['data']['wbi_img']['img_url']
    sub_url = d['data']['wbi_img']['sub_url']
    img_key = img_url.rsplit('/', 1)[1].split('.')[0]
    sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]
    return img_key, sub_key

def main():
    img_key, sub_key = get_wbi_keys()
    if not img_key:
        print('拿不到 wbi keys，退出')
        return
    print(f'wbi keys: {img_key[:8]} / {sub_key[:8]}', flush=True)
    all_videos = []
    pn = 1
    total = None
    while pn <= 15:
        params = {'mid': MID, 'ps': 100, 'pn': pn}
        signed = enc_wbi(params, img_key, sub_key)
        url = 'https://api.bilibili.com/x/space/wbi/arc/search?' + urllib.parse.urlencode(signed)
        print(f'page {pn} ...', flush=True)
        d = fetch(url, {'User-Agent': UA})
        if d is None:
            print(f'page {pn} 彻底失败，保存已获取 {len(all_videos)} 条', flush=True)
            break
        if d.get('code') != 0:
            print(f'page {pn} code={d.get("code")} msg={d.get("message")}', flush=True)
            if d.get('code') in (-799, -412):
                print('  限流，等 60s 重试', flush=True)
                time.sleep(60)
                continue
            break
        data = d.get('data') or {}
        if total is None:
            total = data.get('page', {}).get('count')
            print(f'总视频数: {total}', flush=True)
        vlist = (data.get('list') or {}).get('vlist') or []
        if not vlist:
            print(f'page {pn} vlist 空，结束', flush=True)
            break
        for v in vlist:
            all_videos.append({
                'bvid': v.get('bvid'), 'aid': v.get('aid'),
                'title': v.get('title'), 'length': v.get('length'),
                'play': v.get('play'), 'comment': v.get('comment'),
                'created': v.get('created'), 'tid': v.get('tid'),
                'tname': v.get('tname'), 'desc': (v.get('description') or '')[:200],
            })
        print(f'  +{len(vlist)} (累计 {len(all_videos)})', flush=True)
        # 落盘（防中断丢数据）
        with open(OUT, 'w', encoding='utf-8') as f:
            json.dump(all_videos, f, ensure_ascii=False, indent=1)
        if len(all_videos) >= (total or 1):
            break
        pn += 1
        time.sleep(30)  # 每页间隔 30 秒，防限流

    print(f'\n完成: {len(all_videos)} 条 → {OUT}', flush=True)

if __name__ == '__main__':
    main()
