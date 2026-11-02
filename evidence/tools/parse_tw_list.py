"""把台灣「軍商兩用貨品及技術出口管制清單及一般軍用貨品清單」（115-02-11 公告附件）切成逐號純文字檔。

用法：python -I evidence/tools/parse_tw_list.py <repo_root>
輸入：evidence/text/tw/dual-use-and-military-lists-1150211.txt（pdftotext -layout；頁間為換頁字元 \\f，頁尾單獨一行印刷頁碼）
      data/ccl_index.json（只供第二階段 eccn_tw_map.json 使用）
輸出：
  evidence/text/twl/<CODE>.txt                     每個管制號碼一檔，例如 3A001.txt、5A002.txt（目錄列為「刪除」者如 4D002 亦成檔）
  evidence/text/twl/_notes-cat<N>[p<k>].txt        類別（第5類分部分）標題起至第一個管制號碼前的註解，例如 _notes-cat3.txt、_notes-cat5p2.txt
  evidence/text/twl/_notes-cat<N>[p<k>]-<G>.txt    第一組以外、某組（A–E）開頭的註解，例如 _notes-cat4-D.txt
  evidence/text/twl/_appendix-cat2-deposition.txt  第2類末附表（沉積技術）；_appendix-cat4-app.txt 為第4類末 APP 技術註解
  evidence/text/twl/_numbering.txt（管制號碼說明）、_general-notes.txt、_abbreviations.txt、_definitions.txt、_glossary-en-zh.txt
  evidence/text/twl/ML<n>.txt、_military-list-preface.txt、_definitions-ml.txt（一般軍用貨品清單）
  data/tw_index.json                               管制號碼索引（不含 ML）
  data/eccn_tw_map.json                            依 data/ccl_index.json 標示每個 ECCN 台灣是否有同號與 EAR 號碼型態
每檔第一行是座標標頭；其後原文只做兩件事：去掉頁尾印刷頁碼行、去掉換頁字元，其餘（換行、空白、全形標點）不改。
切法：先以目錄（含頁碼）建立應有的號碼序列，再在正文逐類依序找標題行；正文有、目錄無的號碼另行標記。
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

DOC = "軍商兩用貨品及技術出口管制清單（115-02-11 公告附件）"
SRC_REL = os.path.join("evidence", "text", "tw", "dual-use-and-military-lists-1150211.txt")
DOTS = r"[.．…·]{2,}"
FOOT_RE = re.compile(r"^\s*(\d{1,3})\s*$")
HEAD_RE = re.compile(r"^\s*(?P<pre>[A-Za-z]?)(?P<code>\d[A-E]\d{3})(?=\s|$)(?P<rest>.*)$")
GROUP_RE = re.compile(r"^(?P<cat>\d)(?P<grp>[A-E])(?P<part>[12]?)\s+(?:系統|測試|材料|軟體|技術)")
ML_RE = re.compile(r"^\s*ML(?P<n>\d{1,2})(?![\d.])(?P<rest>.*)$")
SUBITEM_RE = re.compile(r"^(?:[a-z]|\d{1,2})\.")
CONT = tuple("、，,.．。；;：:）)和或及至與")  # 標題行之後若緊接這些字元，視為上一段換行後的交叉引用，不是標題
CAT_NAMES = "0123456789"


class Doc:
    """原文逐行載入：行號以 1 起算（= lines[n-1]），與編輯器／grep 一致；換頁字元不當作換行。"""

    def __init__(self, path):
        raw = open(path, encoding="utf-8", newline="").read()
        lines = raw.replace("\r\n", "\n").split("\n")
        if lines and lines[-1].replace("\f", "").strip() == "":
            lines.pop()  # 最後一個換頁字元後面的空行
        self.lines = lines
        self.pdf = []  # 每行所屬 PDF 頁（換頁字元位於新頁第一行行首）
        pg = 1
        for i, ln in enumerate(lines):
            if i and "\f" in ln:
                pg += 1
            self.pdf.append(pg)
        self.n_pages = pg
        self.K = None
        self.footer = {}  # idx -> 印刷頁碼

    def clean(self, i):
        return self.lines[i].replace("\f", "")

    def find(self, text, a, b=None):
        """a..b 之間第一行去頭尾空白後恰等於 text 者。"""
        for i in range(a, b if b is not None else len(self.lines)):
            if self.clean(i).strip() == text:
                return i
        return None

    def mark_footers(self, body_idx):
        """正文第一頁印刷頁碼為 1；其後每頁恰有一行純數字 = PDF 頁 − K，視為頁尾頁碼。"""
        self.K = self.pdf[body_idx] - 1
        by_page = {}
        for i in range(len(self.lines)):
            by_page.setdefault(self.pdf[i], []).append(i)
        anomalies = []
        for p in range(self.pdf[body_idx], self.n_pages + 1):
            hit = [i for i in by_page[p] if FOOT_RE.match(self.clean(i)) and int(FOOT_RE.match(self.clean(i)).group(1)) == p - self.K]
            if len(hit) == 1:
                self.footer[hit[0]] = p - self.K
            else:
                anomalies.append((p, len(hit)))
        return anomalies

    def printed(self, i):
        return self.pdf[i] - self.K

    def kept(self, a, b):
        """a..b（不含 b）去掉頁尾頁碼行與換頁字元後，頭尾空白行修掉；回傳 [(idx, text)]。"""
        out = [(i, self.clean(i)) for i in range(a, b) if i not in self.footer]
        while out and not out[0][1].strip():
            out.pop(0)
        while out and not out[-1][1].strip():
            out.pop()
        return out


def page_span(doc, kept):
    p1, p2 = doc.printed(kept[0][0]), doc.printed(kept[-1][0])
    f1, f2 = doc.pdf[kept[0][0]], doc.pdf[kept[-1][0]]
    return (p1, p2, f1, f2)


def fmt_pages(p1, p2, f1, f2):
    pr = str(p1) if p1 == p2 else "%d–%d" % (p1, p2)
    pd = str(f1) if f1 == f2 else "%d–%d" % (f1, f2)
    return "印刷頁 %s（PDF 第 %s 頁）" % (pr, pd)


def write_seg(doc, outdir, fname, label, kept):
    p1, p2, f1, f2 = page_span(doc, kept)
    header = "〔%s｜%s｜%s〕" % (DOC, label, fmt_pages(p1, p2, f1, f2))
    with open(os.path.join(outdir, fname), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(header + "\n\n")
        fh.write("\n".join(t for _, t in kept) + "\n")
    return (p1, p2, f1, f2)


# ---------- 目錄 ----------
def parse_toc(doc, a, b):
    toc = {"codes": [], "cats": {}, "groups": [], "parts": {}, "ml": {}, "other": []}
    code_re = re.compile(r"^\s*(\d[A-E]\d{3})\s+(.*?)\s*(?:" + DOTS + r"\s*\.?\s*|\s+)(\d+)\s*$")
    cat_re = re.compile(r"^\s*第(\d)類\s*" + DOTS + r"\s*(\d+)\s*$")
    grp_re = re.compile(r"^\s*(\d)([A-E])([12]?)\s+(\S.*?)\s*" + DOTS + r"\s*(\d+)\s*$")
    part_re = re.compile(r"^\s*第([12])部分\s*" + DOTS + r"\s*(\d+)\s*$")
    ml_re = re.compile(r"^\s*ML(\d+)\s+(.+?)\s*" + DOTS + r"\s*(\d+)\s*$")
    oth_re = re.compile(r"^\s*(\S.*?)\s*" + DOTS + r"\s*(\d+|[A-L])\s*$")
    for i in range(a, b):
        s = doc.clean(i)
        if not s.strip():
            continue
        m = code_re.match(s)
        if m:
            toc["codes"].append({"code": m.group(1), "title_toc": m.group(2).strip(), "page_toc": int(m.group(3)), "toc_line": i + 1})
            continue
        m = cat_re.match(s)
        if m:
            toc["cats"][m.group(1)] = int(m.group(2))
            continue
        m = part_re.match(s)
        if m:
            toc["parts"][m.group(1)] = int(m.group(2))
            continue
        m = ml_re.match(s)
        if m:
            toc["ml"][int(m.group(1))] = {"title": m.group(2), "page": int(m.group(3))}
            continue
        m = grp_re.match(s)
        if m:
            toc["groups"].append({"label": m.group(1) + m.group(2) + m.group(3), "page": int(m.group(5))})
            continue
        m = oth_re.match(s)
        if m:
            toc["other"].append((m.group(1), m.group(2)))
    return toc


def code_key(code, part):
    return (part or 0, "ABCDE".index(code[1]), int(code[2:]))


def regime_of(code):
    t = int(code[2:])
    if t < 100:
        return "WA"
    if t < 200:
        return "MTCR"
    if t < 300:
        return "NSG"
    if t < 400:
        return "AG"
    if t < 500:
        return "CWC"
    if t >= 900:
        return "單邊"
    return "保留"


def join_text(a, b):
    if a and b and a[-1].isascii() and b[0].isascii() and a[-1].isalnum() and b[0].isalnum():
        return a + " " + b
    return a + b


def heading_title(kept, first_token):
    """條首標題：標題行去掉號碼後，接續換行到第一個「：」或「。」為止（遇子項 a./1.、註解、說明即停）。"""
    first = kept[0][1].strip()
    first = first[len(first_token):].strip()
    buf = first
    for _, t in kept[1:]:
        if re.search(r"[：。]", buf) or len(buf) >= 200:
            break
        s = t.strip()
        if not s:
            continue
        if SUBITEM_RE.match(s) or s.startswith(("註解", "技術註解", "說明", "N.B.")):
            break
        buf = join_text(buf, s)
    m = re.search(r"[：。]", buf)
    return buf[: m.end()] if m else buf


# ---------- 正文切分 ----------
def pick_headings(doc, a, b, cat, toc_codes, part_idx):
    """在 [a,b) 內依目錄順序挑各號的標題行，並找出目錄沒列的標題。回傳 [(idx, code, token, in_toc)]。"""
    cands = []
    for i in range(a, b):
        m = HEAD_RE.match(doc.clean(i))
        if m and m.group("code")[0] == cat:
            rest = m.group("rest").strip()
            ok = (rest == "" or not rest.startswith(CONT))
            cands.append((i, m.group("code"), m.group("pre"), ok))
    chosen = {}
    pos = a
    for code in toc_codes:
        for i, c, pre, ok in cands:
            if i >= pos and c == code and pre == "" and ok:
                chosen[code] = (i, code)
                pos = i + 1
                break
    # 找不到者：在前後已找到的號碼之間放寬（容許號碼前多一個字母，如 A2A225）
    order = [c for c in toc_codes]
    for k, code in enumerate(order):
        if code in chosen:
            continue
        lo = max([chosen[c][0] for c in order[:k] if c in chosen] or [a - 1]) + 1
        hi = min([chosen[c][0] for c in order[k + 1:] if c in chosen] or [b])
        for i, c, pre, ok in cands:
            if lo <= i < hi and c == code and ok:
                chosen[code] = (i, code)
                break
    used = {i for i, _ in chosen.values()}
    heads = [(i, c, True) for c, (i, _) in chosen.items()]
    # 目錄沒列的標題：位置介於兩個已找到的號碼之間，且號碼大小也介於兩者之間
    def part_of(i):
        return 2 if (part_idx is not None and i >= part_idx) else 1

    ordered = sorted(heads)
    for i, c, pre, ok in cands:
        if i in used or not ok or pre != "":
            continue
        prev = [h for h in ordered if h[0] < i]
        nxt = [h for h in ordered if h[0] > i]
        if not prev or not nxt:
            continue
        pk, nk = prev[-1], nxt[0]
        if code_key(pk[1], part_of(pk[0])) < code_key(c, part_of(i)) < code_key(nk[1], part_of(nk[0])):
            heads.append((i, c, False))
            ordered = sorted(heads)
            used.add(i)
    return sorted(heads)


def substantive(doc, a, b):
    """區間內除了類別／部分標題、組標題、「無內容」之外是否還有文字。"""
    kept = doc.kept(a, b)
    texts = [t.strip() for _, t in kept if t.strip()]
    rest = []
    skip_next = False
    for t in texts:
        if skip_next:
            skip_next = False
            continue
        if re.fullmatch(r"第\d類|第[12]部分", t):
            skip_next = True  # 其下一行是類別／部分名稱
            continue
        if GROUP_RE.match(t) or t == "無內容":
            continue
        rest.append(t)
    return bool(rest)


# ---------- 第二階段：ECCN ↔ 台灣同號對照 ----------
REASON_RE = re.compile(r"^Reasons?\s+for\s+Control\s*:?\s*(.*)$", re.I)


def ear_range(cat, t):
    """依 evidence/text/ear/738.2.txt 第 41–69 行（Table 1 與 (d)(1)(i)–(iv)）把 ECCN 末三碼分型。回傳 (區段標籤, 型態)。"""
    if t < 100:
        return "000-099 NS", "multilateral_range"
    if t < 200:
        return "100-199 MT", "multilateral_range"
    if t < 290:
        return "200-299 NP", "multilateral_range"
    if t < 300:
        return "200-299 NP（第二碼 2、第三碼 9，738.2 第 65 行）", "unilateral_NP_29x"
    if t < 400:
        return "300-399 CB", "multilateral_range"
    if t < 500:
        return "400-499（738.2 Table 1 無此列）", "multilateral_range"
    if t < 600:
        if cat == "9" and t == 515:
            return "500-599 Firearms, Spacecraft and related commodities", "series_9x515_spacecraft"
        if cat == "0" and t == 521:
            return "500-599 Firearms, Spacecraft and related commodities", "series_0Y521"
        return "500-599 Firearms, Spacecraft and related commodities", "series_5xx_other"
    if t < 700:
        return "600-699 WAML / former USML", "series_600"
    if t < 900:
        return "700-899（738.2 Table 1 無此列）", "not_in_table_1"
    if t < 980:
        return "900-979 Plurilateral NS and RS and other reasons", "plurilateral_900_979"
    if t < 990:
        return "980-989 CC, SS", "unilateral_980_989_CC_SS"
    return "990-999 AT, RS, UN（第二、三碼 99，738.2 第 65 行）", "unilateral_990_999_AT_RS_UN"


TABLE1_LETTER = [(0, 100, "NS"), (100, 200, "MT"), (200, 300, "NP"), (300, 400, "CB")]


def build_map(root, entries, outdir):
    cpath = os.path.join(root, "data", "ccl_index.json")
    if not os.path.exists(cpath):
        print("略過 eccn_tw_map.json：找不到 data/ccl_index.json")
        return
    ccl = json.load(open(cpath, encoding="utf-8"))
    ccl_dir = os.path.join(root, "evidence", "text", "ccl")
    tw = {e["code"]: e for e in entries}

    def make_row(eccn, fname, start):
        """fname 為該 ECCN 條文所在的 ccl 檔，start 為標題行（1 起算）；Reason for Control 取標題行之後第一個。"""
        t = int(eccn[2:])
        rng, base = ear_range(eccn[0], t)
        e = tw.get(eccn)
        status = "absent" if e is None else ("deleted" if e["deleted"] else "present")
        same = status == "present"
        kind = base
        if base == "multilateral_range":
            kind = "multilateral_tw_match" if same else "multilateral_no_tw_match"
        reason, rsrc = None, None
        lines = open(os.path.join(ccl_dir, fname), encoding="utf-8").read().split("\n")
        for n in range(start, len(lines) + 1):
            m = REASON_RE.match(lines[n - 1])
            if m:
                reason = m.group(1).strip() or None
                rsrc = "evidence/text/ccl/%s:%d" % (fname, n)
                break
        letter = next((L for lo, hi, L in TABLE1_LETTER if lo <= t < hi and base == "multilateral_range"), None)
        in_text = None
        if letter and reason is not None:
            in_text = bool(re.search(r"\b" + letter + r"\b", reason))
        return {
            "eccn": eccn,
            "tw_same_code": same,
            "ear_kind": kind,
            "tail_738_2": rng,
            "tw_status": status,
            "tw_regime": e["regime"] if e else None,
            "reason_for_control": reason,
            "reason_src": rsrc,
            "table1_reason_in_text": in_text,
        }

    rows = [make_row(c["eccn"], c["eccn"] + ".txt", 1) for c in ccl]
    ear_set = {c["eccn"] for c in ccl}
    # ccl_index.json 漏收的 ECCN：標題行沒被切檔器認出，內文落在 _notes-*.txt（例如 8D001）
    gaps = []
    gap_re = re.compile(r"^(\d[A-E]\d{3})\s")
    for fn in sorted(os.listdir(ccl_dir)):
        if fn.startswith("_notes-"):
            for n, ln in enumerate(open(os.path.join(ccl_dir, fn), encoding="utf-8").read().split("\n"), 1):
                m = gap_re.match(ln)
                if m and n > 1 and m.group(1) not in ear_set:
                    row = make_row(m.group(1), fn, n)
                    row["heading_src"] = "evidence/text/ccl/%s:%d" % (fn, n)
                    gaps.append(row)
    gap_set = {g["eccn"] for g in gaps}
    tw_only = [{"code": e["code"], "cat": e["cat"], "part": e["part"], "group": e["group"], "regime": e["regime"],
                "title_zh": e["title_zh"], "in_toc": e["in_toc"], "file": e["file"]}
               for e in entries if not e["deleted"] and e["code"] not in ear_set and e["code"] not in gap_set]
    numbering = open(os.path.join(outdir, "_numbering.txt"), encoding="utf-8").read().split("\n")
    hit = [n for n, ln in enumerate(numbering, 1) if re.match(r"^\s*\d{3}-\d{3}：", ln)]
    meta = {
        "ear_rule_source": "evidence/text/ear/738.2.txt 第 41 行（第 3–5 碼意義）、第 43–61 行（Table 1）、第 63–69 行（(i)–(iv)）；0Y521 見 evidence/text/ear/774-supp-5.txt 第 7 行",
        "tw_rule_source": "evidence/text/twl/_numbering.txt 第 %d–%d 行（末三碼 000-099 WA … 900-999 單邊管制）" % (hit[0], hit[-1]) if hit else None,
        "tw_same_code": "台灣清單有同號且該號不是「刪除」",
        "ear_kind": {
            "multilateral_tw_match": "末三碼落在 738.2 Table 1 的 000–399（NS/MT/NP/CB；29x 除外）且台灣有同號",
            "multilateral_no_tw_match": "同上但台灣無同號。『多邊』僅指號碼區段；該號是否真有多邊來源本表不判定，見 table1_reason_in_text 與 reason_for_control",
            "unilateral_NP_29x": "末三碼 290–299（738.2 第 65 行：第二碼 2、第三碼 9 為核擴散關切的單邊管制）",
            "series_5xx_other": "500–599（Firearms, Spacecraft…），不含 9x515、0x521",
            "series_9x515_spacecraft": "9A515/9B515/9D515/9E515（Spacecraft）",
            "series_0Y521": "0A521/0B521/0C521/0D521/0E521（774 增編 5 稱 0Y521 series）",
            "series_600": "600–699（WAML 或前 USML）",
            "plurilateral_900_979": "900–979（738.2 Table 1：Plurilateral NS and RS and other reasons）",
            "unilateral_980_989_CC_SS": "980–989（CC、SS）",
            "unilateral_990_999_AT_RS_UN": "990–999（AT、RS、UN；第二、三碼 99 為單邊，738.2 第 65 行）",
            "not_in_table_1": "700–899，Table 1 無此列（本資料中無）",
        },
        "table1_reason_in_text": "僅對 000–399（不含 29x）計算：該區段對應的 Table 1 原因字母（NS/MT/NP/CB）是否出現在該 ECCN 條文自列的 Reason for Control；條文沒列則為 null",
        "ccl_index_gaps": "ccl_index.json 漏收、但 evidence/text/ccl/_notes-*.txt 內有行首 ECCN 標題的號碼；已另列於 ccl_index_gaps，不計入 map 也不計入 tw_only",
        "counts": {"eccn": len(rows), "tw_same_code_true": sum(r["tw_same_code"] for r in rows), "tw_only": len(tw_only), "ccl_index_gaps": len(gaps)},
    }
    with open(os.path.join(root, "data", "eccn_tw_map.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"meta": meta, "map": rows, "ccl_index_gaps": gaps, "tw_only": tw_only}, fh, ensure_ascii=False, indent=1)
    kinds = {}
    for r in rows:
        kinds.setdefault(r["ear_kind"], [0, 0])
        kinds[r["ear_kind"]][0] += 1
        kinds[r["ear_kind"]][1] += r["tw_same_code"]
    print("eccn_tw_map：EAR %d 個 ECCN、台灣有同號 %d、台灣有而 EAR 無 %d；ccl_index 漏收 %s" % (len(rows), meta["counts"]["tw_same_code_true"], len(tw_only), [g["eccn"] for g in gaps]))
    for k, (n, m) in sorted(kinds.items()):
        print("  %-30s %4d（台灣有同號 %d）" % (k, n, m))
    print("  table1_reason_in_text 為 false：", [r["eccn"] for r in rows if r["table1_reason_in_text"] is False])


def main():
    root = sys.argv[1]
    src = os.path.join(root, SRC_REL)
    outdir = os.path.join(root, "evidence", "text", "twl")
    os.makedirs(outdir, exist_ok=True)
    for fn in os.listdir(outdir):  # 本目錄只由本程式寫入，重跑前清掉舊檔
        if fn.endswith(".txt"):
            os.remove(os.path.join(outdir, fn))
    doc = Doc(src)
    L = len(doc.lines)

    # --- 骨架錨點（以去頭尾空白後整行相等比對；目錄裡同名行帶點線，不會誤中）---
    i_num = doc.find("清單及管制號碼說明", 0)
    anomalies = doc.mark_footers(i_num)
    i_gen = doc.find("軍商兩用貨品及技術出口管制清單", i_num + 1)
    i_abbr = doc.find("字首集合字與縮寫", i_gen)
    i_def = doc.find("專用術語定義", i_abbr)
    i_cat = {}
    pos = i_def
    for n in range(10):
        i_cat[n] = doc.find("第%d類" % n, pos)
        pos = i_cat[n] + 1
    i_gloss = doc.find("專用術語之中英文對照", i_cat[9])
    i_ml = doc.find("一般軍用貨品清單", i_gloss)
    i_mldef = doc.find("本清單所使用之術語定義", i_ml)
    toc = parse_toc(doc, 0, i_num)

    log = []
    written = {}  # fname -> pages
    covered = set()  # 已輸出的行 idx

    def emit(fname, label, a, b):
        kept = doc.kept(a, b)
        if not kept:
            return None
        written[fname] = write_seg(doc, outdir, fname, label, kept)
        covered.update(i for i, _ in kept)
        return kept

    emit("_numbering.txt", "管制號碼說明", i_num, i_gen)
    emit("_general-notes.txt", "分類目錄、一般註解、核能技術／一般技術／核能軟體／一般軟體／一般資訊安全註解、歐盟理事會公報之編輯慣例", i_gen, i_abbr)
    emit("_abbreviations.txt", "字首集合字與縮寫", i_abbr, i_def)
    emit("_definitions.txt", "專用術語定義", i_def, i_cat[0])
    emit("_glossary-en-zh.txt", "專用術語之中英文對照", i_gloss, i_ml)

    # --- 各類 ---
    toc_by_cat = {}
    for t in toc["codes"]:
        toc_by_cat.setdefault(t["code"][0], []).append(t)
    entries = []
    structural = set()  # 有意不輸出的結構行（類別／部分／組標題、無內容）
    for n in range(10):
        cat = str(n)
        a = i_cat[n]
        b = i_cat[n + 1] if n < 9 else i_gloss
        part_idx = doc.find("第2部分", a, b) if n == 5 else None
        heads = pick_headings(doc, a, b, cat, [t["code"] for t in toc_by_cat[cat]], part_idx)
        toc_map = {t["code"]: t for t in toc_by_cat[cat]}
        # 組標題、無內容、附錄
        groups = []
        for i in range(a, b):
            s = doc.clean(i).strip()
            if len(s) <= 30 and GROUP_RE.match(s) and s[0] == cat:
                groups.append((i, GROUP_RE.match(s).group("cat") + GROUP_RE.match(s).group("grp") + GROUP_RE.match(s).group("part")))
            elif s == "無內容":
                structural.add(i)
        specials = []
        for i in range(a, b):
            s = doc.clean(i).strip()
            if n == 2 and s == "表—沉積技術":
                specials.append((i, "_appendix-cat2-deposition.txt", "第2類附表（沉積技術：表、註解、技術註解）"))
            if n == 4 and "調整尖峰效能" in s and s.endswith("技術註解"):
                specials.append((i, "_appendix-cat4-app.txt", "第4類附錄（調整尖峰效能 APP 之技術註解）"))
        bounds = [(i, "entry", c) for i, c, _ in heads] + [(i, "group", g) for i, g in groups] + [(i, "special", (f, lab)) for i, f, lab in specials]
        if part_idx is not None:
            bounds.append((part_idx, "part", 2))
        bounds.sort(key=lambda x: x[0])
        # 項目輸出
        first_entry = {}
        cur_group = None
        for k, (i, kind, data) in enumerate(bounds):
            end = bounds[k + 1][0] if k + 1 < len(bounds) else b
            if kind == "group":
                cur_group = data
            if kind == "entry":
                code = data
                kept = doc.kept(i, end)
                m = HEAD_RE.match(kept[0][1])
                token = m.group("pre") + m.group("code")
                rest = kept[0][1].strip()[len(token):].strip()
                g = cur_group or ""
                part = g[2:] or None
                if g[:2] != code[:2]:
                    log.append("組別與號碼不符 %s 在組 %s" % (code, g))
                fname = code + ".txt"
                pages = write_seg(doc, outdir, fname, code, kept)
                written[fname] = pages
                covered.update(x for x, _ in kept)
                t = toc_map.get(code)
                first_entry.setdefault(part, i)
                entries.append({
                    "code": code,
                    "cat": cat,
                    "part": part,
                    "group": code[1],
                    "regime": regime_of(code),
                    "title_zh": heading_title(kept, token),
                    "page_printed": pages[0],
                    "pdf_page": pages[2],
                    "page_printed_end": pages[1],
                    "pdf_page_end": pages[3],
                    "title_toc": t["title_toc"] if t else None,
                    "page_toc": t["page_toc"] if t else None,
                    "in_toc": bool(t),
                    "deleted": rest in ("刪除", "刪除。"),
                    "heading_token": token if token != code else None,
                    "src_line_start": kept[0][0] + 1,
                    "src_line_end": kept[-1][0] + 1,
                    "file": "evidence/text/twl/" + fname,
                })
            elif kind == "special":
                fname, lab = data
                emit(fname, lab, i, end)
        # 類別／部分開頭註解：標題起至該部分第一個管制號碼
        regions = []
        if n == 5:
            regions = [(a, first_entry[None] if None in first_entry else first_entry.get("1"), "cat5p1", "第5類第1部分 開頭註解（含類別標題）"),
                       (part_idx, first_entry["2"], "cat5p2", "第5類第2部分 開頭註解（含密碼學註解）")]
        else:
            regions = [(a, first_entry[None], "cat%d" % n, "第%d類 開頭註解（含類別標題）" % n)]
        for ra, rb, tag, lab in regions:
            if substantive(doc, ra, rb):
                emit("_notes-%s.txt" % tag, lab, ra, rb)
            else:
                structural.update(range(ra, rb))
        # 第一組以外各組開頭的註解
        firsts = {r[0] for r in regions}
        gl = [x for x in bounds if x[1] == "group"]
        for k, (i, kind, data) in enumerate(bounds):
            if kind != "group":
                continue
            end = bounds[k + 1][0] if k + 1 < len(bounds) else b
            if any(ra <= i < rb for ra, rb, _, _ in regions):
                continue
            if substantive(doc, i, end):
                part = data[2:]
                tag = "cat%s%s-%s" % (n, ("p" + part) if part else "", data[1])
                emit("_notes-%s.txt" % tag, "第%d類%s %s 組開頭註解" % (n, ("第%s部分" % part) if part else "", data[:2]), i, end)
            else:
                structural.update(range(i, end))

    # --- 一般軍用貨品清單 ---
    ml_heads = []
    pos = i_ml + 1
    for n in range(1, 23):
        for i in range(pos, i_mldef):
            m = ML_RE.match(doc.clean(i))
            if m and int(m.group("n")) == n:
                rest = m.group("rest").strip()
                if rest and not rest.startswith(CONT) and (m.group("rest")[:1].isspace() or ord(rest[0]) > 0x2E80):
                    ml_heads.append((i, n))
                    pos = i + 1
                    break
    ml_report = []
    emit("_military-list-preface.txt", "一般軍用貨品清單 開頭註解", i_ml, ml_heads[0][0])
    for k, (i, n) in enumerate(ml_heads):
        end = ml_heads[k + 1][0] if k + 1 < len(ml_heads) else i_mldef
        kept = emit("ML%d.txt" % n, "ML%d" % n, i, end)
        pg = written["ML%d.txt" % n]
        ml_report.append((n, pg[0], toc["ml"].get(n, {}).get("page")))
    emit("_definitions-ml.txt", "一般軍用貨品清單：本清單所使用之術語定義", i_mldef, L)

    # --- 核對 ---
    toc_codes = [t["code"] for t in toc["codes"]]
    got = {e["code"] for e in entries}
    missing = [c for c in toc_codes if c not in got]
    extra = [e["code"] for e in entries if not e["in_toc"]]
    page_diff = [(e["code"], e["page_toc"], e["page_printed"]) for e in entries if e["in_toc"] and e["page_toc"] != e["page_printed"]]
    unassigned = []
    for i in range(i_num, L):
        if i in covered or i in doc.footer or i in structural:
            continue
        if doc.clean(i).strip():
            unassigned.append(i + 1)
    index = [{k: v for k, v in e.items()} for e in entries]
    os.makedirs(os.path.join(root, "data"), exist_ok=True)
    with open(os.path.join(root, "data", "tw_index.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=0)

    print("來源行數 %d，PDF 頁數 %d，印刷頁 = PDF 頁 − %d；頁尾頁碼行 %d 個，頁尾異常頁 %s" % (L, doc.n_pages, doc.K, len(doc.footer), anomalies))
    print("目錄：號碼 %d、類別 %d、部分 %d、組 %d、ML %d" % (len(toc_codes), len(toc["cats"]), len(toc["parts"]), len(toc["groups"]), len(toc["ml"])))
    print("切出：號碼 %d（目錄有 %d、正文有目錄無 %s）；目錄有而正文找不到 %s" % (len(entries), len(entries) - len(extra), extra, missing))
    print("目錄頁碼與正文標題所在印刷頁不同：%d 筆 %s" % (len(page_diff), page_diff))
    print("刪除號碼：", [e["code"] for e in entries if e["deleted"]])
    print("標題行號碼前有多餘字元：", [(e["code"], e["heading_token"]) for e in entries if e["heading_token"]])
    print("ML 標題 %d 個（ML 編號, 正文頁, 目錄頁）：%s" % (len(ml_heads), [x for x in ml_report if x[2] != x[1]]))
    print("輸出檔 %d 個；未歸屬的非空白行 %d：%s" % (len(written), len(unassigned), unassigned[:20]))
    for w in log:
        print("警告：", w)
    build_map(root, entries, outdir)
    return doc, entries, toc, written


if __name__ == "__main__":
    main()
