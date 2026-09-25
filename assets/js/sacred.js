/* Sacred images: the popup, and the "reveal another" picker on the wall page.
   The catalogue is embedded as JSON by layouts/partials/sacred-data.html. */
(function () {
  'use strict';

  var payload = document.getElementById('sacred-images');
  if (!payload) return;

  var images = [];
  try { images = JSON.parse(payload.textContent) || []; } catch (e) { return; }
  if (!images.length) return;

  /* The page's own words, from i18n/ via sacred-data.html, with {placeholders}.
     The fallbacks are the English, for a page that somehow lacks them. */
  var strings = {};
  var stringsEl = document.getElementById('sacred-strings');
  try { strings = JSON.parse(stringsEl ? stringsEl.textContent : '{}') || {}; } catch (e) {}
  var say = function (key, fallback, values) {
    return (strings[key] || fallback).replace(/\{(\w+)\}/g, function (m, k) {
      return k in values ? values[k] : m;
    });
  };

  var nf = new Intl.NumberFormat(document.documentElement.lang || undefined);
  var fmt = function (n) { return typeof n === 'number' ? nf.format(n) : String(n); };

  /* The popup has room for a line, not a table. Takes the first three recorded
     values — which fields those are is the author's decision, since `record` is
     kept in the order they wrote it. */
  var metaLine = function (im) {
    return (im.record || []).slice(0, 3)
      .map(function (r) { return r.value; })
      .filter(Boolean)
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
      img.alt = im.title;
    }
    var set = function (field, value) {
      var el = root.querySelector('[data-field="' + field + '"]');
      if (el) el.textContent = value;
    };
    set('no', say('popupNo', 'SACRED IMAGE № {no}', { no: fmt(im.no) }));
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
      if (counter) counter.textContent = say('wallShowing', 'Showing {shown} of {total}', { shown: fmt(shownCount), total: fmt(images.length) });
      if (!wall.querySelector('img[hidden]')) moreBtn.remove();
    });
  }

  /* The reveal on the Sacred Images page is painted by an inline script in
     layouts/images/section.html — it has to run before first paint. */
})();
