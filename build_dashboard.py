# -*- coding: utf-8 -*-
"""由 summary.json 与 valuation_history.csv 生成单文件 HTML 估值看板。"""
import json
import os

import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

with open(os.path.join(BASE, "summary.json"), encoding="utf-8") as f:
    S = json.load(f)

hist = pd.read_csv(os.path.join(DATA, "csi300_valuation_history.csv"))
hist["日期"] = pd.to_datetime(hist["日期"])
hist = hist.sort_values("日期").tail(121)  # 近十年月末

rows = []
for _, r in hist.iterrows():
    rows.append({
        "d": r["日期"].strftime("%Y-%m"),
        "close": round(float(r["指数"]), 2),
        "pe": round(float(r["滚动市盈率"]), 2),
        "pe_pct": round(float(r["pe_pct_10y"]), 1),
        "ep": round(float(r["earnings_yield"]), 2),
        "erp": round(float(r["erp"]), 2),
        "y10": round(float(r["y10"]), 2),
        "dy": round(float(r["dy"]), 2),
        "eps": round(float(r["eps_ttm"]), 1),
        "roe": round(float(r["roe"]), 2),
        "pb": round(float(r["市净率"]), 2),
    })

stats = {
    "date": S["as_of"],
    "close": S["index_close"],
    "pe": S["indices"]["pe_ttm"]["current"],
    "pe_pct": S["indices"]["pe_ttm"]["pct_10y"],
    "pb": S["indices"]["pb"]["current"],
    "pb_pct": S["indices"]["pb"]["pct_10y"],
    "erp": round(S["indices"]["erp"]["current"], 2),
    "erp_pct": S["indices"]["erp"]["pct_10y"],
    "dy_official": S.get("csindex", {}).get(
        "dy1", round(S["indices"]["dividend_yield_derived"]["current"], 2)),
    "dy_derived": round(S["indices"]["dividend_yield_derived"]["current"], 2),
    "y10": S["bond"]["y10"],
    "y10_pct": S["bond"]["y10_pct_all"],
    "eps_yoy": S["earnings"]["eps_yoy_pct"],
    "drawdown": S["earnings"]["drawdown_from_peak_pct"],
    "roe": S["earnings"]["roe_current"],
    "roe_pct": S["earnings"]["roe_pct_10y"],
    "pe_band": [S["bands"]["pe_10y"]["p20"], S["bands"]["pe_10y"]["p80"]],
    "pe_median": S["bands"]["pe_10y"]["p50"],
    "erp_median": S["bands"].get("erp_10y", {}).get("p50", 5.58),
}

payload = {"rows": rows, "stats": stats}
data_json = json.dumps(payload, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>沪深300 估值看板</title>
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="300.png" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="theme-color" content="#fcfcfb" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0d0d0d" media="(prefers-color-scheme: dark)">
<meta name="application-name" content="沪深300估值">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="沪深300">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="mobile-web-app-capable" content="yes">
<meta name="description" content="沪深300 PE/PB、历史分位、ERP、股息率与盈利指标的月末估值看板。">
<style>
  :root{
    color-scheme: light;
    --surface-1:#fcfcfb; --page:#f9f9f7;
    --text-primary:#0b0b0b; --text-secondary:#52514e; --muted:#898781;
    --grid:#e1e0d9; --axis:#c3c2b7; --border:rgba(11,11,11,.10);
    --series-1:#2a78d6; --series-2:#eb6834; --series-3:#1baf7a; --series-4:#eda100;
    --wash:rgba(42,120,214,.07);
  }
  @media (prefers-color-scheme: dark){
    :root:where(:not([data-theme="light"])){
      color-scheme: dark;
      --surface-1:#1a1a19; --page:#0d0d0d;
      --text-primary:#f0efec; --text-secondary:#c3c2b7; --muted:#898781;
      --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,.10);
      --series-1:#3987e5; --series-2:#d95926; --series-3:#199e70; --series-4:#c98500;
      --wash:rgba(57,135,229,.10);
    }
  }
  :root[data-theme="dark"]{
    color-scheme: dark;
    --surface-1:#1a1a19; --page:#0d0d0d;
    --text-primary:#f0efec; --text-secondary:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,.10);
    --series-1:#3987e5; --series-2:#d95926; --series-3:#199e70; --series-4:#c98500;
    --wash:rgba(57,135,229,.10);
  }
  *{box-sizing:border-box}
  body{
    margin:0; background:var(--page); color:var(--text-primary);
    font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
    line-height:1.55; -webkit-font-smoothing:antialiased;
  }
  .wrap{
    max-width:1060px; margin:0 auto; padding:40px 24px 64px;
    padding-left:max(24px, env(safe-area-inset-left));
    padding-right:max(24px, env(safe-area-inset-right));
  }
  header{display:flex; align-items:flex-start; justify-content:space-between; gap:16px; margin-bottom:28px}
  h1{font-size:26px; line-height:1.25; margin:0 0 6px; font-weight:650; letter-spacing:.01em}
  .sub{color:var(--text-secondary); font-size:13.5px; margin:0}
  .theme-btn{
    border:1px solid var(--border); background:var(--surface-1); color:var(--text-secondary);
    border-radius:999px; padding:7px 13px; font:inherit; font-size:12.5px; cursor:pointer;
  }
  .theme-btn:hover{color:var(--text-primary)}
  .tiles{display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:14px}
  @media (max-width:820px){ .tiles{grid-template-columns:repeat(2,1fr)} }
  @media (max-width:600px){
    .wrap{
      padding:22px 14px 44px;
      padding-left:max(14px, env(safe-area-inset-left));
      padding-right:max(14px, env(safe-area-inset-right));
    }
    header{margin-bottom:18px; gap:10px}
    h1{font-size:21px}
    .sub{font-size:12.5px}
    .theme-btn{padding:6px 10px; font-size:12px; flex:none}
    .tile{padding:13px 13px 11px}
    .tile .value{font-size:23px}
    .card{padding:14px 12px 10px}
    .card h2{font-size:14px}
    .callout{padding:13px 14px; font-size:13px}
    .legend{gap:10px}
    th,td{padding:6px 7px; white-space:nowrap}
    .tablewrap table{min-width:520px}
  }
  .tile{
    background:var(--surface-1); border:1px solid var(--border); border-radius:12px;
    padding:16px 16px 14px; min-width:0;
  }
  .tile .label{font-size:12.5px; color:var(--muted); margin-bottom:6px; white-space:nowrap}
  .tile .value{font-size:27px; font-weight:650; line-height:1.15; letter-spacing:-.01em}
  .tile .note{font-size:12px; color:var(--text-secondary); margin-top:5px}
  .tile .note b{font-weight:600; color:var(--text-primary)}
  .callout{
    background:var(--surface-1); border:1px solid var(--border); border-radius:12px;
    padding:16px 18px; font-size:13.5px; color:var(--text-secondary); margin-bottom:22px;
  }
  .callout strong{color:var(--text-primary); font-weight:600}
  .card{
    background:var(--surface-1); border:1px solid var(--border); border-radius:12px;
    padding:18px 20px 12px; margin-bottom:16px;
  }
  .card h2{font-size:15px; margin:0 0 3px; font-weight:600}
  .card .desc{font-size:12.5px; color:var(--muted); margin:0 0 8px}
  .legend{display:flex; flex-wrap:wrap; gap:14px; margin:6px 0 4px; font-size:12px; color:var(--text-secondary)}
  .legend span{display:inline-flex; align-items:center; gap:6px}
  .legend i{width:14px; height:2px; border-radius:1px; display:inline-block; flex:none}
  .k1{background:var(--series-1)} .k2{background:var(--series-2)}
  .k3{background:var(--series-3)} .k4{background:var(--series-4)}
  .chart{position:relative; width:100%}
  .chart svg{display:block; width:100%; height:auto; overflow:visible}
  .tooltip{
    position:absolute; pointer-events:none; opacity:0; transition:opacity .1s;
    background:var(--surface-1); border:1px solid var(--border); border-radius:8px;
    box-shadow:0 6px 20px rgba(0,0,0,.12); padding:9px 11px; font-size:12px;
    min-width:140px; z-index:3;
  }
  .tooltip .td{color:var(--muted); margin-bottom:5px}
  .tooltip .tr{display:flex; align-items:baseline; justify-content:space-between; gap:14px; margin-top:3px}
  .tooltip .tk{display:flex; align-items:center; gap:6px; color:var(--text-secondary)}
  .tooltip .key{width:12px; height:2px; border-radius:1px; flex:none}
  .tooltip .tv{font-weight:650; color:var(--text-primary); font-variant-numeric:tabular-nums}
  details{margin-top:4px}
  summary{
    cursor:pointer; font-size:12.5px; color:var(--text-secondary);
    padding:8px 0 4px; user-select:none;
  }
  summary:hover{color:var(--text-primary)}
  .tablewrap{max-height:340px; overflow:auto; border-top:1px solid var(--grid); margin-top:6px}
  table{border-collapse:collapse; width:100%; font-size:12.5px}
  th,td{padding:7px 10px; text-align:right; border-bottom:1px solid var(--grid); font-variant-numeric:tabular-nums}
  th:first-child,td:first-child{text-align:left}
  th{position:sticky; top:0; background:var(--surface-1); color:var(--muted); font-weight:500}
  footer{color:var(--muted); font-size:11.5px; line-height:1.7; margin-top:26px}
  svg text{font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1>沪深300 估值看板</h1>
      <p class="sub">数据截至 <span id="asof"></span> · 月末口径 · 乐咕乐股 / 中证指数 / 中债</p>
    </div>
    <button class="theme-btn" id="themeBtn" type="button">切换主题</button>
  </header>

  <section class="tiles" aria-label="核心估值指标">
    <div class="tile">
      <div class="label">收盘点位</div>
      <div class="value" id="v-close"></div>
      <div class="note">距 2007 年历史高点 <b id="v-dd"></b></div>
    </div>
    <div class="tile">
      <div class="label">PE-TTM（整体法）</div>
      <div class="value" id="v-pe"></div>
      <div class="note">近十年分位 <b id="v-pe-pct"></b> · EPS 同比 <b id="v-eps"></b></div>
    </div>
    <div class="tile">
      <div class="label">PB（整体法）</div>
      <div class="value" id="v-pb"></div>
      <div class="note">近十年分位 <b id="v-pb-pct"></b> · ROE <b id="v-roe"></b></div>
    </div>
    <div class="tile">
      <div class="label">股权风险溢价 ERP</div>
      <div class="value" id="v-erp"></div>
      <div class="note">近十年分位 <b id="v-erp-pct"></b> · 10Y 国债 <b id="v-y10"></b></div>
    </div>
  </section>

  <div class="callout" id="callout"></div>

  <section class="card">
    <h2>指数点位、PE-TTM 与历史分位</h2>
    <p class="desc" id="desc-pe"></p>
    <div class="chart" id="chart-pe">
      <svg id="svg-pe" role="img" aria-label="沪深300 点位、PE-TTM 与近十年滚动分位"></svg>
      <div class="tooltip" id="tip-pe"></div>
    </div>
    <details>
      <summary>查看数据表</summary>
      <div class="tablewrap"><table id="tbl-pe">
        <thead><tr><th>月份</th><th>点位</th><th>PE-TTM</th><th>近十年分位</th><th>10Y 国债</th><th>ERP</th></tr></thead>
        <tbody></tbody>
      </table></div>
    </details>
  </section>

  <section class="card">
    <h2>盈利收益率、ERP、股息率与 10 年国债</h2>
    <p class="desc">四项均为百分比，可同轴比较。ERP = 盈利收益率 − 10 年国债；ERP 越高，股票相对债券越便宜。</p>
    <div class="legend" aria-label="图例">
      <span><i class="k1"></i>股权风险溢价 ERP</span>
      <span><i class="k2"></i>盈利收益率 E/P</span>
      <span><i class="k3"></i>股息率（全收益指数推算）</span>
      <span><i class="k4"></i>10 年期国债</span>
    </div>
    <div class="chart" id="chart-erp">
      <svg id="svg-erp" role="img" aria-label="沪深300 股权风险溢价、盈利收益率、股息率与十年国债"></svg>
      <div class="tooltip" id="tip-erp"></div>
    </div>
    <details>
      <summary>查看数据表</summary>
      <div class="tablewrap"><table id="tbl-erp">
        <thead><tr><th>月份</th><th>ERP</th><th>E/P</th><th>股息率*</th><th>10Y 国债</th></tr></thead>
        <tbody></tbody>
      </table></div>
    </details>
  </section>

  <section class="card">
    <h2>EPS、ROE、PE 与 PB</h2>
    <p class="desc" id="desc-eps"></p>
    <div class="chart" id="chart-eps">
      <svg id="svg-eps" role="img" aria-label="沪深300 EPS、ROE、PE 与 PB 近十年走势"></svg>
      <div class="tooltip" id="tip-eps"></div>
    </div>
    <details>
      <summary>查看数据表</summary>
      <div class="tablewrap"><table id="tbl-eps">
        <thead><tr><th>月份</th><th>EPS（元）</th><th>ROE</th><th>PE-TTM</th><th>PB</th></tr></thead>
        <tbody></tbody>
      </table></div>
    </details>
  </section>

  <footer>
    口径：PE/PB 为整体法（总市值 / 总盈利、总净资产），来自乐咕乐股月末数据；ERP = 1/PE-TTM − 10 年期中国国债收益率；
    EPS = 指数点位 ÷ PE-TTM；ROE = PB ÷ PE。分位为每个时点在过去 120 个月样本中的位置。
    股息率*为沪深300全收益指数（H00300）与价格指数（000300）之比推算的近 12 个月已实施分红回报，与中证官网口径（<span id="dy-off"></span>）存在差异，仅用于观察趋势。
    中证指数官网口径与乐咕存在差异（成分权重、盈利口径不同），请勿混用。本页面仅用于估值研究，不构成投资建议。
  </footer>
</div>

<script>
const DATA = __DATA__;
const S = DATA.stats, ROWS = DATA.rows;

document.getElementById('asof').textContent = S.date;
document.getElementById('dy-off').textContent = '最新 ' + S.dy_official.toFixed(2) + '%';
document.getElementById('v-close').textContent = S.close.toLocaleString('zh-CN', {minimumFractionDigits:2, maximumFractionDigits:2});
document.getElementById('v-dd').textContent = S.drawdown.toFixed(1) + '%';
document.getElementById('v-pe').textContent = S.pe.toFixed(2);
document.getElementById('v-pe-pct').textContent = S.pe_pct.toFixed(1) + '%';
document.getElementById('v-eps').textContent = S.eps_yoy.toFixed(1) + '%';
document.getElementById('v-pb').textContent = S.pb.toFixed(2);
document.getElementById('v-pb-pct').textContent = S.pb_pct.toFixed(1) + '%';
document.getElementById('v-roe').textContent = S.roe.toFixed(1) + '%';
document.getElementById('v-erp').textContent = S.erp.toFixed(2) + '%';
document.getElementById('v-erp-pct').textContent = S.erp_pct.toFixed(1) + '%';
document.getElementById('v-y10').textContent = S.y10.toFixed(2) + '%';

document.getElementById('desc-pe').textContent =
  `上：沪深300 点位；中：PE-TTM；下：该时点 PE 在过去 120 个月中的分位。阴影为当前近十年 20–80 分位区间（${S.pe_band[0].toFixed(2)}–${S.pe_band[1].toFixed(2)}），细线为中位数 ${S.pe_median.toFixed(2)}；分位图中的水平细线为 20%/80% 参考线。`;
document.getElementById('desc-eps').textContent =
  `EPS = 指数点位 ÷ PE-TTM；ROE = PB ÷ PE。四个指标量纲不同，分面板共用横轴。当前 ROE ${S.roe.toFixed(1)}%（近十年 ${S.roe_pct.toFixed(0)}% 分位）、PE ${S.pe.toFixed(2)}、PB ${S.pb.toFixed(2)}——PB 偏低主要是盈利能力下滑的结果。`;

const callout = document.getElementById('callout');
callout.append(
  textEl('strong', '一句话读数：', ''),
  document.createTextNode(
    `PE-TTM ${S.pe.toFixed(2)} 处于近十年 ${S.pe_pct.toFixed(0)}% 分位——不算便宜；PB ${S.pb.toFixed(2)} 处于 ${S.pb_pct.toFixed(0)}% 分位，偏低，` +
    `但 ROE 仅 ${S.roe.toFixed(1)}%（近十年 ${S.roe_pct.toFixed(0)}% 分位），低 PB 是盈利能力下滑的结果。` +
    `ERP ${S.erp.toFixed(2)}% 位于 ${S.erp_pct.toFixed(0)}% 分位，主要由 10 年国债跌至 ${S.y10.toFixed(2)}%（历史极低）贡献；` +
    `盈利收益率本身只处于历史中位。盈利端 EPS 同比 ${S.eps_yoy.toFixed(1)}%，估值便宜与否取决于盈利能否企稳。`
  )
);

function textEl(tag, text, cls){
  const el = document.createElement(tag);
  if (cls) el.className = cls;
  el.textContent = text;
  return el;
}

const SVG_NS = 'http://www.w3.org/2000/svg';
function s(tag, attrs){
  const el = document.createElementNS(SVG_NS, tag);
  for (const k in attrs) el.setAttribute(k, attrs[k]);
  return el;
}

function drawFigure(cfg){
  const svg = document.getElementById(cfg.svgId);
  const tip = document.getElementById(cfg.tipId);
  // 窄屏时放大文字/线宽，保证 SVG 缩放后仍有约 11px 的实际字号
  const cw = svg.parentElement.clientWidth || 760;
  const K = Math.min(2.3, Math.max(1, 760 / cw));
  const LW = 2 * Math.min(K, 1.5);
  const R = 4 * (1 + 0.45 * (K - 1));
  const W = 760, MT = 16;
  const ML = 48 + 30 * (K - 1), MR = 98 + 22 * (K - 1);
  const MB = 30 + 8 * (K - 1), GAP = 26 + 4 * (K - 1);
  const panels = cfg.panels;
  // 窄屏同时加高面板，避免 y 轴刻度挤在一起
  const HS = 1 + 0.45 * (K - 1);
  panels.forEach(p => {
    if (p.h0 == null) p.h0 = p.h;
    p.h = p.h0 * HS;
  });
  const totalH = MT + MB + panels.reduce((a, p) => a + p.h, 0) + GAP * (panels.length - 1);
  svg.setAttribute('viewBox', `0 0 ${W} ${totalH}`);
  const rows = cfg.rows, n = rows.length;
  const iw = W - ML - MR;
  const x = i => ML + (n === 1 ? 0 : i / (n - 1)) * iw;

  let top = MT;
  panels.forEach(p => { p.top = top; top += p.h + GAP; });
  const plotBottom = panels[panels.length - 1].top + panels[panels.length - 1].h;
  const yFor = (p, v) => p.top + (p.domain[1] - v) / (p.domain[1] - p.domain[0]) * p.h;

  panels.forEach(p => {
    if (p.name){
      const t = s('text', {x:ML, y:p.top-6*K, 'font-size':10.5*K, fill:'var(--muted)'});
      t.textContent = p.name;
      svg.appendChild(t);
    }
    // 网格线 + y 轴刻度
    p.yticks.forEach(v => {
      svg.appendChild(s('line', {x1:ML, x2:ML+iw, y1:yFor(p,v), y2:yFor(p,v), stroke:'var(--grid)', 'stroke-width':1}));
      const t = s('text', {x:ML-9*K, y:yFor(p,v)+4*K, 'text-anchor':'end', 'font-size':11*K, fill:'var(--muted)'});
      t.textContent = v + (p.unit || '');
      svg.appendChild(t);
    });
    // 基线
    svg.appendChild(s('line', {x1:ML, x2:ML+iw, y1:p.top+p.h, y2:p.top+p.h, stroke:'var(--axis)', 'stroke-width':1}));

    // 分位区间阴影
    if (p.band){
      svg.appendChild(s('rect', {x:ML, y:yFor(p,p.band[1]), width:iw, height:yFor(p,p.band[0])-yFor(p,p.band[1]),
        fill:'var(--wash)'}));
    }
    // 参考线（分位图 20/80）
    (p.refs || []).forEach(v => {
      svg.appendChild(s('line', {x1:ML, x2:ML+iw, y1:yFor(p,v), y2:yFor(p,v),
        stroke:'var(--axis)', 'stroke-width':1, opacity:.55}));
    });
    // 中位线
    if (p.median != null){
      svg.appendChild(s('line', {x1:ML, x2:ML+iw, y1:yFor(p,p.median), y2:yFor(p,p.median),
        stroke:'var(--muted)', 'stroke-width':1, opacity:.55}));
    }

    // 数据线
    const endLabels = [];
    p.series.forEach(ser => {
      let d = '';
      rows.forEach((r, i) => {
        const v = r[ser.key];
        if (v == null || Number.isNaN(v)) return;
        d += (d ? 'L' : 'M') + x(i).toFixed(1) + ' ' + yFor(p, v).toFixed(1);
      });
      svg.appendChild(s('path', {d, fill:'none', stroke:ser.color, 'stroke-width':LW,
        'stroke-linejoin':'round', 'stroke-linecap':'round'}));

      const lv = rows[n-1][ser.key];
      svg.appendChild(s('circle', {cx:x(n-1), cy:yFor(p,lv), r:R, fill:ser.color,
        stroke:'var(--surface-1)', 'stroke-width':2}));
      endLabels.push({y: yFor(p, lv), ser, text: ser.fmt(lv)});
    });

    // 端点标签：重叠时按顺序推开，并用细引线连回数据点
    const fs = 12 * K, minGap = fs * 1.08;
    endLabels.sort((a, b) => a.y - b.y);
    endLabels.forEach((l, i) => {
      l.ly = l.y;
      if (i > 0 && l.ly - endLabels[i-1].ly < minGap) l.ly = endLabels[i-1].ly + minGap;
    });
    const minY = p.top + fs * .7, maxY = p.top + p.h - fs * .3;
    const over = endLabels[endLabels.length-1].ly - maxY;
    if (over > 0) endLabels.forEach(l => { l.ly -= over; });
    if (endLabels[0].ly < minY) endLabels.forEach(l => { l.ly += minY - endLabels[0].ly; });
    endLabels.forEach(l => {
      const lx = x(n-1) + 10*K;
      if (Math.abs(l.ly - l.y) > 0.5) {
        svg.appendChild(s('line', {x1:x(n-1)+R+1, y1:l.y, x2:lx-3, y2:l.ly,
          stroke:l.ser.color, 'stroke-width':1, opacity:.45}));
      }
      const lab = s('text', {x:lx, y:l.ly + 4*K, 'font-size':fs, 'font-weight':600,
        fill:'var(--text-primary)'});
      lab.textContent = l.text;
      svg.appendChild(lab);
    });
  });

  // x 轴刻度：每两年一个 + 末端年份
  const years = {};
  rows.forEach((r, i) => {
    const yr = r.d.slice(0,4);
    if (r.d.slice(5) === '12' || i === 0) years[yr] = i;
  });
  years[rows[n-1].d.slice(0,4)] = n-1;
  Object.keys(years).filter((_, k) => k % 2 === 0).forEach(yr => {
    const i = years[yr];
    svg.appendChild(s('line', {x1:x(i), x2:x(i), y1:plotBottom, y2:plotBottom+4*K, stroke:'var(--axis)', 'stroke-width':1}));
    const t = s('text', {x:x(i), y:plotBottom+8*K+6, 'text-anchor':'middle', 'font-size':11*K, fill:'var(--muted)'});
    t.textContent = yr;
    svg.appendChild(t);
  });

  // 交互层
  const overlay = s('rect', {x:ML, y:MT, width:iw, height:plotBottom-MT, fill:'transparent',
    tabindex:0, role:'application', 'aria-label':cfg.aria});
  const cross = s('line', {x1:0, x2:0, y1:MT, y2:plotBottom, stroke:'var(--axis)',
    'stroke-width':1, opacity:0});
  svg.appendChild(cross);
  const dots = [];
  panels.forEach(p => p.series.forEach(ser => {
    const dot = s('circle', {r:R, fill:ser.color, stroke:'var(--surface-1)',
      'stroke-width':2, opacity:0});
    dots.push({dot, p, ser});
    svg.appendChild(dot);
  }));
  svg.appendChild(overlay);

  let cur = -1;
  function show(i){
    cur = Math.max(0, Math.min(n-1, i));
    const r = rows[cur];
    cross.setAttribute('x1', x(cur)); cross.setAttribute('x2', x(cur));
    cross.setAttribute('opacity', 1);
    dots.forEach(o => {
      o.dot.setAttribute('cx', x(cur));
      o.dot.setAttribute('cy', yFor(o.p, r[o.ser.key]));
      o.dot.setAttribute('opacity', 1);
    });

    tip.textContent = '';
    tip.appendChild(textEl('div', r.d, 'td'));
    panels.forEach(p => p.series.forEach(ser => {
      const row = document.createElement('div'); row.className = 'tr';
      const k = document.createElement('span'); k.className = 'tk';
      const key = document.createElement('span'); key.className = 'key';
      key.style.background = ser.color;
      k.appendChild(key); k.appendChild(document.createTextNode(ser.label));
      const v = document.createElement('span'); v.className = 'tv';
      v.textContent = ser.fmt(r[ser.key]);
      row.appendChild(k); row.appendChild(v); tip.appendChild(row);
    }));

    const rect = svg.getBoundingClientRect();
    const px = x(cur) / W * rect.width;
    const py = yFor(panels[0], r[panels[0].series[0].key]) / totalH * rect.height;
    tip.style.opacity = 1;
    tip.style.left = Math.min(Math.max(px + 14, 8), Math.max(rect.width - 180, 8)) + 'px';
    tip.style.top = Math.max(py - 10, 4) + 'px';
  }
  function hide(){
    cross.setAttribute('opacity', 0);
    dots.forEach(o => o.dot.setAttribute('opacity', 0));
    tip.style.opacity = 0;
  }

  overlay.addEventListener('pointermove', e => {
    const rect = svg.getBoundingClientRect();
    const sx = (e.clientX - rect.left) / rect.width * W;
    show(Math.round((sx - ML) / iw * (n - 1)));
  });
  overlay.addEventListener('pointerdown', e => {
    const rect = svg.getBoundingClientRect();
    const sx = (e.clientX - rect.left) / rect.width * W;
    show(Math.round((sx - ML) / iw * (n - 1)));
  });
  overlay.addEventListener('pointerleave', hide);
  overlay.addEventListener('focus', () => show(cur < 0 ? n-1 : cur));
  overlay.addEventListener('blur', hide);
  overlay.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft'){ show(cur - 1); e.preventDefault(); }
    if (e.key === 'ArrowRight'){ show(cur + 1); e.preventDefault(); }
  });
}

function fmtPct(v){ return v.toFixed(2) + '%'; }
function fmtNum(v){ return v.toFixed(2); }
function fmtOne(v){ return v.toFixed(1) + '%'; }

// PE-TTM + 滚动分位
drawFigure({
  svgId:'svg-pe', tipId:'tip-pe', rows:ROWS, aria:'沪深300 PE-TTM 与近十年滚动分位',
  panels:[
    {h:116, domain:[2900,5500], yticks:[3000,3500,4000,4500,5000,5500], unit:'',
     name:'沪深300 点位',
     series:[{key:'close', color:'var(--series-1)', label:'收盘点位',
              fmt:v=>v.toLocaleString('zh-CN',{maximumFractionDigits:0})}]},
    {h:170, domain:[9,16.5], yticks:[10,12,14,16], unit:'', band:S.pe_band, median:S.pe_median,
     name:'PE-TTM（倍）',
     series:[{key:'pe', color:'var(--series-1)', label:'PE-TTM', fmt:fmtNum}]},
    {h:74, domain:[0,100], yticks:[0,50,100], unit:'%', refs:[20,80],
     name:'近十年滚动分位（%）',
     series:[{key:'pe_pct', color:'var(--series-1)', label:'近十年分位', fmt:fmtOne}]}
  ]
});

// ERP / E-P / 股息率 / 10Y
drawFigure({
  svgId:'svg-erp', tipId:'tip-erp', rows:ROWS, aria:'沪深300 股权风险溢价、盈利收益率、股息率与十年国债',
  panels:[
    {h:272, domain:[0,9.5], yticks:[0,2,4,6,8], unit:'%', median:S.erp_median,
     series:[
       {key:'erp', color:'var(--series-1)', label:'ERP', fmt:fmtPct},
       {key:'ep',  color:'var(--series-2)', label:'盈利收益率', fmt:fmtPct},
       {key:'dy',  color:'var(--series-3)', label:'股息率*', fmt:fmtPct},
       {key:'y10', color:'var(--series-4)', label:'10Y 国债', fmt:fmtPct}
     ]}
  ]
});

// EPS + ROE
drawFigure({
  svgId:'svg-eps', tipId:'tip-eps', rows:ROWS, aria:'沪深300 EPS、ROE、PE 与 PB 近十年走势',
  panels:[
    {h:128, domain:[250,410], yticks:[250,300,350,400], unit:'',
     name:'EPS（元）',
     series:[{key:'eps', color:'var(--series-1)', label:'EPS（元）', fmt:v=>v.toFixed(0)}]},
    {h:128, domain:[10,13.5], yticks:[10,11,12,13], unit:'%',
     name:'ROE（%，PB ÷ PE）',
     series:[{key:'roe', color:'var(--series-1)', label:'ROE', fmt:v=>v.toFixed(1)+'%'}]},
    {h:128, domain:[9,16.5], yticks:[10,12,14,16], unit:'',
     name:'PE-TTM（倍）',
     series:[{key:'pe', color:'var(--series-1)', label:'PE-TTM', fmt:fmtNum}]},
    {h:128, domain:[1.1,1.8], yticks:[1.2,1.4,1.6,1.8], unit:'',
     name:'PB（倍）',
     series:[{key:'pb', color:'var(--series-1)', label:'PB', fmt:fmtNum}]}
  ]
});

// 数据表
function fillTable(sel, cols){
  const tb = document.querySelector(sel + ' tbody');
  const frag = document.createDocumentFragment();
  ROWS.slice().reverse().forEach(r => {
    const tr = document.createElement('tr');
    cols.forEach(c => {
      const td = document.createElement('td');
      td.textContent = c.fmt(r[c.key]);
      tr.appendChild(td);
    });
    frag.appendChild(tr);
  });
  tb.appendChild(frag);
}
fillTable('#tbl-pe', [
  {key:'d', fmt:v=>v}, {key:'close', fmt:v=>v.toFixed(0)}, {key:'pe', fmt:fmtNum},
  {key:'pe_pct', fmt:fmtOne}, {key:'y10', fmt:fmtPct}, {key:'erp', fmt:fmtPct}
]);
fillTable('#tbl-erp', [
  {key:'d', fmt:v=>v}, {key:'erp', fmt:fmtPct}, {key:'ep', fmt:fmtPct},
  {key:'dy', fmt:fmtPct}, {key:'y10', fmt:fmtPct}
]);
fillTable('#tbl-eps', [
  {key:'d', fmt:v=>v}, {key:'eps', fmt:v=>v.toFixed(1)}, {key:'roe', fmt:fmtPct},
  {key:'pe', fmt:fmtNum}, {key:'pb', fmt:fmtNum}
]);

// 主题切换
const btn = document.getElementById('themeBtn');
btn.addEventListener('click', () => {
  const root = document.documentElement;
  const dark = root.dataset.theme === 'dark' ||
    (!root.dataset.theme && matchMedia('(prefers-color-scheme: dark)').matches);
  root.dataset.theme = dark ? 'light' : 'dark';
});

// PWA：仅 https 或 localhost 下注册；本地双击打开（file://）不会触发
const swHost = ['localhost', '127.0.0.1'].includes(location.hostname);
if ('serviceWorker' in navigator && (location.protocol === 'https:' || swHost)) {
  addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  });
}
</script>
</body>
</html>
"""

out = HTML.replace("__DATA__", data_json)
for name in ("沪深300估值看板.html", "index.html"):
    path = os.path.join(BASE, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    print("written:", path, len(out), "bytes")
