/* Midway Ventures LLC - progressive enhancement only. Every page works without this file. */
(function () {
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  if (!header || !toggle) return;
  toggle.addEventListener('click', function () {
    var open = header.classList.toggle('nav-open');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && header.classList.contains('nav-open')) {
      header.classList.remove('nav-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.focus();
    }
  });
  header.addEventListener('click', function (e) {
    if (e.target.closest('.main-nav a')) { header.classList.remove('nav-open'); toggle.setAttribute('aria-expanded', 'false'); }
  });
})();
