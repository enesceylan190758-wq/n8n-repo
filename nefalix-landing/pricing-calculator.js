(function () {
  if (window.__nefalixPricingInit) return;

  function boot() {
    const root = document.getElementById('pricing-page');
    if (!root) return;
    window.__nefalixPricingInit = true;
    document.body.classList.add('page-pricing');

    const state = {
      sector: null,
      subType: null,
      branches: 1,
      staff: '1-5',
      modules: {
        feedback: true,
        inbox: true,
        reviews: true,
        enps: true,
        sentinel: false,
        recall: false,
        pilot: false,
      },
    };

    const sectorBtns = root.querySelectorAll('#pricing-sector-list .pricing-option');
    const sectorTrigger = root.querySelector('#pricing-sector-trigger');
    const sectorPanel = root.querySelector('#pricing-sector-panel');
    const sectorValue = root.querySelector('#pricing-sector-value');
    const subGroups = root.querySelectorAll('.pricing-sub-group');
    const subBtns = root.querySelectorAll('.pricing-sub-group .pricing-option');
    const branchVal = root.querySelector('#pricing-branches');
    const branchHint = root.querySelector('#pricing-branch-hint');
    const summary = root.querySelector('#pricing-summary');
    const steps = root.querySelectorAll('.pricing-steps .pstep');
    const stepBlocks = root.querySelectorAll('.pricing-step-block');
    const staffTabs = root.querySelectorAll('.pricing-staff-tab');
    const modules = root.querySelectorAll('.pricing-module');
    const cards = {
      starter: root.querySelector('[data-package="starter"]'),
      pro: root.querySelector('[data-package="pro"]'),
      enterprise: root.querySelector('[data-package="enterprise"]'),
    };
    const checkoutPlan = root.querySelector('#pricing-checkout-plan');
    const checkoutPrice = root.querySelector('#pricing-checkout-price');
    const checkoutBtn = root.querySelector('#pricing-checkout-btn');
    const minusBtn = root.querySelector('.counter-minus');
    const plusBtn = root.querySelector('.counter-plus');

    const SECTOR_LABELS = { health: 'Sağlık / Klinik', hotel: 'Otel', auto: 'Auto Servis' };
    const SUB_LABELS = {
      health: {
        dental: 'Diş Klinikleri',
        hair: 'Saç Ekimi Merkezleri',
        aesthetic: 'Estetik / Plastik Cerrahi',
        eye: 'Göz Tedavi Merkezi',
      },
      hotel: {
        boutique: 'Butik / Bağımsız Otel',
        chain: 'Otel Zinciri',
        resort: 'Resort / Tatil Oteli',
        city: 'Şehir Oteli',
      },
      auto: {
        independent: 'Bağımsız Servis',
        authorized: 'Yetkili Servis',
        quick: 'Hızlı Bakım / Yağ Değişimi',
        fleet: 'Filo / Ticari Araç',
      },
    };
    const PLAN_META = {
      starter: { name: 'Başlangıç' },
      pro: { name: 'Profesyonel' },
      enterprise: { name: 'Kurumsal' },
    };
    const sectorMult = { health: 1, hotel: 0.92, auto: 0.88 };
    const subMult = {
      health: { dental: 1, hair: 1.06, aesthetic: 1.1, eye: 1.04 },
      hotel: { boutique: 1, chain: 1.08, resort: 1.05, city: 0.98 },
      auto: { independent: 1, authorized: 1.04, quick: 0.95, fleet: 1.1 },
    };
    const staffMult = { '1-5': 1, '6-15': 1.12, '16-30': 1.28, '30+': 1.45 };
    const base = {
      starter: { monthly: 9500, setup: 25000 },
      pro: { monthly: 14900, setup: 50000 },
      enterprise: { monthly: 45000, setup: null },
    };
    const premiumAdd = { sentinel: 3500, recall: 2500 };

    let selectedPkg = 'pro';
    let userPickedPackage = false;

    function formatTl(n) {
      return Math.round(n).toLocaleString('tr-TR');
    }

    function activeModules() {
      return Object.entries(state.modules).filter(([key, on]) => on && key !== 'pilot').length;
    }

    function isReady() {
      return Boolean(state.sector && state.subType);
    }

    function recommendPackage() {
      if (!isReady()) return 'pro';
      if (state.modules.pilot) return 'pro';
      if (state.branches >= 2 || state.staff === '30+') return 'enterprise';
      if (state.staff === '16-30' || state.modules.sentinel || state.modules.recall) return 'pro';
      if (activeModules() <= 2 && state.branches === 1 && state.staff === '1-5') return 'starter';
      return 'pro';
    }

    function calcMonthlyRaw(pkg) {
      if (!isReady()) return base[pkg].monthly;
      let m = base[pkg].monthly * (sectorMult[state.sector] || 1) * (staffMult[state.staff] || 1);
      const sectorSubs = subMult[state.sector] || {};
      m *= sectorSubs[state.subType] || 1;
      if (state.branches > 1) m *= 1 + (state.branches - 1) * 0.18;
      if (pkg !== 'starter') {
        if (state.modules.sentinel) m += premiumAdd.sentinel;
        if (state.modules.recall) m += premiumAdd.recall;
      }
      return m;
    }

    function calcMonthly(pkg) {
      if (state.modules.pilot && pkg === 'pro' && isReady()) {
        return calcMonthlyRaw('starter');
      }
      return calcMonthlyRaw(pkg);
    }

    function calcSetup(pkg) {
      if (state.modules.pilot && pkg === 'pro') return 0;
      return base[pkg].setup;
    }

    function sectorSummaryLabel() {
      if (!state.sector) return 'Sektör seçilmedi';
      const subLabel = state.subType
        ? (SUB_LABELS[state.sector] || {})[state.subType]
        : 'alt tip seçilmedi';
      return `${SECTOR_LABELS[state.sector]} · ${subLabel || ''}`;
    }

    function currentStepIndex() {
      if (!state.sector || !state.subType) return 0;
      if (state.modules.sentinel || state.modules.recall || state.modules.pilot || activeModules() < 4) return 4;
      if (state.staff !== '1-5') return 3;
      if (state.branches !== 1) return 2;
      return 1;
    }

    function updateSteps() {
      const current = currentStepIndex();
      steps.forEach((step, i) => {
        step.classList.toggle('active', i === current);
        step.classList.toggle('done', i < current);
      });
      stepBlocks.forEach((block, i) => {
        block.classList.toggle('is-active-step', i === current);
      });
    }

    function flash(el) {
      if (!el) return;
      el.classList.remove('pricing-flash');
      void el.offsetWidth;
      el.classList.add('pricing-flash');
    }

    function pulsePrices() {
      root.querySelectorAll('.price-amt').forEach((el) => {
        el.classList.remove('pricing-price-pulse');
        void el.offsetWidth;
        el.classList.add('pricing-price-pulse');
      });
    }

    function summaryHtml() {
      if (!isReady()) {
        return '<span class="pricing-summary-meta">Adım 1</span>Önce sektörünüzü ve alt tipinizi seçin — ardından fiyat anında hesaplanır.';
      }
      const names = { starter: 'Başlangıç', pro: 'Profesyonel', enterprise: 'Kurumsal' };
      const rec = recommendPackage();
      const branchLabel = state.branches === 1 ? '1 şube' : `${state.branches} şube`;
      const pilotNote = state.modules.pilot
        ? ` · Pilot: Profesyonel <strong>${formatTl(calcMonthly('pro'))} TL/ay</strong> (Başlangıç fiyatı) · kurulum yok · 6 ay sabit`
        : '';
      return `<span class="pricing-summary-meta">${sectorSummaryLabel()} · ${branchLabel} · ${state.staff} çalışan · ${activeModules()} modül</span>
        Önerilen paket: <strong>${names[rec]}</strong> · <strong>${formatTl(calcMonthly(rec))} TL/ay</strong>${pilotNote}`;
    }

    function updateCheckoutPanel(rec) {
      if (!userPickedPackage) selectedPkg = rec;
      const meta = PLAN_META[selectedPkg] || PLAN_META.pro;
      Object.entries(cards).forEach(([key, card]) => {
        if (!card) return;
        card.classList.toggle('selected', key === selectedPkg);
      });
      if (checkoutPlan) checkoutPlan.textContent = meta.name;
      if (checkoutPrice) {
        checkoutPrice.textContent = isReady()
          ? `${formatTl(calcMonthly(selectedPkg))} TL / ay`
          : 'Sektör seçin';
      }
      if (checkoutBtn) {
        checkoutBtn.textContent = selectedPkg === 'enterprise'
          ? 'Kurumsal teklif için demo al'
          : 'Bu paket için demo randevusu al';
      }
    }

    function render() {
      const rec = recommendPackage();
      Object.entries(cards).forEach(([key, card]) => {
        if (!card) return;
        const monthly = calcMonthly(key);
        const setup = calcSetup(key);
        const amt = card.querySelector('.price-amt');
        const setupEl = card.querySelector('.price-setup');
        const badge = card.querySelector('.pop-badge');
        if (amt) {
          amt.innerHTML = !isReady()
            ? '—<span> /ay</span>'
            : key === 'enterprise' && rec === 'enterprise'
              ? `${formatTl(monthly)} TL<span>+ /ay</span>`
              : `${formatTl(monthly)} TL<span> /ay</span>`;
        }
        if (setupEl) {
          if (state.modules.pilot && key === 'pro') {
            setupEl.textContent = 'Başlangıç fiyatına düşer · 6 ay sabit · kurulum ücreti yok';
          } else if (setup) {
            setupEl.textContent = `+ ${formatTl(setup)} TL kurulum (tek sefer)`;
          } else if (key === 'enterprise') {
            setupEl.textContent = 'Kurulum bedeli teklif ile';
          }
        }
        card.classList.toggle('pop', isReady() && key === rec);
        if (badge) {
          badge.textContent = isReady() && key === rec ? 'ÖNERİLEN' : '';
          badge.style.display = isReady() && key === rec ? '' : 'none';
        }
      });

      if (branchHint) {
        branchHint.textContent = state.branches >= 2
          ? `${state.branches} şube seçildi — Kurumsal paket önerilir.`
          : '2+ şubede otomatik olarak "Kurumsal" paket önerilir.';
      }

      if (summary) {
        summary.innerHTML = summaryHtml();
        flash(summary);
      }

      updateCheckoutPanel(rec);
      updateSteps();
      if (isReady()) pulsePrices();
    }

    function toggleSectorPanel(open) {
      if (!sectorPanel || !sectorTrigger) return;
      const shouldOpen = open ?? sectorPanel.hidden;
      sectorPanel.hidden = !shouldOpen;
      sectorTrigger.classList.toggle('is-open', shouldOpen);
      sectorTrigger.setAttribute('aria-expanded', shouldOpen ? 'true' : 'false');
    }

    function updateSubGroups() {
      subGroups.forEach((group) => {
        group.hidden = group.dataset.sector !== state.sector;
      });
    }

    function selectSector(sector) {
      state.sector = sector;
      state.subType = null;
      sectorBtns.forEach((btn) => btn.classList.toggle('is-selected', btn.dataset.sector === sector));
      subBtns.forEach((btn) => btn.classList.remove('is-selected'));
      if (sectorValue) sectorValue.textContent = SECTOR_LABELS[sector] || 'Seçildi';
      toggleSectorPanel(false);
      updateSubGroups();
      render();
    }

    function selectSubType(type) {
      state.subType = type;
      subBtns.forEach((btn) => {
        const inSector = btn.closest('.pricing-sub-group')?.dataset.sector === state.sector;
        btn.classList.toggle('is-selected', inSector && btn.dataset.sub === type);
      });
      render();
    }

    function selectStaff(tab) {
      state.staff = tab.dataset.staff || '1-5';
      staffTabs.forEach((t) => {
        const on = t === tab;
        t.classList.toggle('active', on);
        t.setAttribute('aria-selected', on ? 'true' : 'false');
      });
      render();
    }

    function toggleModule(item) {
      const key = item.dataset.module;
      if (!key) return;

      if (key === 'pilot') {
        const on = !item.classList.contains('checked');
        item.classList.toggle('checked', on);
        state.modules.pilot = on;
        const cb = item.querySelector('.cb');
        if (cb) cb.textContent = on ? '✓' : '';
        if (on) {
          selectedPkg = 'pro';
          userPickedPackage = true;
        }
        render();
        return;
      }

      const isPremium = item.classList.contains('premium');
      if (!isPremium && item.classList.contains('checked') && activeModules() <= 1) return;

      const on = !item.classList.contains('checked');
      item.classList.toggle('checked', on);
      state.modules[key] = on;
      const cb = item.querySelector('.cb');
      if (cb) cb.textContent = on ? '✓' : '';
      render();
    }

    function onActivate(el, handler) {
      const run = (e) => {
        e.preventDefault();
        handler(e);
      };
      el.addEventListener('click', run);
      el.addEventListener('touchend', run, { passive: false });
    }

    sectorBtns.forEach((btn) => {
      onActivate(btn, () => selectSector(btn.dataset.sector));
    });

    if (sectorTrigger) {
      onActivate(sectorTrigger, () => toggleSectorPanel());
    }

    subBtns.forEach((btn) => {
      onActivate(btn, () => selectSubType(btn.dataset.sub));
    });

    staffTabs.forEach((tab) => {
      onActivate(tab, () => selectStaff(tab));
    });

    modules.forEach((item) => {
      onActivate(item, () => toggleModule(item));
    });

    if (minusBtn) {
      onActivate(minusBtn, () => {
        if (state.branches > 1) {
          state.branches -= 1;
          if (branchVal) branchVal.textContent = state.branches;
          render();
        }
      });
    }

    if (plusBtn) {
      onActivate(plusBtn, () => {
        if (state.branches < 20) {
          state.branches += 1;
          if (branchVal) branchVal.textContent = state.branches;
          render();
        }
      });
    }

    Object.values(cards).forEach((card) => {
      if (!card) return;
      card.addEventListener('click', (e) => {
        if (e.target.closest('.pricing-pay-btn')) return;
        userPickedPackage = true;
        selectedPkg = card.dataset.package || selectedPkg;
        render();
      });
      const payBtn = card.querySelector('.pricing-pay-btn');
      if (payBtn) {
        payBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          userPickedPackage = true;
          selectedPkg = card.dataset.package || selectedPkg;
          render();
        });
      }
    });

    root.querySelectorAll('.reveal').forEach((el) => {
      el.classList.remove('pre');
      el.classList.add('in');
    });

    updateSubGroups();
    render();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
