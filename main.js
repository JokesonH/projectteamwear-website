/* ═══════════════════════════════════════════════
   PROJECT TEAM WEAR — main.js
   Custom cursor · Loader · Navbar · Mobile menu
   Scroll reveal · Stats counter · Design lightbox
   Horizontal scroll drag · Quote form
═══════════════════════════════════════════════ */

'use strict';

/* ─── LOADER ─── */
window.addEventListener('load', () => {
  const loader = document.getElementById('loader');
  if (!loader) return;
  // Min 1.5s loader for the brand moment
  setTimeout(() => loader.classList.add('done'), 1500);
});

/* ─── CUSTOM CURSOR ─── */
(function () {
  const dot  = document.getElementById('cursor-dot');
  const ring = document.getElementById('cursor-ring');
  if (!dot || !ring) return;
  if (window.matchMedia('(hover: none)').matches) return;

  let mx = 0, my = 0;
  let rx = 0, ry = 0;
  let raf;

  document.addEventListener('mousemove', e => {
    mx = e.clientX;
    my = e.clientY;
    dot.style.left = mx + 'px';
    dot.style.top  = my + 'px';
  }, { passive: true });

  function animateRing() {
    rx += (mx - rx) * 0.14;
    ry += (my - ry) * 0.14;
    ring.style.left = rx + 'px';
    ring.style.top  = ry + 'px';
    raf = requestAnimationFrame(animateRing);
  }
  animateRing();

  // Expand ring on hoverable elements
  const hoverEls = 'a, button, .design-card, .gallery-item, .product-card, .kit-opt, input, textarea';
  document.addEventListener('mouseover', e => {
    if (e.target.closest(hoverEls)) document.body.classList.add('cursor-hover');
  });
  document.addEventListener('mouseout', e => {
    if (e.target.closest(hoverEls)) document.body.classList.remove('cursor-hover');
  });

  document.addEventListener('mouseleave', () => { dot.style.opacity = '0'; ring.style.opacity = '0'; });
  document.addEventListener('mouseenter', () => { dot.style.opacity = '1'; ring.style.opacity = '1'; });
})();

/* ─── NAVBAR ─── */
(function () {
  const nav = document.getElementById('navbar');
  if (!nav) return;

  const onScroll = () => {
    nav.classList.toggle('scrolled', window.scrollY > 30);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();

/* ─── SMOOTH SCROLL ─── */
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', e => {
    const target = document.querySelector(link.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    const navH = document.getElementById('navbar')?.offsetHeight ?? 68;
    const top  = target.getBoundingClientRect().top + window.scrollY - navH - 8;
    window.scrollTo({ top, behavior: 'smooth' });
  });
});

/* ─── MOBILE MENU ─── */
const menuBtn    = document.getElementById('menu-btn');
const mobileMenu = document.getElementById('mobile-menu');

if (menuBtn && mobileMenu) {
  menuBtn.addEventListener('click', () => {
    const isOpen = mobileMenu.classList.toggle('open');
    menuBtn.classList.toggle('open', isOpen);
    menuBtn.setAttribute('aria-expanded', isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });
}

function closeMobileMenu() {
  mobileMenu?.classList.remove('open');
  menuBtn?.classList.remove('open');
  menuBtn?.setAttribute('aria-expanded', 'false');
  document.body.style.overflow = '';
}

/* ─── SCROLL REVEAL ─── */
(function () {
  const els = document.querySelectorAll('[data-scroll-reveal]');
  if (!els.length) return;

  const io = new IntersectionObserver(entries => {
    entries.forEach((entry, i) => {
      if (!entry.isIntersecting) return;
      // Stagger siblings
      const siblings = [...entry.target.parentElement.querySelectorAll('[data-scroll-reveal]')];
      const idx = siblings.indexOf(entry.target);
      entry.target.style.transitionDelay = (idx * 0.08) + 's';
      entry.target.classList.add('revealed');
      io.unobserve(entry.target);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  els.forEach(el => io.observe(el));
})();

/* ─── STATS COUNTER ─── */
(function () {
  const nums = document.querySelectorAll('.stat-num[data-count]');
  if (!nums.length) return;

  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el  = entry.target;
      const end = parseInt(el.dataset.count, 10);
      const dur = 1400;
      const step = 16;
      const total = Math.ceil(dur / step);
      let current = 0;

      const timer = setInterval(() => {
        current++;
        const val = Math.round(easeOutExpo(current / total) * end);
        el.textContent = val.toLocaleString();
        if (current >= total) {
          el.textContent = end.toLocaleString();
          clearInterval(timer);
        }
      }, step);

      io.unobserve(el);
    });
  }, { threshold: 0.5 });

  nums.forEach(n => io.observe(n));

  function easeOutExpo(t) {
    return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
  }
})();

/* ─── COLOURWAY AUTO-ROTATION (hover) ─── */
(function () {
  document.querySelectorAll('.collection-card[data-colourways]').forEach(card => {
    let colourways;
    try { colourways = JSON.parse(card.dataset.colourways); } catch { return; }
    if (!colourways || colourways.length < 2) return;

    const img          = card.querySelector('.collection-img');
    const nameTag      = card.querySelector('.colour-name-tag');
    const progressFill = card.querySelector('.colour-progress-fill');
    const dotsWrap     = card.querySelector('.colour-dots-overlay');
    if (!img) return;

    // Ensure smooth opacity cross-fade on the image
    img.style.transition = 'opacity 0.22s ease, transform 0.5s cubic-bezier(0.16,1,0.3,1)';

    // Inject one dot per colourway
    if (dotsWrap) {
      colourways.forEach((_, i) => {
        const dot = document.createElement('span');
        dot.className = 'colour-dot' + (i === 0 ? ' colour-dot--active' : '');
        dotsWrap.appendChild(dot);
      });
    }

    let current  = 0;
    let interval = null;
    const dots   = dotsWrap ? [...dotsWrap.querySelectorAll('.colour-dot')] : [];

    function showColourway(idx, instant) {
      const cw = colourways[idx];

      // Crossfade image
      img.style.opacity = '0';
      clearTimeout(img._swapTimer);
      img._swapTimer = setTimeout(() => {
        img.src = cw.img;
        img.alt = cw.label || '';
        img.style.opacity = '1';
      }, instant ? 0 : 220);

      // Update name tag
      if (nameTag) nameTag.textContent = cw.label || '';

      // Update dots
      dots.forEach((d, i) => d.classList.toggle('colour-dot--active', i === idx));

      // Restart progress bar sweep
      if (progressFill && !instant) {
        progressFill.style.transition = 'none';
        progressFill.style.width = '0%';
        // Force reflow so transition fires properly
        void progressFill.offsetWidth;
        progressFill.style.transition = 'width 1.95s linear';
        progressFill.style.width = '100%';
      }

      current = idx;
    }

    card.addEventListener('mouseenter', () => {
      // Immediately jump to colourway 1 and start the timer
      showColourway(1);
      interval = setInterval(() => {
        showColourway((current + 1) % colourways.length);
      }, 2000);
    });

    card.addEventListener('mouseleave', () => {
      clearInterval(interval);
      interval = null;
      // Reset to first colourway instantly
      showColourway(0, true);
      // Reset progress bar
      if (progressFill) {
        progressFill.style.transition = 'none';
        progressFill.style.width = '0%';
      }
    });
  });
})();

/* ─── COLLECTION CARD LIGHTBOX ─── */
const lightbox   = document.getElementById('lightbox');
const lbBackdrop = document.getElementById('lightbox-backdrop');
const lbImg      = document.getElementById('lightbox-img');
const lbTitle    = document.getElementById('lightbox-title');
const lbClose    = document.getElementById('lightbox-close');

document.querySelectorAll('.collection-img-wrap').forEach(wrap => {
  wrap.style.cursor = 'none';
  wrap.addEventListener('click', () => {
    const card  = wrap.closest('.collection-card');
    const img   = wrap.querySelector('.collection-img');
    const name  = card?.querySelector('.collection-name')?.textContent ?? '';
    const client = card?.querySelector('.collection-client')?.textContent ?? '';
    if (!img || !lightbox) return;
    lbImg.src = img.src;
    lbImg.alt = name;
    lbTitle.textContent = `${name} — ${client}`;
    lightbox.hidden   = false;
    lbBackdrop.hidden = false;
    document.body.style.overflow = 'hidden';
  });
});

function closeLightbox() {
  if (!lightbox) return;
  lightbox.hidden   = true;
  lbBackdrop.hidden = true;
  document.body.style.overflow = '';
}

lbClose?.addEventListener('click', closeLightbox);
lbBackdrop?.addEventListener('click', closeLightbox);

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { closeLightbox(); closeMobileMenu(); }
});

/* ─── QUOTE FORM ─── */
(function () {
  const form    = document.getElementById('quote-form');
  const success = document.getElementById('form-success');
  const error   = document.getElementById('form-error');
  if (!form) return;

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    const btnText = btn.querySelector('.btn-text');

    btnText.textContent = 'Sending…';
    btn.disabled = true;
    success.hidden = true;
    error.hidden   = true;

    try {
      const res = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' },
      });

      if (res.ok) {
        form.reset();
        success.hidden = false;
        btnText.textContent = 'Sent!';
      } else {
        throw new Error();
      }
    } catch {
      error.hidden = false;
      btnText.textContent = 'Send Quote Request';
      btn.disabled = false;
    }
  });
})();
