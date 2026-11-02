"""把 eCFR XML 切成逐條純文字（站上引文點回的檔案）。

用法：python -I evidence/tools/parse_ecfr.py <repo_root>
輸入：evidence/sources/us-ear/{ear,itar}-part-*.xml
輸出：
  evidence/text/ear/<條號>.txt         例如 740.17.txt、774-supp-4.txt（每個 section／supplement 一檔）
  evidence/text/ccl/<ECCN>.txt         Supplement No. 1 to Part 774 依 ECCN 切檔，例如 5A002.txt
  evidence/text/ccl/_notes-<類組>.txt  類別／群組開頭的註記，例如 _notes-cat5p2-A.txt、_notes-cat3-A.txt
  evidence/text/itar/<條號>.txt        22 CFR Part 120／121
  data/ccl_index.json                  ECCN 索引（ECCN、類別、標題、字數）
每檔第一行是座標標頭；其後每段一行，文字與 eCFR 逐字相同（只收斂空白、去掉行內標記）。
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")
ROOT = sys.argv[1]
SRC = os.path.join(ROOT, "evidence", "sources", "us-ear")
TXT = os.path.join(ROOT, "evidence", "text")
BASE_DATE = "2026-10-29"
INLINE = {"I", "B", "E", "SU", "FR", "XREF", "SUB", "AC", "PRTPAGE"}
ECCN_RE = re.compile(r"^(\d[A-E]\d{3}|\d[A-E]\d{2}[A-Z0-9]?)\b")


def inline(e):
    """Concatenate an element's text, descending into inline children."""
    parts = [e.text or ""]
    for c in e:
        if c.tag == "PRTPAGE":
            pass
        else:
            parts.append(inline(c))
        parts.append(c.tail or "")
    return "".join(parts)


def squash(s):
    return re.sub(r"\s+", " ", s).strip()


def blocks(e):
    """Yield text lines for a block-level element."""
    tag = e.tag
    if tag == "NOTE":
        kids = list(e)
        head = ""
        if kids and kids[0].tag == "HED":
            head = squash(inline(kids[0]))
            kids = kids[1:]
        first = True
        for k in kids:
            for ln in blocks(k):
                if first and head:
                    yield head + " " + ln
                    first = False
                else:
                    yield ln
        if first and head:
            yield head
    elif tag == "TABLE":
        for tr in e.iter("TR"):
            cells = [squash(inline(c)) for c in tr if c.tag in ("TD", "TH")]
            if any(cells):
                yield " | ".join(cells)
    elif tag in ("EXTRACT", "DIV", "APPENDIX", "GPOTABLE", "TFOOT", "TBODY", "THEAD"):
        for k in e:
            yield from blocks(k)
    elif tag in ("AUTH", "SOURCE"):
        s = squash(" ".join(inline(k) for k in e))
        if s:
            yield s
    else:
        s = squash(inline(e))
        if s:
            yield s


def write(path, header, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(header + "\n\n")
        fh.write("\n\n".join(lines) + "\n")


def safe(name):
    return re.sub(r"[^\w.\-]+", "-", name).strip("-")


def split_ccl(div9):
    """Split Supplement No. 1 to Part 774 into ECCN files and group-note files."""
    index = []
    cat, part, group = None, None, None
    cur_name, cur_head, cur_lines = None, None, []

    def flush():
        nonlocal cur_name, cur_lines
        if cur_name and cur_lines:
            write(os.path.join(TXT, "ccl", cur_name + ".txt"), cur_head, cur_lines)
        cur_name, cur_lines = None, []

    def walk(children):
        nonlocal cat, part, group, cur_name, cur_head, cur_lines
        for e in children:
            if e.tag in ("DIV", "EXTRACT"):
                walk(list(e))
                continue
            text = squash(inline(e)) if e.tag not in ("NOTE", "TABLE") else ""
            if e.tag in ("HD1", "HD2", "HD3"):
                m = re.match(r"^Category (\d)", text)
                if m:
                    flush()
                    cat, part, group = m.group(1), None, None
                    cur_name = "_notes-cat%s" % cat
                    cur_head = "〔15 CFR Part 774, Supp. No. 1, Category %s 類別註記；eCFR %s〕" % (cat, BASE_DATE)
                    cur_lines = [text]
                    continue
                m = re.match(r"^Part (\d)", text, re.I)
                if m and cat == "5":
                    flush()
                    part, group = m.group(1), None
                    cur_name = "_notes-cat5p%s" % part
                    cur_head = "〔15 CFR Part 774, Supp. No. 1, Category 5 Part %s 註記；eCFR %s〕" % (part, BASE_DATE)
                    cur_lines = [text]
                    continue
                m = re.match(r"^([A-E])\.\s", text)
                if m and cat:
                    flush()
                    group = m.group(1)
                    lab = "cat%s" % cat + ("p%s" % part if part else "")
                    cur_name = "_notes-%s-%s" % (lab, group)
                    cur_head = "〔15 CFR Part 774, Supp. No. 1, %s Group %s 開頭註記；eCFR %s〕" % (lab, group, BASE_DATE)
                    cur_lines = [text]
                    continue
            if e.tag in ("FP-2", "FP-1", "FP", "P") and cat:
                m = ECCN_RE.match(text)
                bold = e.find("B")
                # ECCN 標題多為 FP-2；少數（如 8D001）eCFR 用 FP-1，條件同樣是粗體開頭即 ECCN
                is_head = m and bold is not None and (bold.text or "").strip().startswith(m.group(1)) and e.tag in ("FP-2", "FP-1")
                if is_head:
                    flush()
                    cur_name = m.group(1)
                    cur_head = "〔15 CFR Part 774, Supp. No. 1, ECCN %s；eCFR %s〕" % (cur_name, BASE_DATE)
                    cur_lines = [text]
                    index.append({"eccn": cur_name, "cat": cat, "part": part, "group": cur_name[1], "title": text[len(cur_name):].strip()[:300]})
                    continue
            if cur_name is None:
                cur_name = "_preamble"
                cur_head = "〔15 CFR Part 774, Supp. No. 1 開頭；eCFR %s〕" % BASE_DATE
            cur_lines.extend(blocks(e))

    walk(list(div9))
    flush()
    return index


def main():
    counts = {}
    index = []
    for fn in sorted(os.listdir(SRC)):
        m = re.match(r"(ear|itar)-part-(\d+)\.xml$", fn)
        if not m:
            continue
        kind, part = m.groups()
        tree = ET.parse(os.path.join(SRC, fn))
        rootel = tree.getroot()
        n = 0
        for e in rootel.iter():
            if e.tag not in ("DIV8", "DIV9"):
                continue
            label = e.attrib.get("N", "")
            if e.tag == "DIV9" and label == "Supplement No. 1 to Part 774":
                index = split_ccl(e)
                continue
            if e.tag == "DIV8":
                name = safe(label.replace("§", "").strip())
                coord = "%s CFR § %s" % ("15" if kind == "ear" else "22", label.replace("§", "").strip())
            else:
                mm = re.match(r"Supplement No\. (\d+) to Part (\d+)", label)
                name = "%s-supp-%s" % (mm.group(2), mm.group(1)) if mm else safe(label)
                coord = "%s CFR %s" % ("15" if kind == "ear" else "22", label)
            lines = []
            for k in e:
                lines.extend(blocks(k))
            write(os.path.join(TXT, kind, name + ".txt"), "〔%s；eCFR %s〕" % (coord, BASE_DATE), lines)
            n += 1
        counts[fn] = n
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "ccl_index.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=0)
    print(counts)
    print("ECCN files:", len(index))
    for c in "0123456789":
        print(c, [i["eccn"] for i in index if i["cat"] == c][:12], "...", sum(1 for i in index if i["cat"] == c))


main()
