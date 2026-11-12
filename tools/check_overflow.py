#!/usr/bin/env python3
"""B5 簡報程式檢查（版面部分）：以 Chrome 在 1280×720 原尺寸渲染每頁，量測內容是否溢出
用法：python3 check_overflow.py slides/*.html [--shots 輸出資料夾]
"""
import sys, pathlib
from playwright.sync_api import sync_playwright
args = sys.argv[1:]; shots = None
if "--shots" in args: i = args.index("--shots"); shots = pathlib.Path(args[i+1]); args = args[:i] + args[i+2:]; shots.mkdir(parents=True, exist_ok=True)
issues = 0
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(viewport={"width": 1280, "height": 780})
    for f in [a for a in args if not a.endswith("index.html")]:
        pg.goto(pathlib.Path(f).resolve().as_uri()); pg.wait_for_timeout(300)
        n = pg.eval_on_selector_all(".slide", "e=>e.length")
        for k in range(n):
            pg.evaluate(f"show({k})")
            r = pg.evaluate("""()=>{const s=document.querySelector('.slide.active'),b=s.querySelector('.body'),f=s.querySelector('footer.src');
              const kids=[...b.children];const bottom=Math.max(...kids.map(e=>e.getBoundingClientRect().bottom));
              return {over:b.scrollHeight-b.clientHeight, gap:f.getBoundingClientRect().top-bottom}}""")
            ok = r["over"] <= 1 and r["gap"] >= 4
            if not ok: issues += 1
            print(f"{'❌' if not ok else '✅'} {pathlib.Path(f).stem} p{k+1}: 溢出 {r['over']}px，與出處列距離 {round(r['gap'])}px")
            if shots: pg.locator(".stage").screenshot(path=str(shots/f"{pathlib.Path(f).stem}-p{k+1}.png"))
    b.close()
print(f"版面檢查：{issues} 頁溢出"); sys.exit(1 if issues else 0)
