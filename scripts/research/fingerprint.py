# -*- coding: utf-8 -*-
"""半佛语料量化指纹：按介质分组统计句式特征（全介质版，供增量更新联动）。

用法:
  python3 scripts/research/fingerprint.py            # 全介质均值表
  python3 scripts/research/fingerprint.py --file <语料文件>   # 单篇统计（验证新语料风格）
"""
import os, re, glob, json, sys, argparse

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CERTAIN = ["肯定", "一定", "就是", "其实", "说白了", "真的", "必须", "绝对", "显然", "无非", "本质", "核心", "永远", "只有", "唯一"]
UNCERTAIN = ["可能", "也许", "大概", "或许", "应该", "估计", "说不定", "未必", "不一定"]
TURN = ["但是", "但", "然而", "不过", "可是"]

GROUPS = {
    "公众号": ["corpus/半佛_*.txt", "corpus/wechat/*"],
    "B站口播": ["corpus/bili/subtitles/*.txt"],
    "演讲": ["corpus/interview/半佛_演讲_*"],
    "专访": ["corpus/interview/半佛_访谈_*", "corpus/interview/半佛_对谈_*"],
    "播客": ["corpus/interview/半佛_播客_*.txt"],
}


def clean_body(text):
    lines = text.split("\n")
    return "\n".join(l for l in lines if not l.startswith("# ") and not l.startswith("- ") and not l.startswith("> "))


def stat(body):
    n = len(body)
    if n < 200:
        return None
    compact = re.sub(r"\s+", "", body)
    exclaim = len(re.findall(r"[!！]", compact))
    question = len(re.findall(r"[?？]", compact))
    sents = [s for s in re.split(r"[。！？!?；;]", compact) if len(s) > 1]
    avg_len = round(sum(len(s) for s in sents) / max(1, len(sents)), 1)
    k = max(1, n / 1000)

    def per1000(wl):
        return round(sum(len(re.findall(w, compact)) for w in wl) / k, 1)

    return {
        "字数": n,
        "感叹号/千字": round(exclaim / k, 2),
        "问号/千字": round(question / k, 1),
        "平均句长": avg_len,
        "确定性词/千字": per1000(CERTAIN),
        "不确定性词/千字": per1000(UNCERTAIN),
        "转折词/千字": per1000(TURN),
        "我/千字": per1000(["我"]),
        "你/千字": per1000(["你"]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="统计单篇语料文件（验证新语料风格）")
    args = ap.parse_args()

    if args.file:
        raw = open(args.file, encoding="utf-8").read()
        s = stat(clean_body(raw))
        print(json.dumps(s, ensure_ascii=False, indent=1))
        return

    from collections import defaultdict
    results = {}
    for med, pats in GROUPS.items():
        files = []
        for p in pats:
            for f in glob.glob(os.path.join(BASE, p)):
                if os.path.isdir(f) or f.endswith(".bak"):
                    continue
                files.append(f)
        if not files:
            continue
        agg = defaultdict(float)
        cnt = 0
        print(f"\n== {med}（{len(files)} 篇）==")
        for f in files:
            raw = open(f, encoding="utf-8").read()
            s = stat(clean_body(raw))
            if not s:
                print(f"  {os.path.basename(f)}: 过短跳过")
                continue
            cnt += 1
            print(f"  {os.path.basename(f)}: {s}")
            for k, v in s.items():
                agg[k] += v
        if cnt:
            avg = {k: round(v / cnt, 2) for k, v in agg.items()}
            avg["字数"] = int(avg["字数"])
            results[med] = avg
            print(f"  → {med} 平均: {avg}")
    print("\n===== 汇总（各介质均值）=====")
    print(json.dumps(results, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
