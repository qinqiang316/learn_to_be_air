# -*- coding: utf-8 -*-
"""半佛 B 站视频字幕拉取（代表作 + 分层样本）"""
import json, time, urllib.parse, urllib.request, re, os

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE, 'corpus', 'bili', 'subtitles')
os.makedirs(OUT_DIR, exist_ok=True)

def fetch_json(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Referer': 'https://www.bilibili.com/'})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode('utf-8', errors='ignore'))
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(5 * (i + 1))

def get_cid(bvid):
    d = fetch_json(f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}')
    if d.get('code') != 0:
        raise RuntimeError(f'view {bvid}: {d.get("message")}')
    return d['data']['cid'], d['data'].get('duration', 0), d['data'].get('title', '')

def get_subtitle(bvid, cid):
    d = fetch_json(f'https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}')
    subs = (d.get('data') or {}).get('subtitle', {}).get('subtitles') or []
    if not subs:
        return None
    # 优先中文 AI 字幕
    sub = None
    for s in subs:
        if s.get('lan') in ('zh-CN', 'zh-cn', 'ai-zh'):
            sub = s
            break
    if not sub:
        sub = subs[0]
    sub_url = sub.get('subtitle_url', '')
    if sub_url.startswith('//'):
        sub_url = 'https:' + sub_url
    return sub_url

def download_subtitle(bvid):
    cid, dur, title = get_cid(bvid)
    sub_url = get_subtitle(bvid, cid)
    if not sub_url:
        return None, dur, title
    d = fetch_json(sub_url)
    body = d.get('body') or []
    text = '\n'.join(item.get('content', '') for item in body)
    return text, dur, title

def main():
    # 样本：代表作 + 分层（按播放量排序取 top，混合年份）
    with open(os.path.join(BASE, 'corpus', 'bili', 'video_list.json'), encoding='utf-8') as f:
        videos = json.load(f)
    # 有播放量的按播放量排序，取 top 20；再加几个早期视频（created 最老）
    with_play = [v for v in videos if v.get('play')]
    with_play.sort(key=lambda v: v.get('play', 0), reverse=True)
    top20 = with_play[:20]
    oldest = sorted(with_play, key=lambda v: v.get('created', 0))[:5]
    targets = []
    seen = set()
    for v in top20 + oldest:
        if v['bvid'] not in seen:
            seen.add(v['bvid'])
            targets.append(v)
    print(f'计划拉取 {len(targets)} 个视频字幕')
    results = []
    for i, v in enumerate(targets):
        bvid = v['bvid']
        print(f'[{i+1}/{len(targets)}] {bvid} {v.get("title","")[:30]}', flush=True)
        try:
            text, dur, title = download_subtitle(bvid)
            if text:
                fn = os.path.join(OUT_DIR, f'{bvid}.txt')
                with open(fn, 'w', encoding='utf-8') as f:
                    f.write(f'# {title}\n# 时长: {dur}s 播放: {v.get("play")}\n\n{text}')
                results.append({'bvid': bvid, 'title': title, 'chars': len(text), 'dur': dur, 'play': v.get('play')})
                print(f'  ✅ {len(text)} 字', flush=True)
            else:
                print(f'  ⚠️ 无字幕', flush=True)
        except Exception as e:
            print(f'  ❌ {e}', flush=True)
        time.sleep(2)  # 防限流
    with open(os.path.join(OUT_DIR, 'index.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print(f'\n完成: {len(results)} 个字幕 → {OUT_DIR}')

if __name__ == '__main__':
    main()
