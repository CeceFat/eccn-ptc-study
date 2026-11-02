# 證據包

網站上每一段原文引文都來自這裡，並由 `tools/verify_quotes.py` 逐字核對。

## 結構

```
evidence/
  registry.json        每份來源的網址、發布者、抓取日、大小、SHA-256
  sources/             下載的原檔（不修改）
    us-ear/            15 CFR Parts 730–774（eCFR versioner API，版本日 2026-10-29）
    us-fr/             Federal Register 規則全文（GPO 文字版）
    us-bis/            BIS 指引頁與 PDF
    us-doj/            司法部新聞稿
    tw-law/            全國法規資料庫、經濟部主管法規系統
    tw-trade/          經濟部國際貿易署公告附件與說明頁
  text/                轉出的純文字，網頁引文比對的對象
    ear/               EAR 每一條、每個 Supplement 一檔
    ccl/               CCL 每個 ECCN 一檔，類別與群組註解另存 _notes-*.txt
    itar/              22 CFR 120、121
    fr/ bis/ doj/ tw/  其他來源
    twl/               台灣清單每個管制號碼一檔
  analysis/            台灣清單與 EAR 的逐碼比對報告
  tools/               下載、解析、查核工具
```

每個文字檔第一行是座標標頭，例如 `〔15 CFR Part 774, Supp. No. 1, ECCN 5A002；eCFR 2026-10-29〕`。

## 文字處理

只做兩件事，行號都不變：

1. 刪除 GPO 全文夾帶的 NUL 等控制字元（分頁殘留）。
2. 把中文 PDF 抽字產生的 CJK 相容表意字（U+F900–FAFF）換回標準字。

原檔保持下載時的樣子，可用 `registry.json` 的 SHA-256 核對。

## 未收錄

瓦聖那協議與歐盟清單原文、BIS 個案分類與諮詢意見、付費資料庫、產業標準文件。
貿易署的兩份簡報與一份手冊只存本機（`local-only/`，不進版控、不重新散布）。
