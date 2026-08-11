---
name: writing-style-coach
description: 用户说"学习某博主的文字风格/文风"时使用。搜索博主素材→总结风格→对照用户写作基线→输出学习计划。
---

# 博主文字风格学习

## 触发条件
- 用户说"学习 XX 的风格 / 文风 / 写法"
- 用户想模仿某位博主、作者、UP主的写作方式

## 核心原则
1. **风格结论必须来自本人原文**，不能只抄二手分析。二手拆解只作参考，需用原文验证。
2. **交叉验证**：同一模式至少在 2-3 篇原文里反复出现才算真实 DNA，只出现一次是偶然。
3. **"不做的事"比"做的事"更能定义风格**（禁忌清单：不用什么、不做什么，往往比规则清单更关键）。
4. 学习计划必须带**可验证动作**，不是空泛建议。

## 标准流程

### Step 1 素材收集（30 分钟内）
- web_search 博主名 + 平台（公众号/B站/知乎/专栏），找到：
  - 2-3 篇**可抓全文**的本人文章（转载站优先：woshipm 等常授权转载）
  - 1-2 篇文风拆解/访谈（参考用）
- 下载 HTML：`curl -s -L -A "Mozilla/5.0..." URL -o file.html`
- 提取正文：python 去 script/style/标签 → 存 txt
- 抓不到全文的（公众号原文常被墙），用搜索结果里的长引用片段补充
- **视频/音频语料 → 借用 notebooklm-brief 通道**（见下方"NotebookLM 借用"）：
  - B站视频：借用 `src/source.py` 的 `youtube_match`（B站→YouTube 原片匹配：标题相似+时长接近双条件）→ 命中则传 YouTube 链接让 NotebookLM **服务端自动转写**（省本地转写）；未命中回退 `bilibili_to_audio` 下载音频上传
  - YouTube 视频：直接传链接，NotebookLM 服务端转写
  - 本地音频/视频：直接上传转写

### Step 1.5 NotebookLM 借用（notebooklm-brief 项目）
项目路径 `/Users/qqiang/AI project/06-工具项目/notebooklm-brief`，**必须用 venv python**：
```bash
VPY="/Users/qqiang/.hermes/hermes-agent/venv/bin/python"
"$VPY" main.py "<链接>" --ask "请提取这篇/这个视频的完整文字内容"   # 语料转写
"$VPY" main.py "<链接>" --no-learn --no-archive                    # 只要分析，跳过学习产物和归档
```
- 输出在 `output/笔记-<标题>/`，其中 `<标题>.笔记.md` 含原文/转写全文
- 分析思路借用：NotebookLM 来源约束（只依据材料回答、带引用锚点），适合让模型自证风格结论；`--ask "这个作者的写作风格特征是什么，引用原文佐证"` 可出带锚点的风格初稿
- 需代理访问 Google（macOS 走 Shadowrocket 隧道，proxy 留空直连）；登录态 `~/.notebooklm/profiles/default/storage_state.json`（自动刷新）
- 详细命令/坑见 skill `notebooklm-brief`

### Step 2 风格拆解（对每篇原文过 24 小项）
见 `references/style-dimensions.md`：A节奏结构(6) B词汇(6) C语气(5) D修辞(4) E格式(3) + F禁忌清单 + 量化附录（句式指纹）+ 三重验证。
逐篇记录后：跨篇复现 → 生成力验证（能否推断未见话题写法）→ 排他性（非烂大街特征），三重全过才算 DNA。

### Step 3 学习者画像
读 memory/user profile 中用户的写作基线（口语化程度、句式、结构偏好、禁忌），作为对照基准。没有现成画像就先问用户 3 个问题：平时写什么文体、最想改哪一点、接受哪种学习强度。

### Step 4 差距对照 + 学习计划
- 对照表：维度 | 博主有 | 你有 | 差距 | 练法
- 学习计划：分阶段（模仿复写→逐句对比→内化改造→实战应用），每阶段带可验证练习
- 用 `references/learning-plan-template.md`

### Step 5 交付
- 输出：风格档案 + 学习计划（md）
- 存档到 `/Users/qqiang/AI project/05-日常工具/下载文件/<博主>风格学习/`，含原文 txt 语料
- 首次分析某博主时，把风格档案存为 `references/author-profiles/<博主>.md`，下次直接复用

## 方法来源（2026-08 调研）
- 花叔女娲.skill (`alchaincyf/nuwa-skill`)：表达DNA量化（句式指纹6指标+风格标签7轴）、三重验证、诚实边界
- ghost-writer (`OneSpiral/ghost-writer`)：24维风格细分（节奏结构/词汇/语气/修辞/格式）
- 本 skill 独有：学习者对照表 + 四阶段学习计划（两者都没有）

## 坑位
- **公众号原文 mp.weixin.qq.com 常抓不到**：用 woshipm/36氪/知乎等授权转载站
- **头条 m.toutiao.com 是 JS 渲染**：curl 抓不到正文，换源
- **web_extract 工具不存在**（本机无此工具）：一律 curl + python 提取
- 搜索结果里的"别人怎么评价他"不是风格证据，只当线索
- **notebooklm-brief 必须用 venv python**（bash 的 python PYTHONPATH 被污染会挂）；Google 需代理；详见 skill `notebooklm-brief`

## 支持文件
- `references/style-dimensions.md` — 24小项分析模板（含量化附录+三重验证）
- `references/learning-plan-template.md` — 学习计划模板
- `references/author-profiles/banfo.md` — 半佛仙人风格档案（示例）

## 关联 skill
- `notebooklm-brief` — 视频/音频转写、原文提取、来源约束分析（本项目借用的通道）
