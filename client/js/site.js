/* site.js — shared behaviour for all generated pages (index.html + role pages).
   Handles: theme toggle, footer year, contact form, image galleries,
   and the skill-bar fill animation. No profile-switching logic lives here —
   each page is now a real static page generated from data/profiles.json
   by build/generate_pages.py. */

(function () {
  "use strict";

  /* ---------- Theme toggle ---------- */
  function initTheme() {
    const root = document.body;
    const toggleBtn = document.getElementById("themeToggle");
    // No localStorage dependency — theme choice is session-only. The initial
    // value respects the visitor's OS-level color-scheme preference instead
    // of always forcing dark; the toggle still overrides it for the session.
    const applyLight = (isLight) => {
      root.classList.toggle("light", isLight);
      if (!toggleBtn) return;
      const darkIcon = toggleBtn.querySelector(".theme-icon-dark");
      const lightIcon = toggleBtn.querySelector(".theme-icon-light");
      if (darkIcon && lightIcon) {
        darkIcon.classList.toggle("hidden", isLight);
        lightIcon.classList.toggle("hidden", !isLight);
      }
      toggleBtn.setAttribute("aria-pressed", String(isLight));
    };

    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    applyLight(!prefersDark);

    if (toggleBtn) {
      toggleBtn.addEventListener("click", () => {
        const nowLight = !root.classList.contains("light");
        applyLight(nowLight);
      });
    }
  }

  /* ---------- Mobile nav (hamburger disclosure) ---------- */
  function initMobileNav() {
    const toggle = document.getElementById("mobileNavToggle");
    const panel = document.getElementById("mobileNav");
    if (!toggle || !panel) return;

    const openIcon = toggle.querySelector(".menu-icon-open");
    const closeIcon = toggle.querySelector(".menu-icon-close");

    const setOpen = (isOpen) => {
      panel.classList.toggle("is-open", isOpen);
      toggle.setAttribute("aria-expanded", String(isOpen));
      toggle.setAttribute("aria-label", isOpen ? "Close menu" : "Open menu");
      if (openIcon && closeIcon) {
        openIcon.classList.toggle("hidden", isOpen);
        closeIcon.classList.toggle("hidden", !isOpen);
      }
    };

    toggle.addEventListener("click", () => {
      setOpen(!panel.classList.contains("is-open"));
    });

    // Picking a link should close the menu rather than leave it open
    // underneath the page it just navigated (or scrolled) to.
    panel.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => setOpen(false));
    });

    // If the viewport grows past the mobile breakpoint while the menu is
    // open (e.g. rotating a tablet, or resizing a desktop window), the
    // desktop nav takes over — don't leave the mobile panel stuck open
    // underneath it.
    const desktopQuery = window.matchMedia("(min-width: 768px)");
    const handleBreakpointChange = (e) => {
      if (e.matches) setOpen(false);
    };
    if (desktopQuery.addEventListener) {
      desktopQuery.addEventListener("change", handleBreakpointChange);
    }

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && panel.classList.contains("is-open")) {
        setOpen(false);
        toggle.focus();
      }
    });
  }

  /* ---------- Footer year ---------- */
  function initFooterYear() {
    const el = document.getElementById("year");
    if (el) el.textContent = String(new Date().getFullYear());
  }

  /* ---------- Contact form (Web3Forms) ----------
     Submits directly to Web3Forms's API — no backend of my own required.
     Needs a real access_key (see the hidden input generate_pages.py renders,
     sourced from site.web3formsAccessKey in profiles.json) to actually
     deliver mail; until that's set, submissions will fail gracefully with
     the error status message below. */
  function initContactForm() {
    const form = document.getElementById("contactForm");
    const status = document.getElementById("contactStatus");
    if (!form) return;

    const showStatus = (message, isError) => {
      if (!status) return;
      status.textContent = message;
      status.classList.remove("hidden", "text-secondary", "text-red-400");
      status.classList.add("fade-in-text", isError ? "text-red-400" : "text-secondary");
    };

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalLabel = submitBtn ? submitBtn.textContent : "";
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Sending…";
      }

      try {
        const response = await fetch("https://api.web3forms.com/submit", {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify(Object.fromEntries(new FormData(form))),
        });
        const result = await response.json().catch(() => ({}));

        if (response.ok && result.success) {
          showStatus("Thanks — your message has been sent!", false);
          form.reset();
        } else {
          showStatus("Something went wrong. Please try again or email me directly.", true);
        }
      } catch (err) {
        showStatus("Something went wrong. Please try again or email me directly.", true);
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = originalLabel;
        }
      }
    });
  }

  /* ---------- Image galleries (per-project mini gallery) ---------- */
  const CROSSFADE_MS = 150; // keep in sync with .gallery-img transition duration in style.css

  function setupGallery(root) {
    let images;
    try {
      images = JSON.parse(root.dataset.images || "[]");
    } catch (err) {
      images = [];
    }
    if (!Array.isArray(images) || images.length < 2) return;

    const imgEl = root.querySelector(".gallery-img");
    const dots = Array.from(root.querySelectorAll(".gallery-dot"));
    const prevBtn = root.querySelector(".gallery-prev");
    const nextBtn = root.querySelector(".gallery-next");
    let index = 0;

    function show(nextIndex) {
      if (!imgEl || nextIndex === index) return;
      index = (nextIndex + images.length) % images.length;
      root.dataset.currentIndex = String(index); // so the lightbox opens on the image you were already viewing
      imgEl.style.opacity = "0";
      window.setTimeout(() => {
        imgEl.src = images[index];
        imgEl.style.opacity = "1";
      }, CROSSFADE_MS);

      dots.forEach((dot, i) => {
        // The visible indicator is a small inner <span> — the button
        // itself is just an enlarged (32px) touch target around it.
        const indicator = dot.querySelector("span");
        if (!indicator) return;
        indicator.classList.toggle("bg-primary", i === index);
        indicator.classList.toggle("bg-white/30", i !== index);
      });
    }

    if (prevBtn) prevBtn.addEventListener("click", () => show(index - 1));
    if (nextBtn) nextBtn.addEventListener("click", () => show(index + 1));
    dots.forEach((dot, i) => dot.addEventListener("click", () => show(i)));
  }

  function initGalleries() {
    document.querySelectorAll(".gallery").forEach(setupGallery);
  }

  /* ---------- Lightbox — click any project image to view it full-size ----------
     One shared overlay per page (#lightbox). Works for both single-image and
     multi-image project-media blocks; multi-image ones open on whichever
     screenshot was currently showing, not always the first. */
  function initLightbox() {
    const overlay = document.getElementById("lightbox");
    const imgEl = document.getElementById("lightboxImg");
    const closeBtn = document.getElementById("lightboxClose");
    const prevBtn = document.getElementById("lightboxPrev");
    const nextBtn = document.getElementById("lightboxNext");
    const media = document.querySelectorAll(".project-media[data-images]");
    if (!overlay || !imgEl || !media.length) return;

    let images = [];
    let index = 0;

    function render() {
      imgEl.style.opacity = "0";
      window.setTimeout(() => {
        imgEl.src = images[index];
        imgEl.style.opacity = "1";
      }, CROSSFADE_MS);
      const multi = images.length > 1;
      prevBtn.hidden = !multi;
      nextBtn.hidden = !multi;
    }

    function open(el) {
      try {
        images = JSON.parse(el.dataset.images || "[]");
      } catch (err) {
        images = [];
      }
      if (!images.length) return;
      index = parseInt(el.dataset.currentIndex || "0", 10) || 0;
      imgEl.alt = el.dataset.alt || "";
      imgEl.src = images[index];
      imgEl.style.opacity = "1";
      const multi = images.length > 1;
      prevBtn.hidden = !multi;
      nextBtn.hidden = !multi;
      overlay.classList.remove("hidden");
      overlay.classList.add("flex");
      document.body.style.overflow = "hidden";
    }

    function close() {
      overlay.classList.add("hidden");
      overlay.classList.remove("flex");
      document.body.style.overflow = "";
    }

    function step(delta) {
      index = (index + delta + images.length) % images.length;
      render();
    }

    media.forEach((el) => {
      el.addEventListener("click", (e) => {
        if (e.target.closest(".gallery-prev, .gallery-next, .gallery-dot")) return;
        open(el);
      });
    });

    closeBtn.addEventListener("click", close);
    prevBtn.addEventListener("click", () => step(-1));
    nextBtn.addEventListener("click", () => step(1));
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) close();
    });
    document.addEventListener("keydown", (e) => {
      if (overlay.classList.contains("hidden")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") step(-1);
      if (e.key === "ArrowRight") step(1);
    });
  }

  /* ---------- Skill bars: animate scaleX on mount ----------
     The generator sets data-level and an inline transition-delay on each
     .skill-bar-fill, but leaves transform at its CSS default (scaleX(0)).
     We force a paint at scaleX(0) via double rAF, then set the real
     target so the transition actually fires instead of snapping straight
     to full width. */
  function initSkillBars() {
    const bars = document.querySelectorAll(".skill-bar-fill[data-level]");
    if (!bars.length) return;

    bars.forEach((bar) => {
      bar.style.transform = "scaleX(0)";
    });

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        bars.forEach((bar) => {
          const level = parseFloat(bar.dataset.level || "0");
          bar.style.transform = `scaleX(${Math.max(0, Math.min(100, level)) / 100})`;
        });
      });
    });
  }

  /* ---------- Scroll-triggered reveal ----------
     Elements with .reveal fade/slide in the first time they enter the
     viewport (never re-triggers on subsequent scrolls — this is an entrance,
     not a loop). Reduced-motion users get everything visible immediately,
     with no observer involved at all, rather than an instant-but-still-timed
     transition. */
  function initScrollReveal() {
    const items = document.querySelectorAll(".reveal");
    if (!items.length) return;

    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced || !("IntersectionObserver" in window)) {
      items.forEach((el) => el.classList.add("is-visible"));
      return;
    }

    const observer = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            obs.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.2, rootMargin: "0px 0px -40px 0px" }
    );

    items.forEach((el) => observer.observe(el));
  }

  /* ---------- Network topology (Networking track) ---------- */
  function initTopology() {
    const info = document.getElementById("topologyInfo");
    const nodes = document.querySelectorAll(".topology-node");
    if (!info || !nodes.length) return;

    function show(node) {
      nodes.forEach((n) => n.classList.toggle("is-active", n === node));
      const { name, ip, role } = node.dataset;
      info.innerHTML =
        `<p class="text-muted text-xs">${ip}</p>` +
        `<p class="font-display font-semibold mt-1">${name}</p>` +
        `<p class="text-muted text-sm mt-2">${role}</p>`;
    }

    const canHover = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
    nodes.forEach((node) => {
      node.addEventListener("click", () => show(node));
      if (canHover) node.addEventListener("mouseenter", () => show(node));
    });
  }

  /* ---------- Boot ---------- */
  document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initMobileNav();
    initFooterYear();
    initContactForm();
    initGalleries();
    initSkillBars();
    initScrollReveal();
    initTopology();
    initLightbox();
  });
})();
