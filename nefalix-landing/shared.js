// Cal.com demo randevu (ana site ile aynı: enes-ceylan/15min)
(function (C, A, L) {
  const p = (a, ar) => { a.q.push(ar); };
  const d = C.document;
  C.Cal = C.Cal || function () {
    const cal = C.Cal;
    const ar = arguments;
    if (!cal.loaded) {
      cal.ns = {};
      cal.q = cal.q || [];
      d.head.appendChild(d.createElement('script')).src = A;
      cal.loaded = true;
    }
    if (ar[0] === L) {
      const api = function () { p(api, arguments); };
      const namespace = ar[1];
      api.q = api.q || [];
      if (typeof namespace === 'string') {
        cal.ns[namespace] = cal.ns[namespace] || api;
        p(cal.ns[namespace], ar);
        p(cal, ['initNamespace', namespace]);
      } else p(cal, ar);
      return;
    }
    p(cal, ar);
  };
})(window, 'https://app.cal.com/embed/embed.js', 'init');
Cal('init', '15min', { origin: 'https://app.cal.com' });
Cal.config = Cal.config || {};
Cal.config.forwardQueryParams = true;
Cal.ns['15min']('ui', { hideEventTypeDetails: false, layout: 'month_view' });

const SOCIAL_LINKS = {
  linkedin: 'https://www.linkedin.com/company/nefalixai/',
  instagram: 'https://www.instagram.com/nefalixai/',
  youtube: 'https://www.youtube.com/@Nefalixai',
  whatsapp: 'https://wa.me/905491190819',
};

const CAL_DEMO = {
  href: 'https://cal.com/enes-ceylan/15min',
  link: 'enes-ceylan/15min',
  namespace: '15min',
  config: '{"layout":"month_view","useSlotsViewOnSmallScreen":"true"}',
};

let siteNavHtmlCache = null;

function bindCalDemo(el) {
  if (!el) return;
  if (el.tagName === 'A') {
    el.href = CAL_DEMO.href;
  }
  el.setAttribute('role', 'button');
  el.setAttribute('data-cal-link', CAL_DEMO.link);
  el.setAttribute('data-cal-namespace', CAL_DEMO.namespace);
  el.setAttribute('data-cal-config', CAL_DEMO.config);
  el.removeAttribute('target');
  el.removeAttribute('rel');
  if (el.dataset.calBound) return;
  el.dataset.calBound = '1';
  el.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (typeof Cal === 'function') {
      Cal('modal', {
        calLink: CAL_DEMO.link,
        config: { layout: 'month_view', useSlotsViewOnSmallScreen: 'true' },
      });
      return;
    }
    window.open(CAL_DEMO.href, '_blank', 'noopener,noreferrer');
  });
}

function normalizeLogoWordmark(root = document) {
  root.querySelectorAll('.logo-lockup .logo-word').forEach((el) => {
    el.querySelectorAll('.logo-word-ai').forEach((ai) => ai.remove());
    const text = (el.textContent || '').replace(/\s*AI\s*$/i, '').trim();
    if (text) el.textContent = text;
  });
}

function initDemoCtas() {
  document.querySelectorAll('.btn-demo, .cal-demo').forEach(bindCalDemo);
}

function initLoginLinks() {
  document.querySelectorAll('.btn-login').forEach((el) => {
    const href = (el.getAttribute('href') || '').trim();
    if (!href || href === '#') el.setAttribute('href', '/dashboard/login');
  });
}

const FOOTER_SOCIAL_ICONS = {
  linkedin: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.03-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.95v5.66H9.34V9h3.42v1.56h.05c.47-.9 1.63-1.85 3.36-1.85 3.6 0 4.26 2.37 4.26 5.45v6.29zM5.34 7.43a2.06 2.06 0 110-4.12 2.06 2.06 0 010 4.12zM7.12 20.45H3.56V9h3.56v11.45z"/></svg>',
  instagram: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 2h10a5 5 0 015 5v10a5 5 0 01-5 5H7a5 5 0 01-5-5V7a5 5 0 015-5zm10 2H7a3 3 0 00-3 3v10a3 3 0 003 3h10a3 3 0 003-3V7a3 3 0 00-3-3zm-5 3.5A4.5 4.5 0 1111.5 16 4.5 4.5 0 0112 7.5zm0 2A2.5 2.5 0 1014.5 12 2.5 2.5 0 0012 9.5zM17.25 6.75a1 1 0 11-1 1 1 1 0 011-1z"/></svg>',
  whatsapp: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 00-8.66 15l-.67 2.45 2.51-.66A10 10 0 1012 2zm0 2a8 8 0 018 8.2c0 1.58-.46 3.1-1.33 4.4l-.2.3.09.35.7 2.05-2.1-.55-.34-.09-.3.18A8 8 0 1112 4zm-2.9 4.1c-.16 0-.43.06-.65.3-.22.24-.86.84-.86 2.05 0 1.2.88 2.36 1 2.53.12.17 1.73 2.77 4.28 3.77 2.12.83 2.55.67 3.01.63.46-.04 1.48-.6 1.69-1.18.21-.58.21-1.08.15-1.18-.06-.1-.22-.16-.46-.28-.24-.12-1.43-.7-1.65-.78-.22-.08-.38-.12-.54.12-.16.24-.62.78-.76.94-.14.16-.28.18-.52.06-.24-.12-1.01-.37-1.93-1.18-.71-.63-1.2-1.41-1.34-1.65-.14-.24-.01-.37.1-.49.1-.1.24-.26.36-.39.12-.13.16-.22.24-.37.08-.15.04-.28-.02-.39-.06-.11-.54-1.3-.74-1.78-.2-.47-.4-.41-.54-.42z"/></svg>',
  youtube: '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M23.5 6.2a3 3 0 00-2.1-2.1C19.5 3.5 12 3.5 12 3.5s-7.5 0-9.4.6A3 3 0 00.5 6.2 31 31 0 000 12a31 31 0 00.5 5.8 3 3 0 002.1 2.1c1.9.6 9.4.6 9.4.6s7.5 0 9.4-.6a3 3 0 002.1-2.1A31 31 0 0024 12a31 31 0 00-.5-5.8zM9.75 15.02V8.98L15.5 12l-5.75 3.02z"/></svg>',
};

function initFooterSocial() {
  document.querySelectorAll('.home-footer-brand').forEach((brand) => {
    if (brand.querySelector('.home-footer-social')) return;
    const social = document.createElement('div');
    social.className = 'home-footer-social';
    social.setAttribute('aria-label', 'Bizi takip edin');
    social.innerHTML = `
      <span class="home-footer-social-label">Bizi takip edin</span>
      <div class="home-footer-social-links">
        <a href="${SOCIAL_LINKS.linkedin}" target="_blank" rel="noopener noreferrer" class="home-footer-social-link home-footer-social-linkedin" aria-label="LinkedIn">
          ${FOOTER_SOCIAL_ICONS.linkedin}
          <span>LinkedIn</span>
        </a>
        <a href="${SOCIAL_LINKS.instagram}" target="_blank" rel="noopener noreferrer" class="home-footer-social-link home-footer-social-instagram" aria-label="Instagram">
          ${FOOTER_SOCIAL_ICONS.instagram}
          <span>Instagram</span>
        </a>
        <a href="${SOCIAL_LINKS.youtube}" target="_blank" rel="noopener noreferrer" class="home-footer-social-link home-footer-social-youtube" aria-label="YouTube">
          ${FOOTER_SOCIAL_ICONS.youtube}
          <span>YouTube</span>
        </a>
        <a href="${SOCIAL_LINKS.whatsapp}" target="_blank" rel="noopener noreferrer" class="home-footer-social-link home-footer-social-whatsapp" aria-label="WhatsApp">
          ${FOOTER_SOCIAL_ICONS.whatsapp}
          <span>WhatsApp</span>
        </a>
      </div>
    `;
    const actions = brand.querySelector('.home-footer-actions');
    if (actions) actions.insertAdjacentElement('afterend', social);
    else brand.appendChild(social);
  });
}

function initFooterLayout() {
  document.querySelectorAll('.home-footer-top').forEach((top) => {
    const cols = [...top.querySelectorAll(':scope > .home-footer-col')];
    if (cols.length && !top.querySelector('.home-footer-nav')) {
      const nav = document.createElement('div');
      nav.className = 'home-footer-nav';
      cols.forEach((col) => nav.appendChild(col));
      top.appendChild(nav);
    }
  });

  document.querySelectorAll('.home-footer-actions').forEach((actions) => {
    const links = [...actions.querySelectorAll('a')];
    links.forEach((link) => {
      const label = (link.textContent || '').trim().toLowerCase();
      if (label.includes('demo')) link.classList.add('footer-btn-demo');
      else link.classList.add('footer-btn-mail');
    });
  });

  document.querySelectorAll('.platform-logo').forEach((chip) => {
    const label = chip.querySelector('span');
    const img = chip.querySelector('img');
    if (!label || !img) return;
    const name = label.textContent.trim();
    chip.classList.add('platform-logo-chip');
    chip.setAttribute('title', name);
    if (!img.getAttribute('alt')) img.setAttribute('alt', name);
    label.classList.add('sr-only');
    const src = (img.getAttribute('src') || '').toLowerCase();
    if (src.includes('doktortakvimi')) {
      img.setAttribute('src', '/logos/platforms/doktortakvimi-icon.svg');
      chip.classList.add('platform-logo-doktortakvimi');
    }
  });
}

const TRUST_BADGES_HTML = `
    <p class="trust-badges-kicker">Kliniklerin güvenle tercih ettiği standartlar</p>
    <div class="trust-badges trust-badges-showcase" role="list" aria-label="Güven rozetleri">
      <a href="/kvkk" class="trust-badge trust-badge-card trust-badge-kvkk" role="listitem">
        <span class="trust-badge-glow" aria-hidden="true"></span>
        <span class="trust-badge-medallion">
          <span class="trust-badge-ring" aria-hidden="true"></span>
          <span class="trust-badge-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none"><path d="M12 2l8 4v6c0 5-3.5 9.5-8 10-4.5-.5-8-5-8-10V6l8-4z" stroke="currentColor" stroke-width="1.5"/><path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          </span>
        </span>
        <span class="trust-badge-copy">
          <strong>Yasal Güvence</strong>
          <small>Hastanıza şeffaflık, ekibinize huzur</small>
        </span>
        <span class="trust-badge-cta">Keşfet →</span>
      </a>
      <a href="/veri-guvenligi" class="trust-badge trust-badge-card trust-badge-data" role="listitem">
        <span class="trust-badge-glow" aria-hidden="true"></span>
        <span class="trust-badge-medallion">
          <span class="trust-badge-ring" aria-hidden="true"></span>
          <span class="trust-badge-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none"><path d="M4 6.5h16v11H4z" stroke="currentColor" stroke-width="1.5"/><path d="M8 10.5h8M8 13.5h5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          </span>
        </span>
        <span class="trust-badge-copy">
          <strong>Yerel Altyapı</strong>
          <small>Veriniz Türkiye'de, kontrol sizde</small>
        </span>
        <span class="trust-badge-cta">Keşfet →</span>
      </a>
      <a href="/iys-izin" class="trust-badge trust-badge-card trust-badge-iys" role="listitem">
        <span class="trust-badge-glow" aria-hidden="true"></span>
        <span class="trust-badge-medallion">
          <span class="trust-badge-ring" aria-hidden="true"></span>
          <span class="trust-badge-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none"><path d="M7 4h10v16H7z" stroke="currentColor" stroke-width="1.5"/><path d="M10 8h4M10 12h4M10 16h2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          </span>
        </span>
        <span class="trust-badge-copy">
          <strong>Akıllı İzin</strong>
          <small>Önce izin, sonra etkili iletişim</small>
        </span>
        <span class="trust-badge-cta">Keşfet →</span>
      </a>
      <a href="/hbys-entegrasyon" class="trust-badge trust-badge-card trust-badge-hbys" role="listitem">
        <span class="trust-badge-glow" aria-hidden="true"></span>
        <span class="trust-badge-medallion">
          <span class="trust-badge-ring" aria-hidden="true"></span>
          <span class="trust-badge-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none"><path d="M4 20V9l8-4 8 4v11H4z" stroke="currentColor" stroke-width="1.5"/><path d="M9 20v-4h6v4" stroke="currentColor" stroke-width="1.5"/></svg>
          </span>
        </span>
        <span class="trust-badge-copy">
          <strong>HBYS Hazır</strong>
          <small>Randevu kapanır, akış kendiliğinden başlar</small>
        </span>
        <span class="trust-badge-cta">Keşfet →</span>
      </a>
      <a href="/sektorler#saglik" class="trust-badge trust-badge-card trust-badge-health" role="listitem">
        <span class="trust-badge-glow" aria-hidden="true"></span>
        <span class="trust-badge-medallion">
          <span class="trust-badge-ring" aria-hidden="true"></span>
          <span class="trust-badge-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none"><path d="M12 21s-6-4.2-6-10a3.5 3.5 0 017 0 3.5 3.5 0 017 0c0 5.8-6 10-6 10z" stroke="currentColor" stroke-width="1.5"/></svg>
          </span>
        </span>
        <span class="trust-badge-copy">
          <strong>Sağlık Turizmi</strong>
          <small>Diş, estetik ve klinikler için doğdu</small>
        </span>
        <span class="trust-badge-cta">Keşfet →</span>
      </a>
      <a href="/guvenlik-standartlari" class="trust-badge trust-badge-card trust-badge-cert" role="listitem">
        <span class="trust-badge-glow" aria-hidden="true"></span>
        <span class="trust-badge-medallion">
          <span class="trust-badge-ring" aria-hidden="true"></span>
          <span class="trust-badge-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="10" r="5" stroke="currentColor" stroke-width="1.5"/><path d="M8.5 14.5L6 21l6-2.8L18 21l-2.5-6.5" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>
          </span>
        </span>
        <span class="trust-badge-copy">
          <strong>Kurumsal Güven</strong>
          <small>Şifreli altyapı, onaylı AI yanıtları</small>
        </span>
        <span class="trust-badge-cta">Keşfet →</span>
      </a>
    </div>
  `;

function trustBadgesHtml() {
  return TRUST_BADGES_HTML;
}

function initTrustBadgeMounts() {
  document.querySelectorAll('.trust-badges-mount').forEach((mount) => {
    if (mount.childElementCount) return;
    mount.innerHTML = trustBadgesHtml();
  });
}

function initFooterTrust() {
  document.querySelectorAll('.home-footer').forEach((footer) => {
    const existing = footer.querySelector('.home-footer-trust');
    if (existing) {
      existing.innerHTML = trustBadgesHtml();
      return;
    }
    const bar = document.createElement('div');
    bar.className = 'home-footer-trust';
    bar.innerHTML = trustBadgesHtml();
    const bottom = footer.querySelector('.home-footer-bottom');
    if (bottom) footer.insertBefore(bar, bottom);
    else footer.appendChild(bar);
  });
}

async function initSiteNav() {
  const mount = document.querySelector('nav.site-nav-mount');
  if (!mount) return;

  if (!mount.querySelector('.navwrap')) {
    try {
      if (!siteNavHtmlCache) {
        const res = await fetch('/partials/site-nav.html');
        if (res.ok) siteNavHtmlCache = await res.text();
      }
      if (siteNavHtmlCache) mount.innerHTML = siteNavHtmlCache;
    } catch (_) {}
  }

  if (!mount.querySelector('.navwrap')) return;

  initLoginLinks();
  document.querySelectorAll('nav.site-nav-mount .btn-demo, nav.site-nav-mount .cal-demo').forEach(bindCalDemo);
  normalizeLogoWordmark(mount);
  initMobileNav();
}

function initSectorTabs() {
  const PANEL_SELECTOR = '.sektor-panel, .platform-panel';

  function defaultTarget(tabBar) {
    const active = tabBar.querySelector('.sector-tab.active[data-target]');
    if (active) return active.dataset.target;
    const first = tabBar.querySelector('.sector-tab[data-target]');
    return first ? first.dataset.target : '';
  }

  function hashTarget(tabBar) {
    const hash = (location.hash || '').replace(/^#/, '');
    const valid = [...tabBar.querySelectorAll('.sector-tab[data-target]')].map(t => t.dataset.target);
    if (hash && valid.includes(hash)) return hash;
    return defaultTarget(tabBar);
  }

  function activateTab(tab) {
    const tabBar = tab.closest('.sector-tabs');
    if (!tabBar) return;
    const group = tabBar.dataset.group;
    const target = tab.dataset.target;
    if (!group || !target) return;

    tabBar.querySelectorAll('.sector-tab').forEach(t => {
      const on = t === tab;
      t.classList.toggle('active', on);
      t.setAttribute('aria-selected', on ? 'true' : 'false');
    });

    document.querySelectorAll(`${PANEL_SELECTOR}[data-group="${group}"]`).forEach(panel => {
      const show = panel.dataset.id === target;
      panel.hidden = !show;
      panel.style.display = show ? 'block' : 'none';
    });

    if (history.replaceState) {
      const path = location.pathname;
      const nextHash = target === defaultTarget(tabBar) ? '' : `#${target}`;
      const nextUrl = path + nextHash;
      if (location.pathname + location.hash !== nextUrl) {
        history.replaceState(null, '', nextUrl);
      }
    }
  }

  document.querySelectorAll('.sector-tabs[data-group]').forEach(tabBar => {
    tabBar.querySelectorAll('.sector-tab').forEach(tab => {
      tab.addEventListener('click', () => activateTab(tab));
    });
    const initial = tabBar.querySelector(`.sector-tab[data-target="${hashTarget(tabBar)}"]`)
      || tabBar.querySelector('.sector-tab.active')
      || tabBar.querySelector('.sector-tab');
    if (initial) activateTab(initial);
  });

  window.addEventListener('hashchange', () => {
    document.querySelectorAll('.sector-tabs[data-group]').forEach(tabBar => {
      const tab = tabBar.querySelector(`.sector-tab[data-target="${hashTarget(tabBar)}"]`);
      if (tab) activateTab(tab);
    });
  });
}

function initSubpageBodyClass() {
  if (!document.body.classList.contains('home-refresh-body')) {
    document.body.classList.add('site-subpage');
  }
}

// Scroll reveal (JS yüklenince .pre eklenir, IntersectionObserver ile .in eklenir — JS yoksa içerik baştan görünür)
document.addEventListener('DOMContentLoaded', async function() {
  initSubpageBodyClass();
  initLoginLinks();
  await initSiteNav();
  initGuidedDemo();
  initFooterSocial();
  initFooterLayout();
  initFooterTrust();
  initTrustBadgeMounts();
  initFaqLines();

  initHomepageEffects();
  initFlowStory();
  initPricingPage();
  initDemoCtas();
  normalizeLogoWordmark();
  const reveals = document.querySelectorAll('.reveal');
  reveals.forEach(el => {
    if (el.closest('#pricing-page')) return;
    el.classList.add('pre');
  });
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in'); });
  }, { threshold: 0.12 });
  reveals.forEach(el => obs.observe(el));

  // Sayaç animasyonu (count-up) — JS yüklenince 0'dan başlar, JS yoksa zaten HTML'deki hedef değer görünür
  const counters = document.querySelectorAll('.stat-num[data-target]');
  counters.forEach(el => {
    const suffix = el.dataset.suffix || "";
    const isDecimal = el.dataset.target.includes(".");
    el.textContent = "0" + suffix;
  });
  const counterObs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting && !e.target.dataset.done) {
        e.target.dataset.done = "1";
        const target = parseFloat(e.target.dataset.target);
        const suffix = e.target.dataset.suffix || "";
        const isDecimal = e.target.dataset.target.includes(".");
        let cur = 0;
        const step = target / 40;
        const tick = () => {
          cur += step;
          if (cur >= target) { e.target.textContent = (isDecimal ? target.toFixed(1) : target) + suffix; }
          else { e.target.textContent = (isDecimal ? cur.toFixed(1) : Math.floor(cur)) + suffix; requestAnimationFrame(tick); }
        };
        tick();
      }
    });
  }, { threshold: 0.3 });
  counters.forEach(el => counterObs.observe(el));

  initSectorTabs();

  // Rol sekmeleri (Kaynaklar sayfası önce-sonra tablosu)
  document.querySelectorAll('.role-tab').forEach(tab => {
    tab.addEventListener('click', function() {
      document.querySelectorAll('.role-tab').forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      const target = this.dataset.target;
      document.querySelectorAll('.role-panel').forEach(p => p.style.display = 'none');
      const panel = document.querySelector(`.role-panel[data-id="${target}"]`);
      if (panel) panel.style.display = 'block';
    });
  });

  // Fiyatlandırma adım sayaçları (+/-) — fiyatlar sayfası kendi handler'ını kullanır
  if (!document.getElementById('pricing-page')) {
    document.querySelectorAll('.counter-box').forEach(box => {
      const valEl = box.querySelector('.counter-val');
      box.querySelector('.counter-minus').addEventListener('click', () => {
        let v = parseInt(valEl.textContent, 10);
        if (v > 1) valEl.textContent = v - 1;
      });
      box.querySelector('.counter-plus').addEventListener('click', () => {
        let v = parseInt(valEl.textContent, 10);
        valEl.textContent = v + 1;
      });
    });
  }

  // Modül checkbox toggle (Fiyatlandırma) — fiyatlar sayfası hariç
  if (!document.getElementById('pricing-page')) {
    document.querySelectorAll('.mcheck.premium').forEach(item => {
      item.addEventListener('click', function() {
        this.classList.toggle('checked');
        const cb = this.querySelector('.cb');
        cb.textContent = this.classList.contains('checked') ? '✓' : '';
      });
    });
  }

  // FAQ accordion (kaynaklar vb.)
  document.querySelectorAll('.faq-item h4').forEach(h => {
    h.addEventListener('click', function() {
      const p = this.nextElementSibling;
      const isOpen = p.style.display === 'block';
      p.style.display = isOpen ? 'none' : 'block';
      this.style.setProperty('--rot', isOpen ? '0deg' : '45deg');
    });
  });
});

function initFaqLines() {
  const items = document.querySelectorAll('.faq-line-item');
  if (!items.length) return;

  items.forEach((item) => {
    const btn = item.querySelector('.faq-line-question');
    if (!btn || btn.dataset.faqBound) return;
    btn.dataset.faqBound = '1';

    const toggle = (open) => {
      const shouldOpen = open ?? !item.classList.contains('open');
      if (shouldOpen) {
        items.forEach((other) => {
          if (other !== item) {
            other.classList.remove('open');
            const otherBtn = other.querySelector('.faq-line-question');
            if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
          }
        });
        item.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
        window.requestAnimationFrame(() => {
          item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        });
      } else {
        item.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
      }
    };

    btn.addEventListener('click', () => toggle());
    btn.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        toggle();
      }
    });
  });
}

function initHomepageEffects() {
  const parallaxNodes = document.querySelectorAll('[data-parallax-depth]');
  if (parallaxNodes.length && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    window.addEventListener('mousemove', (e) => {
      const px = (e.clientX / window.innerWidth) - 0.5;
      const py = (e.clientY / window.innerHeight) - 0.5;
      parallaxNodes.forEach((node) => {
        const depth = parseFloat(node.dataset.parallaxDepth || '0');
        node.style.transform = `translate3d(${px * depth * 42}px, ${py * depth * 32}px, 0)`;
      });
    });
  }

  const staggerGroups = document.querySelectorAll('.stat-card, .problem-card, .mod-card, .flow-step, .hero-signal-chip, .hero-floating-card, .story-card, .feature-tile, .feature-lead, .result-box, .faq-item, .refresh-proof-item, .orbit-card');
  staggerGroups.forEach((node, index) => {
    node.classList.add('stagger-item');
    node.style.transitionDelay = `${(index % 6) * 70}ms`;
  });
}

function syncNavShortcuts() {
  const navMid = document.querySelector('.navmid');
  const navRight = document.querySelector('.navright');
  if (!navMid || !navRight) return;

  let holder = navRight.querySelector('.navright-links');
  if (!holder) {
    holder = document.createElement('div');
    holder.className = 'navright-links';
    holder.setAttribute('aria-label', 'Hızlı bağlantılar');
    navRight.insertBefore(holder, navRight.firstChild);
  }

  if (!syncNavShortcuts.nodes) {
    const nodes = [];
    const fiyatlar = navMid.querySelector('.navitem > a[href="/fiyatlar"]')?.closest('.navitem');
    const hakkimizda = navMid.querySelector('.navitem > a[href="/hakkimizda"]')?.closest('.navitem');
    if (fiyatlar) nodes.push(fiyatlar);
    if (hakkimizda) nodes.push(hakkimizda);
    syncNavShortcuts.nodes = nodes;
  }

  const desktop = window.innerWidth >= 1280;
  holder.innerHTML = '';

  if (desktop) {
    syncNavShortcuts.nodes.forEach((item) => {
      const anchor = item.querySelector('a');
      if (!anchor) return;
      const link = anchor.cloneNode(true);
      link.classList.add('navshortcut-link');
      holder.appendChild(link);
      if (item.parentElement === navMid) item.remove();
    });
    holder.style.display = holder.children.length ? 'flex' : 'none';
    return;
  }

  holder.style.display = 'none';
  syncNavShortcuts.nodes.forEach((item) => {
    if (!navMid.contains(item)) navMid.appendChild(item);
  });
}
syncNavShortcuts.nodes = null;

function initMobileNav() {
  const nav = document.querySelector('nav.site-nav-mount');
  const navWrap = nav?.querySelector('.navwrap');
  const navMid = nav?.querySelector('.navmid');
  const navRight = nav?.querySelector('.navright');
  if (!nav || !navWrap || !navMid || !navRight) return;
  if (nav.dataset.mobileNavInit === '1') return;
  nav.dataset.mobileNavInit = '1';

  navWrap.classList.add('mobile-ready');

  let toggle = nav.querySelector('.nav-mobile-toggle');
  if (!toggle) {
    toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'nav-mobile-toggle';
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Menüyü aç');
    toggle.innerHTML = '<span></span><span></span><span></span>';
    navRight.insertBefore(toggle, navRight.firstChild);
  }

  const closeMenu = () => {
    navMid.classList.remove('is-open');
    navMid.querySelectorAll('.navitem.is-open').forEach((item) => item.classList.remove('is-open'));
    toggle.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('mobile-nav-open');
  };

  const openMenu = () => {
    navMid.classList.add('is-open');
    toggle.classList.add('is-open');
    toggle.setAttribute('aria-expanded', 'true');
    document.body.classList.add('mobile-nav-open');
  };

  toggle.addEventListener('click', () => {
    if (navMid.classList.contains('is-open')) closeMenu();
    else openMenu();
  });

  navMid.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => closeMenu());
  });

  navMid.querySelectorAll('.navitem > span').forEach((trigger) => {
    trigger.addEventListener('click', () => {
      if (window.innerWidth > 1279) return;
      const item = trigger.parentElement;
      const shouldOpen = !item.classList.contains('is-open');
      navMid.querySelectorAll('.navitem.is-open').forEach((openItem) => {
        if (openItem !== item) openItem.classList.remove('is-open');
      });
      item.classList.toggle('is-open', shouldOpen);
    });
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeMenu();
  });

  window.addEventListener('resize', () => {
    syncNavShortcuts();
    if (window.innerWidth > 1279) {
      navMid.querySelectorAll('.navitem.is-open').forEach((item) => item.classList.remove('is-open'));
      closeMenu();
    }
  });

  syncNavShortcuts();
  closeMenu();
}

function initGuidedDemo() {
  const modal = document.getElementById('guided-demo-modal');
  if (!modal) return;

  const triggers = document.querySelectorAll('.guided-demo-trigger');
  const closeEls = modal.querySelectorAll('[data-guided-close]');
  const progressEl = document.getElementById('guided-demo-progress');
  const kickerEl = document.getElementById('guided-demo-kicker');
  const titleEl = document.getElementById('guided-demo-title');
  const descriptionEl = document.getElementById('guided-demo-description');
  const pointsEl = document.getElementById('guided-demo-points');
  const formEl = document.getElementById('guided-demo-form');
  const prevBtn = document.getElementById('guided-demo-prev');
  const nextBtn = document.getElementById('guided-demo-next');
  const submitBtn = document.getElementById('guided-demo-submit');
  const demoTargets = Array.from(modal.querySelectorAll('[data-demo-key]'));

  const steps = [
    {
      kicker: 'Google Yorumlar',
      title: 'Google yorum performansınızı tek bakışta görün.',
      description: 'Yeni yorumları, puan değişimini ve hangi yoruma cevap verilmesi gerektiğini aynı panelden takip edin.',
      points: [
        'Memnun hastaya yorum daveti akışı otomatik bağlanır.',
        'Cevap bekleyen yorumlar yöneticinin önüne öncelikli düşer.',
      ],
      activeKeys: ['google'],
    },
    {
      kicker: 'WhatsApp Inbox',
      title: 'Tüm konuşmaları tek sırada yönetin.',
      description: 'WhatsApp mesajları dağılmadan tek inbox içinde toplanır; yapay zeka taslağı ekibin işini hızlandırır.',
      points: [
        'Öncelikli mesajlar otomatik sıralanır.',
        'AI taslak ile ekip cevap süresi kısalır.',
      ],
      activeKeys: ['inbox'],
    },
    {
      kicker: 'Sentinel',
      title: 'İtibar riskini geç kalmadan görün.',
      description: 'Negatif yorum, düşük puan ve problemli sinyaller büyümeden alarm olarak yöneticinin önüne gelir.',
      points: [
        'Kriz sinyali otomatik etiketlenir.',
        'Sorun görünmeden önce aksiyon alınır.',
      ],
      activeKeys: ['sentinel'],
    },
    {
      kicker: 'Recall',
      title: 'Sessiz kalan hastayı yeniden akışa alın.',
      description: 'Geri dönüş vermeyen hasta ve lead listeleri tespit edilir; doğru anda geri çağırma kampanyası açılır.',
      points: [
        'Kayıp gelir fırsatları görünür hale gelir.',
        'Hazır kampanya akışları ile ekip hız kazanır.',
      ],
      activeKeys: ['recall'],
    },
    {
      kicker: 'eNPS',
      title: 'Çalışan memnuniyetini de görünür kılın.',
      description: 'Sadece hasta değil, ekip deneyimi de izlenir; şube bazlı kırılmalar erken fark edilir.',
      points: [
        'eNPS görünümü tek panelde yer alır.',
        'İç operasyon sorunu dış müşteri deneyimine yansımadan fark edilir.',
      ],
      activeKeys: ['enps'],
    },
    {
      kicker: 'Abonelik',
      title: 'Plan, modül ve kullanım yapısını net görün.',
      description: 'Hangi paket aktif, hangi modüller açık ve kullanım seviyesi ne durumda; hepsi aynı görünümde takip edilir.',
      points: [
        'Ödeme ve plan takibi satış sonrası da düzenli kalır.',
        'Büyümeye göre modül ekleme kararı kolaylaşır.',
      ],
      activeKeys: ['billing'],
    },
    {
      kicker: 'Demo Planlama',
      title: 'Şimdi kısa bilgilerinizi bırakın, takvim açılsın.',
      description: 'Formu tamamladıktan sonra uygun saat seçebileceğiniz demo takvimi açılacak.',
      points: [],
      activeKeys: [],
      form: true,
    },
  ];

  let stepIndex = 0;

  function renderPoints(points) {
    pointsEl.innerHTML = points.map((point) => `<div class="guided-demo-point">${point}</div>`).join('');
  }

  function renderStep() {
    const step = steps[stepIndex];
    progressEl.textContent = `Adım ${stepIndex + 1} / ${steps.length}`;
    kickerEl.textContent = step.kicker;
    titleEl.textContent = step.title;
    descriptionEl.textContent = step.description;
    renderPoints(step.points || []);
    pointsEl.classList.toggle('is-hidden', !!step.form);
    formEl.classList.toggle('is-hidden', !step.form);
    nextBtn.classList.toggle('is-hidden', !!step.form);
    submitBtn.classList.toggle('is-hidden', !step.form);
    prevBtn.disabled = stepIndex === 0;
    prevBtn.style.opacity = stepIndex === 0 ? '0.45' : '1';

    const activeKeys = new Set(step.activeKeys || []);
    demoTargets.forEach((node) => {
      const key = node.dataset.demoKey;
      const isActive = activeKeys.has(key);
      node.classList.toggle('is-active', isActive);
      node.classList.toggle('guided-demo-is-dim', activeKeys.size > 0 && !isActive);
    });
  }

  function openModal() {
    stepIndex = 0;
    renderStep();
    modal.classList.remove('is-hidden');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('demo-modal-open');
  }

  function closeModal() {
    modal.classList.add('is-hidden');
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('demo-modal-open');
  }

  function goNext() {
    if (stepIndex < steps.length - 1) {
      stepIndex += 1;
      renderStep();
    }
  }

  function goPrev() {
    if (stepIndex > 0) {
      stepIndex -= 1;
      renderStep();
    }
  }

  triggers.forEach((trigger) => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      openModal();
    });
  });

  closeEls.forEach((el) => el.addEventListener('click', closeModal));
  nextBtn.addEventListener('click', goNext);
  prevBtn.addEventListener('click', goPrev);

  document.addEventListener('keydown', (e) => {
    if (modal.classList.contains('is-hidden')) return;
    if (e.key === 'Escape') closeModal();
    if (e.key === 'ArrowRight' && !nextBtn.classList.contains('is-hidden')) goNext();
    if (e.key === 'ArrowLeft') goPrev();
  });

  formEl.addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = new FormData(formEl);
    const fullName = String(formData.get('fullName') || '').trim();
    const company = String(formData.get('company') || '').trim();
    const phone = String(formData.get('phone') || '').trim();
    const email = String(formData.get('email') || '').trim();

    if (!fullName || !company || !phone || !email) return;

    try {
      localStorage.setItem('nefalixGuidedDemoLead', JSON.stringify({
        fullName,
        company,
        phone,
        email,
        createdAt: new Date().toISOString(),
      }));
    } catch (_) {}

    // Klinik CRM'e lead düşür (fire-and-forget)
    try {
      fetch('/api/clinic/lead-intake', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ad: fullName, telefon: phone, company, email, kaynak: 'Web Demo Formu' }),
        keepalive: true,
      }).catch(() => {});
    } catch (_) {}

    closeModal();

    const config = {
      layout: 'month_view',
      name: fullName,
      email,
      notes: `Firma/Klinik: ${company} | Telefon: ${phone}`,
    };

    window.setTimeout(() => {
      if (typeof Cal === 'function') {
        Cal('modal', {
          calLink: CAL_DEMO.link,
          config,
        });
      } else {
        window.location.href = CAL_DEMO.href;
      }
    }, 140);
  });
}

function initFlowStory() {
  const steps = Array.from(document.querySelectorAll('.flow-step'));
  if (!steps.length) return;

  let activeIndex = 0;
  const setActive = (index) => {
    activeIndex = index;
    steps.forEach((step, i) => step.classList.toggle('active', i === index));
  };

  steps.forEach((step, index) => {
    step.addEventListener('mouseenter', () => setActive(index));
    step.addEventListener('focusin', () => setActive(index));
  });

  setInterval(() => {
    setActive((activeIndex + 1) % steps.length);
  }, 2800);
}

function formatTl(n) {
  return Math.round(n).toLocaleString('tr-TR');
}

function initPricingPage() {
  /* /fiyatlar sayfası pricing-calculator.js ile yönetilir */
}
