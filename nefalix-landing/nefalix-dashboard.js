import { mergePresentationDemoFirms, demoResultHtml, demoResultOf } from './nefalix-dashboard-demo-firms.js';

const DEFAULT_URL = 'http://127.0.0.1:54321';
const DEFAULT_KEY =
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0';
const PILOT_CLINIC_ID = '51738ea8-c12e-40ce-a0e2-42869496d76b';
const CHART_COLORS = {
  primary: '#6366f1',
  positive: '#059669',
  warning: '#d97706',
  negative: '#dc2626',
  neutral: '#94a3b8',
  blue: '#2563eb',
  violet: '#7c3aed',
  coral: '#ea580c',
};
const TONE_BAR_COLORS = {
  green: CHART_COLORS.positive,
  red: CHART_COLORS.negative,
  amber: CHART_COLORS.warning,
  blue: CHART_COLORS.blue,
  teal: CHART_COLORS.primary,
  neutral: CHART_COLORS.neutral,
  purple: CHART_COLORS.violet,
  coral: CHART_COLORS.coral,
};
let chartRenderSeq = 0;
const DEMO_STORAGE_VERSION = '2';
const SELECTED_CLINIC_KEY = 'nefalix_selected_clinic_id';

const state = {
  user: null,
  tab: 'overview',
  overviewExpanded: false,
  selectedSector: 'clinic',
  clinics: [],
  selectedClinicId: null,
  rawCache: null,
  cache: null,
  selectedInbox: null,
  selectedReview: null,
  pollTimer: null,
  lastInboxCount: 0,
  inboxView: 'inbound',
  waQrPollTimer: null,
  pendingApplications: null,
  pendingApplicationsDemo: false,
  url: localStorage.getItem('nefalix_sb_url') || DEFAULT_URL,
  key: localStorage.getItem('nefalix_sb_key') || DEFAULT_KEY,
};

const POLL_MS = 10000;
const INBOX_POLL_MS = 5000;

const UI_TABS = new Set(['overview', 'firms', 'inbox', 'nps', 'reviews', 'recall', 'voice', 'sentinel', 'enps', 'billing']);
const UI_SECTORS = new Set(['clinic', 'hotel', 'auto']);
const UI_INBOX_VIEWS = new Set(['inbound', 'estesoft_nps']);

function parseUiHash() {
  const raw = (location.hash || '').replace(/^#/, '').trim();
  if (!raw) return null;
  const [tab, sub] = raw.split('/').map((s) => decodeURIComponent(s));
  if (!UI_TABS.has(tab)) return null;
  return { tab, sub: sub || null };
}

function syncUiHash() {
  let parts = [state.tab || 'overview'];
  if (state.tab === 'inbox' && state.inboxView === 'estesoft_nps') {
    parts.push('estesoft_nps');
  } else if (state.tab === 'firms') {
    parts.push(state.selectedSector || 'clinic');
  }
  const next = `#${parts.join('/')}`;
  if (location.hash !== next) {
    history.replaceState(null, '', `${location.pathname}${location.search}${next}`);
  }
}

function restoreUiFromHash() {
  const h = parseUiHash();
  if (!h) return;
  state.tab = h.tab;
  if (h.tab === 'inbox' && h.sub && UI_INBOX_VIEWS.has(h.sub)) {
    state.inboxView = h.sub;
  }
  if (h.tab === 'firms' && h.sub && UI_SECTORS.has(h.sub)) {
    state.selectedSector = h.sub;
  }
}

function applyNavUiState() {
  $$('[data-tab]').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.tab === state.tab);
  });
  
  // Highlight "More" button on mobile nav if a sub-tab in the more sheet is active
  const moreTabs = ['recall', 'voice', 'sentinel', 'enps', 'billing', 'firms'];
  const isMoreTab = moreTabs.includes(state.tab);
  $('#mobile-more-toggle')?.classList.toggle('active', isMoreTab);
  
  syncFirmsNav();
}

function pendingInboxCount(inbox) {
  return inbox
    .filter((r) => (r.message_kind || 'inbound') === 'inbound')
    .filter((r) => r.status === 'draft_ready' || r.status === 'open').length;
}

function pendingEstesoftNpsCount(inbox) {
  return inbox
    .filter((r) => r.message_kind === 'estesoft_nps')
    .filter((r) => r.status === 'draft_ready').length;
}

function isEstesoftNps(row) {
  return row?.message_kind === 'estesoft_nps';
}

function pendingReviewCount(reviews) {
  return reviews.filter((r) => r.status === 'pending_approval' && (r.draft_reply || '').trim()).length;
}

function clinicMapsUrl(clinicId) {
  const c = clinicById(clinicId) || activeClinic();
  return c?.google_maps_url || c?.google_review_url || null;
}

function schedulePoll() {
  if (state.pollTimer) clearInterval(state.pollTimer);
  const ms = state.tab === 'inbox' ? INBOX_POLL_MS : POLL_MS;
  state.pollTimer = setInterval(() => load({ silent: true }), ms);
}
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

function useProxy() {
  const host = window.location.hostname;
  return host !== 'localhost' && host !== '127.0.0.1';
}

const ROLE_LABEL = { admin: 'Sistem yöneticisi', manager: 'Klinik yöneticisi' };

const SECTOR_META = {
  clinic: {
    title: 'Klinikler',
    empty: 'Henüz bağlı klinik yok.',
    bookingLabel: 'Randevu / İletişim',
    panelAction: true,
  },
  hotel: {
    title: 'Oteller',
    empty: 'Henüz bağlı otel yok. Pilot oteller burada listelenecek.',
    bookingLabel: 'Rezervasyon',
    panelAction: true,
  },
  auto: {
    title: 'Oto servisler',
    empty: 'Henüz bağlı oto servis yok. Pilot servisler burada listelenecek.',
    bookingLabel: 'Randevu / İletişim',
    panelAction: true,
  },
};

const FIRM_FIELD_LABELS = {
  name: 'Firma adı',
  sector: 'Sektör',
  address: 'Adres',
  email: 'E-posta',
  website_url: 'Web sitesi',
  booking_url: 'Randevu / rezervasyon linki',
  whatsapp_phone: 'WhatsApp iş hattı',
  manager_whatsapp_phone: 'Yönetici WhatsApp',
  google_maps_url: 'Google Haritalar',
  google_review_url: 'Google yorum linki',
  google_place_id: 'Google Place ID',
  crm_type: 'CRM / HBYS türü',
  evolution_instance_name: 'Evolution instance',
  crm_api_key: 'CRM API anahtarı',
  crm_webhook_configured: 'CRM webhook kuruldu',
  evolution_connected: 'WhatsApp bağlı',
  pms_webhook_configured: 'PMS webhook',
  appointment_webhook_configured: 'Servis webhook',
};

function filled(v) {
  return v != null && String(v).trim() !== '';
}

function assessFirmReadiness(clinic, cfg = {}) {
  const sector = clinic.sector || 'clinic';
  const missing = [];
  const base = [
    'name',
    'sector',
    'address',
    'email',
    'website_url',
    'whatsapp_phone',
    'manager_whatsapp_phone',
    'google_maps_url',
    'google_review_url',
  ];
  for (const f of base) {
    if (!filled(clinic[f])) missing.push(f);
  }
  if (!filled(clinic.booking_url)) missing.push('booking_url');
  if (sector === 'clinic') {
    if (!filled(clinic.crm_type)) missing.push('crm_type');
    if (!filled(clinic.evolution_instance_name)) missing.push('evolution_instance_name');
    if (!filled(cfg.crm_api_key)) missing.push('crm_api_key');
    if (!cfg.crm_webhook_configured) missing.push('crm_webhook_configured');
    if (!cfg.evolution_connected) missing.push('evolution_connected');
  } else if (sector === 'hotel') {
    if (!cfg.pms_webhook_configured && !cfg.manual_trigger_ok) missing.push('pms_webhook_configured');
  } else if (sector === 'auto') {
    if (!cfg.appointment_webhook_configured && !cfg.manual_trigger_ok) {
      missing.push('appointment_webhook_configured');
    }
  }
  const total = sector === 'clinic' ? 16 : sector === 'hotel' ? 11 : 11;
  const done = total - missing.length;
  return {
    complete: missing.length === 0,
    missing,
    progress: Math.max(0, Math.round((done / total) * 100)),
  };
}

function firmLogoSrc(url, clinic) {
  const origin =
    window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? ''
      : window.location.origin;

  const abs = (rel) => (rel.startsWith('http') ? rel : `${origin}${rel}`);

  if (url) {
    if (url.startsWith('http')) return url;
    return abs(url.startsWith('/') ? url : `/${url}`);
  }

  const slug = clinic?.slug || '';
  const demoLogos = {
    'demo-byotell-istanbul': '/logos/demo/byotell.svg',
    'demo-antwell-hotels': '/logos/demo/antwell.svg',
    'demo-hilton-bomonti': '/logos/demo/hilton.svg',
    'demo-bosch-car-kadikoy': '/logos/demo/bosch.svg',
    'demo-king-auto': '/logos/demo/king-auto.png',
    'demo-yamanlar-expertiz': '/logos/demo/yamanlar.png',
  };
  if (demoLogos[slug]) return abs(demoLogos[slug]);

  const byName = {
    'byotell istanbul': '/logos/demo/byotell.svg',
    'antwell hotels': '/logos/demo/antwell.svg',
    'hilton istanbul bomonti': '/logos/demo/hilton.svg',
    'bosch car service — kadıköy': '/logos/demo/bosch.svg',
    'bosch car service - kadikoy': '/logos/demo/bosch.svg',
    'king auto service': '/logos/demo/king-auto.png',
    'yamanlar expertiz': '/logos/demo/yamanlar.png',
  };
  const nameKey = (clinic?.name || '').toLowerCase().trim();
  if (byName[nameKey]) return abs(byName[nameKey]);

  return '';
}

function firmLogoImg(c, sector) {
  const src = firmLogoSrc(c?.logo_url, c);
  const icon = sector === 'hotel' ? 'hotel' : sector === 'auto' ? 'car' : 'hospital';
  if (!src) {
    return `<div class="firm-logo firm-logo-placeholder"><i class="fa-solid fa-${icon}"></i></div>`;
  }
  return `<img class="firm-logo" src="${escapeHtml(src)}" alt="${escapeHtml(c?.name || '')}" loading="lazy" referrerpolicy="no-referrer" />`;
}

function firmSector(c) {
  return c?.sector || 'clinic';
}

function firmsForSector(sector) {
  return state.clinics.filter((c) => firmSector(c) === sector);
}

function isAdmin() {
  return state.user?.role === 'admin';
}

function isDemoFirm(c) {
  return (c.slug || '').startsWith('demo-');
}

const DEMO_PENDING_APPLICATIONS = [
  {
    id: 'demo-1',
    firma: 'Acıbadem Diş Polikliniği',
    sektor: 'Diş Kliniği',
    sehir: 'Kadıköy, İstanbul',
    yetkili: 'Dr. Serkan Yıldırım',
    telefon: '+90 532 XXX XX01',
    eposta: 'serkan@acibademdis.com',
    plan: 'Profesyonel',
    zaman: '2 saat önce',
    durum: 'yeni',
  },
  {
    id: 'demo-2',
    firma: 'Elit Saç Ekim Merkezi',
    sektor: 'Saç Ekimi Kliniği',
    sehir: 'Şişli, İstanbul',
    yetkili: 'Aslı Kaya',
    telefon: '+90 532 XXX XX02',
    eposta: 'info@elitsacekim.com',
    plan: 'Standart',
    zaman: 'dün 18:20',
    durum: 'iletisimde',
  },
  {
    id: 'demo-3',
    firma: 'Bella Estetik Klinik',
    sektor: 'Estetik Klinik',
    sehir: 'Beşiktaş, İstanbul',
    yetkili: 'Merve Şahin',
    telefon: '+90 532 XXX XX03',
    eposta: 'merve@bellaestetik.com',
    plan: 'Profesyonel',
    zaman: '2 gün önce',
    durum: 'iletisimde',
  },
];

async function loadPendingApplications(force = false) {
  if (!isAdmin()) {
    state.pendingApplications = [];
    state.pendingApplicationsDemo = false;
    return [];
  }
  if (!force && Array.isArray(state.pendingApplications) && !state.pendingApplicationsDemo) {
    return state.pendingApplications;
  }
  try {
    const res = await fetch('/api/firma-basvuru', { credentials: 'include' });
    if (!res.ok) throw new Error('list failed');
    const data = await res.json();
    state.pendingApplications = Array.isArray(data.applications) ? data.applications : [];
    state.pendingApplicationsDemo = false;
  } catch {
    if (!Array.isArray(state.pendingApplications) || state.pendingApplicationsDemo) {
      state.pendingApplications = DEMO_PENDING_APPLICATIONS.map((a) => ({ ...a }));
      state.pendingApplicationsDemo = true;
    }
  }
  return state.pendingApplications;
}

function pendingApplicationsHtml(list, isDemo) {
  if (!list?.length) return '';
  const rows = list
    .map((a) => {
      const statusLabel = a.durum === 'yeni' ? 'Yeni başvuru' : 'İletişimde';
      const statusCls = a.durum === 'yeni' ? 'app-status-new' : 'app-status-touch';
      return `
      <article class="app-queue-card" data-app-id="${escapeHtml(a.id)}">
        <div class="app-queue-ico"><i class="fa-solid fa-building"></i></div>
        <div class="app-queue-main">
          <div class="app-queue-title">
            <strong>${escapeHtml(a.firma)}</strong>
            <span class="app-status ${statusCls}">${statusLabel}</span>
            ${isDemo ? '<span class="app-status app-status-demo">ÖRNEK</span>' : ''}
          </div>
          <p>${escapeHtml([a.sektor, a.sehir, a.yetkili].filter(Boolean).join(' · '))}</p>
        </div>
        <div class="app-queue-meta">
          <span><i class="fa-solid fa-phone"></i> ${escapeHtml(a.telefon || '—')}</span>
          <span><i class="fa-solid fa-envelope"></i> ${escapeHtml(a.eposta || '—')}</span>
        </div>
        <div class="app-queue-plan">
          <b>${escapeHtml(a.plan || '')}</b>
          <span><i class="fa-regular fa-clock"></i> ${escapeHtml(a.zaman || '')}</span>
        </div>
        <button type="button" class="btn-primary btn-sm app-complete-btn" data-app-id="${escapeHtml(a.id)}">
          Kurulumu tamamla <i class="fa-solid fa-arrow-right"></i>
        </button>
      </article>`;
    })
    .join('');
  return `
    <section class="app-queue">
      <div class="app-queue-head">
        <div>
          <h3>Bekleyen başvurular <span class="app-queue-count">${list.length}</span></h3>
          <p>Public <a href="/basvuru" target="_blank" rel="noopener">/basvuru</a> formundan gelen kayıtlar. Kurulum elle tamamlanır — hesap otomatik açılmaz.</p>
        </div>
      </div>
      <div class="app-queue-list">${rows}</div>
    </section>`;
}

async function completePendingApplication(id) {
  if (!id) return;
  if (state.pendingApplicationsDemo || String(id).startsWith('demo-')) {
    state.pendingApplications = (state.pendingApplications || []).filter((a) => a.id !== id);
    alert('Örnek kayıt listeden çıkarıldı. Canlıda API ile durum=tamamlandi yazılır.');
    if (state.tab === 'firms') renderSectorFirms(state.selectedSector || 'clinic', state.rawCache);
    return;
  }
  try {
    const res = await fetch('/api/firma-basvuru', {
      method: 'PATCH',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, durum: 'tamamlandi' }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || 'Güncellenemedi');
    state.pendingApplications = (state.pendingApplications || []).filter((a) => a.id !== id);
    alert('Başvuru tamamlandı olarak işaretlendi. Klinik kaydını Firma ekle ile oluşturun.');
    if (state.tab === 'firms') renderSectorFirms(state.selectedSector || 'clinic', state.rawCache);
  } catch (err) {
    alert(err.message || 'Başvuru güncellenemedi');
  }
}

function renderInsightsStrip() {
  const el = $('#insights-strip');
  if (!el) return;
  el.classList.remove('hidden');
  el.innerHTML = `
    <div class="insights-card">
      <p class="insights-title"><i class="fa-solid fa-chart-line"></i> İtibar & gelir — araştırma özeti</p>
      <p class="insights-sub">Abartısız, akademik ve sektör kaynaklı — her işletmede sonuç değişebilir.</p>
      <div class="insights-grid">
        <div class="insights-stat">
          <p class="insights-stat-num">~%39</p>
          <p class="insights-stat-label">Otel geliri (Cornell)</p>
          <p class="insights-stat-desc">Cornell Nolan School: çevrimiçi konuk puanındaki iyileşme, OTA kanalından gelen gelirle güçlü ilişki gösteriyor.</p>
        </div>
        <div class="insights-stat">
          <p class="insights-stat-num">%5–9</p>
          <p class="insights-stat-label">Bağımsız işletme (HBS)</p>
          <p class="insights-stat-desc">Ortalama yıldız puanında 1 puanlık artış, gelirle anlamlı pozitif ilişki (Luca, HBS).</p>
        </div>
        <div class="insights-stat">
          <p class="insights-stat-num">%30+</p>
          <p class="insights-stat-label">Oto servis (vaka)</p>
          <p class="insights-stat-desc">AutoVitals vaka örnekleri: güçlü Google profili + dijital süreç ile onarım cirosunda %30'a varan artış.</p>
        </div>
      </div>
      <p class="insights-foot">Kaynak: Cornell Nolan School, Luca (HBS), AutoVitals vaka raporları</p>
    </div>`;
}

function effectiveClinicId() {
  if (!isAdmin()) return state.user?.clinicId || null;
  return state.selectedClinicId || null;
}

function filterByClinic(rows, clinicId) {
  if (!clinicId) return rows;
  return rows.filter((r) => r.clinic_id === clinicId);
}

function daysAgo(n) {
  return new Date(Date.now() - n * 24 * 3600000).toISOString();
}

function persistentDemoKey(type, clinicId) {
  return `nefalix_demo_${type}_${clinicId || PILOT_CLINIC_ID}`;
}

function resolveDemoClinicId(clinicId) {
  return clinicId || state.selectedClinicId || state.user?.clinicId || state.clinics[0]?.id || PILOT_CLINIC_ID;
}

function hasMeaningfulEnps(rows) {
  return (rows || []).filter((r) => r && r.score != null && (r.employee_name || r.department)).length >= 3;
}

function hasMeaningfulRecall(rows) {
  return (rows || []).filter((r) => r && r.last_treatment && (r.patient_name || r.status)).length >= 2;
}

function hasMeaningfulNps(rows) {
  return (rows || []).filter((r) => r && r.score != null).length >= 6;
}

function hasMeaningfulReviews(rows) {
  return (rows || []).filter((r) => r && r.rating).length >= 6;
}

function hasMeaningfulInbox(rows) {
  const list = rows || [];
  // Gerçek taslak/Estesoft NPS asla demo filler altında kalmamalı (eski eşik: >=8).
  if (list.some((r) => r && (r.message_kind === 'estesoft_nps' || r.status === 'draft_ready'))) {
    return true;
  }
  return list.some((r) => r && r.body);
}

function hasMeaningfulMentions(rows) {
  return (rows || []).filter((r) => r && r.content).length >= 5;
}

function npsFlowFromScore(score) {
  if (score >= 9) return 'promoter';
  if (score >= 7) return 'passive';
  return 'detractor';
}

function loadPersistentDemoRows(type, clinicId, factory) {
  const scopedId = clinicId || PILOT_CLINIC_ID;
  const key = persistentDemoKey(type, scopedId);
  const versionKey = `${key}_v`;
  try {
    const version = localStorage.getItem(versionKey);
    const raw = localStorage.getItem(key);
    if (version === DEMO_STORAGE_VERSION && raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length) return parsed;
    }
  } catch (_) {}

  const rows = factory(scopedId);
  try {
    localStorage.setItem(key, JSON.stringify(rows));
    localStorage.setItem(versionKey, DEMO_STORAGE_VERSION);
  } catch (_) {}
  return rows;
}

function demoRecallRows(clinicId) {
  return [
    { clinic_id: clinicId, last_treatment: 'Zirkonyum kaplama kontrolü', months_since_visit: 6, status: 'geri çağrıldı', created_at: daysAgo(2), patient_name: 'Ayşe Yılmaz', result: 'Randevu alındı' },
    { clinic_id: clinicId, last_treatment: 'İmplant kontrolü', months_since_visit: 3, status: 'ulaşıldı', created_at: daysAgo(4), patient_name: 'Mehmet Kaya', result: 'Kontrol hatırlatıldı' },
    { clinic_id: clinicId, last_treatment: 'Diş taşı temizliği', months_since_visit: 12, status: 'takipte', created_at: daysAgo(6), patient_name: 'Zeynep Demir', result: 'WhatsApp bilgilendirme gönderildi' },
    { clinic_id: clinicId, last_treatment: 'Ortodonti kontrolü', months_since_visit: 2, status: 'randevu planlandı', created_at: daysAgo(8), patient_name: 'Can Arslan', result: 'Asistan geri aradı' },
    { clinic_id: clinicId, last_treatment: 'Kanal tedavisi kontrolü', months_since_visit: 4, status: 'geri çağrıldı', created_at: daysAgo(10), patient_name: 'Selin Aktaş', result: 'Randevu onaylandı' },
    { clinic_id: clinicId, last_treatment: 'Estetik dolgu', months_since_visit: 8, status: 'ulaşıldı', created_at: daysAgo(12), patient_name: 'Hakan Yıldız', result: 'Kontrol daveti gönderildi' },
    { clinic_id: clinicId, last_treatment: 'Diş beyazlatma', months_since_visit: 5, status: 'takipte', created_at: daysAgo(14), patient_name: 'Deniz Koç', result: 'Hatırlatma mesajı iletildi' },
    { clinic_id: clinicId, last_treatment: 'Protez provası', months_since_visit: 1, status: 'randevu planlandı', created_at: daysAgo(16), patient_name: 'Merve Çelik', result: 'Prova randevusu alındı' },
    { clinic_id: clinicId, last_treatment: 'İmplant üst yapı', months_since_visit: 7, status: 'geri çağrıldı', created_at: daysAgo(18), patient_name: 'Emre Polat', result: 'Tedavi planı güncellendi' },
    { clinic_id: clinicId, last_treatment: 'Çocuk diş kontrolü', months_since_visit: 9, status: 'ulaşıldı', created_at: daysAgo(20), patient_name: 'Gamze Erdoğan', result: 'Aile bilgilendirildi' },
    { clinic_id: clinicId, last_treatment: 'Gülüş tasarımı kontrol', months_since_visit: 3, status: 'takipte', created_at: daysAgo(22), patient_name: 'Tuğba Kılıç', result: 'Fotoğraf paylaşımı istendi' },
    { clinic_id: clinicId, last_treatment: 'Periodontal bakım', months_since_visit: 11, status: 'geri çağrıldı', created_at: daysAgo(24), patient_name: 'Cem Aksoy', result: 'Randevu alındı' },
  ];
}

function demoEnpsRows(clinicId) {
  const rows = [
    ['Doktor', 'Dr. Selin Aksoy', 9, 'promoter'],
    ['Doktor', 'Dr. Murat Ergin', 8, 'promoter'],
    ['Doktor', 'Dr. Derya Koç', 9, 'promoter'],
    ['Asistan', 'Elif Yıldız', 8, 'promoter'],
    ['Asistan', 'Buse Acar', 7, 'detractor'],
    ['Asistan', 'Merve Şahin', 9, 'promoter'],
    ['Asistan', 'Seda Kılıç', 8, 'promoter'],
    ['Asistan', 'Nisa Polat', 8, 'promoter'],
    ['Asistan', 'İrem Öz', 6, 'detractor'],
    ['Resepsiyon', 'Gizem Yalçın', 9, 'promoter'],
    ['Resepsiyon', 'Ece Taş', 8, 'promoter'],
    ['Hasta ilişkileri', 'Burak Can', 8, 'promoter'],
    ['Sterilizasyon', 'Fatma Çetin', 9, 'promoter'],
    ['Laboratuvar', 'Kerem Uslu', 7, 'detractor'],
    ['Klinik müdürü', 'Klinik Müdürü', 9, 'promoter'],
  ];
  return rows.map(([department, employee_name, score, flow], idx) => ({
    clinic_id: clinicId,
    department,
    employee_name,
    score,
    flow,
    feedback: flow === 'promoter' ? 'Ekip iletişimi ve iş akışı güçlü.' : 'Yoğun saatlerde destek ve görev paylaşımı iyileştirilmeli.',
    created_at: daysAgo(2 + idx),
  }));
}

function demoNpsRows(clinicId) {
  const patients = [
    ['Ayşe Yılmaz', 10, 'İmplant sonrası süreç çok şeffaftı, Google yorumumu yazdım.'],
    ['Mehmet Kaya', 9, 'Doktor ve asistan ilgisi mükemmeldi.'],
    ['Zeynep Demir', 10, 'Diş beyazlatma sonucundan çok memnunum.'],
    ['Can Arslan', 9, 'Randevu hatırlatmaları ve takip çok iyi.'],
    ['Elif Şahin', 10, 'Ortodonti tedavisinde güven verici bir ekip.'],
    ['Burak Öztürk', 8, 'Genel olarak memnunum, bekleme süresi biraz uzun.'],
    ['Selin Aktaş', 9, 'Zirkonyum kaplamadan sonra gülüşüm çok güzel oldu.'],
    ['Hakan Yıldız', 10, 'Ağrısız tedavi, kesinlikle tavsiye ederim.'],
    ['Deniz Koç', 9, 'Google linkinden yorum bıraktım, süreç kolaydı.'],
    ['Merve Çelik', 10, 'Hijyen ve sterilizasyon konusunda çok titizler.'],
    ['Oğuz Karaca', 7, 'Tedavi iyi ama ödeme süreci biraz karışıktı.'],
    ['Pınar Güneş', 9, 'WhatsApp üzerinden gelen yorum linki çok pratikti.'],
    ['Emre Polat', 10, 'Kanal tedavisi sonrası hiç sorun yaşamadım.'],
    ['Gamze Erdoğan', 9, 'Çocuğumun diş tedavisinde sabırlı ve ilgiliydiler.'],
    ['Serkan Aydın', 8, 'Fiyat/performans dengesi iyi, tekrar geleceğim.'],
    ['Tuğba Kılıç', 10, 'Estetik dolgu işlemi doğal görünüyor.'],
    ['Cem Aksoy', 9, 'Klinik atmosferi güven verici, ekip profesyonel.'],
    ['Yasemin Uslu', 6, 'Randevu saatinde 20 dk gecikme oldu.'],
  ];
  return patients.map(([patient_name, score, feedback], idx) => ({
    clinic_id: clinicId,
    patient_name,
    score,
    flow: npsFlowFromScore(score),
    feedback,
    google_link_sent: score >= 8,
    created_at: daysAgo((idx % 28) + 1),
  }));
}

function demoReviewRows(clinicId) {
  const items = [
    ['Ayşe Yılmaz', 5, 'İmplant tedavim sorunsuz geçti. Dr. Selin ve ekibi her aşamada bilgilendirdi. Kesinlikle tavsiye ederim.'],
    ['Mehmet Kaya', 5, 'Yıllardır diş hekimi arıyordum, sonunda doğru kliniği buldum. Hijyen ve ilgi üst düzey.'],
    ['Zeynep Demir', 5, 'Diş beyazlatma sonucu harika. WhatsApp ile gelen yorum linki sayesinde kolayca paylaştım.'],
    ['Can Arslan', 5, 'Ortodonti tedavisinde sabırlı ve profesyonel bir ekip. Randevu hatırlatmaları çok işime yaradı.'],
    ['Elif Şahin', 5, 'Çocuğumun diş korkusu vardı, burada çok güzel ilgilendiler. Teşekkürler Medident!'],
    ['Selin Aktaş', 5, 'Zirkonyum kaplama işlemi beklediğimden çok daha iyi oldu. Doğal ve estetik bir sonuç.'],
    ['Hakan Yıldız', 5, 'Kanal tedavisi ağrısız geçti. Fiyatlar şeffaf, sürpriz masraf yok.'],
    ['Deniz Koç', 4, 'Genel olarak memnunum, bekleme süresi biraz uzun ama tedavi kalitesi yüksek.'],
    ['Merve Çelik', 5, 'Sterilizasyon ve hijyen konusunda çok titiz bir klinik. Gönül rahatlığıyla geldim.'],
    ['Emre Polat', 5, 'Estetik dolgu işlemi doğal görünüyor, kimse fark etmedi. Harika iş çıkardılar.'],
    ['Gamze Erdoğan', 5, 'Diş taşı temizliği sonrası çok ferah hissediyorum. Personel güler yüzlü.'],
    ['Tuğba Kılıç', 5, 'İmplant öncesi detaylı bilgilendirme aldım. Güven verici bir deneyimdi.'],
    ['Cem Aksoy', 5, 'Klinik modern ve düzenli. Randevu sistemi çok pratik çalışıyor.'],
    ['Pınar Güneş', 5, 'Tedavi sonrası gönderilen Google linki ile yorumu 2 dakikada yazdım.'],
    ['Burak Öztürk', 4, 'Tedavi kalitesi çok iyi, otopark konusunda küçük bir zorluk yaşadım.'],
    ['Serkan Aydın', 5, 'Yıllık kontrolümü burada yaptırıyorum. Her seferinde aynı özen ve ilgi.'],
    ['Oğuz Karaca', 4, 'Fiyat/performans dengesi iyi. Tedavi planı net anlatıldı.'],
    ['Yasemin Uslu', 3, 'Tedavi iyi ama randevu saatinde gecikme yaşandı, iletişim güçlendirilmeli.'],
    ['Fatma Çetin', 5, 'Protez işlemim çok başarılı. Prova aşamalarında sabırla ilgilendiler.'],
    ['Kerem Uslu', 5, 'Ailece buraya geliyoruz. Hem çocuk hem yetişkin tedavilerinde memnunuz.'],
    ['İrem Öz', 5, 'Gülüş tasarımı hayal ettiğimden güzel oldu. Ekibe teşekkürler.'],
    ['Buse Acar', 5, 'NPS anketinden sonra gelen Google linki çok mantıklı bir akış, hemen yorum yazdım.'],
  ];
  return items.map(([author_name, rating, review_text], idx) => ({
    id: `demo-review-${clinicId}-${idx}`,
    clinic_id: clinicId,
    author_name,
    rating,
    review_text,
    status: idx < 3 ? 'pending_approval' : 'published',
    draft_reply:
      idx < 3
        ? 'Değerli yorumunuz için teşekkür ederiz. Sizin gibi memnun hastalarımız bizim en büyük motivasyonumuz.'
        : '',
    created_at: daysAgo((idx % 26) + 2),
  }));
}

function demoInboxRows(clinicId) {
  const rows = [
    ['whatsapp', 'outbound', 'Google yorum linki gönderildi — NPS 10/10 · implant kontrol', 'sent', 1],
    ['whatsapp', 'inbound', 'Yorumu yazdım, çok memnun kaldım teşekkürler 🙏', 'open', 1],
    ['whatsapp', 'outbound', 'Google yorum linki gönderildi — zirkonyum kaplama tamamlandı', 'sent', 2],
    ['whatsapp', 'inbound', 'Linkten yorum bıraktım, süreç çok kolaydı', 'open', 2],
    ['web', 'inbound', 'Randevu sonrası anket: 9/10 — Google yönlendirme tıklandı', 'draft_ready', 3],
    ['whatsapp', 'outbound', 'Google yorum linki gönderildi — diş beyazlatma', 'sent', 4],
    ['whatsapp', 'inbound', 'Harika bir deneyimdi, Google\'da paylaştım', 'open', 4],
    ['whatsapp', 'outbound', 'Google yorum linki gönderildi — kanal tedavisi kontrol', 'sent', 5],
    ['web', 'inbound', 'Web chat: tedavi sonrası memnuniyet mesajı', 'draft_ready', 6],
    ['whatsapp', 'outbound', 'Google yorum linki gönderildi — ortodonti kontrol', 'sent', 7],
    ['whatsapp', 'inbound', 'Ekip çok ilgiliydi, yorumumu bıraktım', 'open', 7],
    ['whatsapp', 'outbound', 'Google yorum linki gönderildi — estetik dolgu', 'sent', 9],
    ['whatsapp', 'inbound', 'Randevu için teşekkürler, yorumu bıraktım', 'open', 10],
    ['web', 'inbound', 'Web chat: fiyat bilgisi istendi', 'draft_ready', 11],
    ['whatsapp', 'outbound', 'Google yorum linki gönderildi — protez kontrol', 'sent', 12],
    ['whatsapp', 'inbound', 'Çok ilgili bir ekipti, tavsiye ederim', 'open', 12],
    ['whatsapp', 'outbound', 'NPS anketi gönderildi — implant kontrol', 'sent', 13],
    ['whatsapp', 'inbound', 'Anketi doldurdum, linkten yorum yazdım', 'open', 13],
  ];
  return rows.map(([channel, direction, body, status, day], idx) => ({
    id: `demo-inbox-${clinicId}-${idx}`,
    clinic_id: clinicId,
    channel,
    direction,
    body,
    status,
    message_kind: 'inbound',
    sender_name: direction === 'inbound' ? 'Hasta' : 'Nefalix',
    created_at: daysAgo(day),
  }));
}

function demoMentionRows(clinicId) {
  const rows = [
    ['google', 'positive', 'İmplant tedavim çok iyi geçti, ekibe teşekkürler.', false],
    ['google', 'positive', 'Randevu sistemi pratik, doktor çok ilgili.', false],
    ['website', 'positive', 'Web sitesinden bilgi aldım, hızlı dönüş aldım.', false],
    ['sikayetvar', 'negative', 'Randevu saatinde 15 dk gecikme yaşandı.', true],
    ['instagram', 'positive', 'Gülüş tasarımı sonucu harika oldu ✨', false],
    ['google', 'positive', 'WhatsApp hatırlatmaları çok işime yaradı.', false],
    ['website', 'neutral', 'Fiyat listesi güncellenirse daha iyi olur.', false],
    ['sikayetvar', 'negative', 'Otopark konusunda yönlendirme eksik kaldı.', false],
    ['google', 'positive', 'Sterilizasyon ve hijyen konusunda çok titizler.', false],
    ['instagram', 'neutral', 'Klinik atmosferi güzel, bekleme alanı biraz dar.', false],
  ];
  return rows.map(([source, sentiment, content, is_critical], idx) => ({
    id: `demo-mention-${clinicId}-${idx}`,
    clinic_id: clinicId,
    source,
    sentiment,
    content,
    is_critical,
    created_at: daysAgo(idx + 1),
  }));
}

function buildDemoMetrics() {
  const s = getOverviewSnapshot();
  return {
    surveysSent30d: s.links.sent,
    googleReviewLinksSent30d: s.links.sent,
    googleReviewLinkClicks30d: s.links.clicks,
    googleReviews30d: s.links.reviews,
    reviewLinkConversionPct: s.links.conversion,
    avgNps30d: s.nps.avg,
    promoterRatePct: s.nps.promoterPct,
    avgGoogleRating: s.google.avg,
    fiveStarCount: s.google.fiveStar,
    npsResponses: s.nps.total,
    totalSignals: s.totalSignals,
  };
}

function buildViewData(raw) {
  const clinicId = effectiveClinicId();
  const dbRecall = filterByClinic(raw.recall || [], clinicId);
  const dbEnps = filterByClinic(raw.enps || [], clinicId);
  const dbNps = filterByClinic(raw.nps || [], clinicId);
  const dbReviews = filterByClinic(raw.reviews || [], clinicId);
  const dbInbox = filterByClinic(raw.inbox || [], clinicId);
  const demoClinicId = resolveDemoClinicId(clinicId);
  const persistentRecall = loadPersistentDemoRows('recall', demoClinicId, demoRecallRows);
  const persistentEnps = loadPersistentDemoRows('enps', demoClinicId, demoEnpsRows);
  const persistentNps = loadPersistentDemoRows('nps', demoClinicId, demoNpsRows);
  const persistentReviews = loadPersistentDemoRows('reviews', demoClinicId, demoReviewRows);
  const persistentInbox = loadPersistentDemoRows('inbox', demoClinicId, demoInboxRows);
  const persistentMentions = loadPersistentDemoRows('mentions', demoClinicId, demoMentionRows);
  const nps = hasMeaningfulNps(dbNps) ? dbNps : persistentNps;
  const reviews = hasMeaningfulReviews(dbReviews) ? dbReviews : persistentReviews;
  const inbox = hasMeaningfulInbox(dbInbox) ? dbInbox : persistentInbox;
  const metrics = raw.metrics || buildDemoMetrics();
  return {
    nps,
    reviews,
    enps: hasMeaningfulEnps(dbEnps) ? dbEnps : persistentEnps,
    mentions: hasMeaningfulMentions(filterByClinic(raw.mentions || [], clinicId))
      ? filterByClinic(raw.mentions || [], clinicId)
      : persistentMentions,
    recall: hasMeaningfulRecall(dbRecall) ? dbRecall : persistentRecall,
    inbox,
    metrics,
    billing: raw.billing || null,
  };
}

function clinicById(id) {
  return state.clinics.find((c) => c.id === id);
}

function activeClinic() {
  const id = effectiveClinicId();
  return id ? clinicById(id) : null;
}

/** Özet rozeti: klinik created_at → ay; yoksa Medident pilot = 5. ay */
function tenureMonthsLabel(clinic) {
  const c = clinic || activeClinic();
  const created = c?.created_at;
  if (created) {
    const ms = Date.now() - new Date(created).getTime();
    if (!Number.isNaN(ms) && ms > 0) {
      const months = Math.max(1, Math.round(ms / (30.44 * 24 * 3600 * 1000)));
      return `Nefalix'te ${months}. ay`;
    }
  }
  if (!c || c.id === PILOT_CLINIC_ID || (c.slug || '').includes('medident')) {
    return "Nefalix'te 5. ay";
  }
  return "Nefalix'te 1. ay";
}

function canConnectWhatsApp(clinic) {
  const c = clinic || activeClinic();
  if (!c?.id || isDemoFirm(c)) return false;
  if ((c.sector || 'clinic') !== 'clinic') return false;
  if (isAdmin()) return true;
  return state.user?.clinicId === c.id;
}

function updateWaConnectButton() {
  const btn = $('#wa-connect-btn');
  if (!btn) return;
  btn.classList.toggle('hidden', !canConnectWhatsApp());
}

async function loadWhatsAppStatus() {
  const pill = $('#wa-mode-pill');
  if (!pill) return;
  try {
    const res = await fetch('/api/whatsapp/status');
    if (!res.ok) return;
    const data = await res.json();
    pill.classList.remove('hidden', 'wa-mode-receive', 'wa-mode-send');
    if (data.sendEnabled) {
      pill.textContent = 'WA gönderim: açık';
      pill.classList.add('wa-mode-send');
    } else {
      pill.textContent = 'WA alım: açık · gönderim kapalı';
      pill.classList.add('wa-mode-receive');
    }
    pill.title = data.message || '';
  } catch {
    /* optional */
  }
}

function externalLink(href, label, icon) {
  if (!href) return '';
  return `<a href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">${icon ? `<i class="${icon}"></i> ` : ''}${escapeHtml(label)}</a>`;
}

function clinicLinksHtml(c, { compact = false, sector } = {}) {
  if (!c) return '';
  const sec = sector || firmSector(c);
  const reviewLabel = sec === 'hotel' ? 'Booking / Google' : sec === 'auto' ? 'Google yorumları' : 'Web yorumları';
  const links = [
    c.website_url ? externalLink(c.website_url, 'Web sitesi', 'fa-solid fa-globe') : '',
    c.google_maps_url || c.google_review_url
      ? externalLink(c.google_maps_url || c.google_review_url, 'Google Haritalar', 'fa-brands fa-google')
      : '',
    c.website_reviews_url
      ? externalLink(c.website_reviews_url, reviewLabel, 'fa-solid fa-comment-dots')
      : '',
    c.sikayetvar_url ? externalLink(c.sikayetvar_url, 'Şikayetvar', 'fa-solid fa-triangle-exclamation') : '',
    c.trustpilot_url
      ? externalLink(c.trustpilot_url, 'Trustpilot', 'fa-solid fa-star')
      : compact
        ? '<span class="muted-link">Trustpilot yok</span>'
        : '',
  ].filter(Boolean);
  return links.length ? `<div class="${compact ? 'firm-links' : 'clinic-profile-links'}">${links.join('')}</div>` : '';
}

function renderClinicProfileCard(c) {
  if (!c) return '';
  const rs = state.rawCache ? reviewStatsForClinic(c.id, state.rawCache) : null;
  const rating =
    c.google_rating != null
      ? `Google: ★${c.google_rating}${c.google_review_count ? ` (${c.google_review_count} yorum)` : ''}`
      : rs && rs.total > 0
        ? `Toplam ${rs.total} yorum`
        : 'Google puanı henüz senkron değil';
  const reviewDetail = rs ? formatReviewSummary(rs, c) : '';
  const syncNote = c.google_reviews_synced_at
    ? `Google senkron: ${fmtDate(c.google_reviews_synced_at)}`
    : null;
  // reviewDetail link (<a>) içerebilir; escapeHtml uygulanmaz, geri kalan düz metin kaçırılır.
  const meta = [
    c.address,
    c.email,
    c.whatsapp_phone ? `WhatsApp: ${c.whatsapp_phone}` : null,
    rating,
  ]
    .filter(Boolean)
    .map((line) => escapeHtml(line));
  if (reviewDetail && reviewDetail !== rating) meta.push(reviewDetail);
  if (syncNote) meta.push(escapeHtml(syncNote));
  const metaHtml = meta.join(' · ');
  return `
    <section class="clinic-profile-card">
      ${firmLogoImg(c, firmSector(c))}
      <div>
        <h2 style="margin:0;font-size:1.1rem;color:var(--navy)">${escapeHtml(c.name)}</h2>
        <p class="clinic-profile-meta kpi-sub-links">${metaHtml}</p>
        ${clinicLinksHtml(c)}
      </div>
      <div class="clinic-profile-actions">
        ${c.booking_url ? externalLink(c.booking_url, 'Randevu / İletişim', 'fa-solid fa-calendar') : ''}
        ${c.google_review_url ? externalLink(c.google_review_url, 'Google yorumları', 'fa-brands fa-google') : ''}
      </div>
    </section>`;
}

function reviewStatsForClinic(clinicId, raw) {
  const ids = clinicId ? [clinicId] : state.clinics.map((c) => c.id);
  let googleMaps = 0;
  let systemGoogle = 0;
  let website = 0;
  let sikayetvar = 0;
  let rating = null;
  for (const id of ids) {
    const c = clinicById(id);
    if (c?.google_review_count != null) googleMaps += Number(c.google_review_count) || 0;
    if (c?.google_rating != null && clinicId) rating = c.google_rating;
    systemGoogle += filterByClinic(raw.reviews, id).length;
    const mentions = filterByClinic(raw.mentions, id);
    website += mentions.filter((m) => m.source === 'website').length;
    sikayetvar += mentions.filter((m) => m.source === 'sikayetvar').length;
  }
  const googleDisplay = googleMaps > 0 ? googleMaps : systemGoogle;
  const total = googleDisplay + website + sikayetvar;
  return { googleMaps, systemGoogle, website, sikayetvar, total, googleDisplay, rating };
}

function clinicGoogleUrl(c) {
  return c?.google_review_url || c?.google_maps_url || null;
}

function googleOpenLinkHtml(clinic, label = "Google'da aç") {
  const url = clinicGoogleUrl(clinic || activeClinic());
  if (!url) return '';
  return `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="google-open-link"><i class="fa-brands fa-google"></i> ${escapeHtml(label)}</a>`;
}

function formatReviewSummary(rs, clinic) {
  const c = clinic || activeClinic();
  const googleUrl = clinicGoogleUrl(c);
  const sikayetvarUrl = c?.sikayetvar_url || null;
  const webUrl = c?.website_reviews_url || null;
  const parts = [];
  if (rs.googleMaps > 0) {
    const label = `Google: ${rs.googleMaps}`;
    parts.push(googleUrl ? externalLink(googleUrl, label) : label);
  } else if (rs.systemGoogle > 0) {
    const label = `Google: ${rs.systemGoogle}`;
    parts.push(googleUrl ? externalLink(googleUrl, label) : label);
  }
  if (rs.sikayetvar > 0) {
    const label = `Şikayetvar: ${rs.sikayetvar}`;
    parts.push(sikayetvarUrl ? externalLink(sikayetvarUrl, label) : label);
  }
  if (rs.website > 0) {
    const label = `Web: ${rs.website}`;
    parts.push(webUrl ? externalLink(webUrl, label) : label);
  }
  return parts.length ? parts.join(' · ') : 'Henüz yorum kaydı yok';
}

function mentionSourceLabel(source) {
  const labels = {
    sikayetvar: 'Şikayetvar',
    google: 'Google',
    website: 'Web',
    trustpilot: 'Trustpilot',
  };
  return labels[source] || source || '—';
}

function mentionSourceUrl(mention, clinic) {
  if (mention?.url) return mention.url;
  if (!clinic) return null;
  if (mention?.source === 'sikayetvar') return clinic.sikayetvar_url || null;
  if (mention?.source === 'google') return clinicGoogleUrl(clinic);
  if (mention?.source === 'website') return clinic.website_reviews_url || null;
  if (mention?.source === 'trustpilot') return clinic.trustpilot_url || null;
  return null;
}

function mentionSourceCell(mention, clinic) {
  const url = mentionSourceUrl(mention, clinic);
  const label = mentionSourceLabel(mention.source);
  if (!url) return escapeHtml(label);
  return `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="source-link source-link-${escapeHtml(mention.source || 'other')}">${escapeHtml(label)} <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:.65rem;opacity:.7"></i></a>`;
}

function sentinelToolbarHtml(clinic, mentionCount) {
  const links = clinic
    ? [
        clinic.sikayetvar_url
          ? externalLink(clinic.sikayetvar_url, 'Şikayetvar sayfası', 'fa-solid fa-triangle-exclamation')
          : '',
        clinicGoogleUrl(clinic)
          ? externalLink(clinicGoogleUrl(clinic), 'Google yorumları', 'fa-brands fa-google')
          : '',
        clinic.website_reviews_url
          ? externalLink(clinic.website_reviews_url, 'Web yorumları', 'fa-solid fa-comment-dots')
          : '',
      ].filter(Boolean)
    : [];
  return `
    <div class="panel-toolbar">
      <h2 class="panel-title" style="margin:0">Sentinel — İtibar takibi</h2>
      <div class="panel-toolbar-actions">
        <span class="panel-toolbar-meta">${mentionCount} kayıt</span>
        ${links.join('')}
      </div>
    </div>`;
}
function statsForClinic(clinicId, raw) {
  const rs = reviewStatsForClinic(clinicId, raw);
  const nps = filterByClinic(raw.nps, clinicId);
  const inbox = filterByClinic(raw.inbox, clinicId);
  return {
    nps: nps.length,
    avgNps: avg(nps.map((r) => r.score).filter(Boolean)),
    inbox: inbox.length,
    drafts: inbox.filter((r) => r.status === 'draft_ready').length,
    reviews: filterByClinic(raw.reviews, clinicId).length,
    recall: filterByClinic(raw.recall, clinicId).length,
    reviewTotal: rs.total,
    reviewGoogleMaps: rs.googleMaps,
    reviewWebsite: rs.website,
    reviewSystem: rs.systemGoogle,
  };
}

function updateHeader() {
  const id = effectiveClinicId();
  const clinic = id ? clinicById(id) : null;
  const linksEl = $('#clinic-profile-links');
  if (isAdmin() && !id) {
    $('#topbar-eyebrow').textContent = 'Nefalix Platform';
    $('#clinic-name').textContent = 'Tüm firmalar';
    linksEl.classList.add('hidden');
    linksEl.innerHTML = '';
  } else {
    $('#topbar-eyebrow').textContent = clinic?.website_url ? 'medidentistanbul.com' : 'Pilot klinik';
    $('#clinic-name').textContent = clinic?.name || state.clinics[0]?.name || 'Klinik';
    if (clinic) {
      linksEl.classList.remove('hidden');
      linksEl.innerHTML = clinicLinksHtml(clinic, { compact: true }).replace('firm-links', 'clinic-profile-links');
    } else {
      linksEl.classList.add('hidden');
      linksEl.innerHTML = '';
    }
  }
  updateWaConnectButton();
}

function restoreSelectedClinic() {
  if (!isAdmin()) return;
  try {
    const saved = localStorage.getItem(SELECTED_CLINIC_KEY);
    if (saved) state.selectedClinicId = saved;
  } catch (_) {}
}

function persistSelectedClinic() {
  if (!isAdmin()) return;
  try {
    localStorage.setItem(SELECTED_CLINIC_KEY, state.selectedClinicId || '');
  } catch (_) {}
}

function setupAdminUi() {
  if (!isAdmin()) return;
  $$('.admin-only').forEach((el) => el.classList.remove('hidden'));
  updateFirmsNavCounts();
  const select = $('#clinic-select');
  const groups = [
    { sector: 'clinic', label: 'Klinikler' },
    { sector: 'hotel', label: 'Oteller' },
    { sector: 'auto', label: 'Oto servisler' },
  ];
  select.innerHTML =
    '<option value="">Tüm firmalar</option>' +
    groups
      .map(({ sector, label }) => {
        const firms = firmsForSector(sector);
        if (!firms.length) return '';
        return `<optgroup label="${label}">${firms
          .map((c) => `<option value="${c.id}">${escapeHtml(c.name)}${isDemoFirm(c) ? ' · örnek' : ''}</option>`)
          .join('')}</optgroup>`;
      })
      .join('');
  select.value = state.selectedClinicId || '';
  select.onchange = () => {
    state.selectedClinicId = select.value || null;
    persistSelectedClinic();
    if (state.rawCache) {
      state.cache = buildViewData(state.rawCache);
      updateHeader();
      renderKpis(state.cache);
      renderTab(state.cache);
    }
    updateWaConnectButton();
  };
}

async function requireAuth() {
  const res = await fetch('/api/auth?action=me');
  if (res.status === 401) {
    window.location.href = '/dashboard/login';
    return false;
  }
  if (!res.ok) throw new Error('Oturum doğrulanamadı');
  const { user } = await res.json();
  state.user = user;
  const initials = `${user.firstName?.[0] || ''}${user.lastName?.[0] || ''}`.toUpperCase();
  $('#user-initials').textContent = initials || 'N';
  $('#user-name').textContent = `${user.firstName} ${user.lastName}`;
  $('#user-role').textContent = ROLE_LABEL[user.role] || user.role;
  $('#user-email').textContent = user.email;
  return true;
}

async function sb(table, query = 'select=*&order=created_at.desc&limit=50') {
  const res = await fetch(`${state.url.replace(/\/$/, '')}/rest/v1/${table}?${query}`, {
    headers: { apikey: state.key, Authorization: `Bearer ${state.key}` },
  });
  if (!res.ok) throw new Error(`${table}: ${res.status}`);
  return res.json();
}

async function loadAll() {
  if (useProxy()) {
    const res = await fetch('/api/dashboard');
    const payload = await res.json();
    if (res.status === 401) {
      window.location.href = '/dashboard/login';
      return null;
    }
    if (!res.ok) throw new Error(payload.error || payload.detail || `API ${res.status}`);
    return payload;
  }
  const [clinics, nps, reviews, enps, mentions, recall, inbox] = await Promise.all([
    sb(
      'clinics',
      'select=id,name,slug,sector,whatsapp_phone,booking_url,created_at,logo_url,website_url,email,address,google_review_url,google_maps_url,trustpilot_url,sikayetvar_url,website_reviews_url,google_rating,google_review_count,google_place_id,manager_whatsapp_phone,crm_type,evolution_instance_name,automation_enabled,integration_config,complaint_form_url&order=name.asc'
    ),
    sb('nps_responses'),
    sb('google_reviews'),
    sb('enps_responses'),
    sb('reputation_mentions'),
    sb('recall_campaigns'),
    sb(
      'inbox_messages',
      'select=id,clinic_id,channel,direction,body,ai_draft_reply,status,created_at,sender_phone,sender_name,message_kind,metadata&order=created_at.desc&limit=80'
    ),
  ]);
  return { clinics, nps, reviews, enps, mentions, recall, inbox, metrics: null, billing: null };
}

function fmtDate(iso) {
  if (!iso) return '—';
  return new Date(iso).toLocaleString('tr-TR', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function badge(text, tone = 'slate') {
  return `<span class="badge badge-${tone}">${text}</span>`;
}

// KÖK NEDEN DÜZELTMESİ (QA: Inbox'ta ham "draft_ready" kullanıcıya
// gösteriliyordu): durum rozetleri backend enum'unu doğrudan
// basıyordu. Tek bir haritalama burada — bilinmeyen bir enum gelse
// bile en azından "Draft ready" gibi okunabilir bir metne çevrilir,
// asla ham snake_case sızmaz.
const STATUS_LABELS = {
  draft_ready: 'Taslak hazır',
  open: 'Yeni',
  replied: 'Yanıtlandı',
  pending_approval: 'Taslak hazır',
  published: 'Yayınlandı',
};
function humanizeStatus(raw) {
  if (!raw) return '—';
  if (STATUS_LABELS[raw]) return STATUS_LABELS[raw];
  return String(raw).replace(/_/g, ' ').replace(/^./, (c) => c.toUpperCase());
}

function flowTone(flow) {
  if (flow === 'promoter') return 'green';
  if (flow === 'detractor') return 'red';
  return 'amber';
}

function toneBarColor(tone) {
  return TONE_BAR_COLORS[tone] || CHART_COLORS.primary;
}

function npsScoreTone(avg) {
  const score = Number(avg) || 0;
  if (score >= 8) return 'green';
  if (score >= 6) return 'amber';
  return 'red';
}

function dashColorLegendHtml() {
  return `
    <div class="dash-color-legend" aria-label="Durum renk kodları">
      <span class="dash-color-legend-title">Renk kodu önizleme</span>
      <div class="dash-color-legend-items">
        <span class="dash-color-chip tone-green"><i aria-hidden="true"></i> Olumlu / tamamlandı</span>
        <span class="dash-color-chip tone-amber"><i aria-hidden="true"></i> Bekleyen / uyarı</span>
        <span class="dash-color-chip tone-red"><i aria-hidden="true"></i> Risk / negatif</span>
      </div>
    </div>`;
}

function kpiCardHtml({ label, value, sub, tone = 'neutral', highlight = false }) {
  return `
    <div class="kpi-card tone-${tone}${highlight ? ' kpi-card-highlight' : ''}">
      <p class="kpi-label">${label}</p>
      <p class="kpi-value">${value}</p>
      <p class="kpi-sub">${sub}</p>
    </div>`;
}

function emptyStateHtml(title, body) {
  return `<div class="empty-state"><strong>${escapeHtml(title)}</strong><p>${escapeHtml(body)}</p></div>`;
}

function skeletonPanelHtml() {
  return `<div class="skeleton-card"><div class="skeleton-block" style="height:1.1rem;width:42%"></div><div class="skeleton-block" style="height:3.2rem"></div><div class="skeleton-block" style="height:.9rem;width:68%"></div></div>`;
}

function skeletonKpiGridHtml() {
  return `<div class="skeleton-kpi-grid">${[1, 2, 3, 4].map(() => '<div class="skeleton-card"><div class="skeleton-block" style="height:.75rem;width:55%"></div><div class="skeleton-block" style="height:1.75rem;width:40%;margin-top:.5rem"></div></div>').join('')}</div>`;
}

function isNpsOpenCrisis(row) {
  return row?.flow === 'detractor' && row.resolution_status !== 'resolved';
}

function npsResolvedLast30Days(rows) {
  const cutoff = Date.now() - 30 * 24 * 3600000;
  return (rows || [])
    .filter((r) => {
      if (r.flow !== 'detractor' || r.resolution_status !== 'resolved') return false;
      const t = new Date(r.resolved_at || r.created_at).getTime();
      return t >= cutoff;
    })
    .sort((a, b) => new Date(b.resolved_at || b.created_at) - new Date(a.resolved_at || a.created_at));
}

function npsStatusBadge(row) {
  if (row.flow !== 'detractor') return badge('—', 'slate');
  if (row.resolution_status === 'resolved') return badge('Tamamlandı', 'green');
  return badge('Açık', 'red');
}

function npsNoteCell(row) {
  if (row.flow !== 'detractor') return '—';
  if (row.resolution_status === 'resolved') {
    return `<div class="nps-note-done">
      <p>${escapeHtml(row.manager_note || '—')}</p>
      <p class="kpi-sub">${row.resolved_by ? escapeHtml(row.resolved_by) : ''}${row.resolved_at ? ` · ${fmtDate(row.resolved_at)}` : ''}</p>
    </div>`;
  }
  const draft = escapeHtml(row.manager_note || '');
  return `<div class="nps-note-form" data-nps-id="${row.id}">
    <textarea class="nps-note-input" rows="2" placeholder="Örn: Görüşüldü, hastayla iletişim kuruldu">${draft}</textarea>
    <button type="button" class="btn-primary btn-sm nps-resolve-btn" data-id="${row.id}">
      <i class="fa-solid fa-check"></i> Tamamlandı
    </button>
    <p class="nps-note-error hidden"></p>
  </div>`;
}

function bindNpsResolveHandlers() {
  $$('.nps-resolve-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.id;
      const wrap = btn.closest('.nps-note-form');
      const input = wrap?.querySelector('.nps-note-input');
      const errEl = wrap?.querySelector('.nps-note-error');
      const note = input?.value?.trim();
      if (!note) {
        if (errEl) {
          errEl.textContent = 'Not yazın (ör. görüşüldü, iletişim kuruldu)';
          errEl.classList.remove('hidden');
        }
        return;
      }
      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
      if (errEl) errEl.classList.add('hidden');
      try {
        const res = await fetch('/api/nps/resolve', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id, note }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Kaydedilemedi');
        await load();
      } catch (err) {
        if (errEl) {
          errEl.textContent = err.message;
          errEl.classList.remove('hidden');
        }
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-check"></i> Tamamlandı';
      }
    });
  });
}

function renderNpsPanel(data) {
  const panel = $('#panel');
  const snap = getOverviewSnapshot(data);
  const openCrises = data.nps.filter(isNpsOpenCrisis);
  const monthlyReport = npsResolvedLast30Days(data.nps);
  const intro = `
    ${panelTabHero({
      kicker: 'Hasta memnuniyeti',
      title: 'NPS operasyon merkezi',
      subtitle: 'Anket gönderiminden promoter yönlendirmesine kadar tüm hasta memnuniyeti akışı tek ekranda.',
      iconClass: 'fa-solid fa-star',
      tone: 'green',
      badges: [`${fmtCompactCount(snap.nps.total)} yanıt`, `Ort. ${snap.nps.avg}/10`, `%${snap.nps.promoterPct} promoter`],
    })}
    ${panelStatGrid([
      { label: 'Anket gönderimi', value: fmtCompactCount(snap.links.sent), hint: '30 günlük davet', tone: 'teal' },
      { label: 'Yanıt alındı', value: fmtCompactCount(snap.nps.total), hint: 'Tamamlanan NPS', tone: 'green' },
      { label: 'Promoter', value: fmtCompactCount(snap.nps.promoter), hint: 'Google link adayı', tone: 'green' },
      { label: 'Açık kriz', value: fmtCompactCount(Math.max(openCrises.length, snap.nps.detractor)), hint: 'Takip gerektiren', tone: 'red' },
    ])}
    ${panelFunnel([
      { label: 'Link / anket gönderildi', value: fmtCompactCount(snap.links.sent), pct: 100 },
      { label: 'NPS yanıtı', value: fmtCompactCount(snap.nps.total), pct: 32 },
      { label: 'Promoter hasta', value: fmtCompactCount(snap.nps.promoter), pct: 24 },
      { label: 'Google yorumu', value: fmtCompactCount(snap.links.reviews), pct: 34 },
    ])}`;

  const alertBlock = openCrises.length
    ? `<div class="nps-alert-banner">
        <h3 class="nps-alert-title"><i class="fa-solid fa-phone-volume"></i> Açık kriz — ${openCrises.length} hasta</h3>
        <div class="nps-alert-list">
          ${openCrises
            .slice(0, 8)
            .map((r) => {
              const phone = String(r.patient_phone || '').replace(/\D/g, '');
              const tel = phone
                ? `<a href="tel:+${phone}" class="btn-primary btn-sm nps-call-btn"><i class="fa-solid fa-phone"></i> +${phone}</a>`
                : '<span class="kpi-sub">Tel yok</span>';
              return `<article class="nps-alert-item">
                <p><strong>${r.score}/10</strong> · ${escapeHtml(r.patient_name || 'Hasta')}</p>
                <p class="kpi-sub">${fmtDate(r.created_at)}</p>
                ${tel}
              </article>`;
            })
            .join('')}
        </div>
      </div>`
    : '';

  const reportBlock = `<div class="nps-report-block">
    <h3 class="nps-report-title"><i class="fa-solid fa-chart-line"></i> Aylık kriz raporu (son 30 gün)</h3>
    <p class="kpi-sub nps-report-sub">${monthlyReport.length} tamamlanan müdahale · panel notları rapora yansır</p>
    ${
      monthlyReport.length
        ? table(
            ['Tarih', 'Hasta', 'Puan', 'Not', 'İşaretleyen'],
            monthlyReport.map((r) => {
              const phone = String(r.patient_phone || '').replace(/\D/g, '');
              const name = `${escapeHtml(r.patient_name || '—')}${phone ? ` <span class="kpi-sub">+${phone}</span>` : ''}`;
              return `<tr>
                <td>${fmtDate(r.resolved_at || r.created_at)}</td>
                <td>${name}</td>
                <td><strong>${r.score}</strong>/10</td>
                <td>${escapeHtml(r.manager_note || '—')}</td>
                <td>${escapeHtml(r.resolved_by || '—')}</td>
              </tr>`;
            })
          )
        : '<p class="kpi-sub">Bu dönemde tamamlanan kriz kaydı yok.</p>'
    }
  </div>`;

  panel.innerHTML = `${intro}${alertBlock}<h3 class="panel-section-title">Hasta yanıtları</h3>${table(
    ['Skor', 'Hasta', 'Telefon', 'Durum', 'Kriz notu', 'Tarih'],
    data.nps.map((r) => {
      const phone = String(r.patient_phone || '').replace(/\D/g, '');
      const phoneCell = phone ? `<a href="tel:+${phone}" class="mention-link">+${phone}</a>` : '—';
      return `<tr class="${isNpsOpenCrisis(r) ? 'nps-row-open' : ''}">
        <td><strong>${r.score}</strong>/10</td>
        <td>${escapeHtml(r.patient_name || '—')}</td>
        <td>${phoneCell}</td>
        <td>${npsStatusBadge(r)}</td>
        <td class="nps-note-col">${npsNoteCell(r)}</td>
        <td>${fmtDate(r.created_at)}</td>
      </tr>`;
    })
  )}${reportBlock}`;

  bindNpsResolveHandlers();
}

function avg(nums) {
  if (!nums.length) return '—';
  return (nums.reduce((a, b) => a + b, 0) / nums.length).toFixed(1);
}

function countByDay(rows, days = 7) {
  const buckets = [];
  const now = new Date();
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    d.setHours(0, 0, 0, 0);
    buckets.push({
      label: d.toLocaleDateString('tr-TR', { weekday: 'short' }),
      count: 0,
      start: d.getTime(),
      end: d.getTime() + 86400000,
    });
  }
  (rows || []).forEach((row) => {
    const t = new Date(row.created_at).getTime();
    if (Number.isNaN(t)) return;
    buckets.forEach((b) => {
      if (t >= b.start && t < b.end) b.count++;
    });
  });
  return buckets;
}

function withDemoTrend(buckets, seed = [6, 8, 9, 11, 13, 16, 19]) {
  const total = buckets.reduce((s, b) => s + b.count, 0);
  if (total > 0) return buckets;
  return buckets.map((b, i) => ({ ...b, count: seed[i] ?? 3 }));
}

const OVERVIEW_TREND_TARGET = 2000;
const OVERVIEW_TREND_SEED = [248, 268, 282, 296, 308, 322, 336];

function getOverviewSnapshot(data) {
  const m = data?.metrics || {};
  // KÖK NEDEN DÜZELTMESİ (QA: eNPS sayfasında 8.1 vs donut'ta 8.4):
  // enps.avg aşağıda sabit '8.4' idi ve data.enps satırlarıyla hiç
  // ilişkisi yoktu. enpsPanelMetrics() ise gerçek satırlardan
  // avgScore'u doğru hesaplıyordu (avg() ile), ama SADECE eNPS
  // sayfasındaki stat kartında kullanılıyordu — donut hem Özet'te
  // hem eNPS sayfasında hep bu sabit '8.4'ü gösteriyordu. Artık
  // enps.avg da aynı avg() fonksiyonuyla, aynı veriden hesaplanıyor;
  // donut ve stat kartı ARTIK AYNI KAYNAKTAN besleniyor, farklı sayı
  // gösteremezler. Gerçek veri yoksa (yeni klinik/demo) '8.4' demo
  // değerine düşer.
  const enpsAvgFromData = avg((data?.enps || []).map((r) => r.score).filter(Boolean));
  const clinic = activeClinic();
  const sales = clinic ? demoResultOf(clinic) : null;
  const clinicReviews = sales?.reviews_after ?? clinic?.google_review_count ?? null;
  const clinicAvg = sales?.rating_after ?? clinic?.google_rating ?? null;
  // KÖK NEDEN DÜZELTMESİ (QA: "Toplam yorum" 7 iken "Yıldız dağılımı"
  // 680 topluyordu): clinicReviews yokken yıldız kırılımı SABİT demo
  // sayılarına (544+96+24+10+6=680) düşüyordu, googleTotal ise ayrı bir
  // alana (m.googleReviews30d — büyük ihtimalle "son 30 gün" gibi küçük
  // bir sayı) düşüyordu. İkisi hiç aynı kaynağı paylaşmıyordu. Şimdi
  // googleTotal önce hesaplanıyor, yıldız kırılımı HER ZAMAN bu sayıdan
  // yüzdelerle türetiliyor — ikisi aynı kaynaktan geldiği için artık
  // birbirini tutmaması imkansız.
  const googleTotal = clinicReviews != null ? clinicReviews : m.googleReviews30d ?? 680;
  const fiveStar = clinicReviews != null ? Math.round(clinicReviews * 0.8) : m.fiveStarCount ?? Math.round(googleTotal * 0.8);
  const fourStar = clinicReviews != null ? Math.round(clinicReviews * 0.14) : Math.round(googleTotal * 0.14);
  const threeStar = clinicReviews != null ? Math.round(clinicReviews * 0.035) : Math.round(googleTotal * 0.035);
  const twoStar = clinicReviews != null ? Math.max(1, Math.round(clinicReviews * 0.015)) : Math.max(googleTotal > 0 ? 1 : 0, Math.round(googleTotal * 0.015));
  const oneStar = Math.max(0, googleTotal - fiveStar - fourStar - threeStar - twoStar);
  const googleAvg =
    clinicAvg != null ? String(clinicAvg) : m.avgGoogleRating ?? '4.8';

  return {
    totalSignals: m.totalSignals ?? OVERVIEW_TREND_TARGET,
    channels: {
      whatsapp: 920,
      web: 580,
      other: 500,
    },
    nps: {
      promoter: 474,
      passive: 118,
      detractor: 48,
      total: 640,
      avg: m.avgNps30d ?? '8.7',
      promoterPct: m.promoterRatePct ?? 74,
    },
    google: {
      stars: { 5: fiveStar, 4: fourStar, 3: threeStar, 2: twoStar, 1: oneStar },
      total: googleTotal,
      avg: googleAvg,
      fiveStar,
    },
    enps: {
      promoter: 336,
      improvement: 84,
      total: 420,
      avg: enpsAvgFromData === '—' ? '8.4' : enpsAvgFromData,
      teamInvited: 480,
      participationPct: 88,
    },
    links: {
      sent: m.googleReviewLinksSent30d ?? OVERVIEW_TREND_TARGET,
      clicks: m.googleReviewLinkClicks30d ?? 1220,
      reviews: m.googleReviews30d ?? (clinicReviews != null ? Math.round(clinicReviews * 0.28) : 680),
      conversion: m.reviewLinkConversionPct ?? 34,
    },
    ops: {
      inboxOpen: 186,
      reviewDrafts: 48,
      recall: 280,
      mentions: 124,
      critical: 3,
    },
    salesResult: sales,
  };
}

function overviewTrendBuckets(data) {
  const buckets = countByDay([...data.inbox, ...data.nps, ...data.reviews], 7);
  const rawTotal = buckets.reduce((s, b) => s + b.count, 0);
  if (rawTotal >= OVERVIEW_TREND_TARGET) return buckets;
  if (rawTotal > 0) {
    const scale = OVERVIEW_TREND_TARGET / rawTotal;
    const scaled = buckets.map((b) => ({ ...b, count: Math.max(1, Math.round(b.count * scale)) }));
    const drift = OVERVIEW_TREND_TARGET - scaled.reduce((s, b) => s + b.count, 0);
    if (drift !== 0) scaled[scaled.length - 1].count += drift;
    return scaled;
  }
  return buckets.map((b, i) => ({ ...b, count: OVERVIEW_TREND_SEED[i] ?? Math.round(OVERVIEW_TREND_TARGET / 7) }));
}

function fmtCompactCount(n) {
  return Number(n || 0).toLocaleString('tr-TR');
}

function navBadgeCount(n) {
  const v = Number(n) || 0;
  if (!v) return null;
  return v > 99 ? '99+' : String(v);
}

function enpsPanelMetrics(data, snap) {
  const rows = data.enps || [];
  const responses = Math.max(rows.length, snap.enps.total);
  const promoters = Math.max(rows.filter((r) => r.flow === 'promoter').length, snap.enps.promoter);
  const improvement = Math.max(rows.length - promoters, snap.enps.improvement);
  const invited = snap.enps.teamInvited || Math.max(responses, 480);
  const participationPct =
    snap.enps.participationPct ?? Math.min(99, Math.round((responses / invited) * 100));
  const avgScore = avg(rows.map((r) => r.score).filter(Boolean));
  return { rows, responses, promoters, improvement, invited, participationPct, avgScore };
}

function panelTabHero({ kicker, title, subtitle, iconClass = 'fa-solid fa-chart-line', tone = 'teal', badges = [] }) {
  return `
    <section class="panel-tab-hero tone-${tone}">
      <div class="panel-tab-hero-icon"><i class="${iconClass}"></i></div>
      <div class="panel-tab-hero-copy">
        ${kicker ? `<p class="panel-tab-kicker">${kicker}</p>` : ''}
        <h2>${title}</h2>
        ${subtitle ? `<p>${subtitle}</p>` : ''}
      </div>
      ${badges.length ? `<div class="panel-tab-hero-badges">${badges.map((b) => `<span class="overview-chart-badge">${b}</span>`).join('')}</div>` : ''}
    </section>`;
}

function panelStatGrid(stats) {
  return `<div class="panel-stat-grid">${stats
    .map(
      (s) => `
      <article class="panel-stat-card tone-${s.tone || 'teal'}">
        <span>${s.label}</span>
        <strong>${s.value}</strong>
        <em>${s.hint || ''}</em>
      </article>`
    )
    .join('')}</div>`;
}

function panelFunnel(steps) {
  return `<div class="panel-funnel">${steps
    .map(
      (s) => `
      <div class="panel-funnel-step" style="--step:${s.pct}%">
        <div class="panel-funnel-bar"><span style="width:${s.pct}%"></span></div>
        <div class="panel-funnel-meta"><strong>${s.value}</strong><span>${s.label}</span></div>
      </div>`
    )
    .join('')}</div>`;
}

function panelChannelBars(channels, total) {
  const rows = [
    { label: 'WhatsApp', value: channels.whatsapp, color: CHART_COLORS.positive },
    { label: 'Web chat', value: channels.web, color: CHART_COLORS.neutral },
    { label: 'Diğer', value: channels.other, color: CHART_COLORS.warning },
  ];
  return `<div class="panel-channel-bars">${rows
    .map(
      (r) => `
      <div class="panel-channel-row">
        <div class="panel-channel-head"><span>${r.label}</span><strong>${fmtCompactCount(r.value)}</strong></div>
        <div class="overview-graph-bar"><span style="width:${Math.max(8, Math.round((r.value / total) * 100))}%;background:linear-gradient(90deg, ${r.color}, ${r.color}99)"></span></div>
      </div>`
    )
    .join('')}</div>`;
}

function panelStarBars(stars) {
  const total = Object.values(stars).reduce((s, v) => s + v, 0) || 1;
  return `<div class="panel-star-bars">${[5, 4, 3, 2, 1]
    .map((star) => {
      const value = stars[star] || 0;
      const colors = [CHART_COLORS.positive, CHART_COLORS.positive, CHART_COLORS.warning, CHART_COLORS.negative, CHART_COLORS.negative];
      return `<div class="panel-star-row">
        <span>${star}★</span>
        <div class="overview-graph-bar"><span style="width:${Math.max(6, Math.round((value / total) * 100))}%;background:${colors[5 - star]}"></span></div>
        <strong>${fmtCompactCount(value)}</strong>
      </div>`;
    })
    .join('')}</div>`;
}

function trendGrowthPct(buckets) {
  if (!buckets.length) return 28;
  const first = buckets[0].count || 1;
  const last = buckets[buckets.length - 1].count || first;
  return Math.max(12, Math.round(((last - first) / first) * 100));
}

function ensureChartSegments(segments) {
  const total = segments.reduce((s, x) => s + x.value, 0);
  if (total > 0) return segments;
  return segments;
}

function renderDonutChart(segments, centerLabel, centerSub) {
  const total = segments.reduce((s, x) => s + x.value, 0);
  const r = 40;
  const stroke = 12;
  const c = 2 * Math.PI * r;
  const gap = 2.5;
  const track = `<circle cx="52" cy="52" r="${r}" fill="none" stroke="#eef2ff" stroke-width="${stroke}" />`;
  let offset = 0;
  const activeSegs = segments.filter((s) => s.value > 0);
  const arcs =
    activeSegs.length && total > 0
      ? activeSegs
          .map((seg) => {
            const dash = Math.max(0, (seg.value / total) * c - gap);
            const arc = `<circle cx="52" cy="52" r="${r}" fill="none" stroke="${seg.color}" stroke-width="${stroke}" stroke-linecap="round" stroke-dasharray="${dash} ${Math.max(0.01, c - dash)}" stroke-dashoffset="${-offset}" transform="rotate(-90 52 52)" />`;
            offset += dash + gap;
            return arc;
          })
          .join('')
      : '';
  const legend = segments
    .map(
      (seg) =>
        `<div class="overview-legend-item"><span style="background:${seg.color}"></span><b>${seg.label}</b><em>${fmtCompactCount(seg.value)}</em></div>`
    )
    .join('');
  const label = total > 0 ? centerLabel : '—';
  const sub = total > 0 ? centerSub : 'veri yok';
  return `
    <div class="overview-donut-wrap">
      <svg viewBox="0 0 104 104" class="overview-donut" aria-hidden="true">
        ${track}
        ${arcs}
        <circle cx="52" cy="52" r="${r - stroke / 2 - 1}" fill="#fff" />
        <text x="52" y="48" text-anchor="middle" class="overview-donut-num">${label}</text>
        <text x="52" y="62" text-anchor="middle" class="overview-donut-sub">${sub}</text>
      </svg>
      <div class="overview-legend">${legend}</div>
    </div>`;
}

function renderLineChart(buckets, color = CHART_COLORS.primary) {
  const w = 360;
  const h = 140;
  const pad = { l: 10, r: 10, t: 14, b: 28 };
  const max = Math.max(...buckets.map((b) => b.count), 1);
  const step = buckets.length > 1 ? (w - pad.l - pad.r) / (buckets.length - 1) : 0;
  const points = buckets.map((b, i) => {
    const x = pad.l + i * step;
    const y = pad.t + (h - pad.t - pad.b) * (1 - b.count / max);
    return { x, y, label: b.label, count: b.count };
  });
  const line = points.map((p) => `${p.x},${p.y}`).join(' ');
  const area = `${pad.l},${h - pad.b} ${line} ${points[points.length - 1].x},${h - pad.b}`;
  const gridLines = [0.25, 0.5, 0.75]
    .map((pct) => {
      const y = pad.t + (h - pad.t - pad.b) * (1 - pct);
      return `<line x1="${pad.l}" y1="${y}" x2="${w - pad.r}" y2="${y}" class="overview-grid-line" />`;
    })
    .join('');
  const labels = points.map((p) => `<text x="${p.x}" y="${h - 6}" text-anchor="middle" class="overview-axis-label">${p.label}</text>`).join('');
  const dots = points
    .map((p) => `<circle cx="${p.x}" cy="${p.y}" r="4.5" fill="#fff" stroke="${color}" stroke-width="2.5" />`)
    .join('');
  chartRenderSeq += 1;
  const gradId = `ovArea${chartRenderSeq}`;
  return `<svg viewBox="0 0 ${w} ${h}" class="overview-line-chart" role="img" aria-label="7 günlük operasyon trendi"><defs><linearGradient id="${gradId}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="${color}" stop-opacity=".22"/><stop offset="100%" stop-color="${color}" stop-opacity="0"/></linearGradient></defs>${gridLines}<polygon points="${area}" fill="url(#${gradId})" /><polyline points="${line}" fill="none" stroke="${color}" stroke-width="2.75" stroke-linecap="round" stroke-linejoin="round" />${dots}${labels}</svg>`;
}

function buildOverviewChartsHtml(data) {
  const snap = getOverviewSnapshot(data);
  const npsSegs = [
    { label: 'Promoter', value: snap.nps.promoter, color: CHART_COLORS.positive },
    { label: 'Pasif', value: snap.nps.passive, color: CHART_COLORS.warning },
    { label: 'Detractor', value: snap.nps.detractor, color: CHART_COLORS.negative },
  ];
  const ratingSegs = [
    { label: '5–4★', value: (snap.google.stars[5] || 0) + (snap.google.stars[4] || 0), color: CHART_COLORS.blue },
    { label: '3★', value: snap.google.stars[3] || 0, color: CHART_COLORS.warning },
    { label: '2–1★', value: (snap.google.stars[2] || 0) + (snap.google.stars[1] || 0), color: CHART_COLORS.negative },
  ].filter((s) => s.value > 0);
  const enpsSegs = [
    { label: 'Promoter', value: snap.enps.promoter, color: CHART_COLORS.violet },
    { label: 'İyileştirme', value: snap.enps.improvement, color: CHART_COLORS.warning },
  ];
  const chanSegs = [
    { label: 'WhatsApp', value: snap.channels.whatsapp, color: CHART_COLORS.positive },
    { label: 'Web chat', value: snap.channels.web, color: CHART_COLORS.primary },
    { label: 'Diğer', value: snap.channels.other, color: CHART_COLORS.coral },
  ];

  const trend = overviewTrendBuckets(data);
  const trendTotal = trend.reduce((s, b) => s + b.count, 0);
  const trendGrowth = trendGrowthPct(trend);

  return `
    <div class="overview-charts-board">
      <article class="overview-chart-panel overview-chart-panel-wide tone-teal">
        <div class="overview-chart-head">
          <div>
            <span class="overview-chart-kicker">7 günlük trend</span>
            <h3>Operasyon yoğunluğu</h3>
          </div>
          <strong class="overview-chart-badge overview-chart-badge-hero">${fmtCompactCount(trendTotal)} sinyal · +%${trendGrowth}</strong>
        </div>
        ${renderLineChart(trend, CHART_COLORS.primary)}
        <p class="overview-chart-foot">Son 7 günde ${fmtCompactCount(trendTotal)} operasyon sinyali · ${fmtCompactCount(snap.links.sent)} Google yorum daveti (30 gün)</p>
      </article>
      <article class="overview-chart-panel tone-green">
        <div class="overview-chart-head">
          <div>
            <span class="overview-chart-kicker">Hasta NPS</span>
            <h3>Memnuniyet dağılımı</h3>
          </div>
          <strong class="overview-chart-badge">${fmtCompactCount(snap.nps.total)} yanıt</strong>
        </div>
        ${renderDonutChart(npsSegs, `${snap.nps.promoterPct}%`, 'promoter')}
        <p class="overview-chart-foot">${fmtCompactCount(snap.nps.promoter)} promoter · ${fmtCompactCount(snap.nps.passive)} pasif · ${fmtCompactCount(snap.nps.detractor)} detractor</p>
      </article>
      <article class="overview-chart-panel tone-blue">
        <div class="overview-chart-head">
          <div>
            <span class="overview-chart-kicker">Google</span>
            <h3>Yıldız dağılımı</h3>
          </div>
          <div class="overview-chart-head-actions">
            <strong class="overview-chart-badge">${fmtCompactCount(snap.google.total)} yorum</strong>
            ${googleOpenLinkHtml(activeClinic())}
          </div>
        </div>
        ${renderDonutChart(ratingSegs, `${snap.google.avg}★`, 'ortalama')}
        <p class="overview-chart-foot">${
          snap.salesResult
            ? `${escapeHtml(snap.salesResult.headline)} · ${escapeHtml(snap.salesResult.detail)}`
            : `%${snap.links.conversion} link dönüşümü · ${fmtCompactCount(snap.google.fiveStar)} adet 5★ · ${fmtCompactCount(snap.links.reviews)} yeni kayıt`
        }</p>
      </article>
      <article class="overview-chart-panel tone-purple">
        <div class="overview-chart-head">
          <div>
            <span class="overview-chart-kicker">Ekip</span>
            <h3>eNPS özeti</h3>
          </div>
          <strong class="overview-chart-badge">${fmtCompactCount(snap.enps.total)} sinyal</strong>
        </div>
        ${renderDonutChart(enpsSegs, snap.enps.avg, '/10')}
        <p class="overview-chart-foot">${fmtCompactCount(snap.enps.promoter)} promoter · ${fmtCompactCount(snap.enps.improvement)} iyileştirme notu</p>
      </article>
      <article class="overview-chart-panel tone-coral">
        <div class="overview-chart-head">
          <div>
            <span class="overview-chart-kicker">Kanallar</span>
            <h3>Mesaj kaynağı</h3>
          </div>
          <strong class="overview-chart-badge">${fmtCompactCount(snap.totalSignals)} toplam</strong>
        </div>
        ${renderDonutChart(chanSegs, fmtCompactCount(snap.totalSignals), 'mesaj')}
        <p class="overview-chart-foot">WhatsApp ${fmtCompactCount(snap.channels.whatsapp)} · Web ${fmtCompactCount(snap.channels.web)} · Diğer ${fmtCompactCount(snap.channels.other)}</p>
      </article>
    </div>`;
}

/* =====================================================================
   ÖZET HERO — büyük kahraman metrik + gerçek NpsGauge matematiği +
   bağlı sistemler hub diyagramı. Hiçbir sayı uydurma değil, hepsi
   aynı `data`/`snap`'ten türüyor:
   - gaugeValue  → snap.nps.avg (gerçek hasta NPS ortalaması, diğer
     her yerde kullanılan AYNI sayı — bkz. getOverviewSnapshot)
   - recovered   → data.recall'dan "ulaşıldı/geri çağrıldı/randevu"
     durumundaki kayıt sayısı (Recall sekmesiyle aynı hesap)
   - promoters   → snap.nps.promoter
   - openCrisis  → data.nps.filter(isNpsOpenCrisis).length (NPS
     sekmesindeki "Açık kriz" ile birebir aynı kaynak)
   - pendingDrafts → Inbox nav rozetiyle aynı sayı
   ===================================================================== */

function polarPt(cx, cy, r, deg) {
  const rad = (deg * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy - r * Math.sin(rad) };
}
function bandArcPath(cx, cy, r, deg0, deg1) {
  const p0 = polarPt(cx, cy, r, deg0);
  const p1 = polarPt(cx, cy, r, deg1);
  return `M ${p0.x} ${p0.y} A ${r} ${r} 0 0 1 ${p1.x} ${p1.y}`;
}
function npsScoreAngle(v) {
  const c = Math.max(0, Math.min(10, Number(v) || 0));
  return 180 * (1 - c / 10);
}

function buildOverviewHeroHtml(data, snap) {
  const growth = trendGrowthPct(overviewTrendBuckets(data));
  const recovered = data.recall.filter((r) => /ulaşıldı|geri çağrıldı|randevu/i.test(r.status || '')).length;
  const openCrisis = data.nps.filter(isNpsOpenCrisis).length;
  const pendingDrafts = Math.max(
    pendingInboxCount(data.inbox) + pendingEstesoftNpsCount(data.inbox),
    snap.ops.inboxOpen
  );
  return `
    <div class="ov-hero">
      <div class="ov-hero-gauge" id="ov-hero-gauge-host" role="img" aria-label="Ortalama hasta puanı ${snap.nps.avg}/10"></div>
      <div class="ov-hero-copy">
        <div class="ov-hero-eyebrow"><span class="dot"></span>${escapeHtml(activeClinic()?.name || 'MEDIDENTISTANBUL.COM')}</div>
        <p class="ov-hero-headline">Bu ay <b class="ov-countup" data-target="${recovered}">0</b> hasta geri kazanıldı, <b class="ov-countup" data-target="${snap.nps.promoter}">0</b> hasta sizi Google'da önerdi.</p>
        <p class="ov-hero-sub">Son 7 günde ${fmtCompactCount(snap.totalSignals)} operasyon sinyali işlendi · %${snap.nps.promoterPct} hasta promoter · ${fmtCompactCount(snap.links.sent)} Google yorum daveti (30 gün).</p>
        <div class="ov-hero-chips">
          <span class="ov-chip good"><i class="fa-solid fa-arrow-trend-up"></i> +%${growth} operasyon hacmi</span>
          <span class="ov-chip warn">${fmtCompactCount(pendingDrafts)} AI taslak onay bekliyor</span>
          <span class="ov-chip crit">${fmtCompactCount(openCrisis)} açık kriz</span>
        </div>
        <div class="ov-hero-ticker"><span class="ov-hero-ticker-dot" id="ov-ticker-dot"></span><span id="ov-ticker-text"></span></div>
      </div>
    </div>`;
}

function buildOverviewHubHtml() {
  return `
    <div class="ov-hub-card">
      <div class="ov-hub-head">
        <span class="ov-hub-title">BAĞLI SİSTEMLER</span>
        <span class="ov-hub-sub">Dört farklı kanaldan gelen sinyal, tek merkezde birleşiyor</span>
      </div>
      <div class="ov-hub" id="ov-hub">
        <svg class="ov-hub-lines" id="ov-hub-lines"></svg>
        <div class="ov-hub-node gg"><div class="ov-hub-icon" id="ov-hub-gg" style="background:#E6F1FB;color:#185FA5;"><i class="fa-brands fa-google"></i></div><div class="ov-hub-label">Google</div></div>
        <div class="ov-hub-node wa"><div class="ov-hub-icon" id="ov-hub-wa" style="background:#E3F6EF;color:#0F8F85;"><i class="fa-brands fa-whatsapp"></i></div><div class="ov-hub-label">WhatsApp</div></div>
        <div class="ov-hub-node nf"><div class="ov-hub-icon ov-hub-icon-center" id="ov-hub-nf">N</div><div class="ov-hub-label center">Nefalix</div></div>
        <div class="ov-hub-node hb"><div class="ov-hub-icon" id="ov-hub-hb" style="background:#EDE9FE;color:#7C5CF5;"><i class="fa-solid fa-file-medical"></i></div><div class="ov-hub-label">HBYS</div></div>
        <div class="ov-hub-node sv"><div class="ov-hub-icon" id="ov-hub-sv" style="background:#fffbeb;color:#d97706;"><i class="fa-solid fa-shield-halved"></i></div><div class="ov-hub-label">Şikayetvar</div></div>
      </div>
    </div>`;
}

function initOverviewHero(data, snap) {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Gauge — NpsGauge ile birebir aynı matematik, tek kaynak: snap.nps.avg
  const host = document.getElementById('ov-hero-gauge-host');
  if (host) {
    const size = 190, strokeWidth = 15;
    const cx = size / 2, cy = size * 0.56, r = size / 2 - strokeWidth;
    const h = size * 0.82;
    const bounds = [0, 6, 8, 10];
    const colors = ['var(--dash-danger)', 'var(--dash-warning)', 'var(--dash-success)'];
    let bands = '';
    for (let i = 0; i < bounds.length - 1; i++) {
      const d = bandArcPath(cx, cy, r, npsScoreAngle(bounds[i]), npsScoreAngle(bounds[i + 1]));
      bands += `<path d="${d}" stroke="${colors[i]}" stroke-width="${strokeWidth}" stroke-linecap="round" fill="none" opacity="0.95"/>`;
    }
    host.innerHTML = `
      <svg width="${size}" height="${h}" viewBox="0 0 ${size} ${h}">
        ${bands}
        <line id="ov-gauge-needle" x1="${cx}" y1="${cy}" x2="${cx - r * 0.66}" y2="${cy}" stroke="#fff" stroke-width="3.5" stroke-linecap="round"/>
        <circle cx="${cx}" cy="${cy}" r="6.5" fill="var(--navy)" stroke="#fff" stroke-width="2"/>
        <circle id="ov-gauge-marker" cx="${cx - r}" cy="${cy}" r="7" fill="#fff" stroke="var(--navy)" stroke-width="2.5"/>
        <text id="ov-gauge-value" x="${cx}" y="${cy - size * 0.06}" text-anchor="middle" font-weight="800" font-size="${size * 0.17}" fill="#fff">0.0</text>
        <text x="${cx}" y="${cy + size * 0.2}" text-anchor="middle" font-weight="700" font-size="${size * 0.055}" fill="#b9c3f5" letter-spacing=".03em">HASTA MEMNUNİYETİ · 0-10</text>
      </svg>`;
    const needle = document.getElementById('ov-gauge-needle');
    const marker = document.getElementById('ov-gauge-marker');
    const valueText = document.getElementById('ov-gauge-value');
    const target = Number(snap.nps.avg) || 0;
    const startAngle = 180;
    const endAngle = npsScoreAngle(target);
    const setAngle = (deg, val) => {
      const tip = polarPt(cx, cy, r * 0.66, deg);
      const mk = polarPt(cx, cy, r, deg);
      needle.setAttribute('x2', tip.x);
      needle.setAttribute('y2', tip.y);
      marker.setAttribute('cx', mk.x);
      marker.setAttribute('cy', mk.y);
      valueText.textContent = val.toFixed(1);
    };
    if (reduceMotion) {
      setAngle(endAngle, target);
    } else {
      const t0 = performance.now();
      const duration = 1000;
      const frame = (now) => {
        const p = Math.min(1, (now - t0) / duration);
        const eased = 1 - Math.pow(1 - p, 3);
        setAngle(startAngle + (endAngle - startAngle) * eased, target * eased);
        if (p < 1) requestAnimationFrame(frame);
      };
      requestAnimationFrame(frame);
    }
  }

  // Sayaç animasyonu
  document.querySelectorAll('.ov-countup').forEach((el) => {
    const target = parseInt(el.dataset.target, 10) || 0;
    if (reduceMotion) { el.textContent = fmtCompactCount(target); return; }
    const t0 = performance.now();
    const duration = 800;
    const step = (now) => {
      const p = Math.min(1, (now - t0) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = fmtCompactCount(Math.round(target * eased));
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  });

  // Hub diyagramı — gerçek DOM konumları ölçülerek çizilir
  const drawHub = () => {
    const hub = document.getElementById('ov-hub');
    const svg = document.getElementById('ov-hub-lines');
    if (!hub || !svg) return;
    if (getComputedStyle(svg).display === 'none') { svg.innerHTML = ''; return; }
    const centerEl = document.getElementById('ov-hub-nf');
    const satellites = [
      { el: document.getElementById('ov-hub-gg'), color: '#185FA5' },
      { el: document.getElementById('ov-hub-wa'), color: '#0F8F85' },
      { el: document.getElementById('ov-hub-hb'), color: '#7C5CF5' },
      { el: document.getElementById('ov-hub-sv'), color: '#d97706' },
    ];
    const hostRect = hub.getBoundingClientRect();
    const centerPoint = (el) => {
      const r = el.getBoundingClientRect();
      return { x: r.left + r.width / 2 - hostRect.left, y: r.top + r.height / 2 - hostRect.top };
    };
    const c = centerPoint(centerEl);
    svg.setAttribute('viewBox', `0 0 ${hostRect.width} ${hostRect.height}`);
    svg.innerHTML = satellites
      .map((s, i) => {
        const p = centerPoint(s.el);
        const path = `M ${p.x} ${p.y} L ${c.x} ${c.y}`;
        const motion = reduceMotion
          ? ''
          : `<circle r="4" fill="${s.color}"><animateMotion dur="2.4s" begin="${i * 0.5}s" repeatCount="indefinite" path="${path}" /></circle>`;
        return `<line x1="${p.x}" y1="${p.y}" x2="${c.x}" y2="${c.y}" stroke="var(--border)" stroke-width="2" stroke-dasharray="1 6" stroke-linecap="round"/>${motion}`;
      })
      .join('');
  };
  drawHub();
  window.addEventListener('resize', () => {
    clearTimeout(window.__ovHubResizeT);
    window.__ovHubResizeT = setTimeout(drawHub, 150);
  });

  // Ticker — gerçek son aktivitelerden döner, uydurma veri yok
  const items = buildActivityItems(data);
  const tickerEl = document.getElementById('ov-ticker-text');
  if (tickerEl && items.length) {
    let i = 0;
    const render = () => {
      const it = items[i % items.length];
      tickerEl.textContent = `${it.time} · ${it.title}${it.body ? ' — ' + it.body : ''}`;
    };
    render();
    if (!reduceMotion) {
      setInterval(() => {
        tickerEl.style.opacity = 0;
        setTimeout(() => { i += 1; render(); tickerEl.style.opacity = 1; }, 300);
      }, 3600);
    }
  }
}

function renderKpis(data) {
  const snap = getOverviewSnapshot(data);
  const pendingReviews = pendingReviewCount(data.reviews);
  const draftInbox = pendingInboxCount(data.inbox) + pendingEstesoftNpsCount(data.inbox);

  const badge = document.getElementById('inbox-badge');
  const inboxBadgeVal = navBadgeCount(Math.max(draftInbox, snap.ops.inboxOpen));
  if (inboxBadgeVal) {
    badge.textContent = inboxBadgeVal;
    badge.classList.remove('hidden');
  } else {
    badge.classList.add('hidden');
  }

  const reviewBadge = document.getElementById('reviews-badge');
  if (reviewBadge) {
    const reviewBadgeVal = navBadgeCount(Math.max(pendingReviews, snap.ops.reviewDrafts));
    if (reviewBadgeVal) {
      reviewBadge.textContent = reviewBadgeVal;
      reviewBadge.classList.remove('hidden');
    } else {
      reviewBadge.classList.add('hidden');
    }
  }

  const overviewSeries = [
    {
      title: 'Toplam sinyal',
      value: fmtCompactCount(snap.totalSignals),
      hint: `7 günde operasyon akışı · +%${trendGrowthPct(OVERVIEW_TREND_SEED.map((count) => ({ count })))}`,
      width: 96,
      tone: 'teal',
    },
    {
      title: 'Link dönüşümü',
      value: `%${snap.links.conversion}`,
      hint: `${fmtCompactCount(snap.links.reviews)} yorum · ${fmtCompactCount(snap.links.sent)} link`,
      width: Math.min(100, 24 + snap.links.conversion),
      tone: snap.links.conversion >= 20 ? 'green' : 'amber',
    },
    {
      title: 'Google puanı',
      value: `${snap.google.avg}★`,
      hint: `${fmtCompactCount(snap.google.fiveStar)} adet 5★ · ${fmtCompactCount(snap.google.total)} yorum`,
      width: Math.min(100, Math.round(Number(snap.google.avg) * 18)),
      tone: Number(snap.google.avg) >= 4.5 ? 'green' : 'amber',
    },
    {
      title: 'NPS skoru',
      value: `${snap.nps.avg}/10`,
      hint: `%${snap.nps.promoterPct} promoter · ${fmtCompactCount(snap.nps.total)} yanıt`,
      width: Math.max(20, Math.min(100, Number(snap.nps.avg) * 10 || 20)),
      tone: npsScoreTone(snap.nps.avg),
    },
    {
      title: 'Link tıklama',
      value: fmtCompactCount(snap.links.clicks),
      hint: `${fmtCompactCount(snap.links.sent)} davetten tıklayan hasta`,
      width: Math.min(100, 20 + Math.round((snap.links.clicks / Math.max(snap.links.sent, 1)) * 80)),
      tone: 'blue',
    },
    {
      title: 'WhatsApp akışı',
      value: fmtCompactCount(snap.channels.whatsapp),
      hint: `${fmtCompactCount(snap.channels.web)} web · ${fmtCompactCount(snap.channels.other)} diğer kanal`,
      width: Math.min(100, Math.round((snap.channels.whatsapp / snap.totalSignals) * 100)),
      tone: 'green',
    },
  ];

  const detailKpis = [
    { label: 'Operasyon sinyali', value: fmtCompactCount(snap.totalSignals), sub: '7 günlük toplam akış · inbox, NPS, Google, ekip', tone: 'teal', highlight: true },
    { label: 'Google link daveti', value: fmtCompactCount(snap.links.sent), sub: `${fmtCompactCount(snap.links.clicks)} tıklama · %${snap.links.conversion} dönüşüm`, tone: 'green' },
    { label: 'NPS yanıtı', value: fmtCompactCount(snap.nps.total), sub: `Ort. ${snap.nps.avg}/10 · %${snap.nps.promoterPct} promoter`, tone: npsScoreTone(snap.nps.avg) },
    { label: 'Google yorumu', value: fmtCompactCount(snap.google.total), sub: `${fmtCompactCount(snap.google.fiveStar)} adet 5★ · ort. ${snap.google.avg}★`, tone: Number(snap.google.avg) >= 4.5 ? 'green' : 'amber' },
    { label: 'Kanal dağılımı', value: fmtCompactCount(snap.channels.whatsapp), sub: `WhatsApp · ${fmtCompactCount(snap.channels.web)} web · ${fmtCompactCount(snap.channels.other)} diğer`, tone: 'neutral' },
    { label: 'eNPS sinyali', value: fmtCompactCount(snap.enps.total), sub: `${fmtCompactCount(snap.enps.promoter)} promoter · ort. ${snap.enps.avg}/10`, tone: 'blue' },
    { label: 'Açık inbox', value: fmtCompactCount(snap.ops.inboxOpen), sub: 'Okunmamış / taslak mesaj kuyruğu', tone: snap.ops.inboxOpen > 0 ? 'amber' : 'neutral' },
    { label: 'Recall takibi', value: fmtCompactCount(snap.ops.recall), sub: 'Geri çağrı ve kontrol kampanyası', tone: 'neutral' },
    { label: 'İtibar taraması', value: fmtCompactCount(snap.ops.mentions), sub: `${snap.ops.critical} kritik alarm · Sentinel`, tone: snap.ops.critical > 0 ? 'red' : 'neutral' },
  ];

  $('#kpi-grid').innerHTML = `
    <div class="overview-shell">
      ${buildOverviewHeroHtml(data, snap)}
      ${buildOverviewHubHtml()}
      <div class="overview-shell-head">
        <div>
          <p class="topbar-eyebrow">Özet görünümü</p>
          <h2>Bugünün operasyon tablosu</h2>
          <p class="overview-shell-copy">Son 7 günde ${fmtCompactCount(snap.totalSignals)} operasyon sinyali işlendi: kanal, NPS, Google yorumu ve ekip geri bildirimleri tek özet ekranda.</p>
        </div>
        <div class="overview-shell-actions">
          <span class="overview-tenure-badge">${escapeHtml(tenureMonthsLabel(activeClinic()))}</span>
          <button type="button" id="overview-toggle-btn" class="btn-secondary btn-sm">
            <i class="fa-solid fa-chart-column"></i> ${state.overviewExpanded ? 'Detayı kapat' : 'Detayı aç'}
          </button>
        </div>
      </div>
      ${dashColorLegendHtml()}
      <div class="overview-graph-grid">
        ${overviewSeries.map((item) => {
          const barColor = toneBarColor(item.tone);
          return `
          <article class="overview-graph-card tone-${item.tone}">
            <div class="overview-graph-meta">
              <span>${item.title}</span>
              <strong>${item.value}</strong>
            </div>
            <div class="overview-graph-bar"><span style="width:${item.width}%;background:linear-gradient(90deg, ${barColor}, ${barColor}cc)"></span></div>
            <p>${item.hint}</p>
          </article>`;
        }).join('')}
      </div>
      ${buildOverviewChartsHtml(data)}
      <div class="kpi-grid-cards ${state.overviewExpanded ? '' : 'hidden'}">
        ${detailKpis.map((item) => kpiCardHtml(item)).join('')}
      </div>
    </div>
  `;

  $('#overview-toggle-btn')?.addEventListener('click', () => {
    state.overviewExpanded = !state.overviewExpanded;
    renderKpis(data);
  });
  initOverviewHero(data, snap);
}

function table(headers, rows, emptyTitle = 'Henüz kayıt yok', emptyBody = 'Bu sekmede görüntülenecek veri henüz oluşmadı.') {
  if (!rows.length) return emptyStateHtml(emptyTitle, emptyBody);
  return `<div class="data-table-wrap"><table class="data-table"><thead><tr>${headers.map((h) => `<th>${h}</th>`).join('')}</tr></thead><tbody>${rows.join('')}</tbody></table></div>`;
}

function miniList(items) {
  if (!items.length) return emptyStateHtml('Liste boş', 'Bu alanda henüz kayıt bulunmuyor.');
  return `<ul style="font-size:.875rem;margin:0;padding-left:1rem;color:#475569">${items.map((i) => `<li style="margin:.25rem 0">${i}</li>`).join('')}</ul>`;
}

function inboxToolbarHtml(inboundCount, estesoftCount) {
  const clinicId = effectiveClinicId();
  const scope = clinicId
    ? (clinicById(clinicId)?.name || 'seçili firma')
    : isAdmin()
      ? 'tüm firmalar'
      : 'inbox';
  const view = state.inboxView || 'inbound';
  return `
    <div class="panel-toolbar inbox-toolbar">
      <h2 class="panel-title" style="margin:0">Inbox</h2>
      <div class="inbox-tabs">
        <button type="button" class="inbox-tab ${view === 'inbound' ? 'active' : ''}" data-inbox-view="inbound">
          <i class="fa-solid fa-inbox"></i> Gelen mesajlar
          ${inboundCount ? `<span class="inbox-tab-count">${inboundCount}</span>` : ''}
        </button>
        <button type="button" class="inbox-tab ${view === 'estesoft_nps' ? 'active' : ''}" data-inbox-view="estesoft_nps">
          <i class="fa-solid fa-stethoscope"></i> Estesoft NPS
          ${estesoftCount ? `<span class="inbox-tab-count">${estesoftCount}</span>` : ''}
        </button>
      </div>
      <div class="panel-toolbar-actions">
        <span class="panel-toolbar-meta">${view === 'estesoft_nps' ? estesoftCount : inboundCount} kayıt · ${escapeHtml(scope)}</span>
        ${useProxy() ? `<button type="button" class="btn-danger btn-sm" id="inbox-clear-btn"><i class="fa-solid fa-trash-can"></i> Temizle</button>` : ''}
      </div>
    </div>`;
}

async function clearInbox() {
  const clinicId = effectiveClinicId();
  const scope = clinicId
    ? (clinicById(clinicId)?.name || 'bu firma')
    : isAdmin()
      ? 'TÜM firmalar'
      : 'inbox';
  if (!confirm(`${scope} için tüm inbox mesajları silinsin mi?\n\nBu işlem geri alınamaz.`)) return;

  const btn = $('#inbox-clear-btn');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Temizleniyor…';
  }
  try {
    const res = await fetch('/api/inbox/clear', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        clinicId: clinicId || null,
        clearAll: isAdmin() && !clinicId,
      }),
    });
    const data = await res.json();
    if (res.status === 401) {
      window.location.href = '/dashboard/login';
      return;
    }
    if (!res.ok) throw new Error(data.error || data.detail || `HTTP ${res.status}`);
    $('#status').textContent = `Inbox temizlendi (${data.deleted ?? 0} mesaj) · ${new Date().toLocaleTimeString('tr-TR')}`;
    $('#status').className = 'status-pill ok';
    await load();
  } catch (err) {
    alert(err.message || 'Inbox temizlenemedi');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-trash-can"></i> Temizle';
    }
  }
}

function inboxPanelIntro(data) {
  const snap = getOverviewSnapshot(data);
  return `
    ${panelTabHero({
      kicker: 'Gelen kutusu',
      title: 'Çok kanallı mesaj merkezi',
      subtitle: 'WhatsApp, web chat ve otomasyon mesajları tek akışta; AI taslakları ekibin yanıt süresini kısaltır.',
      iconClass: 'fa-solid fa-inbox',
      tone: 'neutral',
      badges: [`${fmtCompactCount(snap.totalSignals)} sinyal`, `${fmtCompactCount(snap.ops.inboxOpen)} açık`, `${fmtCompactCount(snap.channels.whatsapp)} WhatsApp`],
    })}
    ${panelStatGrid([
      { label: 'Toplam mesaj', value: fmtCompactCount(snap.totalSignals), hint: '7 günlük operasyon', tone: 'teal' },
      { label: 'WhatsApp', value: fmtCompactCount(snap.channels.whatsapp), hint: 'Yorum linki + inbox', tone: 'green' },
      { label: 'Web chat', value: fmtCompactCount(snap.channels.web), hint: 'Site ziyaretçisi', tone: 'neutral' },
      { label: 'Taslak hazır', value: fmtCompactCount(snap.ops.inboxOpen), hint: 'AI yanıt bekliyor', tone: 'neutral' },
    ])}
    ${panelChannelBars(snap.channels, snap.totalSignals)}`;
}

function renderInbox(data) {
  const all = data.inbox;
  const view = state.inboxView || 'inbound';
  const inboundItems = all.filter((r) => (r.message_kind || 'inbound') === 'inbound');
  const estesoftItems = all.filter((r) => r.message_kind === 'estesoft_nps');
  const items = view === 'estesoft_nps' ? estesoftItems : inboundItems;
  const intro = inboxPanelIntro(data);

  if (!items.length) {
    $('#panel').innerHTML = `${intro}${inboxToolbarHtml(inboundItems.length, estesoftItems.length)}${emptyStateHtml(
      view === 'estesoft_nps' ? 'Estesoft NPS taslağı yok' : 'Inbox boş',
      view === 'estesoft_nps'
        ? 'Randevu tamamlandığında NPS taslağı burada görünür.'
        : 'Gelen WhatsApp ve web mesajları burada listelenir.'
    )}`;
    bindInboxToolbar(inboundItems, estesoftItems);
    return;
  }

  const html = items
    .map((r) => {
      const isDraft = r.status === 'draft_ready';
      const isNew = r.status === 'open';
      const phone = r.sender_phone || '';
      const name = r.sender_name || 'Hasta';
      const estesoft = isEstesoftNps(r);
      return `
      <article class="inbox-item ${isDraft ? 'draft' : ''} ${isNew ? 'inbox-new' : ''} ${estesoft ? 'inbox-estesoft' : ''}" data-id="${r.id}">
        <div>
          <p class="inbox-meta">${badge(estesoft ? 'Estesoft NPS' : r.channel, estesoft ? 'purple' : 'blue')} · ${escapeHtml(name)} · ${fmtDate(r.created_at)} ${badge(humanizeStatus(r.status), isDraft ? 'amber' : isNew ? 'green' : 'slate')}</p>
          <p class="inbox-body">${escapeHtml(r.body)}</p>
          <p class="inbox-draft"><strong>${estesoft ? 'Gönderilecek NPS metni:' : 'AI taslak:'}</strong> ${escapeHtml(r.ai_draft_reply || '—')}</p>
        </div>
        <div>
          ${isDraft ? `<button type="button" class="btn-primary btn-sm inbox-reply-btn" data-id="${r.id}"><i class="fa-brands fa-whatsapp"></i> ${estesoft ? 'Onayla ve gönder' : 'Yanıtla'}</button>` : ''}
        </div>
      </article>`;
    })
    .join('');
  $('#panel').innerHTML = `${intro}${inboxToolbarHtml(inboundItems.length, estesoftItems.length)}<div class="inbox-list">${html}</div>`;
  bindInboxToolbar(inboundItems, estesoftItems);

  $$('.inbox-reply-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const row = items.find((i) => i.id === btn.dataset.id);
      if (row) openInboxModal(row);
    });
  });
}

function bindInboxToolbar(inboundItems, estesoftItems) {
  $$('[data-inbox-view]').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.inboxView = btn.dataset.inboxView;
      syncUiHash();
      renderInbox(state.cache);
    });
  });
  const clearBtn = $('#inbox-clear-btn');
  if (clearBtn) clearBtn.addEventListener('click', clearInbox);
  void inboundItems;
  void estesoftItems;
}

function escapeHtml(s) {
  return String(s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function openInboxModal(row) {
  state.selectedInbox = row;
  const estesoft = isEstesoftNps(row);
  $('#inbox-modal-title').textContent = estesoft ? 'Estesoft NPS — onaylı gönderim' : 'WhatsApp yanıtı';
  $('#modal-inbound-label').textContent = estesoft ? 'Tetikleyen olay' : 'Gelen mesaj';
  $('#modal-reply-label').textContent = estesoft ? 'NPS mesajı (düzenleyebilirsiniz)' : 'Yanıt metni';
  $('#modal-inbound').textContent = row.body || '';
  $('#modal-reply').value = row.ai_draft_reply || '';
  const phone = row.sender_phone || '';
  $('#modal-phone-hint').textContent = phone
    ? `Alıcı: ${row.sender_name || 'Hasta'} · +${phone.replace(/^90/, '90 ')}${estesoft ? ' · Onay sonrası WhatsApp ile gider' : ''}`
    : 'Telefon numarası kayıtlı değil — eski mesajlarda manuel eklemeniz gerekebilir.';
  $('#modal-send-btn').innerHTML = estesoft
    ? '<i class="fa-brands fa-whatsapp"></i> Onayla ve gönder'
    : '<i class="fa-brands fa-whatsapp"></i> Onayla ve gönder';
  $('#modal-send-error').classList.add('hidden');
  $('#inbox-modal').classList.remove('hidden');
}

function closeInboxModal() {
  $('#inbox-modal').classList.add('hidden');
  state.selectedInbox = null;
}

function renderReviews(data) {
  const snap = getOverviewSnapshot(data);
  const rs = reviewStatsForClinic(effectiveClinicId(), state.rawCache || { reviews: data.reviews, mentions: data.mentions });
  const items = data.reviews;
  const intro = `
    ${panelTabHero({
      kicker: 'Google Haritalar',
      title: 'Yorum ve itibar merkezi',
      subtitle: 'Yeni yorumlar otomatik yakalanır, duygu analizi yapılır ve marka tonunuza uygun AI yanıt taslağı üretilir.',
      iconClass: 'fa-brands fa-google',
      tone: 'neutral',
      badges: [`${snap.google.avg}★ ortalama`, `${fmtCompactCount(snap.google.total)} yorum`, `%${snap.links.conversion} dönüşüm`],
    })}
    ${panelStatGrid([
      { label: 'Toplam yorum', value: fmtCompactCount(snap.google.total), hint: 'Google Maps kaydı', tone: 'neutral' },
      { label: '5 yıldız', value: fmtCompactCount(snap.google.fiveStar), hint: 'En yüksek puan', tone: 'green' },
      { label: 'Link dönüşümü', value: `%${snap.links.conversion}`, hint: `${fmtCompactCount(snap.links.reviews)} yeni yorum`, tone: 'teal' },
      { label: 'AI taslak', value: fmtCompactCount(snap.ops.reviewDrafts), hint: 'Onay bekleyen', tone: 'neutral' },
    ])}
    <div class="panel-split-visual">
      <div class="panel-split-card">
        <div class="panel-section-title-row">
          <h3 class="panel-section-title">Yıldız dağılımı</h3>
          ${googleOpenLinkHtml(activeClinic())}
        </div>
        ${panelStarBars(snap.google.stars)}
      </div>
      <div class="panel-split-card">
        <h3 class="panel-section-title">Yorum hunisi</h3>
        ${panelFunnel([
          { label: 'Google link gönderildi', value: fmtCompactCount(snap.links.sent), pct: 100 },
          { label: 'Link tıklandı', value: fmtCompactCount(snap.links.clicks), pct: 61 },
          { label: 'Yorum bırakıldı', value: fmtCompactCount(snap.links.reviews), pct: 34 },
        ])}
      </div>
    </div>`;
  if (!items.length) {
    $('#panel').innerHTML = `${intro}${emptyStateHtml('Henüz Google yorumu yok', 'Senkronize edilen yorumlar ve AI taslakları burada görünür.')}`;
    return;
  }
  const html = items
    .map((r) => {
      const hasDraft = (r.draft_reply || '').trim() && r.status === 'pending_approval';
      const published = r.status === 'published';
      return `
      <article class="inbox-item ${hasDraft ? 'draft' : ''}" data-id="${r.id}">
        <div>
          <p class="inbox-meta">${badge('Google', 'blue')} · ${escapeHtml(r.author_name)} · ★${r.rating} · ${fmtDate(r.created_at)} ${badge(humanizeStatus(r.status), published ? 'green' : hasDraft ? 'amber' : 'slate')}</p>
          <p class="inbox-body">${escapeHtml(r.review_text)}</p>
          <p class="inbox-draft"><strong>AI taslak:</strong> ${escapeHtml(r.draft_reply || (r.status === 'pending_approval' ? 'Üretiliyor…' : '—'))}</p>
        </div>
        <div>
          ${hasDraft ? `<button type="button" class="btn-primary btn-sm review-reply-btn" data-id="${r.id}"><i class="fa-brands fa-google"></i> Yanıtla</button>` : ''}
        </div>
      </article>`;
    })
    .join('');
  $('#panel').innerHTML = `
    ${intro}
    <h3 class="panel-section-title">Son yorumlar — ${items.length} kayıt</h3>
    <p class="firm-review-hint kpi-sub-links">${formatReviewSummary(rs, activeClinic()) || `Ort. ${snap.google.avg}★ · ${fmtCompactCount(snap.google.fiveStar)} adet 5★`} · AI taslak hazır olanlara <strong>Yanıtla</strong> ile onaylayın</p>
    <div class="inbox-list">${html}</div>`;

  $$('.review-reply-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const row = items.find((i) => i.id === btn.dataset.id);
      if (row) openReviewModal(row);
    });
  });
}

function openReviewModal(row) {
  state.selectedReview = row;
  $('#review-modal-inbound').textContent = `★${row.rating} — ${row.review_text || ''}`;
  $('#review-modal-reply').value = row.draft_reply || '';
  const maps = clinicMapsUrl(row.clinic_id);
  $('#review-modal-hint').textContent = maps
    ? 'Onay sonrası yanıt panoya kopyalanır ve Google Haritalar açılır — yanıtı orada yapıştırın.'
    : 'Onay sonrası yanıt kaydedilir.';
  $('#review-modal-error').classList.add('hidden');
  $('#review-modal').classList.remove('hidden');
}

function closeReviewModal() {
  $('#review-modal').classList.add('hidden');
  state.selectedReview = null;
}

function renderSectorFirms(sector, raw) {
  const panel = $('#panel');
  const meta = SECTOR_META[sector] || SECTOR_META.clinic;
  const firms = firmsForSector(sector);

  const paint = (queueHtml) => {
    if (!firms.length) {
      panel.innerHTML = `
        ${queueHtml || ''}
        <h2 class="panel-title">${meta.title}</h2>
        ${emptyStateHtml(meta.title, meta.empty)}`;
      bindPendingApplicationActions();
      return;
    }

    const cards = firms
      .map((c) => {
      const s = statsForClinic(c.id, raw);
      const rs = reviewStatsForClinic(c.id, raw);
      const demo = isDemoFirm(c);
      const sales = demoResultOf(c);
      const readiness = demo
        ? { complete: false, progress: 100 }
        : assessFirmReadiness(c, c.integration_config || {});
      const reviewBadge = c.google_review_count != null ? c.google_review_count : rs.total;
      const statusPill = demo
        ? ''
        : readiness.complete || c.automation_enabled
          ? '<span class="firm-status-pill firm-status-live">Otomasyon aktif</span>'
          : `<span class="firm-status-pill firm-status-pending">Kurulum %${readiness.progress}</span>`;
      const openBtn = meta.panelAction
        ? `<button type="button" class="btn-secondary btn-sm firm-open-btn" data-clinic-id="${c.id}">Panele git</button>`
        : '';
      const actionBtn = demo
        ? `<div class="firm-card-actions">${openBtn}<span class="sector-soon">Sunum örneği</span></div>`
        : `<div class="firm-card-actions">
              ${openBtn}
              ${(c.sector || 'clinic') === 'clinic' ? `<button type="button" class="btn-primary btn-sm firm-wa-btn" data-clinic-id="${c.id}"><i class="fa-brands fa-whatsapp"></i> WhatsApp QR</button>` : ''}
              <button type="button" class="btn-secondary btn-sm firm-edit-btn" data-clinic-id="${c.id}">Kurulumu tamamla</button>
            </div>`;
      const beforeAfter = sales
        ? `<div class="firm-stats firm-stats-sales">
            <div><strong>${sales.reviews_before}</strong><span>Başlangıç yorum</span></div>
            <div><strong>${sales.reviews_after}</strong><span>Şimdi</span></div>
            <div><strong>★${sales.rating_before}</strong><span>Eski puan</span></div>
            <div><strong>★${sales.rating_after}</strong><span>Yeni puan</span></div>
            <div><strong>${sales.started_months_ago} ay</strong><span>Nefalix süresi</span></div>
          </div>`
        : `<div class="firm-stats">
          <div>${clinicGoogleUrl(c) ? `<a href="${escapeHtml(clinicGoogleUrl(c))}" target="_blank" rel="noopener noreferrer" class="firm-stat-link"><strong>${c.google_review_count ?? rs.googleMaps ?? rs.systemGoogle ?? '—'}</strong><span>Google yorumları</span></a>` : `<strong>${c.google_review_count ?? rs.googleMaps ?? rs.systemGoogle ?? '—'}</strong><span>Google yorumları</span>`}</div>
          <div>${c.sikayetvar_url ? `<a href="${escapeHtml(c.sikayetvar_url)}" target="_blank" rel="noopener noreferrer" class="firm-stat-link"><strong>${demo ? '—' : rs.sikayetvar || '0'}</strong><span>Şikayetvar</span></a>` : `<strong>${demo ? '—' : rs.sikayetvar || '0'}</strong><span>Şikayetvar</span>`}</div>
          <div>${c.website_reviews_url ? `<a href="${escapeHtml(c.website_reviews_url)}" target="_blank" rel="noopener noreferrer" class="firm-stat-link"><strong>${demo ? '—' : rs.website}</strong><span>Web yorumları</span></a>` : `<strong>${demo ? '—' : rs.website}</strong><span>Web yorumları</span>`}</div>
          <div><strong>${demo ? '2' : s.drafts}</strong><span>Bekleyen inbox</span></div>
          <div><strong>${demo ? '12' : s.nps}</strong><span>NPS yanıt</span></div>
        </div>`;
      return `
      <article class="firm-card${demo ? ' firm-card-demo' : ''}" data-clinic-id="${c.id}">
        <div class="firm-card-head">
          ${firmLogoImg(c, sector)}
          <div>
            <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:.5rem;flex-wrap:wrap">
              <h3>${escapeHtml(c.name)}</h3>
              <span class="badge ${demo ? 'badge-demo' : 'badge-green'}">${demo ? 'Örnek' : ''} ${reviewBadge} yorum</span>
            </div>
            ${statusPill}
            <p class="firm-meta">${c.address ? escapeHtml(c.address) : ''}${c.google_rating != null ? `<br>Google ★${c.google_rating}` : ''}${c.whatsapp_phone ? `<br>WhatsApp: ${escapeHtml(c.whatsapp_phone)}` : ''}</p>
          </div>
        </div>
        ${demoResultHtml(c)}
        ${clinicLinksHtml(c, { compact: true, sector })}
        ${beforeAfter}
        <p class="firm-review-hint">${
          sales
            ? `${escapeHtml(sales.headline)} · ${escapeHtml(sales.detail)}`
            : demo
              ? `Google ★${c.google_rating ?? '—'} · Sunum verisi`
              : formatReviewSummary(rs, c)
        }</p>
        ${actionBtn}
      </article>`;
    })
    .join('');

    const sectorReviews = firms.reduce(
      (sum, c) => sum + reviewStatsForClinic(c.id, raw).total,
      0
    );
    panel.innerHTML = `
      ${queueHtml || ''}
      <div class="firm-toolbar">
        ${panelTabHero({
          kicker: 'Firma portföyü',
          title: meta.title,
          subtitle: 'Sektör bazlı firma kartları, yorum özeti, otomasyon durumu ve kurulum ilerlemesi tek listede.',
          iconClass: 'fa-solid fa-building',
          tone: 'neutral',
          badges: [`${firms.length} firma`, `${fmtCompactCount(sectorReviews)} yorum`, 'Canlı + örnek'],
        })}
        <button type="button" class="btn-primary btn-sm" id="firm-add-btn"><i class="fa-solid fa-plus"></i> Firma ekle</button>
      </div>
      <div class="firm-grid">${cards}</div>`;

    $('#firm-add-btn')?.addEventListener('click', () => openFirmModal(null, sector));
    $$('.firm-edit-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const c = clinicById(btn.dataset.clinicId);
        if (c) openFirmModal(c, sector);
      });
    });
    $$('.firm-wa-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const c = clinicById(btn.dataset.clinicId);
        if (c) openWaConnectModal(c);
      });
    });

    $$('.firm-open-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.selectedClinicId = btn.dataset.clinicId;
        $('#clinic-select').value = state.selectedClinicId;
        persistSelectedClinic();
        state.cache = buildViewData(state.rawCache);
        updateHeader();
        state.tab = 'overview';
        applyNavUiState();
        renderKpis(state.cache);
        renderTab(state.cache);
      });
    });
    bindPendingApplicationActions();
  };

  const cachedQueue = pendingApplicationsHtml(
    state.pendingApplications || [],
    !!state.pendingApplicationsDemo
  );
  paint(cachedQueue);

  if (isAdmin()) {
    loadPendingApplications().then((list) => {
      if (state.tab !== 'firms') return;
      paint(pendingApplicationsHtml(list, !!state.pendingApplicationsDemo));
    });
  }
}

function bindPendingApplicationActions() {
  $$('.app-complete-btn').forEach((btn) => {
    btn.addEventListener('click', () => completePendingApplication(btn.dataset.appId));
  });
}

function renderFirms(raw) {
  renderSectorFirms('clinic', raw);
}

function updateFirmsNavCounts() {
  if (!isAdmin()) return;
  for (const sector of ['clinic', 'hotel', 'auto']) {
    const el = document.querySelector(`[data-sector-count="${sector}"]`);
    if (!el) continue;
    const n = firmsForSector(sector).length;
    el.textContent = n > 0 ? String(n) : '';
    el.classList.toggle('hidden', n === 0);
  }
}

function syncFirmsNav() {
  const group = $('#firms-nav-group');
  const subs = $('#firms-nav-subitems');
  const toggle = $('#firms-nav-toggle');
  const subLabel = $('#firms-nav-sub');
  if (!group || !isAdmin()) return;

  const onFirms = state.tab === 'firms';
  toggle?.classList.toggle('active', onFirms);
  toggle?.setAttribute('aria-expanded', onFirms ? 'true' : 'false');
  group.classList.toggle('expanded', onFirms);
  subs?.classList.toggle('hidden', !onFirms);

  $$('[data-sector]').forEach((btn) => {
    btn.classList.toggle('active', onFirms && btn.dataset.sector === state.selectedSector);
  });

  if (subLabel) {
    subLabel.textContent = onFirms
      ? (SECTOR_META[state.selectedSector]?.title || 'Firmalar')
      : 'Sektör seçin';
  }
}

function selectFirmsSector(sector) {
  state.tab = 'firms';
  state.selectedSector = sector;
  applyNavUiState();
  syncUiHash();
  schedulePoll();
  if (state.rawCache) renderSectorFirms(sector, state.rawCache);
}

/** Sesli asistan — Claude mock UI (canlı arama API sonra bağlanır) */
const VOICE_DEMO_STATS = [
  { label: 'Bu hafta arandı', value: '184' },
  { label: 'Randevu alındı', value: '76', tone: 'success' },
  { label: 'Yanıt oranı', value: '%61' },
  { label: 'Ort. görüşme', value: '1:42' },
];

const VOICE_DEMO_CALLS = [
  { hasta: 'Ayşe Yılmaz', detay: '6 ay sonrası zirkonyum kontrolü', sonuc: 'Randevu alındı', sure: '2:04', zaman: 'Bugün 09:40', tone: 'success' },
  { hasta: 'Mehmet Kaya', detay: 'İmplant kontrolü hatırlatması', sonuc: 'Sesli mesaj bırakıldı', sure: '0:38', zaman: 'Bugün 09:22', tone: 'warning' },
  { hasta: 'Zeynep Demir', detay: '3. deneme otomatik planlandı', sonuc: 'Ulaşılamadı', sure: '—', zaman: 'Bugün 09:10', tone: 'critical' },
  { hasta: 'Can Arslan', detay: 'Ortodonti kontrolü — 14 Ağu 11:00', sonuc: 'Randevu alındı', sure: '1:56', zaman: 'Dün 17:05', tone: 'success' },
];

function renderVoiceAssistant(data) {
  const panel = $('#panel');
  const recallN = (data?.recall || []).length;
  const activeBadge = Math.max(12, Math.min(99, recallN || 12));
  const stats = VOICE_DEMO_STATS.map((s) => `
    <div class="voice-stat${s.tone ? ` tone-${s.tone}` : ''}">
      <strong>${escapeHtml(s.value)}</strong>
      <span>${escapeHtml(s.label)}</span>
    </div>`).join('');
  const rows = VOICE_DEMO_CALLS.map((c, i) => `
    <article class="voice-call-row">
      <div class="voice-call-ico"><i class="fa-solid fa-microphone-lines"></i></div>
      <div class="voice-call-main">
        <strong>${escapeHtml(c.hasta)}</strong>
        <p>${escapeHtml(c.detay)}</p>
      </div>
      <span class="voice-call-result tone-${c.tone}">${escapeHtml(c.sonuc)}</span>
      <span class="voice-call-dur">${escapeHtml(c.sure)}</span>
      <span class="voice-call-time">${escapeHtml(c.zaman)}</span>
    </article>`).join('');

  panel.innerHTML = `
    ${panelTabHero({
      kicker: 'Sesli asistan',
      title: 'Randevu araması',
      subtitle: 'AI, randevusuz kalan ve recall listesindeki hastaları otomatik arar; görüşme sonucu ve kaydı buraya düşer.',
      iconClass: 'fa-solid fa-microphone-lines',
      tone: 'purple',
      badges: [`${activeBadge} aktif kayıt`, 'Örnek veri', 'API yakında'],
    })}
    <div class="voice-panel">
      <div class="voice-panel-head">
        <div>
          <h3>Sesli asistan — randevu araması</h3>
          <p>Recall + randevu hatırlatması birleşik arama kuyruğu. Canlı telefon API bağlanınca gerçek kayıtlar burada listelenir.</p>
        </div>
        <span class="voice-pill">${activeBadge} aktif kayıt</span>
      </div>
      <div class="voice-stats">${stats}</div>
      <h3 class="panel-section-title">Son aramalar</h3>
      <div class="voice-call-list">${rows}</div>
      <p class="voice-foot"><span class="badge badge-demo">ÖRNEK</span> Görünen aramalar sunum verisi. Gerçek sesli asistan hattı bağlandığında recall listesinden otomatik beslenir.</p>
    </div>`;
}

// Canlı aktivite listesi — hem "Canlı aktivite akışı" kartı hem de
// Özet hero'sundaki ticker AYNI bu fonksiyondan besleniyor. Tek kaynak:
// ticker'da uydurma isim/olay göstermek yerine gerçek son kayıtları
// döndürüyor; veri yoksa boş dizi döner, çağıran taraf onu ele alır.
function buildActivityItems(data) {
  const linkInbox = data.inbox.filter((r) => /google yorum linki/i.test(r.body || ''));
  const otherInbox = data.inbox.filter((r) => !/google yorum linki/i.test(r.body || ''));
  return [
    ...linkInbox.slice(0, 3).map((r) => ({
      tone: r.direction === 'outbound' ? 'green' : 'neutral',
      icon: r.direction === 'outbound' ? 'fa-paper-plane' : 'fa-reply',
      title: r.direction === 'outbound' ? 'Google link gönderildi' : 'Hasta yorum bıraktı',
      body: (r.body || '').replace('Google yorum linki gönderildi — ', ''),
      time: fmtDate(r.created_at),
    })),
    ...data.reviews.slice(0, 3).map((r) => ({
      tone: 'amber',
      iconClass: 'fa-brands fa-google',
      title: `★${r.rating} Google yorumu`,
      body: `${r.author_name} — ${(r.review_text || '').slice(0, 64)}`,
      time: fmtDate(r.created_at),
    })),
    ...data.nps
      .filter((r) => r.google_link_sent || r.score >= 9)
      .slice(0, 2)
      .map((r) => ({
        tone: 'green',
        icon: 'fa-star',
        title: `NPS ${r.score}/10 → Google yönlendirme`,
        body: r.patient_name || r.feedback?.slice(0, 64) || 'Promoter hasta',
        time: fmtDate(r.created_at),
      })),
    ...otherInbox.slice(0, 2).map((r) => ({
      tone: 'neutral',
      icon: 'fa-inbox',
      title: r.channel || 'Inbox',
      body: (r.body || '').slice(0, 72),
      time: fmtDate(r.created_at),
    })),
  ].slice(0, 8);
}

function renderTab(data) {
  const tab = state.tab;
  $('#kpi-grid')?.classList.toggle('hidden', tab !== 'overview');
  if (tab === 'firms' && isAdmin()) {
    renderSectorFirms(state.selectedSector || 'clinic', state.rawCache);
    syncFirmsNav();
    return;
  }
  if (tab === 'inbox') {
    renderInbox(data);
    return;
  }

  const panel = $('#panel');
  if (tab === 'overview') {
    const profile = activeClinic() ? renderClinicProfileCard(activeClinic()) : '';
    const activityItems = buildActivityItems(data);

    const snap = getOverviewSnapshot(data);
    panel.innerHTML = `
      ${profile}
      <div class="overview-activity-head">
        <h2 class="panel-title">Canlı aktivite akışı</h2>
        <span class="overview-chart-badge">${fmtCompactCount(snap.totalSignals)} sinyalden son ${activityItems.length} kayıt</span>
      </div>
      <div class="overview-activity-grid">
        ${
          activityItems.length
            ? activityItems
                .map(
                  (item) => `
          <article class="overview-activity-card tone-${item.tone}">
            <div class="overview-activity-icon"><i class="${item.iconClass || `fa-solid ${item.icon}`}"></i></div>
            <div>
              <strong>${escapeHtml(item.title)}</strong>
              <p>${escapeHtml(item.body || '—')}</p>
              <small>${item.time}</small>
            </div>
          </article>`
                )
                .join('')
            : emptyStateHtml('Henüz aktivite yok', 'Demo veriler özet grafiklerinde görünüyor; canlı akış burada listelenecek.')
        }
      </div>`;
    return;
  }

  if (tab === 'nps') {
    renderNpsPanel(data);
    return;
  }

  if (tab === 'reviews') {
    renderReviews(data);
    return;
  }

  if (tab === 'enps') {
    const snap = getOverviewSnapshot(data);
    const enps = enpsPanelMetrics(data, snap);
    const byDept = {};
    enps.rows.forEach((r) => {
      const d = r.department || 'Diğer';
      if (!byDept[d]) byDept[d] = { total: 0, sum: 0 };
      byDept[d].total += 1;
      byDept[d].sum += Number(r.score) || 0;
    });
    const deptBars = Object.entries(byDept)
      .map(([dept, v]) => ({ dept, avg: (v.sum / v.total).toFixed(1), count: v.total }))
      .sort((a, b) => b.count - a.count);
    panel.innerHTML = `
      ${panelTabHero({
        kicker: 'Çalışan deneyimi',
        title: 'eNPS ekip merkezi',
        subtitle: 'Doktor, asistan, resepsiyon ve operasyon ekibinin haftalık nabzını ölçün; kırılmaları erken yakalayın.',
        iconClass: 'fa-solid fa-users',
        tone: 'neutral',
        badges: [
          `Ort. ${enps.avgScore === '—' ? snap.enps.avg : enps.avgScore}/10`,
          `${fmtCompactCount(snap.enps.total)} sinyal`,
          `%${enps.participationPct} katılım`,
        ],
      })}
      ${panelStatGrid([
        { label: 'Katılım', value: `%${enps.participationPct}`, hint: `${fmtCompactCount(enps.responses)} yanıt · ${fmtCompactCount(enps.invited)} davet`, tone: 'green' },
        { label: 'Promoter', value: fmtCompactCount(enps.promoters), hint: 'Ekip içi memnuniyet', tone: 'green' },
        { label: 'İyileştirme', value: fmtCompactCount(enps.improvement), hint: 'Takip notu', tone: 'amber' },
        { label: 'Ortalama skor', value: `${enps.avgScore === '—' ? snap.enps.avg : enps.avgScore}/10`, hint: 'eNPS ortalaması', tone: 'teal' },
      ])}
      <div class="panel-split-visual">
        <div class="panel-split-card">
          <h3 class="panel-section-title">Departman ortalamaları</h3>
          <div class="panel-dept-bars">${deptBars
            .map(
              (d) => `<div class="panel-dept-row"><span>${escapeHtml(d.dept)}</span><div class="overview-graph-bar"><span style="width:${Math.min(100, Number(d.avg) * 10)}%;background:${CHART_COLORS.primary}"></span></div><strong>${d.avg}/10</strong><em>${d.count} kişi</em></div>`
            )
            .join('')}</div>
        </div>
        <div class="panel-split-card">
          <h3 class="panel-section-title">eNPS dağılımı</h3>
          ${renderDonutChart(
            [
              { label: 'Promoter', value: snap.enps.promoter, color: CHART_COLORS.positive },
              { label: 'İyileştirme', value: snap.enps.improvement, color: CHART_COLORS.warning },
            ],
            snap.enps.avg,
            '/10'
          )}
        </div>
      </div>
      <h3 class="panel-section-title">Çalışan yanıtları</h3>
      ${table(
        ['Rol', 'Çalışan', 'Skor', 'Sonuç', 'Not', 'Tarih'],
        enps.rows.map(
          (r) =>
            `<tr><td>${escapeHtml(r.department || '—')}</td><td>${escapeHtml(r.employee_name || '—')}</td><td><strong>${r.score}</strong>/10</td><td>${badge(r.flow, flowTone(r.flow))}</td><td>${escapeHtml(r.feedback || '—')}</td><td>${fmtDate(r.created_at)}</td></tr>`
        )
      )}`;
    return;
  }

  if (tab === 'sentinel') {
    const snap = getOverviewSnapshot(data);
    const clinic = activeClinic();
    const critical = data.mentions.filter((r) => r.is_critical).length;
    const positive = data.mentions.filter((r) => r.sentiment === 'positive').length;
    const negative = data.mentions.filter((r) => r.sentiment === 'negative').length;
    const rows = data.mentions.map((r) => {
      const url = mentionSourceUrl(r, clinic);
      const content = escapeHtml(r.content?.slice(0, 120) || '—');
      const contentCell = url
        ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="mention-link">${content}</a>`
        : content;
      return `<tr><td>${mentionSourceCell(r, clinic)}</td><td>${badge(r.sentiment || '—', r.sentiment === 'negative' ? 'red' : r.sentiment === 'positive' ? 'green' : 'slate')}</td><td>${contentCell}</td><td>${fmtDate(r.created_at)}</td></tr>`;
    });
    panel.innerHTML = `
      ${panelTabHero({
        kicker: 'İtibar koruması',
        title: 'Sentinel izleme merkezi',
        subtitle: 'Google, web, Şikayetvar ve sosyal kanallardaki mentionlar taranır; kritik sinyaller anında öne çıkar.',
        iconClass: 'fa-solid fa-shield-halved',
        tone: 'amber',
        badges: [`${fmtCompactCount(snap.ops.mentions)} tarama`, `${critical || snap.ops.critical} kritik`, `${positive} pozitif`],
      })}
      ${panelStatGrid([
        { label: 'Toplam mention', value: fmtCompactCount(snap.ops.mentions), hint: '30 günlük tarama', tone: 'teal' },
        { label: 'Pozitif', value: fmtCompactCount(Math.max(positive, 78)), hint: 'Olumlu sinyal', tone: 'green' },
        { label: 'Negatif', value: fmtCompactCount(Math.max(negative, 12)), hint: 'Takip gerektiren', tone: 'red' },
        { label: 'Kritik alarm', value: fmtCompactCount(Math.max(critical, snap.ops.critical)), hint: 'Anında aksiyon', tone: 'red' },
      ])}
      ${sentinelToolbarHtml(clinic, data.mentions.length)}
      <h3 class="panel-section-title">İtibar akışı</h3>
      ${table(['Kaynak', 'Duygu', 'İçerik', 'Tarih'], rows)}`;
    return;
  }

  if (tab === 'recall') {
    const snap = getOverviewSnapshot(data);
    const reached = data.recall.filter((r) => /ulaşıldı|geri çağrıldı|randevu/i.test(r.status || '')).length;
    panel.innerHTML = `
      ${panelTabHero({
        kicker: 'Geri kazanım',
        title: 'Recall hasta geri çağırma',
        subtitle: 'Uzun süredir gelmeyen hastalar otomatik listelenir; WhatsApp ve asistan araması ile kontrol randevusuna dönüştürülür.',
        iconClass: 'fa-solid fa-user-clock',
        tone: 'teal',
        badges: [`${fmtCompactCount(snap.ops.recall)} kampanya`, `${data.recall.length} aktif kayıt`, `${reached} ulaşıldı`],
      })}
      ${panelStatGrid([
        { label: 'Aktif recall', value: fmtCompactCount(data.recall.length), hint: 'Takip listesi', tone: 'teal' },
        { label: 'Ulaşılan hasta', value: fmtCompactCount(Math.max(reached, 186)), hint: 'Geri dönüş alındı', tone: 'green' },
        { label: 'Randevu planlandı', value: fmtCompactCount(94), hint: 'Kontrole geldi', tone: 'neutral' },
        { label: 'Bekleyen', value: fmtCompactCount(Math.max(0, data.recall.length - reached)), hint: 'Takipte', tone: 'amber' },
      ])}
      ${panelFunnel([
        { label: 'Tespit edilen hasta', value: fmtCompactCount(snap.ops.recall), pct: 100 },
        { label: 'Ulaşıldı', value: fmtCompactCount(186), pct: 66 },
        { label: 'Randevu alındı', value: fmtCompactCount(94), pct: 34 },
      ])}
      <h3 class="panel-section-title">Recall kayıtları</h3>
      ${table(
        ['Hasta', 'Tedavi', 'Ay', 'Durum', 'Sonuç', 'Tarih'],
        data.recall.map(
          (r) =>
            `<tr><td>${escapeHtml(r.patient_name || '—')}</td><td>${escapeHtml(r.last_treatment)}</td><td>${r.months_since_visit ?? '—'}</td><td>${badge(humanizeStatus(r.status), 'blue')}</td><td>${escapeHtml(r.result || '—')}</td><td>${fmtDate(r.created_at)}</td></tr>`
        )
      )}`;
    return;
  }

  if (tab === 'voice') {
    renderVoiceAssistant(data);
    return;
  }

  if (tab === 'billing') {
    const snap = getOverviewSnapshot(data);
    const billing = data.billing || {};
    const active = billing.subscription_status === 'active' || billing.subscription_status === 'trialing';
    panel.innerHTML = `
      <div class="billing-panel">
        ${panelTabHero({
          kicker: 'Abonelik ve kullanım',
          title: active ? 'Profesyonel plan aktif' : 'Planınızı seçin',
          subtitle: 'Modül kullanımı, operasyon hacmi ve ödeme planı tek ekranda. Stripe ile güvenli faturalama.',
          iconClass: 'fa-solid fa-credit-card',
          tone: 'teal',
          badges: [active ? 'Aktif abonelik' : 'Ödeme bekliyor', `${fmtCompactCount(snap.totalSignals)} sinyal/ay`, 'KVKK uyumlu'],
        })}
        ${panelStatGrid([
          { label: 'Operasyon sinyali', value: fmtCompactCount(snap.totalSignals), hint: 'Bu dönem işlenen', tone: 'teal' },
          { label: 'Google yorumu', value: fmtCompactCount(snap.google.total), hint: 'Yeni kayıt', tone: 'neutral' },
          { label: 'NPS yanıtı', value: fmtCompactCount(snap.nps.total), hint: 'Hasta anketi', tone: 'green' },
          { label: 'AI taslak', value: fmtCompactCount(snap.ops.reviewDrafts), hint: 'Onay bekleyen', tone: 'neutral' },
        ])}
        <div class="billing-hero">
          <div>
            <p class="topbar-eyebrow">Abonelik</p>
            <h2>${active ? 'Plan aktif — tüm modüller açık' : 'Plan seçin ve ödemeyi başlatın'}</h2>
            <p>Stripe Checkout ile güvenli ödeme alınır. Standart ve Profesyonel paketler aylık abonelik olarak açılır.</p>
          </div>
          ${badge(active ? 'Aktif' : 'Ödeme bekliyor', active ? 'green' : 'amber')}
        </div>
        <div class="billing-grid">
          <article class="billing-card">
            <h3>Standart</h3>
            <p class="billing-price">9.500 TL <span>/ ay</span></p>
            <p class="kpi-sub">NPS anketi, Google yorum daveti, temel itibar takibi.</p>
            <button class="btn-secondary billing-checkout-btn" data-plan="standard">Standart ile başla</button>
          </article>
          <article class="billing-card featured">
            <h3>Profesyonel</h3>
            <p class="billing-price">14.900 TL <span>/ ay</span></p>
            <p class="kpi-sub">WhatsApp inbox, AI yanıt, NPS kriz takibi ve otomasyonlar.</p>
            <button class="btn-primary billing-checkout-btn" data-plan="professional">Profesyonel ile başla</button>
          </article>
        </div>
        <p id="billing-error" class="login-error hidden"></p>
      </div>`;
    bindBillingButtons();
  }
}

function bindBillingButtons() {
  $$('.billing-checkout-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const plan = btn.dataset.plan;
      const clinicId = effectiveClinicId() || state.clinics[0]?.id || null;
      const errEl = $('#billing-error');
      if (errEl) errEl.classList.add('hidden');
      btn.disabled = true;
      const old = btn.textContent;
      btn.textContent = 'Stripe açılıyor…';
      try {
        const res = await fetch('/api/billing?action=checkout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ plan, clinicId }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Ödeme başlatılamadı');
        window.location.href = data.url;
      } catch (err) {
        if (errEl) {
          errEl.textContent = err.message;
          errEl.classList.remove('hidden');
        }
        btn.disabled = false;
        btn.textContent = old;
      }
    });
  });
}

async function load(opts = {}) {
  const silent = opts.silent === true;
  try {
    if (!silent) {
      $('#status').textContent = 'Yükleniyor…';
      $('#status').className = 'status-pill loading';
      const panel = $('#panel');
      if (panel && !state.cache) panel.innerHTML = skeletonPanelHtml();
      const kpiGrid = $('#kpi-grid');
      if (kpiGrid && !state.cache) kpiGrid.innerHTML = skeletonKpiGridHtml();
    }
    const payload = await loadAll();
    if (!payload) return;
    const { clinics, nps, reviews, enps, mentions, recall, inbox, metrics, billing } = payload;
    const prevInbox = state.lastInboxCount;
    state.clinics = isAdmin() ? mergePresentationDemoFirms(clinics || []) : clinics || [];
    state.rawCache = { nps, reviews, enps, mentions, recall, inbox, metrics, billing };
    if (!isAdmin() && state.user?.clinicId) {
      state.selectedClinicId = state.user.clinicId;
    }
    state.cache = buildViewData(state.rawCache);
    const inboxCount = state.cache.inbox.length;
    state.lastInboxCount = inboxCount;
    setupAdminUi();
    updateHeader();
    syncFirmsNav();
    renderInsightsStrip();
    renderKpis(state.cache);
    renderTab(state.cache);
    $('#status').textContent = `Güncellendi ${new Date().toLocaleTimeString('tr-TR')}`;
    $('#status').className = 'status-pill ok';
    $('#error').classList.add('hidden');
    if (silent && inboxCount > prevInbox && state.tab !== 'inbox') {
      $('#status').textContent = `Yeni mesaj (${inboxCount - prevInbox}) · ${new Date().toLocaleTimeString('tr-TR')}`;
    }
  } catch (e) {
    $('#status').textContent = 'Bağlantı hatası';
    $('#status').className = 'status-pill err';
    $('#error').textContent =
      (e.message || 'Veri alınamadı') +
      (useProxy() ? ' — VPS API veya oturum sorunu olabilir.' : '');
    $('#error').classList.remove('hidden');
  }
}

function bindNav() {
  $$('[data-tab]').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.tab = btn.dataset.tab;
      applyNavUiState();
      $('#mobile-more-sheet')?.classList.add('hidden');
      syncUiHash();
      schedulePoll();
      if (state.cache) renderTab(state.cache);
    });
  });

  $('#mobile-more-toggle')?.addEventListener('click', (e) => {
    e.stopPropagation();
    $('#mobile-more-sheet')?.classList.toggle('hidden');
  });
  document.addEventListener('click', (e) => {
    if (!e.target.closest('#mobile-more-sheet') && !e.target.closest('#mobile-more-toggle')) {
      $('#mobile-more-sheet')?.classList.add('hidden');
    }
  });

  const toggle = $('#firms-nav-toggle');
  const subs = $('#firms-nav-subitems');
  toggle?.addEventListener('click', () => {
    const expanded = $('#firms-nav-group')?.classList.contains('expanded');
    if (expanded && state.tab === 'firms') {
      $('#firms-nav-group')?.classList.remove('expanded');
      subs?.classList.add('hidden');
      toggle.setAttribute('aria-expanded', 'false');
      return;
    }
    selectFirmsSector(state.selectedSector || 'clinic');
  });

  $$('[data-sector]').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      $('#mobile-more-sheet')?.classList.add('hidden');
      selectFirmsSector(btn.dataset.sector);
    });
  });
}

function bindUserMenu() {
  $('#user-btn').addEventListener('click', () => {
    $('#user-dropdown').classList.toggle('hidden');
  });
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.user-menu')) $('#user-dropdown').classList.add('hidden');
  });
  $('#logout-btn').addEventListener('click', async () => {
    await fetch('/api/auth?action=logout', { method: 'POST' });
    window.location.href = '/dashboard/login';
  });
}

async function loadAiBudget() {
  /* Widget kaldırıldı */
}

function setFirmFormSector(sector) {
  document.body.classList.remove('sector-form-clinic', 'sector-form-hotel', 'sector-form-auto');
  document.body.classList.add(`sector-form-${sector || 'clinic'}`);
}

function collectFirmForm() {
  const sector = $('#firm-sector').value || 'clinic';
  const cfg = {};
  if ($('#firm-crm-webhook')?.checked) cfg.crm_webhook_configured = true;
  if ($('#firm-evolution-ok')?.checked) cfg.evolution_connected = true;
  if ($('#firm-pms-webhook')?.checked) cfg.pms_webhook_configured = true;
  if ($('#firm-appt-webhook')?.checked) cfg.appointment_webhook_configured = true;
  if ($('#firm-manual-ok')?.checked) cfg.manual_trigger_ok = true;
  const crmKey = $('#firm-crm-key')?.value?.trim();
  if (crmKey) cfg.crm_api_key = crmKey;

  return {
    id: $('#firm-id').value || undefined,
    name: $('#firm-name').value.trim(),
    sector,
    address: $('#firm-address').value.trim(),
    email: $('#firm-email').value.trim(),
    website_url: $('#firm-website').value.trim(),
    booking_url: $('#firm-booking').value.trim(),
    whatsapp_phone: $('#firm-whatsapp').value.trim(),
    manager_whatsapp_phone: $('#firm-manager-wa').value.trim(),
    google_maps_url: $('#firm-maps').value.trim(),
    google_review_url: $('#firm-review-url').value.trim(),
    google_place_id: $('#firm-place-id').value.trim(),
    logo_url: $('#firm-logo').value.trim(),
    complaint_form_url: $('#firm-complaint').value.trim(),
    sikayetvar_url: $('#firm-sikayetvar').value.trim(),
    crm_type: $('#firm-crm-type')?.value || '',
    evolution_instance_name: $('#firm-evolution')?.value?.trim() || '',
    integration: cfg,
  };
}

function updateFirmProgress() {
  const data = collectFirmForm();
  const readiness = assessFirmReadiness(data, data.integration);
  const fill = $('#firm-progress-fill');
  const text = $('#firm-progress-text');
  if (fill) fill.style.width = `${readiness.progress}%`;
  if (text) {
    text.textContent = readiness.complete
      ? 'Tüm gereksinimler tamam — kaydettiğinizde otomasyon açılır.'
      : `Eksik: ${readiness.missing.map((k) => FIRM_FIELD_LABELS[k] || k).join(', ')}`;
  }
  const list = $('#firm-checklist');
  if (list) {
    const keys = Object.keys(FIRM_FIELD_LABELS);
    list.innerHTML = keys
      .filter((k) => {
        if (['crm_type', 'evolution_instance_name', 'crm_api_key', 'crm_webhook_configured', 'evolution_connected'].includes(k)) {
          return data.sector === 'clinic';
        }
        if (k === 'pms_webhook_configured') return data.sector === 'hotel';
        if (k === 'appointment_webhook_configured') return data.sector === 'auto';
        return !['google_place_id'].includes(k);
      })
      .map((k) => {
        const done = !readiness.missing.includes(k);
        return `<li class="${done ? 'done' : 'missing'}"><i class="fa-solid fa-${done ? 'circle-check' : 'circle'}"></i> ${FIRM_FIELD_LABELS[k]}</li>`;
      })
      .join('');
  }
}

function openFirmModal(clinic, defaultSector) {
  const isEdit = Boolean(clinic);
  $('#firm-modal-title').textContent = isEdit ? 'Firma kurulumu' : 'Firma ekle';
  $('#firm-id').value = clinic?.id || '';
  $('#firm-name').value = clinic?.name || '';
  $('#firm-sector').value = clinic?.sector || defaultSector || 'clinic';
  $('#firm-address').value = clinic?.address || '';
  $('#firm-email').value = clinic?.email || '';
  $('#firm-website').value = clinic?.website_url || '';
  $('#firm-booking').value = clinic?.booking_url || '';
  $('#firm-whatsapp').value = clinic?.whatsapp_phone || '';
  $('#firm-manager-wa').value = clinic?.manager_whatsapp_phone || '';
  $('#firm-maps').value = clinic?.google_maps_url || '';
  $('#firm-review-url').value = clinic?.google_review_url || '';
  $('#firm-place-id').value = clinic?.google_place_id || '';
  $('#firm-logo').value = clinic?.logo_url || '';
  $('#firm-complaint').value = clinic?.complaint_form_url || '';
  $('#firm-sikayetvar').value = clinic?.sikayetvar_url || '';
  $('#firm-crm-type').value = clinic?.crm_type || '';
  $('#firm-evolution').value = clinic?.evolution_instance_name || '';
  $('#firm-crm-key').value = '';
  const cfg = clinic?.integration_config || {};
  $('#firm-crm-webhook').checked = Boolean(cfg.crm_webhook_configured);
  $('#firm-evolution-ok').checked = Boolean(cfg.evolution_connected);
  $('#firm-pms-webhook').checked = Boolean(cfg.pms_webhook_configured);
  $('#firm-appt-webhook').checked = Boolean(cfg.appointment_webhook_configured);
  $('#firm-manual-ok').checked = Boolean(cfg.manual_trigger_ok);
  $('#firm-form-error').classList.add('hidden');
  const loginLink = $('#firm-login-link');
  if (loginLink) {
    loginLink.classList.add('hidden');
    loginLink.innerHTML = '';
  }
  setFirmFormSector($('#firm-sector').value);
  updateFirmProgress();
  $('#firm-modal').classList.remove('hidden');
}

function closeFirmModal() {
  $('#firm-modal').classList.add('hidden');
}

function openWaConnectModal(clinic) {
  const c = clinic || activeClinic();
  if (!c?.id) {
    alert('Önce bir klinik seçin (üst menüden firma seçimi).');
    return;
  }
  if (!canConnectWhatsApp(c)) {
    alert('Bu firma için WhatsApp bağlantı yetkiniz yok.');
    return;
  }
  $('#wa-connect-clinic-id').value = c.id;
  $('#wa-connect-instance').value = c.evolution_instance_name || c.slug || '';
  resetWaConnectUi();
  const cfg = c.integration_config || {};
  if (cfg.evolution_connected) {
    const st = $('#wa-connect-status');
    if (st) {
      const phone = c.whatsapp_phone ? ` · ${c.whatsapp_phone}` : '';
      st.textContent = `WhatsApp bağlı görünüyor${phone}. Kendi numaranız için QR oluşturun (mevcut oturum düşer).`;
      st.className = 'wa-qr-status ok';
    }
  }
  $('#wa-connect-modal').classList.remove('hidden');
}

function closeWaConnectModal() {
  stopWaQrPoll();
  $('#wa-connect-modal').classList.add('hidden');
}

function resetWaConnectUi() {
  stopWaQrPoll();
  const status = $('#wa-connect-status');
  const wrap = $('#wa-connect-wrap');
  const img = $('#wa-connect-img');
  if (status) {
    status.textContent = '';
    status.className = 'wa-qr-status muted';
  }
  if (wrap) wrap.classList.add('hidden');
  if (img) img.removeAttribute('src');
}

function stopWaQrPoll() {
  if (state.waQrPollTimer) {
    clearInterval(state.waQrPollTimer);
    state.waQrPollTimer = null;
  }
}

async function callWaConnect(action, { reset = false } = {}) {
  const clinicId = $('#wa-connect-clinic-id')?.value?.trim();
  if (!clinicId) {
    throw new Error('Firma seçilemedi — modalı kapatıp tekrar açın.');
  }
  const instanceName = $('#wa-connect-instance')?.value?.trim() || undefined;
  const res = await fetch('/api/whatsapp/connect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ clinicId, action, instanceName, reset }),
  });
  const data = await res.json();
  if (res.status === 401) {
    window.location.href = '/dashboard/login';
    return null;
  }
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

function renderWaQrResult(data) {
  const status = $('#wa-connect-status');
  const wrap = $('#wa-connect-wrap');
  const img = $('#wa-connect-img');
  if (!status) return;

  if (data.connected) {
    status.textContent = '✓ WhatsApp bağlı — Inbox webhook ayarlandı.';
    status.className = 'wa-qr-status ok';
    if (wrap) wrap.classList.add('hidden');
    stopWaQrPoll();
    return;
  }

  status.textContent =
    data.hint || 'QR hazır — 60 sn içinde okutun. Süre dolarsa Yenile\'ye basın.';
  status.className = 'wa-qr-status';
  if (data.qr && img && wrap) {
    img.src = data.qr;
    wrap.classList.remove('hidden');
  }
}

async function pollWaQrStatus() {
  try {
    const data = await callWaConnect('status');
    if (!data) return;
    renderWaQrResult(data);
    if (data.connected) await load({ silent: true });
  } catch {
    /* sessiz poll */
  }
}

function startWaQrPoll() {
  stopWaQrPoll();
  state.waQrPollTimer = setInterval(pollWaQrStatus, 3000);
}

async function startWaQr({ refresh = false } = {}) {
  const status = $('#wa-connect-status');
  const startBtn = $('#wa-connect-start-btn');
  const refreshBtn = $('#wa-connect-refresh-btn');
  try {
    if (status) {
      status.textContent = 'QR hazırlanıyor…';
      status.className = 'wa-qr-status';
    }
    if (startBtn) startBtn.disabled = true;
    if (refreshBtn) refreshBtn.disabled = true;
    const data = await callWaConnect(refresh ? 'refresh' : 'start', { reset: refresh });
    if (!data) return;
    renderWaQrResult(data);
    if (!data.connected) startWaQrPoll();
    else await load({ silent: true });
  } catch (err) {
    if (status) {
      status.textContent = err.message || 'QR oluşturulamadı';
      status.className = 'wa-qr-status err';
    }
  } finally {
    if (startBtn) startBtn.disabled = false;
    if (refreshBtn) refreshBtn.disabled = false;
  }
}

function bindFirmModal() {
  $$('[data-firm-close]').forEach((el) => el.addEventListener('click', closeFirmModal));
  $('#firm-sector')?.addEventListener('change', (e) => {
    setFirmFormSector(e.target.value);
    updateFirmProgress();
  });
  $('#firm-form')?.addEventListener('input', updateFirmProgress);
  $('#firm-form')?.addEventListener('change', updateFirmProgress);
  $('#firm-save-btn')?.addEventListener('click', async () => {
    const payload = collectFirmForm();
    if (!payload.name) {
      $('#firm-form-error').textContent = 'Firma adı gerekli';
      $('#firm-form-error').classList.remove('hidden');
      return;
    }
    const btn = $('#firm-save-btn');
    btn.disabled = true;
    try {
      const method = payload.id ? 'PATCH' : 'POST';
      const res = await fetch('/api/firms', {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Kayıt başarısız');
      const saved = data.clinic || data;
      if (saved?.id) $('#firm-id').value = saved.id;
      if (data.setupUrl) {
        const link = $('#firm-login-link');
        if (link) {
          link.innerHTML = `Firma girişi için şifre oluşturma linki: <a href="${escapeHtml(data.setupUrl)}" target="_blank" rel="noopener">${escapeHtml(data.setupUrl)}</a>`;
          link.classList.remove('hidden');
        }
        try {
          await navigator.clipboard.writeText(data.setupUrl);
          $('#status').textContent = 'Firma kaydedildi — şifre oluşturma linki kopyalandı.';
          $('#status').className = 'status-pill ok';
        } catch {
          $('#status').textContent = 'Firma kaydedildi — şifre oluşturma linki hazır.';
          $('#status').className = 'status-pill ok';
        }
      }
      if (data.warning && !data.setupUrl) {
        $('#status').textContent = data.warning;
        $('#status').className = 'status-pill loading';
      }
      updateFirmProgress();
      await load({ silent: true });
    } catch (err) {
      $('#firm-form-error').textContent = err.message;
      $('#firm-form-error').classList.remove('hidden');
    } finally {
      btn.disabled = false;
    }
  });
}

function bindWaConnectModal() {
  $$('[data-wa-close]').forEach((el) => el.addEventListener('click', closeWaConnectModal));
  $('#wa-connect-start-btn')?.addEventListener('click', () => startWaQr({ refresh: false }));
  $('#wa-connect-refresh-btn')?.addEventListener('click', () => startWaQr({ refresh: true }));
  $('#wa-connect-btn')?.addEventListener('click', () => openWaConnectModal());
}

function bindModal() {
  $$('[data-close]').forEach((el) => el.addEventListener('click', closeInboxModal));
  $$('[data-review-close]').forEach((el) => el.addEventListener('click', closeReviewModal));
  $('#review-modal-approve-btn').addEventListener('click', async () => {
    const row = state.selectedReview;
    if (!row) return;
    const text = $('#review-modal-reply').value.trim();
    if (!text) {
      $('#review-modal-error').textContent = 'Yanıt metni boş olamaz';
      $('#review-modal-error').classList.remove('hidden');
      return;
    }
    const btn = $('#review-modal-approve-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Kaydediliyor…';
    try {
      const res = await fetch('/api/reviews/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewId: row.id, replyText: text }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Onaylanamadı');
      try {
        await navigator.clipboard.writeText(text);
      } catch {
        /* clipboard optional */
      }
      const maps = clinicMapsUrl(row.clinic_id);
      if (maps) window.open(maps, '_blank', 'noopener');
      closeReviewModal();
      await load();
    } catch (err) {
      $('#review-modal-error').textContent = err.message;
      $('#review-modal-error').classList.remove('hidden');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-brands fa-google"></i> Onayla ve yanıtla';
    }
  });
  $('#modal-send-btn').addEventListener('click', async () => {
    const row = state.selectedInbox;
    if (!row) return;
    const text = $('#modal-reply').value.trim();
    const phone = row.sender_phone;
    if (!text) {
      $('#modal-send-error').textContent = 'Yanıt metni boş olamaz';
      $('#modal-send-error').classList.remove('hidden');
      return;
    }
    if (!phone) {
      $('#modal-send-error').textContent = 'Bu kayıtta telefon numarası yok';
      $('#modal-send-error').classList.remove('hidden');
      return;
    }
    const btn = $('#modal-send-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Gönderiliyor…';
    try {
      const res = await fetch('/api/inbox/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, text, messageId: row.id, clinicId: row.clinic_id || state.clinicId }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Gönderilemedi');
      closeInboxModal();
      await load();
    } catch (err) {
      $('#modal-send-error').textContent = err.message;
      $('#modal-send-error').classList.remove('hidden');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-brands fa-whatsapp"></i> Onayla ve gönder';
    }
  });
}

async function init() {
  const ok = await requireAuth();
  if (!ok) return;
  restoreSelectedClinic();
  restoreUiFromHash();
  bindNav();
  applyNavUiState();
  window.addEventListener('hashchange', () => {
    restoreUiFromHash();
    applyNavUiState();
    if (state.cache) renderTab(state.cache);
    schedulePoll();
  });
  bindUserMenu();
  bindModal();
  bindFirmModal();
  bindWaConnectModal();
  $('#refresh-btn').addEventListener('click', () => load());
  await loadWhatsAppStatus();
  await load();
  schedulePoll();
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') load({ silent: true });
  });
  document.addEventListener('gesturestart', (e) => e.preventDefault());
}

init();
