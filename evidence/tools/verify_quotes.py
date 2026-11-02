"""逐一核對網站上的原文引文：每段 .q／.en（帶 data-file）都必須能在證據包文字檔中找到。

用法：python -I evidence/tools/verify_quotes.py <repo_root>
- data-file 為 evidence/text/ 之下的相對路徑，例如 ccl/5A002.txt、tw/trade-act-J0090004.txt
- 引文以「…」或「||」分段，各段分別比對；<cite> 內文字不算引文
- 比對前兩邊都去掉所有空白，並把彎引號、全形空白統一，避免 PDF 換行與排版造成誤判
有任何一段找不到就以非零碼結束。
"""
import glob
import os
import re
import sys
import unicodedata
from html.parser import HTMLParser

sys.stdout.reconfigure(encoding="utf-8")
ROOT = sys.argv[1]
TEXT = os.path.join(ROOT, "evidence", "text")
QUOTE_CLASSES = {"q", "en"}


def norm(s):
    s = re.sub(r"[豈-﫿]", lambda m: unicodedata.normalize("NFKC", m.group()), s)
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace("′", "'").replace("‵", "'")
    return re.sub(r"\s+", "", s)


class Grab(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []      # (data-file, cite, text)
        self.stack = []    # 進入引文元素後的巢狀深度
        self.cur = None
        self.in_cite = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.cur is not None:
            self.stack.append(tag)
            if tag == "cite":
                self.in_cite += 1
            return
        cls = set((a.get("class") or "").split())
        if cls & QUOTE_CLASSES and a.get("data-file"):
            self.cur = {"file": a["data-file"], "cite": a.get("data-cite", ""), "text": [], "line": self.getpos()[0]}
            self.stack = [tag]

    def handle_endtag(self, tag):
        if self.cur is None:
            return
        if tag == "cite" and self.in_cite:
            self.in_cite -= 1
        if self.stack:
            self.stack.pop()
        if not self.stack:
            self.out.append(self.cur)
            self.cur = None

    def handle_data(self, data):
        if self.cur is not None and not self.in_cite:
            self.cur["text"].append(data)


def main():
    cache, total, bad = {}, 0, 0
    for page in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        g = Grab()
        g.feed(open(page, encoding="utf-8").read())
        for q in g.out:
            path = os.path.join(TEXT, q["file"].replace("/", os.sep))
            if path not in cache:
                cache[path] = norm(open(path, encoding="utf-8").read()) if os.path.exists(path) else None
            hay = cache[path]
            text = "".join(q["text"])
            for frag in re.split(r"…|\.\.\.|\|\|", text):
                frag = frag.strip().strip("「」\"")
                if len(norm(frag)) < 6:
                    continue
                total += 1
                if hay is None or norm(frag) not in hay:
                    bad += 1
                    why = "找不到檔案" if hay is None else "找不到引文"
                    print("✗ %s:%d  [%s] %s  %s\n    %s" % (os.path.basename(page), q["line"], q["file"], q["cite"], why, frag[:160]))
    print("checked %d fragments, %d failed" % (total, bad))
    sys.exit(1 if bad else 0)


main()
