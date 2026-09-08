# TradeDNA Design System — State

版本：v0.1（建置中，首次萃取）
最後更新：2026-09-08

---

## 已納入畫面

| # | 畫面名稱 | 斷點 | Figma node-id | 備註 |
|---|---|---|---|---|
| 1 | Home / New Analysis | 390 | 1:2100 | 首張基準稿 |
| 2 | User Center | 390 | 1:2517 | |
| 3 | Chat Default | 390 | 1:2996 | AI 對話介面 |
| 4 | Markets | 390 | 1:2687 | |
| 5 | Trade | 390 | 1:3800 | Order panel 為外部元件，未展開 |
| 6 | Referees（Referral） | 390 | 1:4703 | |
| 7 | Assets | 390 | 1:4549 | |
| 8 | Leaderboard | 390 | 1:5195 | Rows-per-page 為外部元件，未展開 |
| 9 | Vaults | 390 | 1:4994 | |

768 / 1440 斷點：尚未提供稿件。

---

## 待決策

| # | 項目 | 現況 | 需要你決定 |
|---|---|---|---|
| 1 | 專案正式名稱 | 暫用 `TradeDNA`（假設） | 確認正式名稱，Bottom Nav 圖示與文字標籤（Dexless AI / Trade DNA）不一致 |
| 2 | `font-family-data`（Manrope） | 獨立定義，未合併進 Poppins | 確認是否為刻意設計選擇 |
| 3 | `gradient-text-brand-a` vs `-b` | 起始色微差（#b09eff vs #c4b7ff），未強制收斂 | 統一或保留兩者 |
| 4 | `space-075`(6px) | 離群值，僅少數 icon+label gap 使用 | 是否收斂進 `space-100`(8px) |
| 5 | Severity Badge low/high 顏色 | ❌ 未設計，只看到 medium | 需要設計端補值 |
| 6 | Toggle Checkbox checked 態 | ❌ 未在稿件中發現明確視覺 | 需要設計端補值 |
| 7 | Filter Chip "New" 標記色值 | ⚠ estimated（僅目測） | 建議用 Figma 連結重新核對精確色碼 |
| 8 | Score Ring Badge 填色/漸層規則 | ⚠ estimated | 同上 |

---

## 缺漏狀態（見 design-system.md 第 6 節完整表格）

- **Critical**：全站互動元件缺 `focus-visible`；Toggle Checkbox 缺 `checked` 視覺定義
- **High**：主要按鈕缺 `disabled`/`loading`；Severity Badge 缺 low/high 色階
- **Medium**：清單類元件缺 `empty`/極端內容處理；Position Card 缺 `loading`/`error`
- **Low**：Bottom Nav / Tab 缺 `active` 微互動

下次維護時重跑此清單，追蹤是否變短。

---

## 決策紀錄

### 2026-09-08 — 首次建置

- **D-01**：Home 頁盤點時發現 3 個疑慮（pill tab 用整體透明度表現 inactive、CTA 漸層按鈕 vs 外框 pill tab 是否同源、Stat Mini Card 有框/無框版本），使用者裁定「**分開定義**」→ 皆保留為獨立 token/元件定義，不強行合併。適用範圍：
  - `button-primary-*`（CTA 漸層按鈕）與 `tab-pill-*`（Home/Trade DNA 分頁）分開定義
  - `stat-card-outlined-*` 與 `stat-card-plain-*` 分開定義
  - Severity Badge 不臆測補值，僅定義已觀察到的 `medium`
  - 兩組漸層 `gradient-text-brand-a` / `-b` 不強制統一
  - `font-family-data`（Manrope）獨立於 `font-family-body`（Poppins）
  - `color-lime-400`（選中態）獨立於 `color-lime-500`（品牌色）

- **D-02**：4 個未收斂的獨立色，使用者裁定「**收斂進既有 neutral 階梯**」：
  - `#858585`（底部導覽未選取）→ 復用 `color-white.alpha-50`（= `color-text-tertiary`）
  - `#d9d9d9`（走馬燈啟用點）→ 復用 `color-white.alpha-80`
  - `#111212` 與新發現的 `#131519`（Trade/Assets 頁）→ 統一收斂為 `color-neutral-950`(`#111212`)，`#131519` 那幾處列為稽核建議修正項目（原始 Figma 檔尚未修正）
  - `#313131`（圖表柱）→ 保留為 neutral 階梯上的獨立一階 `color-neutral-800`（因屬圖表用實色，非疊加透明度）

- **D-03**：專案樣本從 1 張稿（Home）擴充至 9 張稿（User Center / Chat Default / Markets / Trade / Referees / Assets / Leaderboard / Vaults），語意層判斷已不再只依賴單一畫面。

- **D-04**：Spacing 採「100 起跳的百階制」（`space-050`=4 … `space-500`=40），Radius 採 `xs/sm/md/lg/xl/full` 六階，字級混合 px 值與百階索引；此為本次建置自訂命名，Figma 原始變數命名（如 `Radius/md`=6px、`Radius/lg`=8px）與我方 token 名稱不一致，已在 design-system.md 註明避免混淆。

---

## 下次維護指令參考

- 「新增畫面 + 貼稿」→ 跑 diff，只回報變動
- 「補狀態」→ 針對指定元件（優先建議：Button、Toggle Checkbox、Severity Badge）逐條給選項
- 「打版本」→ 產 changelog，版號升至 v1.0（待 768/1440 斷點與缺漏清單收斂後再升）
