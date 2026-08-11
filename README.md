# be_air — 博主文字风格学习项目（支持任意博主）

> 输入任意博主（不限于半佛）→ 自动搜集素材（文章/视频/音频）→ 24 小项风格拆解 → 对照学习者基线 → 输出定制学习计划。

## 这是什么

把「向某位博主学文字风格」做成一条可复用的流水线，核心是两个 Agent Skill：
- `writing-style-coach` — 风格拆解 + 学习计划（**首次/增量双模式**）
- `blogger-research` — 博主全平台调研（首次加入=搜索建档；再次加入=增量更新）

半佛仙人是首个完整示例（全介质语料 + v4 档案）。

## 博主注册机制

- 注册表：`references/author-profiles/_index.md`（哪些博主已建档）
- **首次加入某博主**：走 `blogger-research` 首次建档模式——搜索该博主公众号/B站/知乎/微博/头条/播客全平台内容 → 建 `references/author-profiles/<博主>.md` 档案 → 语料入 `corpus/<博主>/` → 登记注册表
- **再次加入**：读已有档案 + 语料缺口 → 只补新增内容 → 更新档案对应小节

## 目录结构

```
be_air/
├── SKILL.md                        # writing-style-coach 主流程（多博主通用）
├── notebooklm-output/              # NotebookLM 分析/转写过程文件（与 notebooklm-brief 的 output/ 独立）
│   ├── 笔记-半佛-*                  #   半佛内容分析（5本好书/奶茶加盟/营养工厂/活着就是熬着）
│   ├── 笔记-三五环No117 等          #   播客转写（三五环/姜就一下/新榜编辑部/知行小酒馆E165/E195）
│   └── ...（每个笔记本：归档笔记.md + source/ + generated/ + knowledge/）
├── references/
│   ├── style-dimensions.md         # 24 小项风格拆解模板（含量化附录+三重验证）
│   ├── learning-plan-template.md   # 四阶段学习计划模板
│   └── author-profiles/
│       ├── _index.md               # 博主注册表（哪些博主已建档）
│       └── banfo.md                # 半佛仙人风格档案（示例，含实测量化指纹）
├── corpus/
│   ├── 半佛_盲盒韭菜.txt            # 半佛一手原文语料（2019 代表作，历史平铺）
│   ├── ax_文风拆解.txt             # 文风拆解参考（二手）
│   └── <新博主>/                    # 新博主语料目录（wechat/bili/interview/weibo 子目录）
└── 学习计划_强哥定制.md             # 半佛风格 → 强哥基线的定制计划（示例交付）
```

## 方法来源

- **花叔·女娲.skill** (`alchaincyf/nuwa-skill`)：表达DNA量化（句式指纹 6 指标 + 风格标签 7 轴）、三重验证、诚实边界
- **ghost-writer** (`OneSpiral/ghost-writer`)：24 维风格细分（节奏结构/词汇/语气/修辞/格式）
- **notebooklm-brief**（本项目配套工具）：视频/音频语料服务端转写、原文提取、来源约束分析
- 本 skill 独有：学习者对照表 + 四阶段学习计划

## 快速使用

```bash
# 安装 skill 到 Hermes
cp -r SKILL.md references ~/.hermes/skills/productivity/writing-style-coach/

# 触发
# 对 Hermes 说："学习 XX 博主的文字风格"
```

## 方法论要点

1. **风格结论必须来自本人原文**，二手拆解只作参考
2. **交叉验证**：同一模式 ≥2 篇原文反复出现才算 DNA
3. **"不做的事"比"做的事"更能定义风格**（禁忌清单）
4. 学习计划必须带**可验证动作**

## License

MIT
