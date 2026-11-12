#!/usr/bin/env python3
"""Wiki Lint：程式檢查（AGENTS.md 的 Lint 清單中可自動化的部分）
用法：python3 tools/lint.py
"""
import re, subprocess, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
pages = {p.stem: p for p in WIKI.rglob("*.md") if p.name not in ("index.md", "log.md")}
norm = lambda s: re.sub(r"\s+", "", s)

def fm(text):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    d = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1); d[k.strip()] = v.strip()
    return d

# 來源文字：sources/ 頁的 raw 欄位指向 PDF
src_text = {}
for sid, p in pages.items():
    d = fm(p.read_text(encoding="utf-8"))
    if d.get("type") == "source" and d.get("raw"):
        out = subprocess.run(["pdftotext", "-layout", str(ROOT / d["raw"]), "-"], capture_output=True, text=True).stdout
        # 去掉頁碼行（只有數字）與網頁列印的頁首頁尾，避免跨頁引用被夾斷
        out = "\n".join(l for l in out.splitlines() if not re.fullmatch(r"\s*\d+(\s*/\s*\d+)?\s*", l) and not re.match(r"\s*(https?://|\d{4}/\d{1,2}/\d{1,2})", l))
        # 直排表格在 layout 模式會被拆散，另附 raw 模式文字作為比對備援
        raw_out = subprocess.run(["pdftotext", "-raw", str(ROOT / d["raw"]), "-"], capture_output=True, text=True).stdout
        raw_out = "\n".join(l for l in raw_out.splitlines() if not re.fullmatch(r"\s*\d+(\s*/\s*\d+)?\s*", l) and not re.match(r"\s*(https?://|\d{4}/\d{1,2}/\d{1,2})", l))
        src_text[sid] = norm(out) + "\n" + norm(raw_out)

issues = []
warns = []
inbound = {k: 0 for k in pages}
idx = (WIKI / "index.md").read_text(encoding="utf-8")
for sid, p in pages.items():
    t = p.read_text(encoding="utf-8"); d = fm(t); rel = p.relative_to(ROOT)
    for f in ("title", "type", "sources", "source_date", "updated"):
        if not d.get(f): issues.append(f"{rel}: 缺少 frontmatter 欄位 {f}")
    if d.get("type") in ("concept", "scenario") and "> 白話：" not in t:
        issues.append(f"{rel}: 缺少一句話白話說明")
    srcs = re.findall(r"[\w-]+", d.get("sources", ""))
    for s in srcs:
        if s not in pages: issues.append(f"{rel}: sources 列出不存在的來源頁 {s}")
    for q in re.findall(r"原文：「(.+?)」", t):
        hits = [src_text[s] for s in srcs if norm(q) in src_text.get(s, "")]
        if not hits:
            issues.append(f"{rel}: 原文引用在來源 PDF 找不到 →「{q[:30]}…」")
        else:
            # 截斷句偵測：引用前一個字不是句子/款項邊界 → 可能漏掉前文的適用前提
            src = hits[0]; i = src.find(norm(q)); prev = src[max(0, i-6):i]
            # 只在「前一字是逗號或連接詞」時提醒：代表引用從子句中間開始，前面的條件（…者，）被截掉
            if re.search(r"[，,並]$", prev) and not q.startswith("但"):
                warns.append(f"{rel}: 引用非從句首開始，請確認前文是否有適用前提 →「…{prev}」+「{q[:20]}…」")
    for link in re.findall(r"\[\[([^\]|\\]+)", t):
        if link not in pages: issues.append(f"{rel}: 連結到不存在的頁面 [[{link}]]")
        elif link != sid: inbound[link] += 1
    if sid not in idx: issues.append(f"{rel}: 未列在 index.md")
for k, n in inbound.items():
    if n == 0 and fm(pages[k].read_text(encoding="utf-8")).get("type") != "source":
        issues.append(f"{pages[k].relative_to(ROOT)}: 孤立頁（沒有其他頁連入）")
todo = [str(p.relative_to(ROOT)) for p in pages.values() if "⚠️ 待確認" in p.read_text(encoding="utf-8")]
print(f"檢查 {len(pages)} 頁，發現 {len(issues)} 項問題")
for i in issues: print(" -", i)
if todo: print("待確認標記：", ", ".join(todo))
if warns:
    print(f"⚠️ 截斷引用提醒 {len(warns)} 項（需人工確認，不計入問題）")
    for w in warns: print(" -", w)
sys.exit(1 if issues else 0)
