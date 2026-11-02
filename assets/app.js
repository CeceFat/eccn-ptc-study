/* 共用行為：主題切換、導覽標示、原文閱讀器 */
(function () {
  "use strict";

  /* ---------- theme ---------- */
  var root = document.documentElement;
  function readTheme() {
    try { return localStorage.getItem("eccn-theme"); } catch (e) { return null; }
  }
  function applyTheme(t) {
    if (t === "dark" || t === "light") root.setAttribute("data-theme", t);
    else root.removeAttribute("data-theme");
  }
  applyTheme(readTheme());

  function currentEffective() {
    var set = root.getAttribute("data-theme");
    if (set) return set;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-theme-toggle]");
    if (!b) return;
    var next = currentEffective() === "dark" ? "light" : "dark";
    applyTheme(next);
    try { localStorage.setItem("eccn-theme", next); } catch (err) {}
    b.textContent = next === "dark" ? "☀" : "☾";
  });

  /* ---------- nav current ---------- */
  var here = location.pathname.split("/").pop() || "index.html";
  Array.prototype.forEach.call(document.querySelectorAll("nav.main a"), function (a) {
    var t = a.getAttribute("href");
    if (t === here || (here === "" && t === "index.html")) a.setAttribute("aria-current", "page");
  });

  var tb = document.querySelector("[data-theme-toggle]");
  if (tb) tb.textContent = currentEffective() === "dark" ? "☀" : "☾";

  /* ---------- helpers ---------- */
  window.esc = function (s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };

  /* ---------- reader ---------- */
  var reader = null;
  function ensureReader() {
    if (reader) return reader;
    reader = document.createElement("div");
    reader.className = "reader";
    reader.innerHTML =
      '<div class="reader-panel">' +
        '<div class="reader-head">' +
          '<h3 data-r-title>—</h3>' +
          '<input type="search" data-r-find placeholder="在原文中尋找…" style="min-width:150px">' +
          '<a class="x-btn" data-r-raw href="#" target="_blank" rel="noopener">原始檔</a>' +
          '<button class="x-btn" data-r-close>關閉</button>' +
        '</div>' +
        '<div class="reader-body" data-r-body>載入中…</div>' +
      "</div>";
    document.body.appendChild(reader);
    reader.addEventListener("click", function (e) {
      if (e.target === reader || e.target.closest("[data-r-close]")) close();
    });
    reader.querySelector("[data-r-find]").addEventListener("input", function () { paint(this.value); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") close();
    });
    return reader;
  }
  var rawText = "";
  function paint(term) {
    var body = reader.querySelector("[data-r-body]");
    if (!term) { body.textContent = rawText; return; }
    var safe = esc(rawText);
    /* 原文已跳脫，搜尋詞也要用同一套跳脫，含撇號、引號、<> 的詞才比得到 */
    var re = new RegExp(esc(term).replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
    body.innerHTML = safe.replace(re, function (m) { return "<mark>" + m + "</mark>"; });
    var first = body.querySelector("mark");
    if (first) first.scrollIntoView({ block: "center" });
  }
  function close() { if (reader) reader.removeAttribute("open-state"); }

  window.openReader = function (file, title, term) {
    var r = ensureReader();
    var base = location.pathname.replace(/[^/]*$/, "");
    /* file 為 evidence/text/ 之下的相對路徑，例如 ccl/5A002.txt、ear/740.17.txt、twl/5A002.txt */
    var url = base + "evidence/text/" + file;
    r.querySelector("[data-r-title]").textContent = title || file;
    r.querySelector("[data-r-raw]").href = url;
    r.querySelector("[data-r-find]").value = term || "";
    r.querySelector("[data-r-body]").textContent = "載入中…";
    r.setAttribute("open-state", "1");
    fetch(url).then(function (res) {
      if (!res.ok) throw new Error(res.status);
      return res.text();
    }).then(function (t) {
      rawText = t;
      paint(term || "");
    }).catch(function () {
      rawText = "";
      r.querySelector("[data-r-body]").innerHTML =
        '讀取失敗。若以 file:// 直接開啟本機檔案，瀏覽器會擋下 fetch；請改用 GitHub Pages 網址，' +
        '或直接開啟 <a href="' + url + '">原始檔</a>。';
    });
  };

  document.addEventListener("click", function (e) {
    var a = e.target.closest("[data-open]");
    if (!a) return;
    e.preventDefault();
    openReader(a.getAttribute("data-open"), a.getAttribute("data-title"), a.getAttribute("data-term"));
  });

  /* ---------- 引文區塊自動補座標與「查原文」連結 ----------
     <div class="q" data-file="ccl/5A002.txt" data-cite="ECCN 5A002, Note 2.f" [data-term="..."]> */
  function bestTerm(text) {
    var parts = text.split(/\s*(?:\.{3}|…|\|\|)\s*/);
    var best = "";
    parts.forEach(function (p) { if (p.trim().length > best.length) best = p.trim(); });
    return best.replace(/^[“"「]|[”"」]$/g, "").slice(0, 60);
  }
  Array.prototype.forEach.call(document.querySelectorAll(".q[data-file]"), function (q) {
    var file = q.getAttribute("data-file");
    var cite = q.getAttribute("data-cite") || file;
    var term = q.getAttribute("data-term") || bestTerm(q.textContent);
    var el = document.createElement("cite");
    el.innerHTML = "〔" + esc(cite) + "〕 · " +
      '<a href="#" data-open="' + esc(file) + '" data-title="' + esc(cite) + '" data-term="' + esc(term) + '">在原文中查看</a>';
    q.appendChild(el);
  });
})();
