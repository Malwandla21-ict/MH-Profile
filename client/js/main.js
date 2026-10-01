/* main.js — page behaviour for every generated page.
   Handles: starting the motion effects (fx.js), the light/dark toggle,
   in-page links, the Web3Forms contact form, the image lightbox and the
   track switcher on track.html. Content itself comes from profiles.json via
   build/generate_pages.py; nothing here needs editing when content changes. */
(function () {
  'use strict';

  const doc = document.documentElement;
  const root = document.getElementById('top');
  let fx = null;

  const isVisible = (el) => !!el && el.getClientRects().length > 0;
  const store = {
    get() { try { return sessionStorage.getItem('mh-theme'); } catch (e) { return null; } },
    set(v) { try { sessionStorage.setItem('mh-theme', v); } catch (e) { /* private mode: fine */ } },
  };

  /* ---------- Light / dark ---------- */
  // The homepage swaps between two whole layouts, so before switching we note
  // which section is on screen and jump to the same section afterwards.
  function currentSection() {
    const secs = [...document.querySelectorAll('[data-sec]')].filter(isVisible);
    let best = null;
    secs.forEach((s) => { if (s.getBoundingClientRect().top <= innerHeight * 0.4) best = s; });
    return best ? best.dataset.sec : null;
  }

  function labelToggles() {
    const dark = doc.dataset.theme === 'dark';
    document.querySelectorAll('.theme-toggle').forEach((b) => {
      b.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
      b.setAttribute('aria-pressed', String(dark));
    });
  }

  function setTheme(t, remember) {
    const sec = currentSection();
    doc.dataset.theme = t;
    if (remember) store.set(t);
    labelToggles();
    if (sec) {
      const target = [...document.querySelectorAll('[data-sec="' + sec + '"]')].find(isVisible);
      if (target) {
        const prev = doc.style.scrollBehavior;
        doc.style.scrollBehavior = 'auto';
        scrollTo(0, target.getBoundingClientRect().top + scrollY - (sec === 'hero' ? 0 : 64));
        doc.style.scrollBehavior = prev;
      }
    }
    if (fx) requestAnimationFrame(() => fx.refresh());
  }

  document.querySelectorAll('.theme-toggle').forEach((b) =>
    b.addEventListener('click', () => setTheme(doc.dataset.theme === 'dark' ? 'light' : 'dark', true)));
  labelToggles();

  // Follow the device setting live, unless the visitor picked a look themselves
  const mq = matchMedia('(prefers-color-scheme: dark)');
  const onSystem = (e) => { if (!store.get()) setTheme(e.matches ? 'dark' : 'light', false); };
  mq.addEventListener ? mq.addEventListener('change', onSystem) : mq.addListener(onSystem);

  /* ---------- In-page links ----------
     Each homepage layout has its own copy of every section, so "#work" may
     point at the hidden copy. Resolve to whichever copy is showing. */
  function resolveAnchor(id) {
    return [document.getElementById(id), document.getElementById(id + '-b')].find(isVisible) || null;
  }
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href^="#"]');
    if (!a) return;
    const id = a.getAttribute('href').slice(1);
    if (!id) return;
    const target = id === 'top' ? root : resolveAnchor(id);
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    try { history.replaceState(null, '', '#' + id); } catch (err) { /* ignore */ }
  });
  addEventListener('load', () => {
    const id = location.hash.slice(1);
    if (!id) return;
    const t = resolveAnchor(id);
    if (t) setTimeout(() => t.scrollIntoView(), 60);
  });

  /* ---------- Contact form (Web3Forms) ----------
     Posts straight to Web3Forms, which emails the message on. It needs a real
     access key in profiles.json (site.web3formsAccessKey); until then it shows
     a friendly "email me directly" message instead of pretending to send. */
  document.querySelectorAll('form[data-contact]').forEach((form) => {
    const wrap = form.closest('[data-contact-wrap]');
    const sent = wrap && wrap.querySelector('[data-sent]');
    const err = form.querySelector('[data-error]');
    const btn = form.querySelector('button[type="submit"]');
    const label = btn.querySelector('[data-label]');
    const email = form.dataset.email;

    const showError = (text) => { err.textContent = text; err.hidden = false; };
    form.addEventListener('input', () => { err.hidden = true; });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const name = String(fd.get('name') || '').trim();
      const from = String(fd.get('email') || '').trim();
      const message = String(fd.get('message') || '').trim();
      if (fd.get('botcheck')) return; // spam bots tick the hidden box
      if (!name || !/\S+@\S+\.\S+/.test(from) || !message) {
        showError('Please add your name, a valid email and a message.');
        return;
      }
      const key = String(fd.get('access_key') || '');
      label.textContent = 'Sending…';
      btn.disabled = true;
      try {
        if (!key || key.indexOf('YOUR_') === 0) throw new Error('no-key');
        const res = await fetch('https://api.web3forms.com/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify({
            access_key: key, name, email: from, message,
            subject: 'New message from your portfolio site', from_name: 'Portfolio site',
          }),
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.message || 'failed');
        sent.querySelector('[data-sent-name]').textContent = name;
        sent.querySelector('[data-sent-email]').textContent = from;
        form.hidden = true;
        sent.hidden = false;
      } catch (ex) {
        showError("Couldn't send that right now. Please email me directly at " + email + '.');
      } finally {
        label.textContent = 'Send message';
        btn.disabled = false;
      }
    });

    if (sent) {
      const again = sent.querySelector('[data-again]');
      again && again.addEventListener('click', () => {
        form.reset(); err.hidden = true; sent.hidden = true; form.hidden = false;
        form.querySelector('input[name="name"]').focus();
      });
    }
  });

  /* ---------- Slideshows ----------
     Fades to the next image every few seconds. It pauses while the mouse is
     over it, while it's off screen (so hidden slideshows don't churn), and
     never auto-plays for people who've asked their device for less motion.
     The dots jump to an image; on phones you can swipe. */
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const shows = [];
  document.querySelectorAll('[data-slides]').forEach((box, idx) => {
    const slides = [...box.querySelectorAll('.slide')];
    if (slides.length < 2) return;
    const dots = [...box.querySelectorAll('.slide-dots button')];
    const interval = +(box.dataset.interval || 4500);
    let i = 0, timer = 0, paused = false, onscreen = false, first = true;
    // only the showing image can be tabbed to / clicked
    slides.forEach((s, k) => { if (s.hasAttribute('data-zoom')) s.tabIndex = k === 0 ? 0 : -1; });

    const go = (n) => {
      slides[i].classList.remove('is-active');
      slides[i].setAttribute('aria-hidden', 'true');
      if (slides[i].hasAttribute('data-zoom')) slides[i].tabIndex = -1;
      if (dots[i]) dots[i].removeAttribute('aria-current');
      i = (n + slides.length) % slides.length;
      slides[i].classList.add('is-active');
      slides[i].removeAttribute('aria-hidden');
      if (slides[i].hasAttribute('data-zoom')) slides[i].tabIndex = 0;
      if (dots[i]) dots[i].setAttribute('aria-current', 'true');
      // warm up the next image so the fade never shows a blank frame
      const next = slides[(i + 1) % slides.length];
      if (next.loading === 'lazy') next.loading = 'eager';
    };
    const tick = () => {
      clearTimeout(timer);
      if (reduceMotion || paused || !onscreen || document.hidden || !isVisible(box)) return;
      // stagger the first change so neighbouring cards don't all flip at once
      const wait = first ? interval + (idx % 5) * 650 : interval;
      timer = setTimeout(() => { first = false; go(i + 1); tick(); }, wait);
    };

    dots.forEach((d, k) => d.addEventListener('click', (ev) => { ev.stopPropagation(); go(k); tick(); }));
    const host = box.closest('article, [data-tilt], [data-reveal]') || box;
    host.addEventListener('pointerenter', (ev) => { if (ev.pointerType === 'mouse') { paused = true; tick(); } });
    host.addEventListener('pointerleave', () => { paused = false; tick(); });
    box.addEventListener('focusin', () => { paused = true; tick(); });
    box.addEventListener('focusout', () => { paused = false; tick(); });

    // Swipe left/right on touch screens
    let sx = null, sy = 0;
    box.addEventListener('pointerdown', (ev) => { if (ev.pointerType !== 'mouse') { sx = ev.clientX; sy = ev.clientY; } });
    box.addEventListener('pointerup', (ev) => {
      if (sx === null) return;
      const dx = ev.clientX - sx, dy = ev.clientY - sy;
      sx = null;
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) {
        box._swiped = true; // tells the lightbox this wasn't a tap
        go(i + (dx < 0 ? 1 : -1)); tick();
      }
    });

    const io = new IntersectionObserver((en) => { onscreen = en[0].isIntersecting; tick(); }, { threshold: 0.35 });
    io.observe(box);
    shows.push(tick);
  });
  document.addEventListener('visibilitychange', () => shows.forEach((t) => t()));

  /* ---------- Lightbox ---------- */
  const lb = document.querySelector('[data-lightbox]');
  if (lb) {
    const img = lb.querySelector('img');
    const count = lb.querySelector('.lb-count');
    const prevB = lb.querySelector('.lb-prev');
    const nextB = lb.querySelector('.lb-next');
    let list = [], i = 0, opener = null;
    const show = () => {
      img.src = list[i];
      count.textContent = list.length > 1 ? (i + 1) + ' / ' + list.length : '';
      prevB.hidden = nextB.hidden = list.length < 2;
    };
    const open = (srcs, start, from) => {
      list = srcs; i = start; opener = from; show();
      lb.classList.add('open'); lb.setAttribute('aria-hidden', 'false');
      lb.querySelector('.lb-close').focus();
    };
    const close = () => {
      lb.classList.remove('open'); lb.setAttribute('aria-hidden', 'true');
      if (opener) opener.focus();
    };
    const step = (d) => { i = (i + d + list.length) % list.length; show(); };
    document.addEventListener('click', (e) => {
      const z = e.target.closest('[data-zoom]');
      if (!z) return;
      const box = z.closest('[data-slides]');
      if (box && box._swiped) { box._swiped = false; return; }
      try { open(JSON.parse(z.dataset.zoom), +(z.dataset.start || 0), z); } catch (ex) { /* bad data */ }
    });
    document.addEventListener('keydown', (e) => {
      const z = e.target.closest && e.target.closest('[data-zoom]');
      if (z && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); z.click(); return; }
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowRight') step(1);
      if (e.key === 'ArrowLeft') step(-1);
    });
    lb.querySelector('.lb-close').addEventListener('click', close);
    prevB.addEventListener('click', () => step(-1));
    nextB.addEventListener('click', () => step(1));
    lb.addEventListener('click', (e) => { if (e.target === lb) close(); });
  }

  /* ---------- Track switcher (track.html) ----------
     All five tracks are already on the page; this shows one at a time,
     scrambles the heading in and fills the skill bars, without reloading. */
  const tp = document.querySelector('[data-track-page]');
  if (tp) {
    const GLYPHS = 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789#%&*+/<>';
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const panels = [...tp.querySelectorAll('[data-panel]')];
    const tabs = [...tp.querySelectorAll('[data-tab]')];
    const navCv = tp.querySelector('[data-nav-cv]');
    let barTimer = 0, raf = 0;

    const scrambleIn = (el) => {
      const text = el.dataset.text;
      cancelAnimationFrame(raf);
      if (reduce) { el.textContent = text; return; }
      const s = performance.now();
      const stepFn = (now) => {
        const p = Math.min(1, (now - s) / 750), n = Math.floor(p * text.length);
        let o = text.slice(0, n);
        for (let j = n; j < text.length; j++) o += text[j] === ' ' ? ' ' : GLYPHS[(Math.random() * GLYPHS.length) | 0];
        el.textContent = p < 1 ? o : text;
        if (p < 1) raf = requestAnimationFrame(stepFn);
      };
      raf = requestAnimationFrame(stepFn);
    };

    const select = (key, first) => {
      const panel = panels.find((p) => p.dataset.panel === key) || panels[0];
      key = panel.dataset.panel;
      panels.forEach((p) => { p.hidden = p !== panel; });
      tabs.forEach((t) => {
        const on = t.dataset.tab === key;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        // On phones the tab strip scrolls sideways; keep the active tab in view
        if (on && t.parentElement.scrollWidth > t.parentElement.clientWidth) {
          t.parentElement.scrollTo({ left: t.offsetLeft - 8, behavior: first ? 'auto' : 'smooth' });
        }
      });
      if (navCv) navCv.href = panel.dataset.cv;
      document.title = panel.dataset.title;
      try { history.replaceState(null, '', '?t=' + key); } catch (e) { /* file:// in some browsers */ }
      if (!first && scrollY > 0) scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });

      const head = panel.querySelector('[data-head]');
      if (head) scrollY < innerHeight ? scrambleIn(head) : (head.textContent = head.dataset.text);

      const bars = [...panel.querySelectorAll('[data-level]')];
      bars.forEach((b) => { b.style.transition = 'none'; b.style.width = '0%'; });
      clearTimeout(barTimer);
      barTimer = setTimeout(() => bars.forEach((b, j) => {
        b.style.transition = '';
        b.style.transitionDelay = (j * 90) + 'ms';
        b.style.width = b.dataset.level + '%';
      }), first ? 300 : 80);

      if (fx) requestAnimationFrame(() => fx.refresh());
    };

    tp.addEventListener('click', (e) => {
      const t = e.target.closest('[data-tab],[data-go]');
      if (!t) return;
      const key = t.dataset.tab || t.dataset.go;
      if (t.dataset.tab && t.getAttribute('aria-selected') === 'true') return;
      select(key);
    });
    // Arrow keys move between tabs, like a native tab strip
    tp.querySelector('[role="tablist"]').addEventListener('keydown', (e) => {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      const i = tabs.findIndex((t) => t.getAttribute('aria-selected') === 'true');
      const n = tabs[(i + (e.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length];
      n.focus(); select(n.dataset.tab);
    });

    let start = 'software';
    try { start = new URLSearchParams(location.search).get('t') || start; } catch (e) { /* ignore */ }
    select(start, true);
  }

  /* ---------- Motion ---------- */
  if (window.MHFX && root) fx = window.MHFX.init(root);
})();
