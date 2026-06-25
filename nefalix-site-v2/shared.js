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

const CAL_DEMO = {
  href: 'https://cal.com/enes-ceylan/15min',
  link: 'enes-ceylan/15min',
  namespace: '15min',
  config: '{"layout":"month_view","useSlotsViewOnSmallScreen":"true"}',
};

function bindCalDemo(el) {
  el.href = '#';
  el.setAttribute('role', 'button');
  el.setAttribute('data-cal-link', CAL_DEMO.link);
  el.setAttribute('data-cal-namespace', CAL_DEMO.namespace);
  el.setAttribute('data-cal-config', CAL_DEMO.config);
  el.removeAttribute('target');
  el.removeAttribute('rel');
  if (!el.dataset.calBound) {
    el.dataset.calBound = '1';
    el.addEventListener('click', (e) => e.preventDefault());
  }
}

// Scroll reveal (JS yüklenince .pre eklenir, IntersectionObserver ile .in eklenir — JS yoksa içerik baştan görünür)
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.btn-demo, .cal-demo').forEach(bindCalDemo);

  initPricingPage();
  const reveals = document.querySelectorAll('.reveal');
  reveals.forEach(el => el.classList.add('pre'));
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

  // Sektör sekmeleri (Sektörler sayfası)
  document.querySelectorAll('.sector-tab').forEach(tab => {
    tab.addEventListener('click', function() {
      const group = this.closest('.sector-tabs').dataset.group;
      document.querySelectorAll(`.sector-tabs[data-group="${group}"] .sector-tab`).forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      const target = this.dataset.target;
      document.querySelectorAll(`.sektor-panel[data-group="${group}"]`).forEach(p => p.style.display = 'none');
      const panel = document.querySelector(`.sektor-panel[data-group="${group}"][data-id="${target}"]`);
      if (panel) panel.style.display = 'block';
    });
  });

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

  // FAQ accordion
  document.querySelectorAll('.faq-item h4').forEach(h => {
    h.addEventListener('click', function() {
      const p = this.nextElementSibling;
      const isOpen = p.style.display === 'block';
      p.style.display = isOpen ? 'none' : 'block';
      this.style.setProperty('--rot', isOpen ? '0deg' : '45deg');
    });
  });
});

function formatTl(n) {
  return Math.round(n).toLocaleString('tr-TR');
}

function initPricingPage() {
  const root = document.getElementById('pricing-page');
  if (!root) return;

  const state = {
    sector: 'health',
    branches: 1,
    staff: '1-5',
    modules: {
      feedback: true,
      inbox: true,
      reviews: true,
      enps: true,
      sentinel: false,
      recall: false,
    },
  };

  const sectorCards = root.querySelectorAll('.pricing-sector-card');
  const staffTabs = root.querySelectorAll('.pricing-staff-tab');
  const branchVal = root.querySelector('#pricing-branches');
  const branchHint = root.querySelector('#pricing-branch-hint');
  const summaryEl = root.querySelector('#pricing-summary');
  const steps = root.querySelectorAll('.pricing-steps .pstep');
  const cards = {
    starter: root.querySelector('[data-package="starter"]'),
    pro: root.querySelector('[data-package="pro"]'),
    enterprise: root.querySelector('[data-package="enterprise"]'),
  };

  const sectorMult = { health: 1, hotel: 0.92, auto: 0.88 };
  const staffMult = { '1-5': 1, '6-15': 1.12, '16-30': 1.28, '30+': 1.45 };
  const base = {
    starter: { monthly: 9500, setup: 25000 },
    pro: { monthly: 19500, setup: 50000 },
    enterprise: { monthly: 45000, setup: null },
  };
  const premiumAdd = { sentinel: 3500, recall: 2500 };

  function activeModules() {
    return Object.values(state.modules).filter(Boolean).length;
  }

  function recommendPackage() {
    if (state.branches >= 2 || state.staff === '30+') return 'enterprise';
    if (state.staff === '16-30' || state.modules.sentinel || state.modules.recall) return 'pro';
    if (activeModules() <= 2 && state.branches === 1 && state.staff === '1-5') return 'starter';
    return 'pro';
  }

  function calcMonthly(pkg) {
    let m = base[pkg].monthly * (sectorMult[state.sector] || 1) * (staffMult[state.staff] || 1);
    if (state.branches > 1) m *= 1 + (state.branches - 1) * 0.18;
    if (pkg !== 'starter') {
      if (state.modules.sentinel) m += premiumAdd.sentinel;
      if (state.modules.recall) m += premiumAdd.recall;
    }
    return m;
  }

  function updateSteps() {
    const done = [
      true,
      state.sector !== 'health' || state.branches !== 1,
      state.staff !== '1-5',
      state.modules.sentinel || state.modules.recall || activeModules() < 4,
      true,
    ];
    steps.forEach((step, i) => {
      step.classList.toggle('active', i === 4 || done[i]);
      step.classList.toggle('done', done[i]);
    });
  }

  function render() {
    const rec = recommendPackage();
    Object.entries(cards).forEach(([key, card]) => {
      if (!card) return;
      const monthly = calcMonthly(key);
      const amt = card.querySelector('.price-amt');
      const setup = card.querySelector('.price-setup');
      const badge = card.querySelector('.pop-badge');
      if (amt) {
        amt.innerHTML = key === 'enterprise' && rec === 'enterprise'
          ? `${formatTl(monthly)} TL<span>+ /ay</span>`
          : `${formatTl(monthly)} TL<span> /ay</span>`;
      }
      if (setup && base[key].setup) {
        setup.textContent = `+ ${formatTl(base[key].setup)} TL kurulum (tek sefer)`;
      }
      card.classList.toggle('pop', key === rec);
      if (badge) {
        badge.textContent = key === rec ? 'ÖNERİLEN' : '';
        badge.style.display = key === rec ? '' : 'none';
      }
    });

    if (branchHint) {
      branchHint.textContent = state.branches >= 2
        ? `${state.branches} şube seçildi — Kurumsal paket önerilir.`
        : '2+ şubede otomatik olarak "Kurumsal" paket önerilir.';
    }

    if (summaryEl) {
      const names = { starter: 'Başlangıç', pro: 'Profesyonel', enterprise: 'Kurumsal' };
      summaryEl.innerHTML = `Size önerilen paket: <strong>${names[rec]}</strong> · Tahmini <strong>${formatTl(calcMonthly(rec))} TL/ay</strong> · Pilot: ilk 3 ay <strong>5.000 TL</strong>`;
    }

    updateSteps();
  }

  sectorCards.forEach(card => {
    card.addEventListener('click', () => {
      state.sector = card.dataset.sector || 'health';
      sectorCards.forEach(c => c.classList.toggle('featured', c === card));
      render();
    });
  });

  staffTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      state.staff = tab.dataset.staff || '1-5';
      staffTabs.forEach(t => t.classList.toggle('active', t === tab));
      render();
    });
  });

  root.querySelectorAll('.pricing-module').forEach(item => {
    item.addEventListener('click', () => {
      const key = item.dataset.module;
      if (!key) return;
      const isPremium = item.classList.contains('premium');
      if (!isPremium) {
        const checked = item.classList.contains('checked');
        if (checked && activeModules() <= 1) return;
      }
      item.classList.toggle('checked');
      state.modules[key] = item.classList.contains('checked');
      const cb = item.querySelector('.cb');
      if (cb) cb.textContent = item.classList.contains('checked') ? '✓' : '';
      render();
    });
  });

  const minus = root.querySelector('.counter-minus');
  const plus = root.querySelector('.counter-plus');
  if (minus && plus && branchVal) {
    minus.addEventListener('click', () => {
      if (state.branches > 1) {
        state.branches -= 1;
        branchVal.textContent = state.branches;
        render();
      }
    });
    plus.addEventListener('click', () => {
      if (state.branches < 20) {
        state.branches += 1;
        branchVal.textContent = state.branches;
        render();
      }
    });
  }

  render();
}
