"""依 manifest 下載官方來源，並寫出來源登錄檔（網址、日期、大小、SHA-256）。

用法：python -I evidence/tools/fetch_sources.py <repo_root> <manifest.json> [--only 前綴]
manifest 每筆：{"id","class","title","publisher","url","dest","license","note"}
- dest 相對於 evidence/（例如 sources/us-bis/encryption-faqs.pdf；local-only/ 開頭者不進 git）
- 已存在且非空的檔案不重抓（要重抓先刪檔）
- 輸出 evidence/registry.json：manifest 加上 retrieved、status、bytes、sha256、content_type
只下載資料、不執行任何下載內容。
"""
import gzip
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
TODAY = time.strftime("%Y-%m-%d")

root, manifest_path = sys.argv[1], sys.argv[2]
only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
ev = os.path.join(root, "evidence")
reg_path = os.path.join(ev, "registry.json")
registry = {}
if os.path.exists(reg_path):
    registry = {r["id"]: r for r in json.load(open(reg_path, encoding="utf-8"))}

items = json.load(open(manifest_path, encoding="utf-8"))
for it in items:
    if only and not it["id"].startswith(only):
        continue
    dest = os.path.join(ev, it["dest"].replace("/", os.sep))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    rec = dict(registry.get(it["id"], {}))
    rec.update(it)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        data = open(dest, "rb").read()
        rec.setdefault("retrieved", TODAY)
        rec.setdefault("status", 200)
    else:
        req = urllib.request.Request(it["url"], headers={"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    data = gzip.decompress(data)
                rec["status"] = r.status
                rec["content_type"] = r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            print("FAIL", it["id"], e.code, it["url"])
            rec["status"] = e.code
            registry[it["id"]] = rec
            continue
        except urllib.error.URLError as e:
            # 部分台灣政府站台未送出中繼憑證，Python 驗證失敗；改用 curl（Windows 版走 Schannel，會依 AIA 補鏈，仍驗證憑證）
            if "CERTIFICATE_VERIFY_FAILED" not in repr(e):
                print("FAIL", it["id"], repr(e)[:120], it["url"])
                rec["status"] = "error"
                registry[it["id"]] = rec
                continue
            res = subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", "120", "-o", dest, "-w", "%{http_code}\t%{content_type}", it["url"]],
                                 capture_output=True, text=True)
            code, _, ctype = res.stdout.partition("\t")
            if res.returncode != 0 or code != "200":
                print("FAIL", it["id"], "curl", res.returncode, code, it["url"])
                rec["status"] = "error"
                registry[it["id"]] = rec
                continue
            data = open(dest, "rb").read()
            rec["status"] = 200
            rec["content_type"] = ctype
            rec["via"] = "curl"
        except Exception as e:  # noqa: BLE001 - report and continue with the next source
            print("FAIL", it["id"], repr(e)[:120], it["url"])
            rec["status"] = "error"
            registry[it["id"]] = rec
            continue
        else:
            with open(dest, "wb") as fh:
                fh.write(data)
        rec["retrieved"] = TODAY
        time.sleep(1.5)
    rec["bytes"] = len(data)
    rec["sha256"] = hashlib.sha256(data).hexdigest()
    registry[it["id"]] = rec
    print("ok  %-34s %9d  %s" % (it["id"], len(data), it["dest"]))

rows = sorted(registry.values(), key=lambda r: r["id"])
with open(reg_path, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(rows, fh, ensure_ascii=False, indent=1)
print("registry rows:", len(rows))
