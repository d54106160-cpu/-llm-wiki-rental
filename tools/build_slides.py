#!/usr/bin/env python3
"""由 slides/src/*.json 產生教學 HTML 簡報（溫暖親切風）
用法：python3 tools/build_slides.py
"""
import json, re, html, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT, WIKI = ROOT/"slides/src", ROOT/"slides", ROOT/"wiki"

def wiki_titles():
    t = {}
    for p in WIKI.rglob("*.md"):
        m = re.search(r"^title:\s*(.+)$", p.read_text(encoding="utf-8"), re.M)
        if m: t[p.stem] = m.group(1).strip()
    return t
TITLES = wiki_titles()

def md(s):  # **粗體** → <strong>
    s = html.escape(s)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

CSS = """
:root{--bg:#FBF6EE;--card:#FFFFFF;--accent:#E8833A;--accent-soft:#FCE6D4;--text:#3B2F2A;--muted:#7A6A60;--line:#EADFD2;--green:#3E7C59;--green-soft:#E3F1E8;--yellow-soft:#FFF4D6}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:#EFE6D8;color:var(--text);font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif}
.viewport{position:fixed;inset:0 0 64px 0;display:flex;align-items:center;justify-content:center;overflow:hidden}
.stage{width:1280px;height:720px;position:relative;transform-origin:center center;flex:none}
.slide{position:absolute;inset:0;background:var(--bg);border-radius:28px;box-shadow:0 12px 40px rgba(59,47,42,.18);padding:48px 64px 84px;display:none;flex-direction:column;overflow:hidden}
.slide.active{display:flex}
.slide .body{flex:1;min-height:0;overflow:hidden;display:flex;flex-direction:column;gap:18px}
.kicker{font-size:18px;color:var(--accent);font-weight:700;letter-spacing:.05em}
h1{font-size:46px;line-height:1.25;font-weight:800}
h2{font-size:38px;line-height:1.3;font-weight:800;margin-bottom:6px}
h2 .emo{margin-right:12px}
.plain{background:var(--accent-soft);border-radius:18px;padding:14px 22px;font-size:22px;line-height:1.55}
.plain b{color:var(--accent);margin-right:8px}
ul.points,ol.points{font-size:23px;line-height:1.55;padding-left:30px;display:flex;flex-direction:column;gap:6px}
ul.points li::marker{color:var(--accent)}
ol.points li::marker{color:var(--accent);font-weight:800}
strong{color:#B4561A}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.col{background:var(--card);border:2px solid var(--line);border-radius:20px;padding:16px 22px}
.col h3{font-size:21px;color:var(--accent);margin-bottom:8px}
.col ul{font-size:20px;line-height:1.5;padding-left:24px}
table{border-collapse:separate;border-spacing:0;width:100%;font-size:21px;background:var(--card);border-radius:18px;overflow:hidden;border:2px solid var(--line)}
th,td{padding:12px 18px;text-align:left;border-bottom:1px solid var(--line);line-height:1.45}
th{background:var(--accent);color:#fff;font-weight:700}
tr:last-child td{border-bottom:none}
td:first-child{font-weight:700;color:var(--muted);width:150px}
.quote{background:var(--card);border-left:8px solid var(--accent);border-radius:14px;padding:14px 22px;font-size:20px;line-height:1.6}
.quote .label{font-size:15px;font-weight:700;color:var(--accent);display:block;margin-bottom:2px}
.quote .ref{color:var(--muted);font-size:16px;margin-left:6px}
.calc{background:var(--green-soft);border-radius:14px;padding:12px 20px;font-size:20px;line-height:1.5}
.calc .label{font-weight:800;color:var(--green);margin-right:8px}
.todo{background:var(--yellow-soft);border:2px dashed #E3B341;border-radius:14px;padding:10px 18px;font-size:18px}
.scenario{background:var(--card);border:3px solid var(--accent);border-radius:24px;padding:20px 28px;display:flex;flex-direction:column;gap:12px}
.scenario .story{font-size:22px;background:var(--accent-soft);border-radius:14px;padding:12px 18px}
.scenario .story b{color:var(--accent);margin-right:10px}
.tag-scn{display:inline-block;background:var(--accent);color:#fff;border-radius:999px;padding:4px 14px;font-size:16px;font-weight:700;margin-bottom:6px}
.cover{justify-content:center}
.cover .body{justify-content:center;gap:26px}
.cover .big{font-size:84px}
.goals{background:var(--card);border-radius:22px;padding:20px 30px;border:2px solid var(--line)}
.goals h3{font-size:20px;color:var(--accent);margin-bottom:8px}
.goals ul{font-size:23px;line-height:1.6;padding-left:28px}
.recap ol{font-size:26px;line-height:1.6;padding-left:34px}
.points.compact{font-size:20px;gap:2px}.recap.compact{padding:12px 26px}.recap.compact ol{font-size:20px;line-height:1.5}.recap.compact h3{margin-bottom:2px}
footer.src{position:absolute;left:64px;right:180px;bottom:26px;display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:14px;color:var(--muted)}
footer.src .pill{background:#fff;border:1.5px solid var(--line);border-radius:999px;padding:3px 12px;color:var(--text)}
.pageno{position:absolute;right:64px;bottom:26px;font-size:16px;color:var(--muted);font-weight:700}
.nav{position:fixed;bottom:14px;left:50%;transform:translateX(-50%);display:flex;gap:10px;align-items:center;z-index:5}
.nav button,.nav a{background:var(--text);color:#fff;border:none;border-radius:999px;padding:8px 18px;font-size:15px;cursor:pointer;text-decoration:none;font-family:inherit}
.nav button:disabled{opacity:.35;cursor:default}
.progress{position:fixed;top:0;left:0;height:5px;background:var(--accent);transition:width .25s;z-index:5}
.disclaimer{font-size:15px;color:var(--muted)}
"""

JS = """
const slides=[...document.querySelectorAll('.slide')];let i=0;
const prev=document.getElementById('prev'),next=document.getElementById('next'),bar=document.querySelector('.progress');
function show(n){i=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,k)=>s.classList.toggle('active',k===i));
 prev.disabled=i===0;next.disabled=i===slides.length-1;bar.style.width=((i+1)/slides.length*100)+'%';history.replaceState(null,'','#'+(i+1));}
function fit(){const s=Math.min((innerWidth-24)/1280,(innerHeight-88)/720);document.querySelector('.stage').style.transform='scale('+s+')';}
prev.onclick=()=>show(i-1);next.onclick=()=>show(i+1);
addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();show(i+1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();show(i-1)}});
addEventListener('resize',fit);fit();show((parseInt(location.hash.slice(1))||1)-1);
"""

def pills(cites, refs=()):
    out = ['<span>📚 出處：</span>']
    for c in cites:
        out.append(f'<span class="pill">{html.escape(TITLES.get(c, c))}</span>')
    return "<footer class='src'>" + "".join(out) + "</footer>"

def quote_html(q):
    return (f"<div class='quote'><span class='label'>📜 原文</span>「{html.escape(q['text'])}」"
            f"<span class='ref'>（{html.escape(q['ref'])}）</span></div>")

def render_slide(s, ch, n, total):
    t = s.get("type", "content")
    parts = []
    if t == "cover":
        parts.append(f"<div class='kicker'>第 {ch['no']} 章</div><div class='big'>{ch['emoji']}</div><h1>{md(s['title'])}</h1>")
        parts.append("<div class='goals'><h3>🎯 這一章你會學到</h3><ul>" + "".join(f"<li>{md(g)}</li>" for g in s["goals"]) + "</ul></div>")
    elif t == "recap":
        parts.append(f"<h2><span class='emo'>📝</span>{md(s['title'])}</h2>")
        if s.get("points_before"):
            parts.append("<ul class='points compact'>" + "".join(f"<li>{md(p)}</li>" for p in s["points_before"]) + "</ul>")
            if s.get("quote"): parts.append(quote_html(s["quote"]))
        parts.append(f"<div class='goals recap{' compact' if s.get('points_before') else ''}'><h3>本章重點</h3><ol>" + "".join(f"<li>{md(p)}</li>" for p in s["points"]) + "</ol></div>")
        parts.append("<div class='disclaimer'>＊本簡報僅供學習，實際以主管機關最新公告為準。</div>")
    elif t == "scenario":
        parts.append(f"<div><span class='tag-scn'>🗂 情境卡</span><h2>{md(s['title'])}</h2></div>")
        sc = [f"<div class='story'><b>情境</b>{md(s['story'])}</div>"]
        if s.get("steps"):
            sc.append("<ol class='points'>" + "".join(f"<li>{md(x)}</li>" for x in s["steps"]) + "</ol>")
        parts.append("<div class='scenario'>" + "".join(sc) + "</div>")
        parts.append("<div class='disclaimer'>＊實際以主管機關最新公告為準。</div>")
    else:
        parts.append(f"<h2>{('<span class=emo>'+s['emoji']+'</span>') if s.get('emoji') else ''}{md(s['title'])}</h2>")
        if s.get("plain"): parts.append(f"<div class='plain'><b>白話</b>{md(s['plain'])}</div>")
        if s.get("points"): parts.append("<ul class='points'>" + "".join(f"<li>{md(p)}</li>" for p in s["points"]) + "</ul>")
        if s.get("columns"):
            parts.append("<div class='cols'>" + "".join(
                f"<div class='col'><h3>{md(c['head'])}</h3><ul>" + "".join(f"<li>{md(p)}</li>" for p in c["points"]) + "</ul></div>"
                for c in s["columns"]) + "</div>")
        if s.get("table"):
            tb = s["table"]
            parts.append("<table><tr>" + "".join(f"<th>{md(h)}</th>" for h in tb["head"]) + "</tr>" +
                         "".join("<tr>" + "".join(f"<td>{md(c)}</td>" for c in r) + "</tr>" for r in tb["rows"]) + "</table>")
        if s.get("points_after"): parts.append("<ul class='points'>" + "".join(f"<li>{md(p)}</li>" for p in s["points_after"]) + "</ul>")
    if s.get("quote") and not (t == "recap" and s.get("points_before")): parts.append(quote_html(s["quote"]))
    if s.get("calc"): parts.append(f"<div class='calc'><span class='label'>🧮 試算示例</span>{md(s['calc'])}</div>")
    if s.get("todo"): parts.append(f"<div class='todo'>🚧 尚待補充：{md(s['todo'])}</div>")
    cls = "slide" + (" cover" if t == "cover" else "")
    return (f"<section class='{cls}' data-n='{n}'><div class='body'>{''.join(parts)}</div>"
            f"{pills(s['cites'])}<div class='pageno'>{n} / {total}</div></section>")

def page(title, inner, nav_extra=""):
    return f"""<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>
<style>{CSS}</style></head><body><div class="progress"></div>
<div class="viewport"><div class="stage">{inner}</div></div>
<div class="nav"><a href="index.html">🏠 目錄</a><button id="prev">← 上一頁</button><button id="next">下一頁 →</button>{nav_extra}</div>
<script>{JS}</script></body></html>"""

INDEX_CSS = """
body{background:#FBF6EE;color:#3B2F2A;font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif;margin:0}
.wrap{max-width:1080px;margin:0 auto;padding:56px 28px 64px}
.hero{background:#fff;border-radius:28px;padding:40px 44px;box-shadow:0 8px 30px rgba(59,47,42,.10);margin-bottom:32px}
.hero .k{color:#E8833A;font-weight:700;letter-spacing:.05em}
.hero h1{font-size:40px;margin:8px 0 12px}
.hero p{font-size:18px;line-height:1.7;color:#5B4B42;margin:0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:22px}
.card{display:flex;flex-direction:column;gap:10px;background:#fff;border:2px solid #EADFD2;border-radius:24px;padding:24px 26px;text-decoration:none;color:inherit;transition:transform .15s,border-color .15s}
a.card:hover{transform:translateY(-4px);border-color:#E8833A}
.card .emo{font-size:42px}
.card .no{color:#E8833A;font-weight:700;font-size:15px}
.card h2{font-size:24px;margin:0}
.card .meta{font-size:14px;color:#7A6A60;line-height:1.6}
.card .tags{display:flex;flex-wrap:wrap;gap:6px}
.card .tags span{background:#FCE6D4;border-radius:999px;padding:2px 10px;font-size:13px}
.card.pending{opacity:.6;border-style:dashed}
.status{display:inline-block;font-size:13px;font-weight:700;border-radius:999px;padding:3px 12px;background:#3E7C59;color:#fff;align-self:flex-start}
.pending .status{background:#C9A227}
.foot{margin-top:36px;font-size:14px;color:#7A6A60;line-height:1.8}
"""

def build():
    chapters = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(SRC.glob("*.json"))]
    today = datetime.date.today().isoformat()
    cards = []
    for ch in chapters:
        if ch.get("status") == "pending":
            cards.append(f"<div class='card pending'><div class='emo'>{ch['emoji']}</div><div class='no'>第 {ch['no']} 章</div>"
                         f"<h2>{html.escape(ch['title'])}</h2><span class='status'>⏳ 資料累積中</span>"
                         f"<div class='meta'>{html.escape(ch.get('pending_note',''))}</div></div>")
            continue
        n = len(ch["slides"])
        inner = "".join(render_slide(s, ch, k+1, n) for k, s in enumerate(ch["slides"]))
        (OUT/f"{ch['id']}.html").write_text(page(f"第 {ch['no']} 章｜{ch['title']}", inner), encoding="utf-8")
        srcs = sorted({src for pg in ch["pages"] for src in re.findall(r"[\w-]+", re.search(r"^sources:\s*(.+)$", (next(WIKI.rglob(pg+'.md'))).read_text(encoding='utf-8'), re.M).group(1))})
        cards.append(f"<a class='card' href='{ch['id']}.html'><div class='emo'>{ch['emoji']}</div><div class='no'>第 {ch['no']} 章 · {n} 頁</div>"
                     f"<h2>{html.escape(ch['title'])}</h2><span class='status'>✅ 可閱讀</span>"
                     ""
                     f"<div class='tags'>" + "".join(f"<span>{html.escape(TITLES.get(s,s))}</span>" for s in srcs) + "</div></a>")
    idx = f"""<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>第一次在外租屋就上手｜教學簡報</title><style>{INDEX_CSS}</style></head><body><div class="wrap">
<div class="hero"><div class="k">🏠 台灣租屋入門 · 給第一次在外租屋的大學生</div><h1>第一次在外租屋就上手</h1>
<p>從簽約、押金與租金、住的期間、提前解約、租期結束，到租金補貼，一章一個主題。每一頁都標示資料出處，內容全部來自本專案的 LLM Wiki，Wiki 則整理自政府公開的法規與契約規範。</p></div>
<div class="grid">{''.join(cards)}</div>
<div class="foot">簡報更新：{today}　｜　資料來源：租賃住宅市場發展及管理條例（修正 2023-02-08）、住宅租賃定型化契約應記載及不得記載事項（修正 2025-04-18）、住宅租賃契約書範本（修正 2024-07-08）、民法債編租賃（查詢 2026-11-11）、三百億元中央擴大租金補貼專案計畫作業規定（115.10.6 修正）及 116 年度附表、115 年度租金補貼申請書<br>
＊本簡報僅供學習，不構成法律意見；實際以主管機關最新公告為準。</div></div></body></html>"""
    (OUT/"index.html").write_text(idx, encoding="utf-8")
    print("built:", ", ".join(ch["id"] for ch in chapters))

if __name__ == "__main__":
    build()
