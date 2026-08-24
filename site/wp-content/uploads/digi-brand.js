/* ============================================================
   Digicomplish — navbar green detector.
   The client wants: WHEN a header bar's background actually turns
   green, its text becomes white; OTHERWISE the header is left
   exactly as it was. This script only ADDS/REMOVES the
   `.nav-on-green` class (styled in digi-brand.css) — it never
   changes any colour directly, so non-green states stay original.
   ============================================================ */
(function () {
  'use strict';

  // Brand accent is #FF9B00 => rgb(255,155,0). Treat a surface as "accent"
  // when it is opaque and clearly warm/orange-dominant (red high, blue low).
  function isAccent(bg) {
    if (!bg) return false;
    var m = bg.match(/rgba?\(([^)]+)\)/);
    if (!m) return false;
    var p = m[1].split(',').map(function (n) { return parseFloat(n); });
    var r = p[0], g = p[1], b = p[2], a = p.length > 3 ? p[3] : 1;
    if (a < 0.5) return false;                 // transparent => not accent
    return r > 180 && (r - b) > 90 && g < 210 && (g - b) > 40;
  }

  function bars() {
    return document.querySelectorAll('header .vamtam-sticky-header, header .elementor-sticky');
  }

  function update() {
    bars().forEach(function (bar) {
      var accent = isAccent(getComputedStyle(bar).backgroundColor);
      bar.classList.toggle('nav-on-accent', accent);
    });
  }

  // Buttons: when a button's own background actually turns green (e.g. the
  // theme's green hover fill), give it white text. Non-green buttons
  // (transparent / underline styles) are never touched.
  function markBtn(btn) {
    if (!btn) return;
    btn.classList.toggle('btn-on-accent', isAccent(getComputedStyle(btn).backgroundColor));
  }
  function btnFrom(e) {
    var t = e.target;
    return t && t.closest ? t.closest('.elementor-button') : null;
  }
  function bindButtons() {
    // Delegated hover — measured AFTER the hover style applies (rAF).
    document.addEventListener('mouseover', function (e) {
      var b = btnFrom(e); if (b) requestAnimationFrame(function () { markBtn(b); });
    }, true);
    document.addEventListener('focusin', function (e) {
      var b = btnFrom(e); if (b) requestAnimationFrame(function () { markBtn(b); });
    }, true);
    document.addEventListener('mouseout', function (e) {
      var b = btnFrom(e); if (b) b.classList.remove('btn-on-accent');
    }, true);
    document.addEventListener('focusout', function (e) {
      var b = btnFrom(e); if (b) b.classList.remove('btn-on-accent');
    }, true);
    // Also catch buttons that are green in their RESTING state.
    document.querySelectorAll('.elementor-button').forEach(markBtn);
  }

  // ---------- Home hero slider: advance the slides one by one ----------
  function initSliders() {
    document.querySelectorAll('.digi-slider').forEach(function (root) {
      var slides = [].slice.call(root.querySelectorAll('.digi-slide'));
      if (slides.length < 2) return;
      var dotsWrap = root.querySelector('.digi-slider-dots');
      var progressEl = root.querySelector('.digi-slider-progress > span');
      var delay = parseInt(root.getAttribute('data-interval'), 10) || 6000;
      var section = root.closest('.elementor-top-section') || document;
      var vids = [].slice.call(section.querySelectorAll('.digi-hero-vid'));
      var hasVid = vids.length >= slides.length && vids.length > 0;
      var durEls = slides.map(function (s) { return s.querySelector('.digi-slide-dur'); });
      var i = Math.max(0, slides.findIndex(function (s) { return s.classList.contains('is-active'); }));
      var timer = null, fallback = null, dots = [];

      function fmt(t) { if (!isFinite(t) || t < 0) t = 0; var m = Math.floor(t / 60), s = Math.floor(t % 60); return m + ':' + (s < 10 ? '0' : '') + s; }
      function paint(p) { if (progressEl) progressEl.style.width = (Math.max(0, Math.min(1, p)) * 100) + '%'; }
      function fallbackTimer() { clearTimeout(fallback); fallback = setTimeout(function () { show(i + 1); }, delay); }

      function activateVideo(n) {
        vids.forEach(function (v, k) {
          v.classList.toggle('is-active', k === n);
          if (k !== n) { try { v.pause(); } catch (e) {} }
        });
        var v = vids[n]; if (!v) return;
        if (v.getAttribute('preload') === 'none') { v.setAttribute('preload', 'auto'); try { v.load(); } catch (e) {} }
        var nx = vids[(n + 1) % vids.length];            // warm up the next clip
        if (nx && nx.getAttribute('preload') === 'none') { nx.setAttribute('preload', 'metadata'); try { nx.load(); } catch (e) {} }
        try { v.currentTime = 0; } catch (e) {}
        var pr = v.play();
        if (pr && pr.catch) pr.catch(function () { fallbackTimer(); });  // autoplay blocked -> keep advancing
      }
      function setDur(n) { var v = vids[n], el = durEls[n]; if (v && el && isFinite(v.duration)) el.textContent = fmt(v.duration); }

      function show(n) {
        i = (n + slides.length) % slides.length;
        slides.forEach(function (s, k) { s.classList.toggle('is-active', k === i); });
        dots.forEach(function (d, k) { d.classList.toggle('is-active', k === i); d.setAttribute('aria-selected', k === i ? 'true' : 'false'); });
        paint(0);
        if (hasVid) { clearTimeout(fallback); activateVideo(i); setDur(i); }
      }
      function start() { if (hasVid) return; stop(); timer = setInterval(function () { show(i + 1); }, delay); }
      function stop() { if (timer) { clearInterval(timer); timer = null; } }

      if (dotsWrap) {
        slides.forEach(function (_, k) {
          var b = document.createElement('button');
          b.type = 'button'; b.setAttribute('role', 'tab'); b.setAttribute('aria-label', 'Go to slide ' + (k + 1));
          b.addEventListener('click', function () { show(k); if (!hasVid) start(); });
          dotsWrap.appendChild(b); dots.push(b);
        });
      }

      if (hasVid) {
        vids.forEach(function (v, k) {
          v.muted = true; v.setAttribute('muted', ''); v.setAttribute('playsinline', '');
          v.addEventListener('loadedmetadata', function () { setDur(k); if (k === i) paint(0); });
          v.addEventListener('timeupdate', function () {
            if (k === i && isFinite(v.duration) && v.duration > 0) {
              paint(v.currentTime / v.duration);
              if (durEls[k]) durEls[k].textContent = fmt(Math.max(0, v.duration - v.currentTime));
            }
          });
          v.addEventListener('ended', function () { if (k === i) show(i + 1); });
          v.addEventListener('error', function () { if (k === i) fallbackTimer(); });
        });
        show(i);
        root.addEventListener('mouseenter', function () { var v = vids[i]; if (v) try { v.pause(); } catch (e) {} });
        root.addEventListener('mouseleave', function () { var v = vids[i]; if (v) try { v.play(); } catch (e) {} });
        document.addEventListener('visibilitychange', function () {
          var v = vids[i]; if (!v) return;
          if (document.hidden) { try { v.pause(); } catch (e) {} } else { try { v.play(); } catch (e) {} }
        });
      } else {
        show(i); start();
        root.addEventListener('mouseenter', stop);
        root.addEventListener('mouseleave', start);
        document.addEventListener('visibilitychange', function () { if (document.hidden) { stop(); } else { start(); } });
      }
    });
  }

  // ---------- Stat counters: numbers count up when scrolled into view ----------
  function initCounters() {
    var els = [].slice.call(document.querySelectorAll('.digi-count, .digi-stat .big'));
    if (!els.length) return;

    var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Parse "1000+", "100%", "3+" into prefix / number / suffix, then zero it out.
    els = els.filter(function (el) {
      var m = el.textContent.trim().match(/^(\D*?)([\d.,]+)(\D*)$/);
      if (!m) return false;
      el.setAttribute('data-pre', m[1]);
      el.setAttribute('data-target', m[2].replace(/,/g, ''));
      el.setAttribute('data-suf', m[3]);
      if (!reduced) el.textContent = m[1] + '0' + m[3];
      return true;
    });
    if (reduced || !els.length) return;

    function run(el) {
      if (el.getAttribute('data-counted')) return;
      el.setAttribute('data-counted', '1');
      var pre = el.getAttribute('data-pre') || '';
      var suf = el.getAttribute('data-suf') || '';
      var target = parseFloat(el.getAttribute('data-target'));
      var dec = (el.getAttribute('data-target').split('.')[1] || '').length;
      var dur = 1800, start = null;
      function step(ts) {
        if (start === null) start = ts;
        var p = Math.min(1, (ts - start) / dur);
        var eased = 1 - Math.pow(1 - p, 3);            // ease-out cubic
        var v = target * eased;
        el.textContent = pre + (dec ? v.toFixed(dec) : Math.round(v)) + suf;
        if (p < 1) requestAnimationFrame(step);
        else el.textContent = pre + (dec ? target.toFixed(dec) : target) + suf;
      }
      requestAnimationFrame(step);
    }

    function inView(el) {
      var r = el.getBoundingClientRect();
      var vh = window.innerHeight || document.documentElement.clientHeight;
      return r.top < vh * 0.9 && r.bottom > 0;
    }
    function pending() { return els.filter(function (el) { return !el.getAttribute('data-counted'); }); }

    // Deliberately synchronous: gating this behind requestAnimationFrame would
    // deadlock in a background tab (rAF is frozen, so the "ticking" flag would
    // never reset and the counters would stay at zero forever). Only a handful
    // of elements are measured, so the cost is negligible.
    function check() {
      pending().forEach(function (el) { if (inView(el)) run(el); });
      if (!pending().length) {
        window.removeEventListener('scroll', check);
        window.removeEventListener('resize', check);
      }
    }

    // Scroll-driven check is the primary trigger — it works even where
    // IntersectionObserver callbacks are throttled (e.g. background tabs).
    window.addEventListener('scroll', check, { passive: true });
    window.addEventListener('resize', check, { passive: true });
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { run(e.target); io.unobserve(e.target); }
        });
      }, { threshold: 0.35 });
      els.forEach(function (el) { io.observe(el); });
    }
    check();
    // Re-check once the tab becomes visible (counters parked off-screen in a
    // background tab would otherwise sit at zero).
    document.addEventListener('visibilitychange', function () { if (!document.hidden) check(); });
    // Failsafe: never leave a stat stuck showing 0 — if anything above failed,
    // snap any still-pending, already-visible counter to its final value.
    setTimeout(function () {
      pending().forEach(function (el) {
        if (inView(el)) {
          el.setAttribute('data-counted', '1');
          el.textContent = (el.getAttribute('data-pre') || '') +
                           el.getAttribute('data-target') +
                           (el.getAttribute('data-suf') || '');
        }
      });
    }, 5000);
  }

  // ---------- Solutions mega-menu placement ----------
  // The theme's smartmenus script writes an inline `left` on every open
  // sub-menu, which beats CSS. So instead of fighting it in the stylesheet we
  // re-place the panel here (fixed + centred under the header) whenever it is
  // shown, and re-assert it on resize/scroll.
  function initMega() {
    var panels = [].slice.call(document.querySelectorAll('ul.sub-menu.digi-mega'));
    if (!panels.length) return;

    function place(panel) {
      if (window.innerWidth <= 1024) {           // drawer mode — leave to CSS
        ['position', 'left', 'top', 'transform', 'width'].forEach(function (p) {
          panel.style.removeProperty(p);
        });
        return;
      }
      // Position the panel exactly under the VISIBLE nav bar (not the whole
      // <header>, whose height includes stacked spacer/mobile bars) so it opens
      // beneath the navbar instead of over it.
      var bar = panel.closest('.vamtam-sticky-header') || panel.closest('header');
      var br = bar ? bar.getBoundingClientRect() : null;
      var bottom = br ? br.bottom : 80;
      if (bottom <= 0 || bottom > 200) {                 // sanity clamp
        var fx = document.querySelector('header .vamtam-sticky-header--fixed, header .vamtam-sticky-header');
        bottom = fx ? fx.getBoundingClientRect().height || 80 : 80;
      }
      var w = Math.min(1260, document.documentElement.clientWidth - 48);
      panel.style.setProperty('position', 'fixed', 'important');
      panel.style.setProperty('left', '50%', 'important');
      panel.style.setProperty('transform', 'translateX(-50%)', 'important');
      panel.style.setProperty('top', Math.max(0, bottom) + 'px', 'important');
      panel.style.setProperty('width', w + 'px', 'important');
      panel.style.setProperty('margin', '0', 'important');
    }

    function visible(el) {
      var cs = getComputedStyle(el);
      return cs.display !== 'none' && cs.visibility !== 'hidden';
    }

    panels.forEach(function (panel) {
      // re-place whenever smartmenus toggles it
      try {
        new MutationObserver(function () { if (visible(panel)) place(panel); })
          .observe(panel, { attributes: true, attributeFilter: ['style', 'class'] });
      } catch (e) { /* observer unsupported — hover handler below still covers it */ }
      var li = panel.closest('li');
      if (li) {
        li.addEventListener('mouseenter', function () { setTimeout(function () { place(panel); }, 0); });
        li.addEventListener('focusin', function () { place(panel); });
      }
    });
    window.addEventListener('resize', function () {
      panels.forEach(function (p) { if (visible(p)) place(p); });
    }, { passive: true });
    window.addEventListener('scroll', function () {
      panels.forEach(function (p) { if (visible(p)) place(p); });
    }, { passive: true });
  }

  function boot() {
    update();
    bindButtons();
    initSliders();
    initCounters();
    initMega();
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update, { passive: true });
    // Catch class/style changes made by the theme's sticky script.
    try {
      var mo = new MutationObserver(update);
      bars().forEach(function (bar) {
        mo.observe(bar, { attributes: true, attributeFilter: ['class', 'style'] });
      });
    } catch (e) { /* MutationObserver unsupported — scroll/resize still cover it */ }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();

/* ---------- Page-load transition ("movie switch" wipe) ---------- */
(function () {
  try {
    function run() {
      if (document.getElementById('dc-pagefx')) return;
      var fx = document.createElement('div');
      fx.id = 'dc-pagefx';
      for (var i = 0; i < 5; i++) fx.appendChild(document.createElement('span'));
      document.body.appendChild(fx);
      document.body.classList.add('dc-fx-in');
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { fx.classList.add('is-done'); });
      });
      setTimeout(function () { if (fx && fx.parentNode) fx.parentNode.removeChild(fx); }, 1300);
    }
    if (document.body) run(); else document.addEventListener('DOMContentLoaded', run);
  } catch (e) { /* no-op */ }
})();
