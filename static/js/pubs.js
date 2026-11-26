(function () {
  var bar = document.querySelector(".filters");
  if (!bar) return;
  var chips = Array.prototype.slice.call(bar.querySelectorAll(".chip"));
  var search = bar.querySelector(".search");
  var items = Array.prototype.slice.call(document.querySelectorAll("li.pub"));
  var years = Array.prototype.slice.call(document.querySelectorAll("section.year"));
  var empty = document.querySelector(".empty");
  var types = null; // null = all
  bar.hidden = false;

  function apply() {
    var q = search.value.trim().toLowerCase();
    var shown = 0;
    items.forEach(function (li) {
      var ok = (!types || types.indexOf(li.dataset.type) !== -1) &&
               (!q || li.dataset.search.indexOf(q) !== -1);
      li.hidden = !ok;
      if (ok) shown++;
    });
    years.forEach(function (sec) {
      sec.hidden = !sec.querySelector("li.pub:not([hidden])");
    });
    empty.hidden = shown !== 0;
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      chips.forEach(function (c) { c.setAttribute("aria-pressed", c === chip ? "true" : "false"); });
      var f = chip.dataset.filter;
      types = f === "all" ? null : f.split(",");
      apply();
    });
  });
  search.addEventListener("input", apply);
})();
