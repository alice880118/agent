# TradeDNA Design System

> 反推自 Figma 檔案 `test-for-agent`（9 張畫面：Home / New Analysis、User Center、Chat Default、Markets、Trade、Referees、Assets、Leaderboard、Vaults）。
> **真相來源**：本檔（人看）+ `tokens.json`（機器讀，W3C DTCG 格式）+ `ds-state.md`（版號與決策紀錄）。三份檔案同步維護，缺一不可。
> 平台：Mobile Web App，寬度 390（唯一斷點，尚未提供 768/1440 稿件）。單一 Dark Mode，尚無 Light Mode 稿件。

---

## 0. 文件說明

- 專案名稱暫定 **TradeDNA**（假設，見 `ds-state.md` 決策紀錄）。
- 命名規則嚴格依照 3 層架構：L1 Primitive → L2 Semantic → L3 Component，只能往下引用一層。
- **畫稿時只能綁 L2 semantic token，絕不可直接綁 L1。** 看到有人在元件上直接寫死 `color-lime-500` 而不是 `color-bg-accent`，就是命名違規（DS-001）。
- 圖片素材（走勢圖、頭像、Points System 背景圖）不進 token 系統，只有其外框/圓角/漸層文字等視覺屬性納管。

---

## 1. 命名規範速查

```
L1  {category}-{family}-{scale}          例：color-lime-500
L2  {category}-{role}-{prominence}[-{state}]   例：color-bg-accent-hover
L3  {component}-{part}-{property}[-{variant}][-{state}]  例：button-primary-bg-hover
```

雙軌映射：kebab-case 的 `-` 對應 Figma Variables 的 `/`；L3 一律加 `component/` 前綴。
狀態詞彙固定：`default / hover / active / focus / disabled / selected / checked / loading / error / success / read-only / empty`。`active` 只表示按下瞬間，「已選取」一律用 `selected`。

---

## 2. L1 Primitive Tokens

### 2.1 顏色

| Token | 值 | 說明 |
|---|---|---|
| `color-neutral-1000` | `#000000` | 畫布底色 |
| `color-neutral-950` | `#111212` | 卡片/導覽深底（原稿另有 `#131519` 用在 Trade、Assets 頁，視覺幾乎相同，**已收斂為同一顆**，那幾處列入稽核建議修正） |
| `color-neutral-800` | `#313131` | 圖表柱體實色（Most Active Hours） |
| `color-white` | `#ffffff` | 純白（100%） |
| `color-white-alpha-90` | `#ffffffe5` | |
| `color-white-alpha-80` | `#ffffffcc` | 收斂原稿 `#d9d9d9`（走馬燈啟用點）於此 |
| `color-white-alpha-60` | `#ffffff99` | |
| `color-white-alpha-50` | `#ffffff80` | 收斂原稿 `#858585`（底部導覽未選取）於此 |
| `color-white-alpha-40` | `#ffffff66` | |
| `color-white-alpha-30` | `#ffffff4d` | |
| `color-white-alpha-20` | `#ffffff33` | |
| `color-white-alpha-10` | `#ffffff1a` | |
| `color-white-alpha-5`  | `#ffffff0d` | |
| `color-lime-500` | `#dbfd5c` | 品牌強調色 |
| `color-lime-500-alpha-30` | `#dbfd5c4d` | 品牌色 30% 疊加（Leaderboard 當前使用者列高亮），獨立定義，不與 white-alpha 系列混用 |
| `color-lime-400` | `#c8e840` | 「已選中」互動態專用色，與品牌色 `lime-500` 同色系但**刻意分開定義**（Markets 篩選 tab 選中態文字） |
| `color-teal-500` | `#46ccb9` | 金融方向性：上漲/多單/買入 |
| `color-pink-500` | `#ff41a3` | 金融方向性：下跌/空單/賣出 |

> `color-teal-500` / `color-pink-500` 依你的規範「金融方向性 positive/negative 不跟 success/danger 混用」，L2 一律以 `positive` / `negative` 命名，不用 `success` / `danger`。

### 2.2 漸層（獨立定義，非核心調色盤，暫不重複使用於他處）

| Token | 定義 | 出現位置 |
|---|---|---|
| `gradient-button-primary` | `linear-gradient(#7053f3 0%, #76bab2 55%, #e3ff94 100%)` | Add funds / Ask Trade DNA 按鈕底 |
| `gradient-text-brand-a` | `linear-gradient(#b09eff 0%, #76bab2 60%, #e3ff94 100%)` | "Points System" 標題文字 |
| `gradient-text-brand-b` | `linear-gradient(#c4b7ff 0%, #76bab2 63%, #e3ff94 100%)` | "AI insight" 標籤文字 |

⚠ `gradient-text-brand-a` 與 `-b` 起始色微差（`#b09eff` vs `#c4b7ff`），**未強制收斂**，列入未解決事項。

### 2.3 間距

| Token | 值 |
|---|---|
| `space-050` | 4 |
| `space-075` | 6 ⚠ 離群值，只在少數 icon+label gap 出現，建議之後併入 `space-100` |
| `space-100` | 8 |
| `space-150` | 12 |
| `space-200` | 16 |
| `space-250` | 20 |
| `space-300` | 24 |
| `space-500` | 40 |

### 2.4 圓角

| Token | 值 |
|---|---|
| `radius-xs` | 4 |
| `radius-sm` | 6 |
| `radius-md` | 8 |
| `radius-lg` | 12 |
| `radius-xl` | 16 |
| `radius-full` | 999 |

### 2.5 字體

| Token | 值 | 說明 |
|---|---|---|
| `font-family-heading` | Poppins (SemiBold/Medium) | 標題、標籤 |
| `font-family-body` | Poppins (Medium) | 內文、數值 |
| `font-family-data` | Manrope (SemiBold/Medium) | ⚠ 新發現，Trade / Assets 頁部分數字標籤使用，獨立定義，**未確認是否刻意**，見未解決事項 |
| `font-family-system` | SF Pro Text | 僅 StatusBar（系統元件），不進自訂元件 token |

| Token | 值 |
|---|---|
| `font-size-050` | 10 |
| `font-size-100` | 12 |
| `font-size-150` | 13 |
| `font-size-200` | 14 |
| `font-size-300` | 16 |
| `font-size-400` | 20 |
| `font-size-500` | 24 |
| `font-size-700` | 28 |

| Token | 值 |
|---|---|
| `line-height-100` | 12 |
| `line-height-150` | 14 |
| `line-height-200` | 16 |
| `line-height-250` | 18 |
| `line-height-300` | 20 |
| `line-height-400` | 24 |
| `line-height-500` | 28 |

| Token | 值 |
|---|---|
| `font-weight-medium` | 500 |
| `font-weight-semibold` | 600 |
| `font-weight-bold` | 700 |

---

## 3. L2 Semantic Tokens

### 3.1 顏色 — 背景

| Token | 值來源 | 用途 |
|---|---|---|
| `color-bg-canvas` | `color-neutral-1000` | App 底色 |
| `color-bg-surface` | `color-neutral-950` | 導覽列、底部導覽背景 |
| `color-bg-surface-raised` | `color-white-alpha-5` | 卡片底（AI insight、Summary 卡） |
| `color-bg-surface-subtle` | `color-white-alpha-10` | 次要卡片底、頭像框底 |
| `color-bg-surface-emphasis` | `color-white-alpha-20` | Severity badge 底 |
| `color-bg-accent` | `color-lime-500` | 品牌強調底 |
| `color-bg-accent-subtle` | `color-lime-500-alpha-30` | 當前使用者高亮列 |
| `color-bg-chart-bar` | `color-neutral-800` | 圖表柱體（非高亮） |

### 3.2 顏色 — 文字 / 圖示

| Token | 值來源 | 用途 |
|---|---|---|
| `color-text-primary` | `color-white` | 主要文字、大數字 |
| `color-text-secondary` | `color-white-alpha-90` | 次要強調文字（Consistent、Healthy 前的名詞） |
| `color-text-tertiary` | `color-white-alpha-50` | 說明文字、標籤；亦收斂原「底部導覽未選取」`#858585` |
| `color-text-quaternary` | `color-white-alpha-40` | 更弱層級（Main Cause 標籤） |
| `color-text-disabled` | `color-white-alpha-30` | 停用狀態文字 |
| `color-text-brand` | `color-lime-500` | 品牌強調文字、分頁底線 |
| `color-text-selected` | `color-lime-400` | 篩選 tab 選中態文字（與 brand 分開定義） |
| `color-text-positive` | `color-teal-500` | 上漲、多單、Strong/Healthy 評級 |
| `color-text-negative` | `color-pink-500` | 下跌、空單 |
| `color-icon-primary` | `color-white` | 主要圖示 |
| `color-icon-tertiary` | `color-white-alpha-50` | 次要圖示 |
| `color-icon-disabled` | `color-white-alpha-30` | 停用圖示 |

### 3.3 顏色 — 邊框

| Token | 值來源 | 用途 |
|---|---|---|
| `color-border-subtle` | `color-white-alpha-5` | Stat card 邊框（無強調款） |
| `color-border-default` | `color-white-alpha-10` | 一般卡片、Chip 邊框 |
| `color-border-strong` | `color-white-alpha-30` | 次要按鈕邊框 |
| `color-border-accent` | `color-lime-500` | 選中態 outline（New Analysis pill、Behavior Stats 底線同色） |

### 3.4 間距語意

| Token | 值來源 | 用途 |
|---|---|---|
| `space-inset-sm` | `space-100`(8) | 小型卡片內距 |
| `space-inset-md` | `space-150`(12) | 一般卡片內距 |
| `space-inset-lg` | `space-200`(16) | 頁面左右邊距 |
| `space-stack-sm` | `space-050`(4) | 文字群組垂直間距 |
| `space-stack-md` | `space-100`(8) | 卡片內區塊間距 |
| `space-stack-lg` | `space-200`(16) | 卡片之間垂直間距 |
| `space-inline-sm` | `space-050`(4) | icon + 文字間距 |
| `space-inline-md` | `space-100`(8) | 按鈕內圖示與文字 |
| `space-gutter-lg` | `space-300`(24) | 區塊間垂直節奏 |

---

## 4. L3 Component Tokens（核心可複用元件）

### 4.1 Button

| Token | 值 |
|---|---|
| `button-primary-bg-default` | `gradient-button-primary` |
| `button-primary-text` | `color-white` |
| `button-primary-radius` | `radius-md`（一般）/ `radius-full`（pill 款如 Add funds） |
| `button-primary-bg-disabled` | `color-bg-surface-subtle` ❌ 未設計，見狀態稽核 |
| `button-outline-border-default` | `color-border-strong` |
| `button-outline-text-default` | `color-text-tertiary` |
| `button-outline-bg-hover` | ❌ 未設計 |

### 4.2 Tab（兩種，依規則 1 分開定義）

**Pill Tab**（頂部 Home/Trade DNA、User Center 的 Deposit/Withdraw/Transfer）
| Token | 值 |
|---|---|
| `tab-pill-bg-selected` | `color-bg-surface-subtle` |
| `tab-pill-text-selected` | `color-text-primary` |
| `tab-pill-bg-default` | transparent |
| `tab-pill-text-default` | `color-text-secondary` |
| `tab-pill-opacity-inactive` | 0.5（原稿以整體透明度表現未選取，非分開定義文字/圖示色，保留原做法但正式命名） |

**Underline Tab**（Behavior Stats / Health Details / Market Regime、Markets 篩選列）
| Token | 值 |
|---|---|
| `tab-underline-text-selected` | `color-text-primary`（一般）／`color-text-selected`（Markets 篩選列，各自獨立） |
| `tab-underline-text-default` | `color-text-tertiary` |
| `tab-underline-indicator-bg` | `color-text-brand` |

### 4.3 Card

| Token | 值 |
|---|---|
| `card-bg` | `color-bg-surface-raised` |
| `card-radius` | `radius-lg` |
| `card-padding` | `space-inset-md` |

### 4.4 Stat Mini Card（依規則 1 分開定義兩款）

**有框款**（Summary 區、Vault TVL/APY）
| Token | 值 |
|---|---|
| `stat-card-outlined-border` | `color-border-default` |
| `stat-card-outlined-bg` | transparent |
| `stat-card-outlined-radius` | `radius-md` |

**無框款**（AI insight 內 Win Rate / Avg loss vs win）
| Token | 值 |
|---|---|
| `stat-card-plain-border` | `color-border-subtle` |
| `stat-card-plain-bg` | transparent |

共用：
| Token | 值 |
|---|---|
| `stat-card-label` | `color-text-tertiary` |
| `stat-card-value` | `color-text-primary` |
| `stat-card-annotation-positive` | `color-text-positive` |

### 4.5 Badge / Chip

| Token | 值 |
|---|---|
| `badge-severity-bg-medium` | `color-bg-surface-emphasis` |
| `badge-severity-text-medium` | `color-text-primary` |
| `badge-severity-bg-low` | ❌ 未設計 |
| `badge-severity-bg-high` | ❌ 未設計 |
| `tag-behavioral-bg` | `color-bg-surface-raised` |
| `tag-behavioral-border` | `color-border-default` |
| `tag-behavioral-text` | `color-text-secondary` |
| `chip-filter-bg-new` | ❌ 未取得明確色值，估計值，見 `⚠ estimated` |

### 4.6 Bottom Navigation

| Token | 值 |
|---|---|
| `nav-item-icon-selected` | `color-text-primary` |
| `nav-item-label-selected` | `color-text-primary`（bold） |
| `nav-item-icon-default` | `color-text-tertiary` |
| `nav-item-label-default` | `color-text-tertiary` |

### 4.7 Market/Position Row（Markets、Leaderboard、Vaults 通用列表列）

| Token | 值 |
|---|---|
| `list-row-divider` | `color-border-subtle` |
| `list-row-bg-selected` | `color-bg-accent-subtle`（Leaderboard「You」列） |
| `list-row-value-positive` | `color-text-positive` |
| `list-row-value-negative` | `color-text-negative` |

### 4.8 Direction Tag（Trade 頁 Long/Short）

| Token | 值 |
|---|---|
| `tag-direction-text-long` | `color-text-positive` |
| `tag-direction-text-short` | `color-text-negative` |
| `tag-direction-bg` | `color-bg-surface-subtle` |

### 4.9 Input / Search

| Token | 值 |
|---|---|
| `input-bg` | `color-bg-surface-subtle` |
| `input-border-default` | `color-border-default` |
| `input-text-placeholder` | `color-text-tertiary` |
| `input-border-focus` | ❌ 未設計 |
| `input-border-error` | ❌ 未設計 |

### 4.10 Chart

| Token | 值 |
|---|---|
| `chart-bar-default` | `color-bg-chart-bar` |
| `chart-bar-highlight` | `gradient-button-primary`（依資料決定，非固定樣式） |
| `chart-axis-label` | `color-text-tertiary` |
| `chart-axis-label-emphasis` | `color-text-primary` |

---

## 5. 元件清單總覽（9 張畫面彙整）

| 元件 | 出現畫面 | 變體 | 綁定 Token 家族 |
|---|---|---|---|
| StatusBar | 全部 | — | 系統元件，不納管 |
| Top Nav / Icon Button | Home, Assets | — | `color-icon-*` |
| Pill Tab | Home, User Center | selected/default | `tab-pill-*` |
| Underline Tab | Home, Markets | selected/default | `tab-underline-*` |
| Total Assets 摘要 | Home, Assets | — | `color-text-*`, `color-text-positive/negative` |
| Gradient CTA Button | Home（Add funds / Ask Trade DNA）, Leaderboard（Trade now） | — | `button-primary-*` |
| Outline Button | Home, Trade, Referees, Vaults | — | `button-outline-*` |
| Icon Nav Item | Home, User Center, Assets | — | `color-icon-*`, `color-bg-surface-subtle` |
| Promo Banner Card | Home | — | `gradient-text-brand-a`, dots indicator |
| Market Ticker Card | Home | positive/negative | `stat-card-*`, `color-text-positive/negative` |
| Score Ring Badge | Home | — | ⚠ estimated |
| AI Insight Card | Home | — | `card-*` |
| Stat Mini Card | Home, Trade, Referees, Vaults | outlined/plain | `stat-card-*` |
| Severity Badge | Home | medium only | `badge-severity-*` |
| Cause/Action Row | Home | — | `color-text-quaternary/secondary` |
| Behavioral Tag Chip | Home | — | `tag-behavioral-*` |
| Bar Chart | Home | default/highlight | `chart-*` |
| Bottom Navigation | 全部 | selected/default | `nav-item-*` |
| Wallet Address Row | User Center, Leaderboard, Referees | — | `color-text-*` + copy icon |
| Footer + Social Icons | User Center | — | `color-text-tertiary` |
| Chat Bubble / Suggestion Card | Chat Default | — | `card-*` |
| Quick Reply Chip | Chat Default | — | `tag-behavioral-*`（沿用） |
| Chat Input Box | Chat Default | — | `input-*` |
| Position Info Bar | Chat Default | — | `tag-direction-*` |
| Header Segmented Tab | Markets, Trade | — | `tab-underline-*` |
| Search Input | Markets, Vaults, Leaderboard | — | `input-*` |
| Stat Row（24h volume 等） | Markets | — | `stat-card-plain-*` |
| Filter Chip Row | Markets | 含 "New" 標記 | `chip-filter-*` ⚠ estimated |
| Sortable Table Header | Markets, Leaderboard | — | `color-text-tertiary` + sort icon |
| Market/Ranking Row | Markets, Leaderboard | — | `list-row-*` |
| Token Selector | Trade | — | `input-*`, `color-icon-*` |
| Order Panel（外部元件） | Trade | — | 未展開，需另行盤點 |
| Position Card | Trade | — | `card-*`, `tag-direction-*` |
| Action Chip（Leverage/TP-SL/Close） | Trade | — | `button-outline-*` |
| Toggle Checkbox | Trade, Assets | — | ❌ 未設計 checked 態顏色細節 |
| Referral Code/Link Row | Referees | — | `input-*` + copy icon |
| Revenue Split Card | Referees | — | `card-*` |
| Area/Line Chart | Referees | — | `chart-*`（新用法，需與 bar chart 對齊） |
| Per-Referee Card | Referees | — | `card-*`, `stat-card-*` |
| Balance Card（per-asset） | Assets | — | `card-*`, `stat-card-plain-*` |
| Hero Heading + CTA | Leaderboard, Vaults | — | `gradient-text-brand-*`, `button-primary-*` |
| Points Summary Card | Leaderboard | — | `card-*` |
| Pagination Control | Leaderboard | — | 外部元件，需另行盤點 |
| Vault Card | Vaults | — | `card-*`, `stat-card-*` |
| Chain Icon Row | Vaults | — | `color-icon-*` |

---

## 6. 狀態矩陣稽核結果

| 元件 | default | hover | active | focus | disabled | loading | error | empty |
|---|---|---|---|---|---|---|---|---|
| Button/primary | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | — | — |
| Button/outline | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | — | — |
| Tab/pill | ✅ | ❌ | — | ❌ | — | — | — | — |
| Tab/underline | ✅ | ❌ | — | ❌ | — | — | — | — |
| Input/search | ✅ | — | — | ❌ | ❌ | — | ❌ | — |
| Stat Mini Card | ✅ | — | — | — | — | ❌(載入中骨架未設計) | — | ❌ |
| Severity Badge | ✅(medium only) | — | — | — | — | — | — | — |
| Market Row | ✅ | ❌ | ❌(可點擊進入詳情?) | ❌ | — | ❌ | — | ❌(搜尋無結果) |
| Toggle Checkbox | ✅(unchecked) | — | — | ❌ | ❌ | — | — | — |
| Position Card | ✅ | — | — | — | — | ❌(平倉中) | ❌(下單失敗) | — |
| Bottom Nav Item | ✅ | — | — | ❌ | — | — | — | — |

### 缺漏清單

- **Critical** — 全站互動元件（Button、Tab、Input、Market Row、Nav Item）都缺 `focus-visible`，鍵盤操作者完全無法辨識焦點。最小修法：統一用 `color-border-accent` 加 2px outline + 2px offset，不要另外發明顏色。
- **Critical** — Toggle Checkbox 缺 `checked` 狀態的明確視覺定義（只看到 unchecked 空心方框），核對稿件後仍未見勾選態，需要設計補齊才能實作。
- **High** — 主要動作按鈕（Ask Trade DNA、Deposit、Close 等）缺 `disabled` / `loading` 態，使用者在等待網路回應時容易重複點擊送出。
- **High** — Severity Badge 只設計了 `medium`，`low` / `high` 兩種嚴重度沒有對應顏色，AI insight 若判斷出高風險會沒有視覺依據。
- **Medium** — Market Row、Vault Card 等清單類元件缺 `empty`（搜尋無結果）與極端內容（超長交易對代碼）處理。
- **Medium** — Position Card 缺 `loading`（下單/平倉中）與 `error`（失敗）態。
- **Low** — Bottom Nav Item、Tab 缺 `active`（按下瞬間）微互動，只有 selected/default 二態。

---

## 7. RWD 規範

目前僅有 390 寬（Mobile Web）稿件，**768 / 1440 尚未提供**，本文件的 spacing/typography 尺度均以 390 為準，未來補上其他斷點前不要假設等比縮放。

---

## 8. 未解決事項

1. **專案正式名稱**待確認（暫用 TradeDNA，Bottom Nav 圖示卻叫 `Dexless AI`）。
2. **`font-family-data`（Manrope）** 是否為刻意的「數字等寬感」設計選擇，還是遺留的元件庫殘留字體，需要你確認；目前獨立定義、未合併進 Poppins。
3. `gradient-text-brand-a` / `-b` 起始色微差是否要統一。
4. `space-075`(6px) 是否要收斂進 `space-100`(8px)。
5. Filter Chip（"New" 標記）、Score Ring Badge、Toggle Checkbox 的 checked 態、Chart Highlight 邏輯目前只能從單張截圖判讀，標記 `⚠ estimated`，建議之後用 Figma 連結重新核對精確色值/圓角。
6. Order Panel（Trade 頁）、Rows-per-page（Leaderboard 頁）為外部/巢狀元件實例，本次未展開盤點，需要時再個別跑一次 Step 1-2。
7. `#131519` 出現在 Trade、Assets 頁，已建議統一改用 `#111212`（`color-neutral-950`），但原始 Figma 檔尚未修正，稽核時會持續抓到這個差異，直到設計端統一。
