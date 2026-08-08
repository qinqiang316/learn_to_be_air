# -*- coding: utf-8 -*-
"""半佛 B 站视频标题风格分析"""
import json, re, os
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'corpus', 'bili', 'video_list.json')

def main():
    with open(DATA, encoding='utf-8') as f:
        videos = json.load(f)
    print(f'总视频数: {len(videos)}')
    titles = [v['title'] for v in videos]

    # 1. 标题长度分布
    lens = [len(t) for t in titles]
    print(f'\n=== 标题长度 ===')
    print(f'平均: {sum(lens)/len(lens):.1f} 字, 最短: {min(lens)}, 最长: {max(lens)}')
    hist = Counter((l//5)*5 for l in lens)
    for k in sorted(hist):
        print(f'  {k}-{k+4}字: {hist[k]} 条')

    # 2. 前缀模式
    print(f'\n=== 前缀模式 ===')
    pf = Counter()
    for t in titles:
        if t.startswith('【半佛】'): pf['【半佛】'] += 1
        elif t.startswith('半佛'): pf['半佛'] += 1
        elif t.startswith('《'): pf['《书名》开头'] += 1
        else: pf['其他'] += 1
    for k, v in pf.most_common():
        print(f'  {k}: {v} ({v/len(titles)*100:.0f}%)')

    # 3. 结尾标点（问号/感叹号/句号）
    print(f'\n=== 结尾标点 ===')
    ep = Counter(t[-1] for t in titles)
    for k, v in ep.most_common():
        print(f'  {k!r}: {v} ({v/len(titles)*100:.0f}%)')

    # 4. 问号标题
    qs = [t for t in titles if '?' in t or '？' in t]
    print(f'\n=== 问号标题 {len(qs)} 条 ({len(qs)/len(titles)*100:.0f}%) ===')
    for t in qs[:20]:
        print('  ', t)

    # 5. 高频词
    print(f'\n=== 高频词（2字+） ===')
    words = Counter()
    for t in titles:
        body = re.sub(r'【半佛】', '', t)
        for w in re.findall(r'[\u4e00-\u9fa5]{2,}', body):
            words[w] += 1
    for w, c in words.most_common(30):
        print(f'  {w}: {c}')

    # 6. 句式模板
    print(f'\n=== 常见句式模板 ===')
    pats = Counter()
    for t in titles:
        body = re.sub(r'【半佛】', '', t).strip()
        if body.endswith('？') or body.endswith('?'): pats['疑问式'] += 1
        elif '到底' in body or '怎么' in body or '为什么' in body or '如何' in body: pats['探究式(为什么/如何/怎么/到底)'] += 1
        elif '让我' in body or '把我' in body or '给我' in body: pats['第一人称经历式(让我/把我/给我)'] += 1
        elif '是' in body: pats['判断式(…是…)'] += 1
        elif body.startswith('别') or body.startswith('不要') or body.startswith('劝'): pats['劝诫式'] += 1
        elif '？' not in body and len(body) <= 12: pats['短断言式'] += 1
        else: pats['其他'] += 1
    for k, v in pats.most_common():
        print(f'  {k}: {v}')

if __name__ == '__main__':
    main()
