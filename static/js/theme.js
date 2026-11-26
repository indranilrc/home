(function () {
  var root = document.documentElement;
  var btn = document.querySelector(".theme-toggle");
  if (!btn) return;
  function current() {
    return root.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  function paint() {
    var dark = current() === "dark";
    btn.textContent = dark ? "● dark" : "○ light";
    btn.setAttribute("aria-pressed", dark ? "true" : "false");
  }
  btn.hidden = false;
  btn.addEventListener("click", function () {
    var next = current() === "dark" ? "light" : "dark";
    root.dataset.theme = next;
    try { localStorage.setItem("theme", next); } catch (e) {}
    paint();
  });
  paint();
})();
