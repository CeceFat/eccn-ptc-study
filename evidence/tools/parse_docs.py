"""把 FR 全文、BIS／DOJ 網頁、官方 PDF 轉成純文字（站上引文點回的檔案）。

用法：python -I evidence/tools/parse_docs.py <repo_root>
輸入：evidence/registry.json 所列的 sources/（us-fr、us-bis、us-doj、tw-*、intl）
輸出：evidence/text/<fr|bis|doj|tw|intl>/<檔名>.txt；第一行是座標標頭
PDF 用 pdftotext -enc UTF-8（須在 PATH）；HTML 去除 script／style／導覽後保留內文。
"""
import html
import json
import os
import re
import subprocess
import sys
import unicodedata
import zipfile

sys.stdout.reconfigure(encoding="utf-8")
ROOT = sys.argv[1]
EV = os.path.join(ROOT, "evidence")
OUT = os.path.join(EV, "text")
MAP = {"us-fr": "fr", "us-bis": "bis", "us-doj": "doj", "tw-trade": "tw", "tw-law": "tw", "intl": "intl",
       "cn": "cn", "sea": "sea", "us-import": "usimp", "eu": "eu"}
HTMLISH = (".html", ".htm", ".shtml", ".xhtml", ".asp", ".aspx", ".php", ".xml", "")


def read_text(path):
    """依 BOM／meta charset 解碼；中國政府網站常見 GBK，解不開 UTF-8 就改用 gb18030。"""
    data = open(path, "rb").read()
    if data.startswith(b"\xef\xbb\xbf"):
        return data[3:].decode("utf-8", errors="replace")
    m = re.search(rb"charset=[\"']?([A-Za-z0-9_-]+)", data[:4096])
    enc = m.group(1).decode("ascii").lower() if m else "utf-8"
    if enc in ("gb2312", "gbk", "gb18030"):
        enc = "gb18030"
    try:
        return data.decode(enc)
    except (UnicodeDecodeError, LookupError):
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("gb18030", errors="replace")


def docx_text(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", errors="replace")
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<w:tab/>", "\t", xml)
    return html.unescape(re.sub(r"<[^>]+>", "", xml)).strip() + "\n"


def strip_html(raw):
    raw = re.sub(r"<(script|style|noscript|svg)\b.*?</\1>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
    raw = re.sub(r"<(br|/p|/div|/li|/tr|/h[1-6]|/section|/article|/table|/ul|/ol)\b[^>]*>", "\n", raw, flags=re.I)
    raw = re.sub(r"<(li)\b[^>]*>", "\n- ", raw, flags=re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    lines = [re.sub(r"[ \t ]+", " ", ln).strip() for ln in raw.split("\n")]
    out, blank = [], False
    for ln in lines:
        if ln:
            out.append(ln)
            blank = False
        elif not blank:
            out.append("")
            blank = True
    return "\n".join(out).strip() + "\n"


def fr_text(raw):
    m = re.search(r"<pre>(.*)</pre>", raw, re.S)
    body = m.group(1) if m else raw
    body = re.sub(r"<[^>]+>", "", body)
    return html.unescape(body).strip() + "\n"


def main():
    reg = json.load(open(os.path.join(EV, "registry.json"), encoding="utf-8"))
    n = 0
    for r in reg:
        dest = r["dest"]
        parts = dest.split("/")
        if parts[0] == "local-only":
            sub, base = "local", parts[-1]
        elif parts[0] == "sources" and parts[1] in MAP:
            sub, base = MAP[parts[1]], parts[-1]
        else:
            continue
        src = os.path.join(EV, dest.replace("/", os.sep))
        if not os.path.exists(src):
            continue
        stem, ext = os.path.splitext(base)
        target_dir = os.path.join(EV, "local-only", "text") if sub == "local" else os.path.join(OUT, sub)
        target = os.path.join(target_dir, stem + ".txt")
        os.makedirs(target_dir, exist_ok=True)
        head = "〔%s｜%s｜抓取 %s｜%s〕\n\n" % (r.get("publisher", ""), r.get("title", ""), r.get("retrieved", ""), r.get("url", ""))
        if ext.lower() == ".pdf" or (ext == "" and open(src, "rb").read(4) == b"%PDF"):
            res = subprocess.run(["pdftotext", "-enc", "UTF-8", "-layout", src, "-"], capture_output=True)
            text = res.stdout.decode("utf-8", errors="replace")
        elif ext.lower() == ".docx":
            text = docx_text(src)
        else:
            raw = read_text(src)
            if parts[1:2] == ["us-fr"]:
                text = fr_text(raw)
            elif ext.lower() in HTMLISH:
                text = strip_html(raw)
            else:
                text = raw
        # GPO 全文夾帶 NUL 等控制字元（分頁殘留）；原檔不動，只在文字輸出端清掉，保留 \n \t \f
        text = re.sub(r"[\x00-\x08\x0b\x0e-\x1f]", "", text)
        # 中文 PDF 抽字常出現 CJK 相容表意字（U+F900–FAFF，如「不」抽成 U+F967）；一對一換回標準字，行號不變
        text = re.sub(r"[豈-﫿]", lambda m: unicodedata.normalize("NFKC", m.group()), text)
        with open(target, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(head + text)
        n += 1
        print("%-44s %8d chars" % (stem, len(text)))
    print("converted", n)


main()
