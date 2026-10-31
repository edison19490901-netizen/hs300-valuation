# 沪深300 估值看板

用公开数据复现沪深300指数的估值分析：**PE/PB 与历史分位、ERP 与股债性价比、EPS/ROE 盈利质量**。

在线看板（手机可直接"添加到主屏幕"，像 App 一样使用）：

**https://edison19490901-netizen.github.io/hs300-valuation/**

> 数据为月末口径，来自乐咕乐股、中证指数、中债（经 akshare）。仅供研究，不构成投资建议。

## 看板内容

| 卡片 | 回答的问题 |
|---|---|
| 指数点位、PE-TTM 与历史分位 | 相对自身历史贵不贵？分位处于什么位置？ |
| 盈利收益率、ERP、股息率与 10 年国债 | 相对债券贵不贵？ERP 高是股票便宜还是债券太贵？ |
| EPS、ROE、PE 与 PB | 盈利质量是否支撑估值？低 PB 是不是低 ROE 造成的？ |

交互：十字线 tooltip（手机点按可用）、键盘左右键、每张卡片可展开数据表、深色模式。

## 本地运行

```bash
python -m pip install -U akshare pandas openpyxl

REFRESH=1 python analyze.py     # 拉取数据、计算分位/ERP，写 summary.json 与 data/*.csv
python build_dashboard.py       # 生成 index.html 与 沪深300估值看板.html
```

不联网、只改图表时，直接运行 `python build_dashboard.py` 即可。

## 文件说明

| 文件 | 作用 |
|---|---|
| `analyze.py` | 数据抓取与指标计算（`REFRESH=1` 强制刷新缓存） |
| `build_dashboard.py` | 生成单文件 HTML 看板 |
| `index.html` | 在线看板入口（PWA 启动页） |
| `manifest.webmanifest` / `sw.js` | PWA 清单与离线缓存 |
| `300.png` 等图标 | App 图标 |
| `沪深300估值报告.md` | 方法论、当前读数、局限 |
| `HANDOFF.md` | 交接文档：数据口径、更新流程、排错 |
| `summary.json` | 全部指标与分位的结构化结果 |
| `data/` | 原始月度数据与派生序列 |

## 口径提示

- PE、PB 主口径为**整体法（市值加权）**，乐咕乐股月度数据；与中证官网数值不同，**不要混用**。
- 股息率历史用 `H00300 / 000300` 全收益指数推算，与官网"最新分红/总市值"口径存在差异，看板中已注明。
- 分位同时给出近 5 年、近 10 年、全历史，结论对样本期敏感。

详见 [沪深300估值报告.md](沪深300估值报告.md) 与 [HANDOFF.md](HANDOFF.md)。
