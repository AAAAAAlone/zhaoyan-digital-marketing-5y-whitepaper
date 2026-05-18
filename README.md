# 赵岩的数字营销实战群 · 五年汇报白皮书

全量 **342,260** 条群消息（2021-04-18 — 2026-05-15）的数据分析与可视化交付物。

## 内容

| 路径 | 说明 |
|------|------|
| [`赵岩的数字营销实战群-五年汇报白皮书-by加玮.md`](./赵岩的数字营销实战群-五年汇报白皮书-by加玮.md) | 主白皮书（结论作主标题，图表 + 原始数据引用） |
| [`03-图表规范与清单.md`](./03-图表规范与清单.md) | 22 张图规范（C01—C22）；桑基图按年 **100% 占比** |
| [`assets/charts/`](./assets/charts/) | 1920×1080 PNG 图表 |
| [`assets/data/`](./assets/data/) | 原始 JSON（`manifest.json`、`l1-topics.json`、`expand-stats.json` 等） |
| [`ppt/index.html`](./ppt/index.html) | 杂志风横向网页 PPT（52 页，结论标题 + 结构 kicker） |

## 本地预览 PPT

```bash
cd ppt && python3 -m http.server 8765
# 浏览器打开 http://localhost:8765/
```

## 制图

```bash
python3 export_all_charts.py   # 生成 PNG + 更新 assets/data
python3 gen_deck_full.py       # 重建 ppt/index.html
python3 build_whitepaper_v2.py # 向 MD 注入 GitHub 图床链接
```

## 数据说明

- **占比图**（C08、C09、C13、C15）：每年合计 100%，用于看结构迁移。
- **绝对值图**（C04—C07、C10 等）：看体量与峰值；群总量下降时议题绝对值也会下降。
- 原始消息 `*.jsonl` 体积过大，**未纳入本仓库**；统计来自本地全量扫描脚本。

## 许可

群内发言引用见白皮书第六篇；数据图表与文稿 © 加玮 / 加搜科技整理用途。
