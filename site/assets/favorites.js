(function (global) {
  var KEY = "sury-paper-favs";

  function load() {
    try {
      var raw = JSON.parse(localStorage.getItem(KEY) || "[]");
      if (!Array.isArray(raw)) return [];
      return raw.filter(function (id) { return typeof id === "string" && id; });
    } catch (e) {
      return [];
    }
  }

  function save(ids) {
    localStorage.setItem(KEY, JSON.stringify(ids));
  }

  function has(id) {
    return load().indexOf(id) !== -1;
  }

  function toggle(id) {
    if (!id) return false;
    var ids = load();
    var i = ids.indexOf(id);
    if (i >= 0) ids.splice(i, 1);
    else ids.unshift(id);
    save(ids);
    return i < 0;
  }

  var ICON =
    '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">' +
    '<path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" d="M7 4.5h10a1 1 0 0 1 1 1V20l-6-2.8L6 20V5.5a1 1 0 0 1 1-1z"/>' +
    "</svg>";

  function paint(btn, on) {
    if (!btn.querySelector("svg")) btn.innerHTML = ICON;
    btn.setAttribute("aria-pressed", on ? "true" : "false");
    btn.setAttribute("aria-label", on ? "取消收藏" : "收藏");
    btn.classList.toggle("on", on);
    btn.title = on ? "取消收藏（仅本机浏览器）" : "收藏到本机浏览器";
  }

  function injectStyle() {
    if (document.getElementById("paper-fav-style")) return;
    var s = document.createElement("style");
    s.id = "paper-fav-style";
    s.textContent =
      "button.fav-btn{" +
      "flex-shrink:0;display:inline-flex;align-items:center;justify-content:center;" +
      "width:2rem;height:2rem;padding:0;border:1px solid var(--accent);" +
      "border-radius:6px;background:#fff;color:var(--accent);cursor:pointer;}" +
      "button.fav-btn svg{display:block;}" +
      "button.fav-btn:hover{background:#e8f2f6;}" +
      "button.fav-btn.on path{fill:currentColor;}";
    document.head.appendChild(s);
  }

  function mountReader() {
    var id = document.documentElement.getAttribute("data-paper-id");
    if (!id) return;
    var bar = document.querySelector("header.bar");
    if (!bar || bar.querySelector(".fav-btn")) return;
    injectStyle();
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "fav-btn";
    paint(btn, has(id));
    btn.addEventListener("click", function () {
      paint(btn, toggle(id));
    });
    bar.appendChild(btn);
    global.addEventListener("storage", function (ev) {
      if (ev.key === KEY) paint(btn, has(id));
    });
  }

  global.PaperFav = {
    KEY: KEY,
    load: load,
    has: has,
    toggle: toggle
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountReader);
  } else {
    mountReader();
  }
})(window);
