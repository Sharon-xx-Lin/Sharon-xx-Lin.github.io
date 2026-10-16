/* ============================================================
   林晓煊 · 个人主页 —— 交互脚本
   1. 滚动入场 / 导航高亮 / 阅读进度
   2. 复制微信号
   3. 深浅主题切换（已开放，选择写入 localStorage）· 语言切换（英文版待做）
   ------------------------------------------------------------
   摄影区「静止态高对比黑白 + 网点，hover 解出彩色原图」是纯 CSS 实现的
   （见 style.css 的 .dither-wrap 段），这里不再需要任何像素处理脚本。
   ============================================================ */
(function () {
  "use strict";

  /* ---------- 工具 ---------- */
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  /* 每个初始化模块独立容错：任一模块抛错都不影响其它模块（避免整页白屏） */
  function safe(label, fn) {
    try { fn(); } catch (e) {
      console.error("[site] " + label + " 初始化失败：", e);
    }
  }

  /* ---------- Toast ---------- */
  var toastEl = $("#toast");
  var toastTimer = null;
  function toast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("show"); }, 2200);
  }

  /* ============================================================
     1. 滚动入场 / 导航高亮 / 进度条
     ============================================================ */
  /* 滚动入场：用滚动位置判断而不是 IntersectionObserver ——
     懒加载图片在未加载时高度为 0，IO 对零面积元素可能永远不触发 */
  function initReveal() {
    var els = $$(".reveal");
    if (!els.length) return;
    var stopped = false;
    var ro = null;

    function stop() {
      if (stopped) return;
      stopped = true;
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", check);
      if (ro) { try { ro.disconnect(); } catch (e) {} }
      if (poll) clearInterval(poll);
    }

    function check() {
      for (var i = els.length - 1; i >= 0; i--) {
        var el = els[i];
        var r = el.getBoundingClientRect();
        if (r.top < window.innerHeight * 0.92) {
          el.classList.add("visible");
          els.splice(i, 1);
        }
      }
      if (!els.length) stop();
    }

    var timer = null;
    function onScroll() {
      if (timer) return;                 // 尾部节流：滚动停止后 90ms 统一检查
      timer = setTimeout(function () { timer = null; check(); }, 90);
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", check);
    window.addEventListener("load", check);          // 图片加载完成、高度确定后复查
    window.addEventListener("hashchange", function () { setTimeout(check, 400); });

    /* 手风琴展开/收起会改变页面高度，而这种情况不会派发 scroll 事件：
       折叠线以下的 .reveal 会永远停在 opacity:0（表现为「少了几段经历」）。
       所以在 details 的 toggle 后补一次检查。 */
    $$("details").forEach(function (d) {
      d.addEventListener("toggle", function () { setTimeout(check, 60); });
    });

    /* 更通用的兜底：任何引起 body 尺寸变化的布局变化都复查一次 */
    if (typeof ResizeObserver === "function") {
      try {
        ro = new ResizeObserver(function () { check(); });
        ro.observe(document.body);
      } catch (e) { ro = null; }
    }

    // 兜底轮询：防止某些环境下滚动事件/定时器被节流导致内容不显示（全部显示后自动停止）
    var poll = setInterval(check, 400);
    setTimeout(function () { if (!stopped) clearInterval(poll); }, 12000);
    check();
  }

  function initNav() {
    var links = $$("#navLinks a");
    var sections = links
      .map(function (a) { return $(a.getAttribute("href")); })
      .filter(Boolean);

    function onScroll() {
      // 进度条
      var doc = document.documentElement;
      var max = doc.scrollHeight - window.innerHeight;
      var p = max > 0 ? (window.scrollY / max) * 100 : 0;
      $("#progressBar").style.width = p + "%";

      // 当前 section
      var current = sections[0];
      sections.forEach(function (sec) {
        if (sec.getBoundingClientRect().top <= 120) current = sec;
      });
      links.forEach(function (a) {
        a.classList.toggle("active", a.getAttribute("href") === "#" + current.id);
      });
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ============================================================
     2. 复制微信号
     ============================================================ */
  function initCopy() {
    var el = $("#copyWechat");
    if (!el) return;
    function copy() {
      var text = "LOXOXOLO";
      function ok() { toast("已复制微信号：" + text); }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(ok, function () { toast("微信号：" + text); });
      } else {
        var ta = document.createElement("textarea");
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand("copy"); ok(); } catch (e) { toast("微信号：" + text); }
        document.body.removeChild(ta);
      }
    }
    el.addEventListener("click", copy);
    el.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); copy(); }
    });
  }

  /* ============================================================
     3-a. 深浅主题切换
     ------------------------------------------------------------
     真正的配色全部在 CSS 变量里（html[data-theme]），JS 只负责：
       ① 翻转 data-theme  ② 写 localStorage  ③ 同步 meta/favicon/无障碍标签
     ============================================================ */
  var THEME_KEY = "site-theme";
  // 与 <head> 里的内联 favicon 对应（黑底白框 ↔ 白底黑框），主题一变标签图标也跟着反色
  var FAVICON = {
    dark: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'>" +
          "<rect width='16' height='16' fill='black'/><rect x='3' y='3' width='10' height='10' fill='white'/>" +
          "<rect x='6' y='6' width='4' height='4' fill='black'/></svg>",
    light: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'>" +
           "<rect width='16' height='16' fill='white'/><rect x='3' y='3' width='10' height='10' fill='black'/>" +
           "<rect x='6' y='6' width='4' height='4' fill='white'/></svg>"
  };

  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);

    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", theme === "light" ? "#ffffff" : "#000000");

    var icon = document.querySelector('link[rel="icon"]');
    if (icon) icon.setAttribute("href", FAVICON[theme]);

    var btn = $("#themeToggle");
    if (btn) {
      var label = theme === "light" ? "切换深色模式" : "切换浅色模式";
      btn.setAttribute("title", label);
      btn.setAttribute("aria-label", label);
      btn.setAttribute("aria-pressed", theme === "light" ? "true" : "false");
    }
  }

  function initTheme() {
    applyTheme(currentTheme());   // head 里已预置，这里补同步 meta/favicon/标签

    var btn = $("#themeToggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var next = currentTheme() === "light" ? "dark" : "light";
      applyTheme(next);
      try { localStorage.setItem(THEME_KEY, next); } catch (e) {}  // 存储不可用时仅本次会话生效
      toast(next === "light" ? "◑ 浅色模式" : "◐ 深色模式");
    });

    /* 多标签页之间保持一致：另一个标签页改了主题，这边跟着变
       （storage 事件只在「其它」标签页触发，不会造成自己改自己） */
    window.addEventListener("storage", function (e) {
      if (e.key !== THEME_KEY || (e.newValue !== "light" && e.newValue !== "dark")) return;
      applyTheme(e.newValue);
    });
  }

  /* ============================================================
     3-b. 语言切换（英文版仍在做，先保留占位提示）
     ============================================================ */
  function initLang() {
    var btn = $("#langToggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      toast("EN English version on the way");
    });
  }

  /* ---------- 启动 ---------- */
  /* 主题单独提前执行：它依赖的元素（head 的 meta/link、导航里的按钮）在本脚本之前
     就已解析完，放进 DOMContentLoaded 会让 favicon / theme-color 晚一拍，刷新时
     能看见标签图标闪一下。放在这里就能和首帧同步。 */
  safe("theme", initTheme);

  document.addEventListener("DOMContentLoaded", function () {
    safe("reveal", initReveal);
    safe("nav", initNav);
    safe("copy", initCopy);
    safe("lang", initLang);
    window.__siteInit = true;   // 通知 head 里的兜底脚本
  });
})();
