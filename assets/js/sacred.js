/* Sacred images: the popup, and the "reveal another" picker on the wall page.
   The catalogue is embedded as JSON by layouts/partials/popup.html. */
(function () {
  'use strict';

  var payload = document.getElementById('sacred-images');
  if (!payload) return;

  var images = [];
  try { images = JSON.parse(payload.textContent) || []; } catch (e) { return; }
  if (!images.length) return;

  var fmt = function (n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ','); };

  /* Metadata line: only the fields actually recorded. */
  var metaLine = function (im) {
    return [im.mount, im.carried, im.filed]
      .filter(function (v) { return v && v !== 'not recorded'; })
      .join(' · ');
  };

  /* Pick an index other than `avoid`, so "reveal another" always changes. */
  var pick = function (avoid) {
    if (images.length === 1) return 0;
    var n = avoid;
    while (n === avoid) n = Math.floor(Math.random() * images.length);
    return n;
  };

  /* --------------------------------------------------------------- popup --- */

  var scrim = document.querySelector('[data-sacred-popup]');
  var current = -1;
  var lastFocus = null;

  var paint = function (root, i) {
    var im = images[i];
    var img = root.querySelector('[data-field="img"]');
    if (img) {
      img.src = im.url;
      img.style.objectPosition = im.position;
      img.alt = im.title;
    }
    var set = function (field, value) {
      var el = root.querySelector('[data-field="' + field + '"]');
      if (el) el.textContent = value;
    };
    set('no', 'SACRED IMAGE № ' + fmt(im.no));
    set('title', im.title);
    set('meta', metaLine(im));
  };

  var open = function (i) {
    if (!scrim) return;
    lastFocus = document.activeElement;
    current = typeof i === 'number' ? i : pick(current);
    paint(scrim, current);
    scrim.hidden = false;
    document.body.style.overflow = 'hidden';
    var close = scrim.querySelector('[data-sacred-close]');
    if (close) close.focus();
  };

  var close = function () {
    if (!scrim || scrim.hidden) return;
    scrim.hidden = true;
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  };

  if (scrim) {
    scrim.addEventListener('click', function (e) {
      if (e.target === scrim || e.target.closest('[data-sacred-close]')) close();
      else if (e.target.closest('[data-sacred-another]')) { current = pick(current); paint(scrim, current); }
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  }

  document.addEventListener('click', function (e) {
    var trigger = e.target.closest('[data-sacred-open]');
    if (!trigger) return;
    e.preventDefault();
    var idx = trigger.getAttribute('data-sacred-open');
    open(idx === '' || idx === null ? undefined : parseInt(idx, 10));
  });

  /* ------------------------------------------------ the wall's "show more" --- */

  var wall = document.querySelector('[data-wall]');
  var moreBtn = document.querySelector('[data-wall-more]');
  if (wall && moreBtn) {
    var step = parseInt(wall.getAttribute('data-wall-step'), 10) || 12;
    moreBtn.addEventListener('click', function () {
      var hidden = wall.querySelectorAll('img[hidden]');
      Array.prototype.slice.call(hidden, 0, step).forEach(function (img) { img.hidden = false; });

      var shownCount = wall.querySelectorAll('img:not([hidden])').length;
      var counter = document.querySelector('[data-wall-count]');
      if (counter) counter.textContent = 'Showing ' + shownCount + ' of ' + images.length;
      if (!wall.querySelector('img[hidden]')) moreBtn.remove();
    });
  }

  /* The reveal on the Sacred Images page is painted by an inline script in
     layouts/images/section.html — it has to run before first paint. */
})();
