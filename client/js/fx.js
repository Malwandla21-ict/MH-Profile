(function () {
  const C = 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789#%&*+/<>';
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const EASE = 'cubic-bezier(.2,.7,.2,1)';

  function scramble(el, dur) {
    if (!el.dataset.text) el.dataset.text = el.textContent;
    const t = el.dataset.text;
    dur = dur || +(el.dataset.dur || 650);
    cancelAnimationFrame(el._sr);
    const s = performance.now();
    const step = (now) => {
      const p = clamp((now - s) / dur);
      const n = Math.floor(p * t.length);
      let o = t.slice(0, n);
      for (let i = n; i < t.length; i++) o += /\s/.test(t[i]) ? t[i] : C[(Math.random() * C.length) | 0];
      el.textContent = p < 1 ? o : t;
      if (p < 1) el._sr = requestAnimationFrame(step);
    };
    el._sr = requestAnimationFrame(step);
  }

  function init(root, opts = {}) {
    if (!root) return { destroy() {}, refresh() {} };
    const reduce = opts.reduce || matchMedia('(prefers-reduced-motion: reduce)').matches;
    const timers = [];

    const io = new IntersectionObserver((es) => es.forEach((en) => {
      if (!en.isIntersecting) return;
      const el = en.target; io.unobserve(el);
      if (el._riseEl) { const r = el._riseEl; requestAnimationFrame(() => { r.style.transform = 'none'; }); return; }
      if (el.hasAttribute('data-reveal') || el.hasAttribute('data-rise')) requestAnimationFrame(() => { el.style.opacity = 1; el.style.transform = 'none'; });
      if (el.hasAttribute('data-scramble') && !reduce) timers.push(setTimeout(() => scramble(el), +(el.dataset.delay || 0)));
    }), { threshold: 0.12, rootMargin: '0px 0px -5% 0px' });

    function refresh() {
      root.querySelectorAll('[data-reveal],[data-rise],[data-scramble]').forEach((el) => {
        if (el._fx) return; el._fx = 1;
        const d = (el.dataset.delay || 0) + 'ms';
        if (!reduce && el.hasAttribute('data-reveal')) {
          el.style.opacity = 0; el.style.transform = 'translateY(28px)';
          el.style.transition = `opacity .9s ${EASE} ${d}, transform .9s ${EASE} ${d}`;
        }
        if (!reduce && el.hasAttribute('data-rise')) {
          el.style.transform = 'translateY(108%)';
          el.style.transition = `transform 1.2s cubic-bezier(.16,1,.3,1) ${d}`;
          let w = el.parentElement;
          while (w && w !== root && !(w.style && w.style.clipPath)) w = w.parentElement;
          const proxy = document.createElement('span');
          proxy.style.cssText = 'position:absolute;inset:0;pointer-events:none;';
          const host = (w && w !== root) ? w : el.parentElement;
          if (getComputedStyle(host).position === 'static') host.style.position = 'relative';
          host.appendChild(proxy); proxy._riseEl = el;
          io.observe(proxy);
          return;
        }
        io.observe(el);
      });
      root.querySelectorAll('[data-scramble-host]').forEach((h) => {
        if (h._sh) return; h._sh = 1;
        h.addEventListener('pointerenter', () => {
          if (reduce) return;
          (h.hasAttribute('data-scramble-hover') ? [h] : h.querySelectorAll('[data-scramble-hover]')).forEach((el) => scramble(el, 420));
        });
      });
      root.querySelectorAll('[data-stack]').forEach((c, i) => { c.style.top = (96 + i * 22) + 'px'; });
    }

    let mx = innerWidth * 0.7, my = innerHeight * 0.35, raf = 0;
    function frame() {
      raf = 0;
      root.style.setProperty('--mx', mx + 'px');
      root.style.setProperty('--my', my + 'px');
      root.querySelectorAll('[data-glow]').forEach((el) => {
        const b = el.getBoundingClientRect();
        el.style.setProperty('--gx', (mx - b.left) + 'px');
        el.style.setProperty('--gy', (my - b.top) + 'px');
      });
      if (reduce) return;
      root.querySelectorAll('[data-magnetic]').forEach((el) => {
        const b = el.getBoundingClientRect();
        const dx = mx - (b.left + b.width / 2), dy = my - (b.top + b.height / 2);
        const R = Math.max(b.width, b.height) / 2 + 56;
        if (Math.hypot(dx, dy) < R) {
          el.style.transition = 'transform .25s ease-out';
          el.style.transform = `translate(${dx * 0.32}px, ${dy * 0.42}px)`;
        } else if (el.style.transform) {
          el.style.transition = 'transform .7s cubic-bezier(.2,1.8,.4,1)';
          el.style.transform = '';
        }
      });
      root.querySelectorAll('[data-tilt]').forEach((el) => {
        const b = el.getBoundingClientRect();
        const nx = (mx - (b.left + b.width / 2)) / innerWidth, ny = (my - (b.top + b.height / 2)) / innerHeight;
        el.style.transform = `perspective(1100px) rotateY(${nx * 16}deg) rotateX(${-ny * 16}deg)`;
      });
    }
    const onMove = (e) => { mx = e.clientX; my = e.clientY; if (!raf) raf = requestAnimationFrame(frame); };

    function onScroll() {
      const vh = innerHeight, vw = innerWidth;
      if (!reduce) {
        root.querySelectorAll('[data-drift]').forEach((el) => {
          const host = el.closest('[data-drift-host]') || root;
          const top = Math.min(0, host.getBoundingClientRect().top);
          el.style.transform = `translate3d(${top * +el.dataset.drift}px,0,0)`;
        });
        root.querySelectorAll('[data-parallax]').forEach((el) => {
          const b = el.parentElement.getBoundingClientRect();
          el.style.transform = `translate3d(0,${(b.top + b.height / 2 - vh / 2) * +el.dataset.parallax}px,0) scale(1.18)`;
        });
      }
      root.querySelectorAll('[data-hscroll]').forEach((sec) => {
        const track = sec.querySelector('[data-htrack]'), stick = sec.querySelector('[data-hstick]');
        if (!track || !stick) return;
        const narrow = vw < 820 || reduce;
        if (narrow) {
          sec.style.height = 'auto'; stick.style.position = 'relative'; stick.style.height = 'auto';
          track.style.transform = 'none'; track.style.flexDirection = 'column'; track.style.width = 'auto';
          return;
        }
        stick.style.position = 'sticky'; stick.style.height = '100vh';
        track.style.flexDirection = 'row'; track.style.width = 'max-content';
        const dist = Math.max(0, track.scrollWidth - vw);
        sec.style.height = (dist + vh) + 'px';
        const p = dist ? clamp(-sec.getBoundingClientRect().top / dist) : 0;
        track.style.transform = `translate3d(${-p * dist}px,0,0)`;
        const n = track.children.length;
        const cnt = sec.querySelector('[data-hcount]');
        if (cnt) cnt.textContent = String(Math.min(n, Math.round(p * (n - 1)) + 1)).padStart(2, '0');
        const bar = sec.querySelector('[data-hbar]');
        if (bar) bar.style.transform = `scaleX(${p})`;
      });
      root.querySelectorAll('[data-words]').forEach((c) => {
        const b = c.getBoundingClientRect();
        const p = reduce ? 1 : clamp((vh * 0.82 - b.top) / (b.height + vh * 0.25));
        const ws = c.querySelectorAll('[data-word]');
        ws.forEach((w, i) => { w.style.opacity = (i + 0.5) / ws.length <= p ? 1 : 0.16; });
      });
      if (!reduce) {
        const cards = [...root.querySelectorAll('[data-stack]')];
        cards.forEach((c, i) => {
          const inner = c.firstElementChild, next = cards[i + 1];
          if (!inner || !next) return;
          const p = clamp(1 - (next.getBoundingClientRect().top - c.getBoundingClientRect().top) / (vh * 0.75));
          inner.style.transform = `scale(${1 - p * 0.06})`;
          inner.style.filter = `brightness(${1 - p * 0.45})`;
        });
      }
    }

    root.querySelectorAll('[data-cycle]').forEach((el) => {
      const words = (el.dataset.cycle || '').split('|'); let i = 0;
      if (reduce || words.length < 2) return;
      timers.push(setInterval(() => { i = (i + 1) % words.length; el.dataset.text = words[i]; scramble(el, 600); }, 2600));
    });

    refresh();
    addEventListener('pointermove', onMove, { passive: true });
    document.addEventListener('scroll', onScroll, { passive: true, capture: true });
    addEventListener('resize', onScroll);
    onScroll(); frame();
    timers.push(setTimeout(onScroll, 400));

    return {
      refresh() { refresh(); onScroll(); },
      destroy() {
        removeEventListener('pointermove', onMove);
        document.removeEventListener('scroll', onScroll, { capture: true });
        removeEventListener('resize', onScroll);
        io.disconnect(); timers.forEach((t) => { clearTimeout(t); clearInterval(t); });
      },
    };
  }

  window.MHFX = { init, scramble };
})();
