(function () {
  document.querySelectorAll("a.email[data-u]").forEach(function (a) {
    var addr = a.getAttribute("data-u") + "@" + a.getAttribute("data-d");
    a.href = "mailto:" + addr;
    a.textContent = "Email";
    a.title = addr;
  });
})();
