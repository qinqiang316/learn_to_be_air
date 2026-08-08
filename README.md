# be_air — 博主文字风格学习项目

> 输入任意博主 → 自动搜集素材（文章/视频/音频）→ 24 小项风格拆解 → 对照学习者基线 → 输出定制学习计划。

## 这是什么

把「向某位博主学文字风格」做成一条可复用的流水线，核心是一份 Agent Skill（`writing-style-coach`），外加半佛仙人的完整示例。

## 目录结构

```
be_air/
├── SKILL.md                        # writing-style-coach 主流程
├── references/
│   ├── style-dimensions.md         # 24 小项风格拆解模板（含量化附录+三重验证）
│   ├── learning-plan-template.md   # 四阶段学习计划模板
│   └── author-profiles/
│       └── banfo.md                # 半佛仙人风格档案（含实测量化指纹）
├── corpus/
│   ├── 半佛_盲盒韭菜.txt            # 一手原文语料（2019 代表作）
│   └── ax_文风拆解.txt             # 文风拆解参考（二手）
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
cp -r SKILL.md references ~/AppData/Local/hermes/skills/productivity/writing-style-coach/

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
