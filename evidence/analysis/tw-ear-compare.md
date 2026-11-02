# 台灣軍商兩用貨品清單 vs 美國 EAR（CCL）逐號比對

> 更新註記（2026-11-02）：本報告完成後，EAR 切檔器補正一處漏切（8D001 的標題在 eCFR 中為 FP-1 元素），`data/ccl_index.json` 現為 638 個 ECCN、台灣同號 354 個。第 2 節的 637／353 為補正前數字，其餘內容不受影響。

> 狀態：**部分完成**。已做完的號碼逐項列出差異；未做完的號碼在第 7 節標「未完成」。所有引文皆由程式依『檔案＋行號＋錨字串』從證據檔取出並斷言存在（逐字）；座標中 EAR 為 `ccl/<ECCN>.txt:行號`，台灣為 `twl/<號碼>.txt:行號（印刷頁）`。

## 1. 方法與核對

**切檔**：`evidence/tools/parse_tw_list.py` 以目錄（印刷頁碼）建立應有號碼序列，再於正文逐類依序找標題行；每頁只做兩件事：去掉頁尾頁碼行（全文 349 頁各恰一行，印刷頁 = PDF 頁 − 13）與換頁字元。來源檔 sha256 `87931c70…b71a`（相容表意字已由協調者換回標準字，行號不變）。

**核對（目錄號碼數 vs 切出數）**：目錄列 **383** 個管制號碼；正文切出 **386** 個，差 **+3**，差的是 **1C117、3D006、6E201**（正文有標題、目錄漏列）；目錄有而正文找不到者 0。另：目錄頁碼與正文標題所在印刷頁不同者 9 筆（0B007、1A005、1C118、1C229、1C236、1C237、1C238、2D001、2E001，皆差 ±1 頁，以正文為準）；4D002、4D003 目錄與正文皆為「刪除」，各成一檔並標 `deleted`；2A225 正文標題行為『A2A225』（多一個 A），原文不改、索引記 `heading_token`；其餘非空白正文行皆已歸屬某一輸出檔（未歸屬 0）。

**輸出**：`evidence/text/twl/` 共 428 個檔（號碼檔 386、ML1–ML22 共 22、底線檔 20）；`data/tw_index.json` 386 筆。一般軍用貨品清單 22 個 ML 標題皆與目錄頁碼一致，故逐 ML 成檔。

**號碼規則依據**：EAR `evidence/text/ear/738.2.txt` 第 41 行（第 3–5 碼意義）、第 43–61 行（Table 1：000-099 NS、100-199 MT、200-299 NP、300-399 CB、500-599、600-699、900-979、980-989、990-999）、第 65 行（第二、三碼 99 為單邊；2 與 9 為核擴散關切之單邊）；台灣 `evidence/text/twl/_numbering.txt` 第 45–54 行（000-099 WA、100-199 MTCR、200-299 NSG、300-399 AG、400-499 CWC、500-899 保留、900-999 單邊管制）。738.2 Table 1 沒有 400-499 與 700-899 列。

**比對法**：把兩邊各自切成『標籤項＋註解』區塊（a./a.1./1.、Note/N.B./Technical Note 與 註解/說明/技術註解），台灣側的子項層級由編號序列推斷、並以 EAR 的區塊鍵當歧義時的參考；區塊鍵相同者配對，鍵不同但註解型別、序號與根標籤相同者視為『置換配對』。配對後（a）列只在一邊的區塊、佔位（[Reserved]／刪除）不一致；（b）抽出所有帶單位數字（先剔除 ECCN 參照、註解編號、標準編號），比對兩邊數值集合，並另比對比較詞（超過／以上／小於／以下…）、全部／任一連接詞與 ECCN 交互引用。判定標準：**翻譯／編排差異**＝同一管制內容的措辭、順序、編號、單位寫法或參照註記不同；**實質差異**＝數值、單位、明示的比較運算、除外清單、子項有無在兩邊文字上不同；**無法判定**＝文字確有不同，但是否影響範圍或成因在兩份文本內無法判斷。

**不列入的雜訊**：『最高至 X 且包含 X』與 EAR『up to and including X』（同義、數字重複）；『bit』與『位元』、『cm 2』與『cm2』等單位寫法；英文 one/two… 與阿拉伯數字。

## 2. 號碼型態與同號對照（data/eccn_tw_map.json）

EAR（`ccl_index.json`）637 個 ECCN 中，台灣有同號（非『刪除』）者 **353**；台灣有而 EAR 無同號者 **30**（見下）；`ccl_index.json` 漏收 `8D001`（標題落在 `ccl/_notes-cat8-D.txt:5`），已另列 `ccl_index_gaps`，不計入。

| ear_kind | EAR 號碼數 | 台灣有同號 |
|---|---|---|
| multilateral_no_tw_match | 37 | 0 |
| multilateral_tw_match | 335 | 335 |
| plurilateral_900_979 | 24 | 18 |
| series_0Y521 | 5 | 0 |
| series_5xx_other | 17 | 0 |
| series_600 | 76 | 0 |
| series_9x515_spacecraft | 4 | 0 |
| unilateral_980_989_CC_SS | 29 | 0 |
| unilateral_990_999_AT_RS_UN | 103 | 0 |
| unilateral_NP_29x | 7 | 0 |

「多邊」僅指號碼落在 738.2 Table 1 的 000–399 區段；條文自列的 Reason for Control 未含該區段字母者（`table1_reason_in_text=false`）：1C355、1E355、3A090、3A232、4A090、4D090、4E091。

**台灣有、EAR 無同號（30）**：0A001、0B001、0B002、0B003、0B004、0B005、0B006、0B007、0C001、0C002、0C003、0C004、0C005、1B235、1C012、1C238、1C450、2B219、3A102、3D225、3E225、6D203、6E203、7D104、9A112、9A121、9A350、9A901、9B107、9C108。

**台灣 900–999 單邊碼（19）在 EAR 是否同號**：2B910 有；2D910 有；2E903 有；2E910 有；3A901 有；3A904 有；3B903 有；3B904 有；3C907 有；3C908 有；3C909 有；3D901 有；3D907 有；3E901 有；3E905 有；4A906 有；4D906 有；4E906 有；9A901 **無**。EAR 900–979 區段 24 個號碼中，台灣沒有同號者：0A919、0A977、0A978、0A979、0D977、0E977。

## 3. 各號逐項差異（已判讀部分）


### 3A001

**[3A001-01] 數值｜實質差異（疑為版本落差或台灣自定）｜b.7.a 訊號分析儀延伸頻率：90 GHz → 110 GHz**

- EAR `ccl/3A001.txt:459` …「uency range of “signal analyzers” beyond 90 GHz;」
- 台灣 `twl/3A001.txt:515`（印刷頁 146） 「   a.設計用於延伸〝訊號分析儀〞頻率範圍超過110 GHz；」

**[3A001-02] 數值｜實質差異（疑為版本落差或台灣自定）｜b.7.b.1 訊號產生器延伸範圍：90 GHz → 110 GHz**

- EAR `ccl/3A001.txt:463` 「b.7.b.1. Beyond 90 GHz;」
- 台灣 `twl/3A001.txt:518`（印刷頁 147） 「     1.超過110 GHz；」

**[3A001-03] 數值｜實質差異（疑為版本落差或台灣自定）｜b.7.b.2 頻率範圍上限：90 GHz → 110 GHz（輸出功率 100 mW/20 dBm 兩邊相同）**

- EAR `ccl/3A001.txt:465` …「ency range exceeding 43.5 GHz but not exceeding 90 GHz;」
- 台灣 `twl/3A001.txt:520`（印刷頁 147） 「        超過110 GHz；」

**[3A001-04] 數值｜實質差異（疑為版本落差或台灣自定）｜b.7.c.2 網路分析儀：輸出功率 31.62 mW(15 dBm) → 100 mW(20 dBm)，上限 90 → 110 GHz**

- EAR `ccl/3A001.txt:471` …「. To an output power greater than 31.62 mW (15 dBm) anywhere within the frequency ran」…
- EAR `ccl/3A001.txt:471` …「ency range exceeding 43.5 GHz but not exceeding 90 GHz;」
- 台灣 `twl/3A001.txt:524`（印刷頁 147） 「     2.輸出功率大於100 mW(20dBm)，頻率範圍超過43.5 GHz 但未」
- 台灣 `twl/3A001.txt:525`（印刷頁 147） 「        超過110 GHz；」

**[3A001-05] 骨架｜實質差異（疑為版本落差或台灣自定）｜b.7.c.3：EAR 有 1 mW(0 dBm)、90–110 GHz 子項，台灣為「刪除」**

- EAR `ccl/3A001.txt:473` 「b.7.c.3. To an output power greater than 1 mW (0 dBm) anywhere within the frequency ran」…
- 台灣 `twl/3A001.txt:526`（印刷頁 147） 「     3.刪除」

**[3A001-06] 數值｜實質差異（疑為版本落差或台灣自定）｜b.11.d 頻率合成範圍上限：37 GHz → 43.5 GHz**

- EAR `ccl/3A001.txt:517` …「ency range exceeding 31.8 GHz but not exceeding 37 GHz;」
- 台灣 `twl/3A001.txt:585`（印刷頁 148） 「      超過43.5 GHz 時，低於500 μs；」

**[3A001-07] 數值｜實質差異（疑為版本落差或台灣自定）｜b.5 可調濾波器調整時間單位：10 ms（EAR）vs 10 μs（台灣）；無法由文本判斷哪邊為誤植**

- EAR `ccl/3A001.txt:449` …「5:1 frequency band (fmax/fmin) in less than 10 ms and having any of the following:」
- 台灣 `twl/3A001.txt:503`（印刷頁 146） 「5. 含 有 5 個 以 上 可 調 式 共 振 器 ， 可 於 10 μs 內 調 整 1.5 ： 1 頻 帶」

**[3A001-08] 比較詞｜無法判定｜b.5 諧振器數：more than 5 vs 5個以上（邊界含括不同）**

- EAR `ccl/3A001.txt:449` …「pass or band-stop filters, having more than 5 tunable resonators capable of tuning across a 1.5:1 」…
- 台灣 `twl/3A001.txt:503`（印刷頁 146） 「5. 含 有 5 個 以 上 可 調 式 共 振 器 ， 可 於 10 μs 內 調 整 1.5」…
- 說明：『以上』在台灣法規用語通常含本數，英文 more than 不含；是否刻意無法由兩份文本判定。

**[3A001-09] 比較詞｜實質差異（疑為版本落差或台灣自定）｜a.5.a.4 解析度上界：less than 16 bit vs 小於或等於16位元**

- EAR `ccl/3A001.txt:123` …「resolution of 14 bit or more, but less than 16 bit, with a “sample rate” greater tha」…
- 台灣 `twl/3A001.txt:68`（印刷頁 137） 「      4. 解析度為14位元或以上，但小於或等於16位元，〝取樣率〞」
- 說明：台灣字面較寬；但同檔 a.5.a.5 已涵蓋 16 位元以上且取樣率門檻更低，對整體涵蓋範圍影響有限（僅就條文推得，非外部資料）。

**[3A001-10] 比較詞｜無法判定｜a.2.a 環境溫度：above 398 K vs 398 K 以上**

- EAR `ccl/3A001.txt:97` …「eration at an ambient temperature above 398 K (+125 °C);」
- 台灣 `twl/3A001.txt:29`（印刷頁 137） 「   a. 被評定為可於398 K (125 °C)以上之環境溫度下操作；」
- 說明：同 b.5 之邊界用語問題。

**[3A001-11] 比較詞｜無法判定｜a.2.b 環境溫度：below 218 K vs 218 K 以下**

- EAR `ccl/3A001.txt:99` …「eration at an ambient temperature below 218 K (−55 °C); or」
- 台灣 `twl/3A001.txt:31`（印刷頁 137） 「   b. 被評定為可於218 K (-55 °C)以下之環境溫度下操作；或」
- 說明：同上。

**[3A001-12] 比較詞｜實質差異（疑為版本落差或台灣自定）｜i.1 頻率上界：less than 20 GHz vs 未超過20 GHz（i.2 兩邊皆含 20 GHz，台灣於 20 GHz 時 i.1、i.2 重疊）**

- EAR `ccl/3A001.txt:725` …「frequency of more than 10 GHz but less than 20 GHz, an optical insertion loss equal 」…
- 台灣 `twl/3A001.txt:817`（印刷頁 153） 「   1. 最大操作頻率超過10 GHz 但未超過20 GHz，光學介入損失等於」

**[3A001-13] 比較詞｜無法判定｜i.1.b 測量頻率：more than 1 GHz vs 1 GHz 或以上**

- EAR `ccl/3A001.txt:729` …「V when measured at a frequency of more than 1 GHz; or」
- 台灣 `twl/3A001.txt:820`（印刷頁 153） 「      b. ‵ 半波電壓′(‵Vπ′)在頻率1 GHz 或以上時測量小於4 V；或」
- 說明：同 b.5。

**[3A001-14] 比較詞｜無法判定｜i.2.b 測量頻率：more than 1 GHz vs 1 GHz 或以上**

- EAR `ccl/3A001.txt:735` …「V when measured at a frequency of more than 1 GHz.」
- 台灣 `twl/3A001.txt:824`（印刷頁 153） 「      b. ‵ 半波電壓′(‵Vπ′)在頻率1 GHz 或以上時測量小於5 V。」
- 說明：同 b.5。

**[3A001-15] 比較詞｜無法判定｜e.3 充放電時間：less than one second vs 1秒內**

- EAR `ccl/3A001.txt:637` …「be fully charged or discharged in less than one second and having all of the following:」
- 台灣 `twl/3A001.txt:743`（印刷頁 151） 「3. 特別被設計為可於1秒內完全充電及放電之〝超導〞電磁鐵或電」
- 說明：「1秒內」是否含恰為 1 秒無法判定。

**[3A001-16] 骨架｜實質差異（疑為版本落差或台灣自定）｜a.9：EAR 為 [Reserved]，台灣仍列「類神經網路積體電路」**

- EAR `ccl/3A001.txt:211` 「a.9. [Reserved]」
- 台灣 `twl/3A001.txt:174`（印刷頁 140） 「9. 類神經網路積體電路；」

**[3A001-17] 引用｜實質差異（疑為版本落差或台灣自定）｜e.1 註解範圍：EAR「3A001.e」整個 e 項 vs 台灣「3A001.e.1.」僅 e.1**

- EAR `ccl/3A001.txt:615` 「Note: 3A001.e does not control batteries, including single-cell batteries.」
- 台灣 `twl/3A001.txt:718`（印刷頁 151） 「  註解：3A001.e.1.不管制電池組，包括由單一電池芯組成之電池」

**[3A001-18] 骨架｜實質差異（疑為版本落差或台灣自定）｜EAR 自設 j–y 保留與 z 項（引用 3A090 效能參數）；台灣全檔無 z 項、無 3A090**

- EAR `ccl/3A001.txt:741` 「j. through y. [Reserved]」
- EAR `ccl/3A001.txt:743` …「eds the performance parameters in 3A090, as follows:」
- EAR `ccl/3A001.txt:745` …「he performance parameters in ECCN 3A090.a, except those 3A001.b.2 and b.3 i」…
- （此側無對應段落）台灣 twl/3A001.txt 全檔不含「3A090」（程式斷言）；data/tw_index.json 亦無 3A090。

**[3A001-19] 骨架｜翻譯／編排差異｜技術註解 b.9.c.2 之 1、2 順序互換（EAR：體積算例在前；台灣：開機時間在前）**

- EAR `ccl/3A001.txt:501` 「1. To calculate the volume in 3A001.b.9.b, the following example is provide」…
- EAR `ccl/3A001.txt:503` 「2. The 'turn-on time' in 3A001.b.9.a refers to the time from fully-off」…
- 台灣 `twl/3A001.txt:558`（印刷頁 147） 「  1. 就3A001.b.9.a.目的，所述之‵開機時間′指的是完全關機到完全」
- 台灣 `twl/3A001.txt:562`（印刷頁 148） 「  2. 就3A001.b.9.b.目的，計算3A001.b.9.b.所述之體積，如下例所」

**[3A001-20] 骨架｜翻譯／編排差異｜a.2 技術註解位置：EAR 在 a.2 與 a.2.a 之間，台灣在 a.2.c 之後（定義文字相同）**

- EAR `ccl/3A001.txt:95` …「: For the purposes of 3A001.a.2, 'non-volatile memories' are memories with data retention」…
- 台灣 `twl/3A001.txt:41`（印刷頁 137） 「     就3A001.a.2.目的，‵非揮發性記憶體′為電源關閉後儲存的資料」

**[3A001-21] 骨架｜翻譯／編排差異｜EAR 的 N.B. 參照 3A901（台灣無對應註記；3A901 於台灣清單存在）**

- EAR `ccl/3A001.txt:103` …「cuits not specified by 3A001.a.2, see 3A901.a.」
- EAR `ccl/3A001.txt:277` …「 (QLAs) not specified by 3A001.b, see ECCN 3A901.b.」

**[3A001-22] 骨架｜翻譯／編排差異｜台灣獨有的參照『說明』（參照 3A101、3A201）**

- 台灣 `twl/3A001.txt:57`（印刷頁 137） 「     說明：參照3A101。」
- 台灣 `twl/3A001.txt:722`（印刷頁 151） 「  說明：參照3A201.a.及軍用貨品清單。」
- 台灣 `twl/3A001.txt:745`（印刷頁 151） 「  說明：參照3A201.b.」

**[3A001-23] 骨架｜翻譯／編排差異｜b.4.f 的 N.B.1–3 vs 說明1–3、註解1 [Reserved] vs 刪除**

- EAR `ccl/3A001.txt:441` 「2. For 'transmit/receive modules' and 'transmit modules' see 3A001.b.12.」
- EAR `ccl/3A001.txt:445` 「Note 1: [Reserved]」
- 台灣 `twl/3A001.txt:491`（印刷頁 146） 「  說明2：‵傳輸/接收模組′與‵傳輸模組′，參考3A001.b.12.。」
- 台灣 `twl/3A001.txt:497`（印刷頁 146） 「  註解1：刪除。」


### 3A002

**[3A002-24] 數值｜實質差異（疑為版本落差或台灣自定）｜c.2 訊號分析儀：DANL −150 dBm/Hz → −160 dBm/Hz，上限 90 → 110 GHz**

- EAR `ccl/3A002.txt:67` …「e Level (DANL) less (better) than −150 dBm/Hz anywhere within the frequency ran」…
- EAR `ccl/3A002.txt:67` …「ency range exceeding 43.5 GHz but not exceeding 90 GHz;」
- 台灣 `twl/3A002.txt:34`（印刷頁 155） 「    (優於)-160 dBm/Hz，其頻率超過43.5 GHz 但不超過110 GHz；」
- 台灣 `twl/3A002.txt:34`（印刷頁 155） …「   (優於)-160 dBm/Hz，其頻率超過43.5 GHz 但不超過110 GHz；」

**[3A002-25] 數值｜實質差異（疑為版本落差或台灣自定）｜c.3 頻率：90 GHz → 110 GHz**

- EAR `ccl/3A002.txt:69` …「nal analyzers” having a frequency exceeding 90 GHz;」
- 台灣 `twl/3A002.txt:36`（印刷頁 155） 「   3. 〝訊號分析儀〞頻率超過110 GHz；」

**[3A002-26] 數值｜實質差異（疑為版本落差或台灣自定）｜c.4.a 即時頻寬：170 MHz → 520 MHz**

- EAR `ccl/3A002.txt:73` 「c.4.a. 'Real-time bandwidth' exceeding 170 MHz; and」
- 台灣 `twl/3A002.txt:40`（印刷頁 155） 「      a. ‵即時頻寬′超過520 MHz；及」

**[3A002-27] 數值｜實質差異（疑為版本落差或台灣自定）｜c.4.b.1 訊號持續時間：15 µs → 8 μs**

- EAR `ccl/3A002.txt:77` …「, of signals having a duration of 15 µs or less; or」
- 台灣 `twl/3A002.txt:44`（印刷頁 155） …「     1. 具100%的發現率，於間隙或訊號的開窗效應持續時間為8 μs」

**[3A002-28] 數值｜實質差異（疑為版本落差或台灣自定）｜c.4.b.2 訊號持續時間：15 µs → 8 μs**

- EAR `ccl/3A002.txt:79` …「 for signals having a duration of 15 µs or less;」
- 台灣 `twl/3A002.txt:48`（印刷頁 155） 「           續時間為8 μs 或以下；」

**[3A002-29] 數值｜實質差異（疑為版本落差或台灣自定）｜d.2、d.3.g、d.4.a、d.4.b、d.5.d、d.6 頻率上限：90 GHz → 110 GHz**

- EAR `ccl/3A002.txt:101` …「ency range exceeding 43.5 GHz but not exceeding 90 GHz;」
- EAR `ccl/3A002.txt:117` …「quency range exceeding 75 GHz but not exceeding 90 GHz.」
- EAR `ccl/3A002.txt:121` …「uency range exceeding 3.2 GHz but not exceeding 90 GHz; or」
- EAR `ccl/3A002.txt:123` …「uency range exceeding 3.2 GHz but not exceeding 90 GHz;」
- EAR `ccl/3A002.txt:135` …「quency range exceeding 75 GHz but not exceeding 90 GHz; or」
- EAR `ccl/3A002.txt:139` 「d.6. A maximum frequency exceeding 90 GHz;」
- 台灣 `twl/3A002.txt:86`（印刷頁 156） 「   但不超過110 GHz；」
- 台灣 `twl/3A002.txt:102`（印刷頁 156） 「   g. 在頻率超過75 GHz，但不超過110 GHz 的條件下，頻率變化」
- 台灣 `twl/3A002.txt:108`（印刷頁 156） 「   a. 在頻率超過3.2 GHz 但不超過110 GHz，10 Hz ≤F ≤ 10 kHz 範圍」
- 台灣 `twl/3A002.txt:111`（印刷頁 156） 「   b. 在頻率超過3.2 GHz 但不超過110 GHz，10 kHz < F ≤ 100 kHz」
- 台灣 `twl/3A002.txt:130`（印刷頁 156） 「   d. 在頻率範圍超過75 GHz 但不超過 110 GHz 情況下，超過5.0」
- 台灣 `twl/3A002.txt:140`（印刷頁 157） 「   6. 最大頻率超過110 GHz；」

**[3A002-30] 數值｜實質差異（疑為版本落差或台灣自定）｜e.1 網路分析儀：31.62 mW(15 dBm) → 100 mW(20 dBm)，上限 90 → 110 GHz**

- EAR `ccl/3A002.txt:151` 「e.1. An output power exceeding 31.62 mW (15 dBm) anywhere within the operating fre」…
- EAR `ccl/3A002.txt:151` …「ency range exceeding 43.5 GHz but not exceeding 90 GHz;」
- 台灣 `twl/3A002.txt:152`（印刷頁 157） 「   1. 輸出功率超過100 mW (20 dBm)之任一處其最大操作頻率超過」
- 台灣 `twl/3A002.txt:154`（印刷頁 157） 「      43.5 GHz 但未超過110 GHz；」

**[3A002-31] 骨架｜實質差異（疑為版本落差或台灣自定）｜e.2：EAR 有 1 mW(0 dBm)、90–110 GHz 子項，台灣為「刪除」**

- EAR `ccl/3A002.txt:153` 「e.2. An output power exceeding 1 mW (0 dBm) anywhere within the operating fre」…
- 台灣 `twl/3A002.txt:155`（印刷頁 157） 「   2. 刪除；」

**[3A002-32] 比較詞｜無法判定｜a.6.a 持續資料產出量：more than 6.4 Gbit/s vs 6.4 Gbit/s 或以上**

- EAR `ccl/3A002.txt:47` …「tained 'continuous throughput' of more than 6.4 Gbit/s to disk or solid-state drive memo」…
- 台灣 `twl/3A002.txt:14`（印刷頁 154） 「                     Gbit/s 或以上；及」
- 說明：同 3A001 b.5 邊界用語問題。

**[3A002-33] 比較詞｜實質差異（疑為版本落差或台灣自定）｜h.1.d 解析度：14 bit or more but less than 16 bit vs 大於14位元，但小於或等於16位元**

- EAR `ccl/3A002.txt:191` 「h.1.d. A resolution of 14 bit or more but less than 16 bit, with a “sample rate” greater tha」…
- 台灣 `twl/3A002.txt:188`（印刷頁 158） 「      d. 解析度大於14位元，但小於或等於16位元，〝取樣率〞大於」
- 說明：台灣同檔 3A001.a.5.a.4 寫「14位元或以上」，3A002.h.1.d 寫「大於14位元」，台灣兩處自相不一致。

**[3A002-34] 比較詞｜實質差異（疑為版本落差或台灣自定）｜h.1.e 解析度：16 bit or more vs 大於16位元（字面上恰為 16 位元者不在台灣 h.1.e 內）**

- EAR `ccl/3A002.txt:193` 「h.1.e. A resolution of 16 bit or more with a “sample rate” greater than」…
- 台灣 `twl/3A002.txt:191`（印刷頁 158） 「      e. 解析度大於16位元，〝取樣率〞大於每秒180百萬次取樣」

**[3A002-35] 骨架｜翻譯／編排差異｜a.1–a.5：EAR 以範圍『a.1. to a.5. [Reserved]』表示，台灣逐項『刪除』**

- EAR `ccl/3A002.txt:41` 「a.1. to a.5. [Reserved]」
- 台灣 `twl/3A002.txt:6`（印刷頁 154） 「               1. 刪除；」
- 台灣 `twl/3A002.txt:10`（印刷頁 154） 「               5. 刪除；」

**[3A002-36] 骨架｜翻譯／編排差異｜技術註解位置：EAR 把 'pulse duration' 定義放在 d 項末；台灣放在 d.1.b 之後**

- EAR `ccl/3A002.txt:147` …「 For the purposes of 3A002.d.1.a, 'pulse duration' is defined as the time interval f」…
- 台灣 `twl/3A002.txt:77`（印刷頁 155） 「      a. ‵脈衝持續時間′小於25ns；及」


### 5A001

**[5A001-37] 邏輯詞｜實質差異（疑為版本落差或台灣自定）｜b.2 連接詞：having all of the following（全部） vs 具有任何下列特性（任一）**

- EAR `ccl/5A001.txt:63` …「 the 1.5 MHz to 87.5 MHz band and having all of the following:」
- 台灣 `twl/5A001.txt:22`（印刷頁 186） 「2. 操作於1.5 MHz至87.5 MHz頻帶之無線電設備，具有任何下列特」
- 說明：台灣同項 a 款結尾為「及」，字面與「任何」並存；是否為誤譯無法由文本判定。

**[5A001-38] 比較詞｜無法判定｜d.1–d.4 相控陣列天線頻率：above 31.8/57/66/90 GHz vs 31.8/57/66/90 GHz 以上**

- EAR `ccl/5A001.txt:117` 「d.1. Rated for operation above 31.8 GHz, but not exceeding 57 GHz, and ha」…
- EAR `ccl/5A001.txt:123` 「d.4. Rated for operation above 90 GHz;」
- 台灣 `twl/5A001.txt:106`（印刷頁 187） 「   1. 額定操作頻率在31.8 GHz以上，但未超過57 GHz，及其有效輻」
- 台灣 `twl/5A001.txt:118`（印刷頁 187） 「   4. 額定操作頻率在90 GHz以上；」
- 說明：同 3A001 b.5 邊界用語問題。

**[5A001-39] 比較詞｜無法判定｜e 測向設備頻率：above 30 MHz vs 30 MHz 頻率以上**

- EAR `ccl/5A001.txt:137` …「quipment operating at frequencies above 30 MHz and having all of the following, 」…
- 台灣 `twl/5A001.txt:138`（印刷頁 188） 「e. 在30 MHz頻率以上操作之無線電定向設備，且具下列所有特性，」
- 說明：同上。

**[5A001-40] 比較詞｜無法判定｜b.6 語音編碼速率：less than 700 bit/s vs 700 bit/s 以下**

- EAR `ccl/5A001.txt:103` …「'voice coding' output at rates of less than 700 bit/s.」
- 台灣 `twl/5A001.txt:81`（印刷頁 187） 「      bit/s以下者。」
- 說明：同上。

**[5A001-41] 骨架｜實質差異（疑為版本落差或台灣自定）｜a 項註解 2（衛星用設備除外）只在台灣**

- EAR `ccl/5A001.txt:49` 「Note: 5A001.a.3 and 5A001.a.4 apply only to electronic equipment.」
- 台灣 `twl/5A001.txt:11`（印刷頁 185） …「2：5A001.a.2.、5A001.a.3.及5A001.a.4.不管制設計或改裝用」
- 說明：此列 EAR 側引的是 a 項唯一的註解，以示位置；EAR 該項下無衛星用設備除外之註解。

**[5A001-42] 數值｜翻譯／編排差異｜技術註解 c 絕對溫度單位：台灣寫小寫 k（293 k），EAR 為 K**

- EAR `ccl/5A001.txt:113` …「 ambient temperature is a nominal 293 K (20 °C) and relative humidity 40%. Equiva」…
- 台灣 `twl/5A001.txt:101`（印刷頁 187） 「   293 k (20 °C)，相對濕度為40 %。可使用等效國家標準於此驗證測」

**[5A001-43] 骨架｜翻譯／編排差異｜N.B. 參照對象不同：EAR 指向 5A980 與 USML；台灣僅『參閱軍用貨品管制』**

- EAR `ccl/5A001.txt:167` …「previously specified by 5A001.i), see also 5A980 and the U.S. Munitions List (22 C」…
- 台灣 `twl/5A001.txt:177`（印刷頁 188） 「   說明1：參閱軍用貨品管制。」


### 3D001

**[3D001-44] 引用｜實質差異（疑為版本落差或台灣自定）｜標題範圍：EAR 納入 3A090 並排除 3B903、3B904 等；台灣僅『3A001.b.至3A002.h.或3B 所述』，無除外亦無 3A090**

- EAR `ccl/3D001.txt:3` …「controlled by 3A001.b to 3A002.h, 3A090, or 3B (except 3B001.a.4, c, d, f.1, f.5, k to n, p.2, p.4」…
- 台灣 `twl/3D001.txt:3`（印刷頁 170） 「3D001 為〝開發〞或〝生產〞3A001.b.至3A002.h.或3B 所述之設備而特別設」
- 說明：台灣 3B 含其自有 3B903、3B904，故 3D001 與台灣 3D901 在字面上重疊；台灣是否另有解釋無法判定。


### 3E001

**[3E001-45] 引用｜實質差異（疑為版本落差或台灣自定）｜標題範圍：EAR 排除 3A901、3A904、3B903、3B904、3C907–3C909 等；台灣『3A、3B 或3C』無除外**

- EAR `ccl/3E001.txt:3` …「s controlled by 3A (except 3A069, 3A901, 3A904, 3A980, 3A981, 3A991, 3A992, or 3」…
- 台灣 `twl/3E001.txt:3`（印刷頁 171） 「3E001 依照一般技術註解，〝技術〞係指〝開發〞或〝生產〞3A、3B 或3C」

**[3E001-46] 引用｜實質差異（疑為版本落差或台灣自定）｜註解 2 範圍：EAR『3A001.a.3 to a.14 or z』vs 台灣『3A001.a.3.至3A001.a.12.』**

- EAR `ccl/3E001.txt:55` …「integrated circuits controlled by 3A001.a.3 to a.14 or z, having all of the following:」
- 台灣 `twl/3E001.txt:9`（印刷頁 172） 「          註解2：3E001不管制3A001.a.3.至3A001.a.12.所述且具有下列所有特」

**[3E001-47] 骨架｜實質差異（疑為版本落差或台灣自定）｜PDK 排除：EAR 在 Cat 3 E 組開頭註記（適用 3E001 與 3E905）；台灣作 3E001 註解 3（僅 3E001）**

- EAR `ccl/_notes-cat3-E.txt:5` 「Note 1 to Cat 3 Product Group E: 3E001 and 3E905 do not apply to 'Process Design Kits' ('PDKs') unless they include libr」…
- 台灣 `twl/3E001.txt:16`（印刷頁 172） 「          註解3：3E001不管制‵製程設計套件′(‵PDKs′) 除非其包括可實現3A001」


### 3E002

**[3E002-48] 引用｜實質差異（疑為版本落差或台灣自定）｜註解 1 範圍：EAR『3E002』整項 vs 台灣『3E002.c.』**

- EAR `ccl/3E002.txt:37` 「Note 1: 3E002 does not control “technology” for multimedia extensions.」
- 台灣 `twl/3E002.txt:30`（印刷頁 172） 「           註解1：3E002.c.不管制多媒體延伸之〝技術〞。」

**[3E002-49] 比較詞｜無法判定｜a 項計算數：more than two vs 2個以上**

- EAR `ccl/3E002.txt:29` …「ocessor unit' designed to perform more than two calculations on 'floating-point' vectors (one-」…
- 台灣 `twl/3E002.txt:8`（印刷頁 172） 「            a. 設計用於同時執行2個以上‵浮點′向量(32位元或以上之一維陣列)計」
- 說明：同 3A001 b.5 邊界用語問題。

**[3E002-50] 骨架｜翻譯／編排差異｜註解 1–3 位置：EAR 緊接 c 項；台灣置於技術註解 2 之後（內容對應）**

- EAR `ccl/3E002.txt:37` 「Note 1: 3E002 does not control “technology” for multimedia exten」…
- 台灣 `twl/3E002.txt:30`（印刷頁 172） 「           註解1：3E002.c.不管制多媒體延伸之〝技術〞。」


### 5A002

**[5A002-51] 骨架｜實質差異（疑為版本落差或台灣自定）｜註解 2.b（銀行用密碼設備）：EAR 有實質內容，台灣為『刪除』；台灣改列於技術註解 1.h**

- EAR `ccl/5A002.txt:145` …「pecially designed and limited for banking use or 'money transactions';」
- 台灣 `twl/5A002.txt:123`（印刷頁 200） 「b. 刪除；」
- 台灣 `twl/5A002.txt:41`（印刷頁 198） 「   h. 專為銀行使用或貨幣交易（包括票價或信用卡功能的收集和」

**[5A002-52] 骨架｜實質差異（疑為版本落差或台灣自定）｜註解 2.f（僅無線個人區域網路功能）：EAR 有實質內容，台灣為『刪除』；台灣改列於技術註解 1.g**

- EAR `ccl/5A002.txt:155` …「rity” functionality is limited to wireless “personal area network ” functionality implementing only published or co」…
- 台灣 `twl/5A002.txt:147`（印刷頁 200） 「f. 刪除；」
- 台灣 `twl/5A002.txt:37`（印刷頁 198） 「   g. 僅實施已發布或商業加密標準的無線〝個人區域網路〞功」

**[5A002-53] 數值｜實質差異（疑為版本落差或台灣自定）｜註解 2.g 同時使用者數：16 → 32**

- EAR `ccl/5A002.txt:157` …「 (20 dBm) or less, and supporting 16 or fewer concurrent users;」
- 台灣 `twl/5A002.txt:152`（印刷頁 200） 「 32戶或以下之同時上線用戶；」

**[5A002-54] 骨架｜實質差異（疑為版本落差或台灣自定）｜註解 2.e 內容不同：台灣另增兩項條件（1.符合加密註解；2.『所述安全演算法』不受客製化影響且僅實施已發布或商業密碼標準）；EAR 有『anti-piracy functions』例外，台灣無**

- EAR `ccl/5A002.txt:153` …「mmercial cryptographic standards (except for anti-piracy functions, which may be non-published) and 」…
- 台灣 `twl/5A002.txt:140`（印刷頁 200） 「  1.非客製化的設備符合加密註解（第5類 – 第2部分中」
- 台灣 `twl/5A002.txt:143`（印刷頁 200） 「  2.非客製化設備的「資料保密加密」具有「所述安全」

**[5A002-55] 骨架｜實質差異（疑為版本落差或台灣自定）｜技術註解 1（‵資料機密性密碼學′之排除功能）：EAR 為 a–g；台灣為 a–j（增 g 無線個人區域網路、h 銀行用、j 未啟動功能；EAR g 密鑰管理對應台灣 i，範圍由 a–f 擴為 a–h）**

- EAR `ccl/5A002.txt:83` 「1.g. Key management in support of any function described in paragraphs 1.a to 1.f of this Technical Note paragraph 」…
- 台灣 `twl/5A002.txt:44`（印刷頁 198） 「   i. 支援且限於上述a至h段所述功能和能力的密鑰管理；或」
- 台灣 `twl/5A002.txt:45`（印刷頁 198） 「   j. 未啟動或啟用的加密功能或能力，且僅能透過安全的〝加密」

**[5A002-56] 骨架｜無法判定｜a 項前言：EAR 內含『usable, has been activated, or can be activated by any means other than secure “cryptographic activation”』；台灣前言無此語（疑移至技術註解 1.j），法律效果是否相同無法判定**

- EAR `ccl/5A002.txt:51` …「is usable, has been activated, or can be activated by any means other than secure “cryptographic activation”, as fo」…
- 台灣 `twl/5A002.txt:7`（印刷頁 197） 「            a. 設計或修改用於具‵描述安全演算法′之‵資料機密性密碼學′，如」

**[5A002-57] 骨架｜實質差異（疑為版本落差或台灣自定）｜EAR 自設 z 項（引用 3A090/4A090），台灣無**

- EAR `ccl/5A002.txt:217` 「z. Other commodities, as follows:」
- EAR `ccl/5A002.txt:219` …「eed the performance parameters in 3A090.a or 4A090.a;」
- （此側無對應段落）台灣 twl/5A002.txt 全檔不含「3A090」（程式斷言）。

**[5A002-58] 引用｜翻譯／編排差異｜技術註解引用號：EAR 對 readers/writers 寫 Note 2.a.2；台灣寫 a.1.b.2.（定義內容相同）**

- EAR `ccl/5A002.txt:143` …「2 of Note 2: 'For the purposes of 5A002.a Note 2.a.2, 'readers/writers' include equipm」…
- 台灣 `twl/5A002.txt:118`（印刷頁 199） 「              就5A002.a. 註解2 a.1.b.2.目的，‵讀卡機/寫入機′包」


### _notes-cat5p2

**[_notes-cat5p2-59] 比較詞｜實質差異（疑為版本落差或台灣自定）｜註解 2：EAR 為『適用許可例外 TMP/BAG』；台灣為『第5類第2部分不管制作為使用者私人用途之產品』（法律效果不同）**

- EAR `ccl/_notes-cat5p2.txt:7` …「ersonal use or as tools of trade, are eligible for License Exceptions TMP or BAG, subject to the terms and conditi」…
- 台灣 `twl/_notes-cat5p2.txt:8`（印刷頁 196） 「註解2：第5類第2部分不管制作為使用者私人用途之產品。」

**[_notes-cat5p2-60] 引用｜實質差異（疑為版本落差或台灣自定）｜註解 3 開頭：EAR 另含 5D002.z.1、z.5、z.6；台灣僅 5A002、5D002.a.1.、.b.、.c.1.**

- EAR `ccl/_notes-cat5p2.txt:9` …「ECCNs 5A002, 5D002.a.1, .b, .c.1, z.1, z.5, and z.6, do not control items as follows:」
- 台灣 `twl/_notes-cat5p2.txt:11`（印刷頁 196） …「002、5D002.a.1.、5D002.b.、5D002.c.1.不管制下列項目：」

**[_notes-cat5p2-61] 數值｜實質差異（疑為版本落差或台灣自定）｜註解 3 之 N.B.（美國自行分類／分類申請門檻：對稱 64 bits、非對稱 768 bits、橢圓曲線 128 bits）只在 EAR**

- EAR `ccl/_notes-cat5p2.txt:51` …「raphy Note employing a key length greater than 64 bits for the symmetric algorithm (or, 」…
- EAR `ccl/_notes-cat5p2.txt:51` …「lgorithms, employing a key length greater than 768 bits for asymmetric algorithms describ」…
- EAR `ccl/_notes-cat5p2.txt:51` …「 Technical note 2.b to 5A002.a or greater than 128 bits for elliptic curve algorithms, or」…
- （此側無對應段落）台灣 twl/_notes-cat5p2.txt 全檔不含『64』『768』『128』（程式斷言）。

**[_notes-cat5p2-62] 骨架｜翻譯／編排差異｜註解 1：EAR [Reserved] vs 台灣 刪除；註解 3.a.4 主管機關用語：exporter's country vs 會員國**

- EAR `ccl/_notes-cat5p2.txt:5` 「Note 1: [Reserved]」
- EAR `ccl/_notes-cat5p2.txt:27` …「 the appropriate authority in the exporter's country in order to ascertain compliance 」…
- 台灣 `twl/_notes-cat5p2.txt:7`（印刷頁 196） 「註解1：刪除。」
- 台灣 `twl/_notes-cat5p2.txt:25`（印刷頁 196） 「           4. 必要時，可應會員國主管機關之要求，出口商應提供貨物」


### 5B001

**[5B001-63] 骨架｜翻譯／編排差異｜台灣多列 b.5『刪除』；EAR 到 b.4 為止**

- EAR `ccl/5B001.txt:61` 「b.4. Radio equipment employing Quadrature-Amplitude-Modulation (QAM) techniques above level 1,02」…
- 台灣 `twl/5B001.txt:19`（印刷頁 190） 「               5. 刪除。」


### 5D001

**[5D001-64] 骨架｜翻譯／編排差異｜技術註解位置：EAR 在 e.1 之後；台灣在 e.2 之後（定義文字相同）**

- EAR `ccl/5D001.txt:71` 「1. For the purposes of 5D001.e, a 'handover interface' is a physical and logical interface, designed for use by an authorise」…
- 台灣 `twl/5D001.txt:26`（印刷頁 191） 「                 1. 5D001.e.所述之‵切換介面′為實體與邏輯介面，設計為授權執」


### 5D002

**[5D002-65] 骨架｜實質差異（疑為版本落差或台灣自定）｜EAR 另有 d [Reserved]、N.B.、e–y 保留與 z 項（引用 3A090/4A090、3D001/4D001）；台灣無**

- EAR `ccl/5D002.txt:75` 「d. [Reserved]」
- EAR `ccl/5D002.txt:81` 「z. Other software, as follows:」
- EAR `ccl/5D002.txt:83` …「eed the performance parameters in 3D001 for 3A090.a or 4D001 for 4A090.a;」
- （此側無對應段落）台灣 twl/5D002.txt 全檔不含「3A090」（程式斷言）。

**[5D002-66] 引用｜翻譯／編排差異｜c.1 引用寫法：EAR『5A002.a, .c, .d or .e』vs 台灣『5A002.a.、5A002.c.、5A002.d.或5A002.e.』（內容相同）**

- EAR `ccl/5D002.txt:61` 「c.1. Equipment specified by 5A002.a, .c, .d or .e;」
- 台灣 `twl/5D002.txt:15`（印刷頁 204） 「               1. 5A002.a.、5A002.c.、5A002.d.或5A002.e.管制之設備；」


### 5A004

**[5A004-67] 骨架｜實質差異（疑為版本落差或台灣自定）｜EAR 另有 c–y 保留與 z 項（引用 3A090/4A090）；台灣無**

- EAR `ccl/5A004.txt:77` 「c. through y. [Reserved]」
- EAR `ccl/5A004.txt:81` …「eed the performance parameters in 3A090.a or 4A090.a;」
- （此側無對應段落）台灣 twl/5A004.txt 全檔不含「3A090」（程式斷言）。


### 5B002

**[5B002-68] 引用｜實質差異（疑為版本落差或台灣自定）｜b 款軟體引用：EAR『5D002.a, z.1 through z.4, or 5D002.c or z.6 through z.9』；台灣僅『5D002.a.或 5D002.c.』**

- EAR `ccl/5B002.txt:33` …「4, or of “software” controlled by 5D002.a, z.1 through z.4, or 5D002.c or z.6 through z.9.」
- 台灣 `twl/5B002.txt:7`（印刷頁 203） 「               述之設備，或5D002.a.或 5D002.c.所述之〝軟體〞其〝資訊安全〞」


### 5E002

**[5E002-69] 引用｜實質差異（疑為版本落差或台灣自定）｜a 款引用 EAR 含 z 項：『5D002.a, z.1 through z.3, or 5D002.c, z.6 through z.8』；台灣無 z**

- EAR `ccl/5E002.txt:45` …「“software” controlled by 5D002.a, z.1 through z.3, or 5D002.c, z.6 through z.8.」
- 台灣 `twl/5E002.txt:6`（印刷頁 204） …「或 5B002 所 述 而 設 計 或 修 改 之 設 備 ， 或 5D002.a.」


### 7A005

**[7A005-70] 骨架｜翻譯／編排差異｜台灣以『說明』列參照 7A105 與軍用貨品管制；EAR 放在 Related Controls（Items 以外）**

- EAR `ccl/7A005.txt:25` 「Related Controls: (1) See also ECCNs 7A105, 7A611 and 7A994. Commercially available “satellit」…
- 台灣 `twl/7A005.txt:6`（印刷頁 257） 「           說明：參照7A105。」
- 台灣 `twl/7A005.txt:8`（印刷頁 257） 「           說明：專為軍事用途設計之設備，參見軍用貨品管制。」


### 7A105

**[7A105-71] 骨架｜無法判定｜a 款：EAR『missiles』（EAR 定義語，定義在 Part 772，證據包未收）vs 台灣列舉 9A004 太空發射載具、9A104 探空火箭、9A012/9A112.a 無人飛行載具；範圍是否相同無法判定**

- EAR `ccl/7A105.txt:27` 「Items: a. Designed or modified for use in “missiles”; or」
- 台灣 `twl/7A105.txt:6`（印刷頁 260） 「            a. 設計或修改為用於9A004所述之太空發射載具、9A104所述之探空」

**[7A105-72] 引用｜實質差異（疑為版本落差或台灣自定）｜標題：台灣加『除7A005所述外』；EAR 無此除外語**

- EAR `ccl/7A105.txt:3` 「7A105 Receiving equipment for 'navigation satellite systems', having any of the following char」…
- 台灣 `twl/7A105.txt:3`（印刷頁 260） 「7A105 除7A005所述外之‵衛星導航系統′接收設備，具下列任一特性，及特別」

**[7A105-73] 骨架｜翻譯／編排差異｜『衛星導航系統』定義：EAR 放 Related Definitions；台灣放註解 2（內容相同）**

- EAR `ccl/7A105.txt:25` 「Related Definitions: 'Navigation satellite systems' include Global Navigation Satellite Syste」…
- 台灣 `twl/7A105.txt:25`（印刷頁 260） 「              2. 7A105中之‵衛星導航系統′包括全球衛星導航系統(GNSS，例如」


### 7E001

**[7E001-74] 引用｜實質差異（疑為版本落差或台灣自定）｜台灣納入 7D101 至 7D103；EAR 僅 7A、7B、7D001–7D003、7D005（並除外自有 7A994、7B994）**

- EAR `ccl/7E001.txt:3` …「pment or “software,” specified by 7A. (except 7A994), 7B. (except 7B994), 7D001, 7D002, 7D003 or 7D005.」
- 台灣 `twl/7E001.txt:4`（印刷頁 264） 「          7D005與7D101至7D103所述設備或〝軟體〞之〝技術〞。」


### 3E905

**[3E905-75] 骨架｜實質差異（疑為版本落差或台灣自定）｜EAR 有註解 1（含 'process recipes'）、註解 2（不適用於 tool qualification 或 maintenance）、技術註解；台灣 3E905 無**

- EAR `ccl/3E905.txt:37` 「Note 1: 3E905 includes 'process recipes'.」
- EAR `ccl/3E905.txt:39` 「Note 2: 3E905. does not apply for tool qualification or maintenance.」
- EAR `ccl/3E905.txt:41` …「he purposes of Note 1 to 3E905, a 'process recipe' is a set of conditions and parameters for a particular p」…
- （此側無對應段落）台灣 twl/3E905.txt 沒有註解 1、註解 2 與技術註解（程式斷言：全檔無『註解1』『註解2』『技術註解：』『製程配方』；僅標題行有『一般技術註解』一詞）。


### 2B910

**[2B910-76] 引用｜翻譯／編排差異｜d 款少了對 c 款的引用：EAR『specified in 2B910.c』；台灣無（內容對應）**

- EAR `ccl/2B910.txt:59` …「'in-process monitoring' equipment specified in 2B910.c.」
- 台灣 `twl/2B910.txt:21`（印刷頁 123） 「            d.封閉迴路控制系統，設計用於‵製程監測′設備的回應，在製造過程」

## 4. 機器比對統計（含已讀與未細讀）

欄位：EAR 區塊／台灣區塊／對上（含置換）／只在EAR／只在台灣／佔位不一致／數值或單位旗標／比較詞旗標／引用旗標。

| 號碼 | EAR | 台灣 | 對上 | 只EAR | 只台灣 | 佔位 | 數值 | 比較詞 | 引用 |
|---|---|---|---|---|---|---|---|---|---|
| 3A001 | 316 | 306 | 299 | 17 | 7 | 2 | 28 | 12 | 5 |
| 3A002 | 92 | 94 | 89 | 3 | 5 | 2 | 18 | 8 | 1 |
| 3D001 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| 3E001 | 5 | 7 | 5 | 0 | 2 | 0 | 0 | 0 | 2 |
| 3E002 | 12 | 13 | 12 | 0 | 1 | 0 | 1 | 1 | 1 |
| 3E003 | 10 | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5A001 | 91 | 90 | 88 | 3 | 2 | 0 | 5 | 9 | 1 |
| 5B001 | 13 | 14 | 13 | 0 | 1 | 0 | 0 | 0 | 0 |
| 5D001 | 24 | 24 | 21 | 3 | 3 | 0 | 0 | 0 | 0 |
| 5E001 | 49 | 49 | 49 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5A002 | 97 | 90 | 84 | 13 | 6 | 2 | 4 | 0 | 8 |
| 5A003 | 4 | 4 | 4 | 0 | 0 | 0 | 1 | 0 | 0 |
| 5A004 | 20 | 14 | 14 | 6 | 0 | 0 | 0 | 0 | 0 |
| 5B002 | 3 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5D002 | 38 | 16 | 16 | 22 | 0 | 0 | 0 | 0 | 1 |
| 5E002 | 5 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| 7A005 | 5 | 7 | 5 | 0 | 2 | 0 | 0 | 0 | 0 |
| 7A105 | 7 | 9 | 7 | 0 | 2 | 0 | 0 | 0 | 3 |
| 7D005 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 7E001 | 2 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 1 |
| 2B910 | 18 | 18 | 18 | 0 | 0 | 0 | 2 | 0 | 1 |
| 2D910 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2E903 | 4 | 4 | 4 | 0 | 0 | 0 | 1 | 0 | 0 |
| 2E910 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3A901 | 9 | 9 | 9 | 0 | 0 | 0 | 0 | 3 | 0 |
| 3A904 | 3 | 3 | 3 | 0 | 0 | 0 | 1 | 2 | 0 |
| 3B903 | 10 | 10 | 10 | 0 | 0 | 0 | 1 | 1 | 0 |
| 3B904 | 3 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3C907 | 3 | 3 | 3 | 0 | 0 | 0 | 0 | 2 | 0 |
| 3C908 | 3 | 3 | 3 | 0 | 0 | 0 | 0 | 2 | 0 |
| 3C909 | 5 | 5 | 5 | 0 | 0 | 0 | 0 | 2 | 0 |
| 3D901 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3D907 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3E901 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3E905 | 4 | 1 | 1 | 3 | 0 | 0 | 0 | 0 | 0 |
| 4A906 | 23 | 23 | 23 | 0 | 0 | 0 | 3 | 0 | 0 |
| 4D906 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 4E906 | 3 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |

## 5. 無差異的號碼（逐段讀過兩邊全文）

3E003、5A003、5B002（除 z 引用）、5E002（除 z 引用）、7D005 在子項骨架與數值上兩邊一致；台灣 900–999 單邊碼中 2D910、2E903、2E910、3A901、3A904、3B903、3B904、3C907、3C908、3C909、3D901、3D907、3E901、4D906、4E906 兩邊文字（含數值）一致（台灣條文與 EAR 逐句對應），4A906 僅核對各級量子位元門檻與 C-NOT 錯誤值（兩邊一致），技術註解未逐字讀完；差異僅列於第 3 節的 2B910（引用）與 3E905（EAR 多註解）。

## 6. 已知限制

- pdftotext 版面斷行：台灣條文跨行、跨頁，部分字距被拉開（如『5 個 以 上』），子項標號在換頁處可能脫落（如 5A001.b.3.b 註解之『a』無句點）；子項層級是由編號序列推斷，不是版面縮排。
- 中英文編號對齊有誤差：EAR 為完整路徑（a.1.b.），台灣為相對編號；註解的父項依『上一個標籤』決定，兩邊註解位置不同時以『置換配對』處理，仍可能漏配。
- 以 EAR 區塊鍵當歧義參考，會讓台灣結構傾向貼近 EAR；台灣獨有結構仍會被標為『只在台灣』，但判定時以人工讀原文為準。
- 數值抽取不含中文數字（一、二…）與部分英文數詞；比較詞偵測只是旗標，已人工逐一看過旗標項，但未旗標處不保證完全一致。
- EAR 側只比 `Items` 之後與標題行；License Requirements、License Exceptions 等美國獨有欄位不在比對範圍。
- 『判為版本落差』只是依文本差異的推測；證據包沒有 Wassenaar 原文，無法確認哪邊較新。

## 7. 未完成／僅部分完成

- **未完成**：5E001（機器比對：骨架 49 對 49 全部對上、數值與比較詞無旗標，但未人工逐段複核語意）。
- **部分完成**：3A001（已判讀 b.7、b.11、b.5、a.2、a.5.a.4、i、e.1、e.3、a.9、z 及主要註記位置；830 行台灣條文未逐行人工讀完，其餘旗標屬措辭雜訊但未逐條列出）；3A002（數值與骨架旗標已判讀，台灣側全文未逐行讀完）；5A001（已判讀 b.2、b.6、c、d、e、a 註解、N.B.；f/h/j 次要註記未逐項列）。
- 台灣 9A901 在 EAR 無同號，未做內容比對（無對象）。
- 第 3 節外的次要『置換』與註記位置差異（如 3A001 b.4.f 各註解）僅整批列一筆。

