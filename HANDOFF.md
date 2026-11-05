# HANDOFF：沪深300 估值看板

> 交接时间：2026-10-31　｜　数据快照：2026-10-30　｜　目录：`D:\Claudeee\沪深300估值`

---

## 1. 项目目标

用公开数据复现沪深300的估值分析，回答三个问题：

1. **相对自身历史贵不贵**：PE/PB/股息率 + 历史分位；
2. **相对债券贵不贵**：ERP、盈利收益率、股债利差；
3. **盈利质量是否支撑估值**：EPS、ROE、净利润趋势。

产出是一个单文件 HTML 看板（可双击离线打开）+ 一个可安装的 PWA 在线版 + 一份方法报告 + 可复现的 Python 脚本。

---

## 2. 当前结论快照（2026-10-30）

| 指标 | 当前 | 近10年分位 | 近5年分位 | 全历史分位 |
|---|---:|---:|---:|---:|
| 收盘点位 | 3,985.50 | — | — | — |
| PE-TTM（整体法） | 12.17 | 47.5% | 61.7% | 42.9% |
| 静态 PE | 13.21 | 62.5% | 70.0% | 50.2% |
| PE 中位数 | 17.56 | 5.0% | 3.3% | 5.4% |
| PB（整体法） | 1.33 | 27.5% | 45.0% | 16.2% |
| ROE（PB ÷ PE） | 10.93% | 8.3% | 16.7% | 3.9% |
| 盈利收益率 E/P | 8.22% | 53.3% | 40.0% | 57.5% |
| ERP | 6.57% | 84.2% | 71.7% | 82.6% |
| 10 年国债 | 1.65% | — | — | 1.1% |
| 股息率（全收益指数推算） | 2.39% | 68.3% | 38.3% | 69.7% |
| 股息率（中证官网） | 3.05% | — | — | — |
| EPS 同比 | -6.9% | — | — | — |

**一句话结论：**

- PE 处于近十年中位（47.5%），近五年偏中上（61.7%）——**不是极端便宜**；
- PB 1.33 偏低（27.5%），但 ROE 10.93% 处于近十年 **8.3% 分位**——**低 PB 是盈利能力下滑的结果**，不是资产被极端低估；
- ERP 6.57% 处于 84.2% 分位，但 E/P 只有 53.3% 分位，10 年国债 1.65% 处于历史 1.1% 分位——**“便宜”主要是债券太贵**；
- PE 中位数 17.56 处于 5% 分位：**典型个股很便宜，大市值权重股相对贵**，市场广度差；
- EPS 同比 -6.9%，盈利仍在下修；结论是**赔率中性偏正、胜率偏弱**，适合定投/分批，不适合追涨。

---

## 3. 文件与职责

| 文件 | 作用 |
|---|---|
| `analyze.py` | 拉取数据、计算分位/ERP/EPS/ROE、输出 `summary.json` 与 `data/*.csv` |
| `build_dashboard.py` | 读取 `summary.json` + `data/csi300_valuation_history.csv`，生成 HTML |
| `沪深300估值看板.html` | 最终看板，双击即可打开，无需服务器 |
| `index.html` | 同一份看板的在线入口（GitHub Pages 根路径），由 `build_dashboard.py` 一并生成 |
| `manifest.webmanifest` | PWA 清单：名称、图标、`display: standalone` |
| `sw.js` | 离线缓存：页面导航联网优先，断网回退缓存 |
| `更新并发布.bat` | Windows 一键脚本：抓数据 → 重建页面 → 提交 → 确认后推送 |
| `300.png` / `300-192.png` / `300-512.png` / `300-maskable.png` / `apple-touch-icon.png` | App 图标（由 `300.png` 派生） |
| `README.md` | 仓库首页说明与在线地址 |
| `.nojekyll` | 让 GitHub Pages 跳过 Jekyll，静态文件原样发布 |
| `沪深300估值报告.md` | 方法论 + 数据表 + 解读 + 局限 |
| `summary.json` | 全部指标与分位的结构化结果 |
| `data/csi300_valuation_history.csv` | 核心月末序列：点位、PE、PB、10Y、E/P、ERP、股息率、EPS、ROE、滚动分位 |
| `data/*_pe.csv` / `data/*_pb.csv` | 各指数原始 PE/PB 月度数据（沪深300、上证50、中证500、中证1000、中证800） |
| `data/bond_yield.csv` | 中国 10 年期国债收益率（2005 至今） |
| `data/dividend_yield.csv` | 全收益指数推算的股息率序列 |

关键代码位置：

- `analyze.py:46` `fetch_dividend_yield()` — 用 H00300 / 000300 推算股息率
- `analyze.py:88` `main()` — 数据抓取、指标计算、写 `summary.json`
- `build_dashboard.py:60` `HTML` — 页面模板与全部前端逻辑（含 PWA meta）
- `build_dashboard.py:341` `drawFigure()` — 通用多面板图：窄屏字号/面板高度自适应、端点标签防重叠
- `build_dashboard.py:634` — 数据注入，同时写 `沪深300估值看板.html` 与 `index.html`
- `sw.js:2` — 离线缓存版本号；改动页面后需递增

---

## 4. 本地环境

- Windows 11，Git Bash（也可用 PowerShell / cmd）
- Python 3.13
- 依赖：`akshare`、`pandas`、`openpyxl`（读中证 xls 必需）

首次安装：

```bash
cd /d/Claudeee/沪深300估值
python -m pip install -U akshare pandas openpyxl
```

需要联网访问：

- `legulegu.com`：指数 PE/PB（akshare `stock_index_pe_lg` / `stock_index_pb_lg`）
- `csindex.com.cn`：中证官网估值、全收益指数
- 东方财富 / 中债：10 年期国债（akshare `bond_zh_us_rate`）

---

## 5. 本地运行与更新数据（核心）

### 5.1 日常更新（最常用）

```bash
cd /d/Claudeee/沪深300估值
REFRESH=1 python analyze.py     # 强制刷新全部数据
python build_dashboard.py       # 重新生成看板
explorer.exe 沪深300估值看板.html
```

`REFRESH=1` 会重新拉取：

- 乐咕乐股 PE/PB（沪深300 及 4 个对比指数）
- 10 年期国债收益率
- 沪深300 全收益/价格指数（用于股息率）
- 中证指数官网最新估值

耗时通常 30–90 秒，取决于网络；`bond_yield.csv` 是全历史，单次约 8 秒。

### 5.2 只重建页面（不联网）

如果只改了图表/文案，不需要重新抓数据：

```bash
python build_dashboard.py
```

### 5.3 不加强制刷新

```bash
python analyze.py
```

此时 `data/*.csv` 全部走本地缓存，只有“中证指数官网口径”会实时请求（失败会回退）。

### 5.4 PowerShell / cmd

PowerShell：

```powershell
$env:REFRESH=1; python analyze.py
python build_dashboard.py
```

cmd（换盘要带 `/d`，环境变量用 `set` 单独一行）：

```bat
cd /d D:\Claudeee\沪深300估值
set "REFRESH=1"
python analyze.py
python build_dashboard.py
```

发布到 GitHub 的 cmd 写法见 10.2。

### 5.5 数据新鲜度说明

- PE/PB/分位序列是**月末数据**：当月数据要等月末（最后一个交易日）才出现；月中运行会停留在上一个月末。
- 中证官网 `indicator.xls` 只提供最近约 20 个交易日，所以“官网口径”只用于最新值对照，不用于历史分位。
- 看板页头日期读取 `summary.json` 的 `as_of`，不会写死。

### 5.6 缓存与故障处理

| 现象 | 处理 |
|---|---|
| 连接被重置 / `RemoteDisconnected` | 重试；东财、中证接口偶发断连 |
| `summary.json` 里 `csindex` 是 error | 不影响主流程；`build_dashboard.py` 会回退到推算股息率，稍后重跑即可 |
| 某个同业指数（如中证800）报错 | 非阻塞，重跑或忽略；该指数不参与看板主图 |
| 终端中文乱码 | Windows 控制台编码问题；CSV/HTML/MD 均为 UTF-8，用浏览器或编辑器打开正常 |
| `ModuleNotFoundError: openpyxl` | `python -m pip install openpyxl` |
| 数据看起来没更新 | 确认用了 `REFRESH=1`；或直接删除 `data/` 下对应 CSV 再跑 |

---

## 6. 数据口径与计算方式

### 6.1 PE / PB

来源：乐咕乐股，月度。主要列：

- `滚动市盈率`：整体法 TTM（总市值 / 近 12 个月净利润）——**主口径**
- `静态市盈率`：整体法静态
- `滚动市盈率中位数`：成分股 PE 中位数
- `等权滚动市盈率`：等权平均
- `市净率`：整体法 PB

> 中证官网同日 PE 为 13.76 / 15.00，乐咕为 12.17 / 13.21，差异来自成分权重、盈利覆盖与亏损股处理。**不要混用**。

### 6.2 分位

- `pe_pct_10y`：每个时点 PE 在过去 **120 个月**（含当月）中的分位，用于看板副图。
- `summary.json` 的 `pct_10y` / `pct_5y` / `pct_all`：当前值在最后 120 / 60 / 全部样本中的分位。
- 分位采用“历史值 ≤ 当前值”的比例。

### 6.3 ERP 与 E/P

- `E/P = 100 / PE-TTM`（%）
- `ERP = E/P − 10 年期国债收益率`
- 10Y 国债按月末最近可得交易日对齐

### 6.4 EPS 与 ROE

- `EPS = 指数点位 / PE-TTM`
- `ROE = PB / PE × 100`（等价于 E/B，TTM 盈利 / 最新净资产）

### 6.5 股息率（重要口径差异）

公开接口没有沪深300历史股息率序列。本项目的做法：

```
R_t = 沪深300全收益指数(H00300) / 沪深300价格指数(000300)
股息率_t ≈ (R_t / R_{t-12} − 1) × 100
```

含义是“过去 12 个月已实施分红的回报”，与中证官网的“最新分红公告 / 总市值”口径不同：

- 推算值（2026-10-30）：**2.39%**
- 中证官网：**3.05%**

看板中标注为“股息率（全收益指数推算）*”，脚注说明差异；报告同时列出两个口径。

### 6.6 对比指数

上证50、中证500、中证1000、中证800 的 PE/PB 及**全历史**分位。注意看板/报告中的对比表用的是全历史分位，不是 10 年分位。

---

## 7. 看板设计要点

三张卡片：

1. **指数点位、PE-TTM 与历史分位**
   - 三个共用横轴的面板：点位 / PE / 滚动分位
   - 不使用双 Y 轴（点位与 PE 量纲不同，双轴会制造虚假相关）
   - PE 面板有 10 年 20–80 分位阴影 + 中位线
   - 分位面板有 20%/80% 参考线

2. **盈利收益率、ERP、股息率与 10 年国债**
   - 四条曲线同为百分比，共用一条 Y 轴
   - 图例 + 端点直接标注 + 数据表；浅色系列（青/黄）靠标签和表格满足可读性

3. **EPS、ROE、PE 与 PB**
   - 四个面板共用横轴（EPS 元、ROE %、PE 倍、PB 倍，量纲各不相同，不能同轴叠加）
   - ROE 低是当前“低 PB”的关键解释；PE 与 PB 同屏便于对照“PB = PE × ROE”

交互：十字线 + 全部序列 tooltip（手机点按可用）、键盘左右键、每个卡片可展开数据表、深浅色主题切换。

响应式：桌面保持原尺寸；窄屏按 `K = 760 / 容器宽度` 放大 SVG 字号与线宽，并按 `HS` 加高面板，保证手机端读数清晰；端点标签会自动错开并用细引线连回数据点。

配色使用 dataviz 参考调色板并通过校验：

```bash
node <dataviz>/scripts/validate_palette.js "#2a78d6,#eb6834,#1baf7a,#eda100" --mode light
```

浅色模式下青/黄对比度低于 3:1，已用“端点标签 + 数据表”作为补偿（relief rule）。

---

## 8. 已知限制 / 后续可做

1. **股息率历史是推算值**，不是官方口径；若找到官方历史序列（Wind/Choice/韭圈儿），替换 `fetch_dividend_yield()` 即可。
2. 同业指数的分位是**全历史**口径，若要统一成 10 年，改 `analyze.py` 中 `peers` 部分。
3. 中证官网估值接口只有最近 20 个交易日，无法用于历史分位。
4. ROE 为 `PB/PE` 近似值，使用 TTM 盈利与最新净资产，未做平均净资产调整。
5. 看板数据为月末快照，不适合盘中择时；估值是赔率，不是 timing。
6. 在线版是**静态快照**，不会自动更新；每次更新数据后需要重新构建并 `git push`（见 10.2）。
7. 离线模式显示的是**最后一次成功缓存的页面**，不是实时行情；数据日期以页头为准。
8. iOS 不提供 Chrome 式安装按钮，只能通过 Safari 分享菜单“添加到主屏幕”。
9. 可加 Windows 任务计划程序，每月最后一个交易日自动运行：

```bat
cd /d D:\Claudeee\沪深300估值
set REFRESH=1 && python analyze.py && python build_dashboard.py
git add -A && git commit -m "auto: monthly update" && git push
```

---

## 9. 快速验证清单

更新后建议检查：

- [ ] 页头日期是否为新月份
- [ ] 收盘点位是否与行情软件一致（±0.1%）
- [ ] PE/PB 是否与中证官网同口径方向一致（数值可不同）
- [ ] 三张图末端标注是否等于 `summary.json` 中的当前值
- [ ] 数据表行数是否为 121（近十年月末）
- [ ] 深色模式下四色曲线是否可辨
- [ ] 线上地址能打开、控制台无报错（`index.html` 已随构建更新）
- [ ] 手机宽度下无横向溢出、图表字可读、点按能出 tooltip
- [ ] 改动页面后 `sw.js` 的 `CACHE` 版本已递增并已推送

---

## 10. 在线部署（GitHub Pages + PWA）

> 本轮（2026-10-31）完成：建仓并推送 GitHub、开启 Pages、把看板改造成可安装的 PWA、针对手机重做图表字号与布局，并在 360 / 390 / 1280px 下逐项验证。

- 仓库：<https://github.com/edison19490901-netizen/hs300-valuation>（public；免费 Pages 要求公开仓库）
- 看板：<https://edison19490901-netizen.github.io/hs300-valuation/>
- Pages 来源：`main` 分支根目录，`https_enforced: true`；推送后自动构建，约 1 分钟
- `.nojekyll`：跳过 Jekyll，静态文件原样发布
- 仓库 Homepage 已指向上面地址

### 10.1 本轮改动清单

| 改动 | 说明 |
|---|---|
| GitHub 仓库 | `git init -b main` → `gh repo create hs300-valuation --public --source=. --remote=origin --push` |
| Pages | `gh api -X POST repos/<owner>/<repo>/pages`，`source.branch=main`、`source.path=/` |
| 在线入口 | `build_dashboard.py` 现在同时写 `index.html` 与 `沪深300估值看板.html`，两者内容相同 |
| PWA 清单 | `manifest.webmanifest`：`display: standalone`、`start_url/scope = ./`、256/192/512/maskable 图标 |
| 图标 | 以 `300.png`（256×256，透明底）为主图标；派生白底 maskable、Apple touch icon |
| 离线 | `sw.js`：导航“联网优先 + 断网回退”，静态资源“缓存优先” |
| 移动端图表 | 窄屏放大 SVG 字号/线宽、加高面板、端点标签防重叠、点按出 tooltip |
| 移动端表格 | 6 列数据表改为卡片内横向滚动，日期不换行 |
| 页面元信息 | 双 `theme-color`、`apple-mobile-web-app-*`、`viewport-fit=cover`、safe-area 内边距 |

### 10.2 更新数据并发布

Git Bash 下 `cd /d/Claudeee/沪深300估值`；cmd 下用 `cd /d D:\Claudeee\沪深300估值`（cmd 换盘必须带 `/d`）。

**方式 A：Git Bash**

```bash
cd /d/Claudeee/沪深300估值
REFRESH=1 python analyze.py
python build_dashboard.py        # 同时更新 index.html 与 沪深300估值看板.html
git status
git add -A && git commit -m "更新 2026-11 月末数据"
git push
```

**方式 B：cmd（在当前文件夹）**

在资源管理器地址栏输入 `cmd` 回车，即可在当前目录打开 cmd。

```bat
set "REFRESH=1"
python analyze.py
python build_dashboard.py
start "" "index.html"
git status
git add -A
git commit -m "更新 2026-11 月末数据"
git push
```

要点：

- cmd 里 **`set "REFRESH=1"` 必须单独一行**；`REFRESH=1 python analyze.py` 是 Bash 语法，cmd 不认。变量只在当前窗口有效，不想刷新时执行 `set "REFRESH="` 或直接关窗口。
- 预览用 `start "" "index.html"`；不要用 `explorer.exe`，它成功时也可能返回非 0，串联时会被误判失败。
- cmd 支持**整段粘贴**，会按行依次执行，不用一行行敲。
- 也可合并为一行，`&&` 保证前一步成功才继续：

```bat
set "REFRESH=1" && python analyze.py && python build_dashboard.py && start "" "index.html" && git add -A && git commit -m "更新 2026-11 月末数据" && git push
```

**方式 C：一键脚本 `更新并发布.bat`**

双击，或在 cmd 里执行 `更新并发布.bat`。脚本会：

1. 自动切到脚本所在目录；
2. `REFRESH=1` 抓数据 → 构建页面 → 打开本地预览；
3. 列出改动并 `git add -A`；
4. `git commit`（信息为 `update: monthly data`，可在脚本内修改）；
5. **push 前询问 `Publish to GitHub now? (Y/N)`**，输入 `Y` 才推送；
6. 任一步失败立即停止并提示，不会带错误继续发布。

> 脚本为纯 ASCII 输出，避免 cmd 代码页导致中文乱码。首次运行时的 `git add -A` 会把脚本自身一并提交。

推送后等 1–2 分钟刷新网页（GitHub Pages 本身有约 10 分钟 `Cache-Control`，CDN 通常更快）。

- 页面导航走“联网优先”，只要联网就会取到新版本，不依赖清缓存。
- 若改了 `index.html` 的引用资源（图标等），把 `sw.js` 顶部的 `CACHE` 版本号加一，旧缓存会在新 SW 激活时删除。
- 只在本地看：双击 `沪深300估值看板.html` 即可，`file://` 下不会注册 Service Worker，不影响使用。

### 10.3 手机上像 App 一样使用

- **页面内“安装”按钮**：头部有“安装”按钮。Chrome 触发 `beforeinstallprompt` 时直接调起原生安装框；否则弹出分平台指引（Android / iOS / 微信 / 桌面）。
- **Android Chrome**：打开网址 → 菜单 → “安装应用 / 添加到主屏幕”。之后以独立窗口打开，断网也能看最近一次缓存。
  - 若点“安装应用”没反应或失败，通常是国内网络连不上 Google 生成 WebAPK 的服务器，属已知限制；改用“添加到主屏幕”创建快捷方式，或换 Edge / 手机自带浏览器“添加到桌面”。
- **iPhone Safari**：打开网址 → 分享 → “添加到主屏幕”。图标为 `300.png`，启动后隐藏浏览器地址栏。
- iOS 不会触发浏览器安装事件，页面按钮会显示 Safari 分享菜单的图文指引，这不是故障。
- **微信/QQ 内置浏览器**不支持安装，需先“···”→“在浏览器打开”。
- 已添加到主屏的页面在联网打开时会自动拿到新数据；断网时显示最后一次成功缓存的版本。

### 10.4 PWA 实现细节

**清单 `manifest.webmanifest`**

- `name: 沪深300估值`、`short_name: 沪深300`、`display: standalone`
- `start_url` / `scope` / `id` 都是 `./`，仓库改名或换路径无需改代码
- 图标：`300.png`（256, any）、`300-192.png`、`300-512.png`、`300-maskable.png`（512, maskable）
- `theme_color: #fcfcfb`、`background_color: #f9f9f7`

**Service Worker `sw.js`**

- `install`：`cache.addAll(SHELL)` 预缓存页面、清单、全部图标，然后 `skipWaiting`
- `activate`：删除除当前 `CACHE` 外的旧缓存，`clients.claim()`
- 导航请求：先 `fetch`，成功则回写 `./index.html`；失败回退缓存
- 其它同源 GET：缓存优先，未命中再请求并回填（只缓存 200 的同源响应）
- 注册条件：`https:` 或 `localhost`；`file://` 不注册

**图标生成**（换图时执行，保持文件名不变）

```python
from PIL import Image
src = Image.open("300.png").convert("RGBA")
for s in (192, 512):
    src.resize((s, s), Image.LANCZOS).save(f"300-{s}.png", optimize=True)
# maskable / apple-touch-icon：白底画布 + 居中图标（70% / 88%），避免 iOS 透明底变黑
```

### 10.5 移动端图表适配（`build_dashboard.py:341` `drawFigure`）

- `K = min(2.3, max(1, 760 / 容器宽度))`：按容器宽度放大 SVG 内字号（轴刻度 11×K、端点标签 12×K、面板名 10.5×K），使手机上实际字号约 10–11px。
- 左右边距、底部边距、面板间距随 `K` 增加，给放大后的刻度与端点标签留空间。
- 面板高度额外乘 `HS = 1 + 0.45 × (K-1)`，避免 6 个 Y 轴刻度挤在一起；桌面端 `K=1`，保持原样。
- 线宽 `2×min(K,1.5)`、端点圆点半径随 `K` 增大，小屏不至于细到看不见。
- 端点标签按 y 排序，间距不足 `1.08×字号` 时依次推开，并用 1px 半透明引线连回数据点（ERP 图 2.39% 与 1.65% 就会出现）。
- `pointerdown` 也能触发 tooltip，手机点按即可读数；十字线、左右键逻辑不变。
- CSS 断点：`≤820px` 指标卡 2 列；`≤600px` 收紧页边距/卡片内边距、数据表 `min-width:520px` + `nowrap`，表格在卡片内横向滚动。

### 10.6 本轮验证记录

| 项目 | 结果 |
|---|---|
| 线上首页 / 清单 / SW / 图标 | HTTP 200；`manifest` 为 `application/manifest+json`，`sw.js` 为 `application/javascript` |
| Chrome 安装条件 | `Page.getInstallabilityErrors` 仅报 `in-incognito`（Playwright 无痕上下文），`manifest.errors = []` |
| Service Worker | `hs300-valuation-v2` 已激活并控制页面 |
| 断网 | 断网后重载仍显示 3 张图、4 个指标卡 |
| 手机布局 | 390 / 360px 下 `scrollWidth == innerWidth`，无横向溢出；图表轴字号约 10.2px |
| 交互 | 点按图表出 tooltip；主题切换；数据表 121 行 |
| 控制台 | 无报错 |
| 桌面 | 1280px 下版式与改造前一致 |

### 10.7 线上问题排查

| 现象 | 处理 |
|---|---|
| Pages 打开 404 | 确认仓库 Settings → Pages 为 `main` / `(root)`；确认 `.nojekyll` 已推送；看 Actions/Pages 构建状态 |
| 推送后网页没变 | 等 1–2 分钟；强制刷新；GitHub Pages 有约 10 分钟缓存 |
| 手机主屏仍是旧版 | 联网重开一次（导航联网优先）；仍不行则递增 `sw.js` 的 `CACHE` 版本并推送，必要时在浏览器里注销 Service Worker |
| Chrome 没有“安装应用” | 必须是 https、清单可访问、含 192/512 图标、SW 已激活；公司网络/隐私模式可能屏蔽 |
| iOS 图标变黑底 | iOS 不支持透明图标，已改用白底 `apple-touch-icon.png` |
| 手机上图表字太小/刻度重叠 | 检查 `drawFigure` 的 `K` / `HS` 计算是否拿到正确容器宽度；必要时下调 `K` 上限 |
| 清单或 SW 404 | 确认文件在仓库根目录且文件名大小写一致（Pages 区分大小写） |

---

*本交接文档与代码、报告一同放在项目根目录。所有数据来自公开接口，仅供研究，不构成投资建议。*
