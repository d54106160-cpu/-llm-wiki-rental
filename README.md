# 台灣租屋入門 LLM Wiki ＋ 教學 HTML 簡報

給第一次在外租屋的大學生：以 6 份政府公開的法規與契約規範建立 LLM Wiki（32 頁），再以 Wiki 作為唯一知識來源，製作 6 章、45 頁的教學 HTML 簡報。

做法參考 Andrej Karpathy 的 LLM Wiki：`raw/` 原始資料 → `wiki/` 整理頁 → `AGENTS.md` 規則檔。

## 快速瀏覽

| 想看什麼 | 從哪裡開始 |
|---|---|
| 教學簡報 | `slides/index.html`（下載後用瀏覽器開啟；或 GitHub Pages：`https://<帳號>.github.io/<repo>/slides/`） |
| Wiki 目錄 | [`wiki/index.md`](wiki/index.md) |
| 執行日誌 | [`wiki/log.md`](wiki/log.md)：每次 ingest、lint、審查、workflow 修改的紀錄 |
| 規則檔 | [`AGENTS.md`](AGENTS.md)：Wiki 結構、ingest／lint／簡報流程與使用者決定 |
| 審查報告 | [`slides/reviews/`](slides/reviews/)：兩版簡報各 3 輪獨立 AI 審查 |

Wiki 頁面之間的 `[[頁面代號|名稱]]` 是 Obsidian 的連結語法，在 GitHub 上只會顯示為文字。若要點擊連結並看 graph view，請用 [Obsidian](https://obsidian.md) 以資料夾開啟本 repo。

## 資料夾結構

```
.
├─ AGENTS.md            規則檔（schema）
├─ raw/                 原始 PDF，只讀不改
│  ├─ laws/             租賃住宅市場發展及管理條例、民法（租賃）
│  ├─ templates/        契約書範本、應記載及不得記載事項
│  └─ subsidies/        租金補貼作業規定、116 年度附表、115 年度申請書
├─ wiki/
│  ├─ index.md          目錄
│  ├─ log.md            執行日誌（只往後加）
│  ├─ sources/          來源摘要 7 頁
│  ├─ concepts/         概念頁 16 頁
│  └─ scenarios/        情境頁 9 頁
├─ slides/
│  ├─ index.html        簡報首頁，連到 6 章
│  ├─ 01～06-*.html     各章簡報
│  ├─ src/*.json        各章內容（每頁標註引用的 Wiki 頁）
│  ├─ chapters.md       章節與 Wiki 頁的對應表
│  └─ reviews/          獨立 AI 審查報告
└─ tools/
   ├─ lint.py           Wiki 檢查
   ├─ build_slides.py   由 JSON 產生 HTML
   ├─ check_slides.py   簡報內容檢查
   └─ check_overflow.py 簡報版面溢出檢查（Chrome 實測）
```

## 來源（6 篇）

| # | 來源 | 版本 |
|---|---|---|
| 1 | 租賃住宅市場發展及管理條例 | 修正 2023-02-08 |
| 2 | 住宅租賃定型化契約應記載及不得記載事項 | 修正 2025-04-18 |
| 3 | 住宅租賃契約書範本（含簽約注意事項） | 修正 2024-07-08 |
| 4 | 民法 債編 租賃（第 421～463-1 條） | 查詢 2026-11-11 |
| 5 | 三百億元中央擴大租金補貼專案計畫作業規定＋116 年度附表 | 115.10.6 修正 |
| 6 | 115 年度租金補貼申請書 | 2025-12-11 |

## Workflow（loop / graph）

**階段 A：建 Wiki（每篇來源一輪）**

1. A1 取得資料，放入 `raw/`
2. A2 列出重點與適用前提 → 使用者確認
3. A3 寫入 Wiki（來源、概念、情境頁，更新 index 與 log）
4. A4 Lint：`lint.py` 程式檢查＋人工檢查白話是否超出原文；不通過回 A3
5. 通過 → git commit → 進入階段 B

**階段 B：做簡報（只重做受影響章節）**

1. B1 找出受影響章節；相關 Wiki 頁少於 3 頁先不產生
2. B2 章節大綱 → 使用者確認
3. B3–B4 依確認的風格產生 HTML
4. B5 程式檢查：`check_slides.py`、`check_overflow.py`，再看截圖
5. B6 獨立 AI 審查：每輪全新代理，只給簡報與引用的 Wiki 頁
6. B7 只修報告列出的問題 → 回 B5
7. 停止條件：沒有嚴重或中等問題，或修滿 3 輪 → 發布＋git commit

## 重新執行檢查

需要 Python 3 與 poppler-utils（`pdftotext`）；版面檢查另需 Playwright 與 Chrome。

```bash
python3 tools/lint.py                  # Wiki：原文引用、截斷引用、必要欄位、連結
python3 tools/build_slides.py          # 由 slides/src/*.json 產生 HTML
python3 tools/check_slides.py          # 簡報：出處、原文、數字＋單位、頁數、待確認內容、渲染完整性
python3 tools/check_overflow.py slides/0*.html --shots shots/   # 版面溢出＋截圖
```

## 執行結果

- Wiki：32 頁，lint 0 項問題
- 簡報第 2 版獨立 AI 審查：

| 輪次 | 嚴重 | 中等 | 輕微 |
|---|---|---|---|
| 第 1 輪 | 1 | 2 | 12 |
| 第 2 輪 | 0 | 1 | 12 |
| 第 3 輪 | 0 | 0 | 14 |

第 3 輪達到停止條件；之後修正的輕微問題未再送 AI 審查（記錄於 `wiki/log.md`）。

## 使用者決定的規則

- 條例與民法規定不同時，採「特別法優於普通法」，以條例為準。此原則並非來源所載，頁面中皆標示為使用者決定。
- Wiki 中標記「⚠️ 待確認」的內容，完全不放入簡報。
- 範圍著重租屋相關事項；最新申請期間等時效性資訊不在範圍內。

## 聲明

本專案為課程作業，內容整理自政府公開資料，僅供學習，不構成法律意見。實際規定以主管機關最新公告為準。
