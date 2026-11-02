# 出口管制產品分類 自學站

把晶片、軟體與技術對應到美國《出口管理規則》（EAR）的 ECCN 與台灣「軍商兩用貨品及技術出口管制清單」管制號碼的自學筆記。
網站：<https://cecefat.github.io/eccn-ptc-study/>

## 內容

| 頁面 | 內容 |
|---|---|
| `start.html` 入門 | 給全新手：七個問題、十二個概念、怎麼讀 ECCN、三個問題、給專利人的對照 |
| `index.html` 總覽 | 先記住的結論、常見說法查核、閱讀路線 |
| `method.html` 分類方法 | 是否受 EAR 管、管轄、Supp. 4 審查順序、specially designed、分類決定書範本 |
| `cat5p2.html` 加密 5P2 | 5A002.a 結構、除外註記、密碼學註解、5A992.c、§740.17 申報路徑、台灣 115 年版差異 |
| `cat3.html` 半導體 Cat 3 | 群組註解、3A001、3A991、3A090 與晶圓廠推定、3E002、最終用途 |
| `taiwan.html` 台灣制度 | 貿易法與管理辦法、管制地區、清單結構、ECCN 對照表、逐碼比對 |
| `offshore.html` 海外生產 | 四節點配對：台灣出貨、工廠所在國、目的地進口、交易對象；EAR 跟著物品走 |
| `cn-us.html` 中國 → 美國 | 中國出口管制法、條例與清單、專項措施；美國原產地、強迫勞動、FCC、聯網車；兩邊衝突 |
| `sea.html` 東南亞 → 美國／歐盟 | 新加坡、馬來西亞、泰國、越南、菲律賓的戰略物資管制；歐盟強迫勞動與產品法規 |
| `cases.html` 產品演練 | 五個假設規格的產品原型逐步分類 |
| `tech.html` 技術與視同出口 | 技術定義、視同出口與再出口、不受 EAR 管的資訊、de minimis 與 FDP、執法案例 |
| `evidence.html` 方法與證據 | 證據包、工具、官方材料品質警語、來源總表 |
| `quiz.html` 自我檢測 | 12 題 |

## 證據包

見 [`evidence/README.md`](evidence/README.md)。重建與查核：

```
python -I evidence/tools/fetch_sources.py . <manifest.json>
python -I evidence/tools/parse_ecfr.py .
python -I evidence/tools/parse_docs.py .
python -I evidence/tools/parse_tw_list.py .
python -I evidence/tools/verify_quotes.py .
```

## 聲明

個人自學整理，不是法律意見；產品案例為假設規格的演練，不對應任何特定產品。
法規版本：EAR 取自 eCFR 版本日 2026-10-29；台灣清單為 115-02-11 經貿字第11550200140號公告附件。
美國聯邦政府著作屬公共領域；我國法令與公文依著作權法第 9 條不得為著作權之標的。
