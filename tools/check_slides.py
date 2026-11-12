#!/usr/bin/env python3
"""B5 簡報程式檢查（內容部分）
1 每頁有出處  2 引用頁存在  3 引用頁屬於章節對應表  4 原文與 Wiki 完全一致且從句首開始
5 數字在引用頁找得到（🧮 試算示例除外）  6 每章 4–8 頁、合計 ≥ 15 頁
用法：python3 tools/check_slides.py [章節代號...]
"""
import json, re, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
WIKI = {p.stem: p.read_text(encoding="utf-8") for p in (ROOT/"wiki").rglob("*.md")}
CN = "零一二三四五六七八九"
def cn(n):
    if n < 10: return CN[n]
    if n < 20: return "十" + (CN[n%10] if n%10 else "")
    if n < 100: return CN[n//10] + "十" + (CN[n%10] if n%10 else "")
    return None
def num_found(n, text):
    if re.search(rf"(?<![\d,]){n}(?![\d,])", text.replace(" ", "")) or re.search(rf"(?<!\d){n}(?!\d)", text): return True
    c = cn(n); return bool(c and c in text)
def texts(s):
    out = [s.get("title",""), s.get("plain",""), s.get("story",""), s.get("todo","")]
    for k in ("points","points_before","points_after","goals","steps"): out += s.get(k, [])
    for c in s.get("columns", []): out += [c["head"]] + c["points"]
    if s.get("table"): out += s["table"]["head"] + [x for r in s["table"]["rows"] for x in r]
    return [re.sub(r"\*\*", "", t) for t in out]

only = set(sys.argv[1:])
issues, total = [], 0
for p in sorted((ROOT/"slides/src").glob("*.json")):
    ch = json.loads(p.read_text(encoding="utf-8"))
    if ch.get("status") == "pending" or (only and ch["id"] not in only): continue
    n = len(ch["slides"]); total += n
    if not 4 <= n <= 8: issues.append(f"{ch['id']}: 頁數 {n} 不在 4–8")
    for k, s in enumerate(ch["slides"], 1):
        tag = f"{ch['id']} p{k}"
        cites = s.get("cites", [])
        if not cites: issues.append(f"{tag}: 沒有出處"); continue
        for c in cites:
            if c not in WIKI: issues.append(f"{tag}: 引用頁不存在 [[{c}]]")
            elif c not in ch["pages"]: issues.append(f"{tag}: 引用頁 [[{c}]] 未列在章節對應表（chapters）→ 增量更新會漏掉此章")
        src = "\n".join(WIKI.get(c, "") for c in cites)
        # 8 待確認內容不得出現在簡報（2026-11-12 使用者決定）
        if s.get("todo") or any(w in t for t in texts(s) for w in ("待確認", "尚待補充")):
            issues.append(f"{tag}: 出現待確認／尚待補充內容（依規則不得放入簡報）")
        if s.get("quote"):
            q = s["quote"]["text"]
            if "「" + q not in src: issues.append(f"{tag}: 原文與引用頁不一致或非從句首開始 →「{q[:24]}…」")
        nsrc = re.sub(r"\s|\*|,", "", src)
        for t in texts(s):
            t2 = re.sub(r"\s", "", t)
            for m in re.finditer(r"(\d[\d,]*)(個月|日|天|年|%|元|款|條|項|種|頁)?", t2):
                v, unit = int(m.group(1).replace(",", "")), m.group(2)
                if unit:  # 數字＋單位一起比對，避免「3 個月」被「第 3 條」誤判為存在
                    units = {"日":["日","天"],"天":["日","天"],"%":["%","百分之"]}.get(unit,[unit])
                    forms = [f"{v}{u}" for u in units] + [f"{cn(v)}{u}" for u in units if cn(v)] + ([f"百分之{cn(v)}"] if unit=="%" and cn(v) else [])
                    ok = any(f in nsrc for f in forms)
                else:
                    ok = num_found(v, src)
                if not ok: issues.append(f"{tag}: 數字「{m.group(0)}」在引用頁找不到 → 「{t[:30]}…」")
    # 7 渲染完整性：資料中的原文、試算、待補充都必須真的出現在產生的 HTML
    hp = ROOT/"slides"/f"{ch['id']}.html"
    if hp.exists():
        h = re.sub(r"<[^>]+>", "", hp.read_text(encoding="utf-8")).replace("&quot;", '"').replace("&#x27;", "'")
        for k, s in enumerate(ch["slides"], 1):
            for key in ("quote", "calc", "todo"):
                v = s.get(key)
                v = v["text"] if isinstance(v, dict) else v
                if v and re.sub(r"\*\*", "", v) not in h:
                    issues.append(f"{ch['id']} p{k}: {key} 在資料中有、但產生的 HTML 沒有顯示")
if not only and total < 15: issues.append(f"全部章節合計 {total} 頁 < 15")
print(f"檢查 {total} 頁投影片，發現 {len(issues)} 項問題")
for i in issues: print(" -", i)
sys.exit(1 if issues else 0)
