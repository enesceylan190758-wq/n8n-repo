/* Nefalix Hasta CRM — Supabase clinic-* API + cookie oturum */
(function () {
  if (window.Nefalix) return;

  const LS = window.localStorage;
  const API = '/api/blog';
  const K = { auth: 'nfx_auth', lastRoute: 'nfx_last_route', seq: 'nfx_seq' };

  let _boot = null;
  let _contacts = [];
  let _dynamic = [];
  let _randevu = [];
  let _teklif = [];
  let _payments = [];
  let _notes = {};
  let _readyPromise = null;
  let _seed = { danisan: [], dinamik: [], kasa: [], bakiye: [] };

  function lsGet(k, d) { try { const v = JSON.parse(LS.getItem(k)); return v == null ? d : v; } catch (e) { return d; } }
  function lsSet(k, v) { try { LS.setItem(k, JSON.stringify(v)); } catch (e) {} }

  const USERS = [
    { id: 'abdulkadir', name: 'Abdülkadir Yaşar', initials: 'AY', role: 'Yönetici', email: 'akadir@nefalix.com' },
    { id: 'enes', name: 'Enes Ceylan', initials: 'EC', role: 'CTO · Saha', email: 'enes@nefalix.com' },
    { id: 'kader', name: 'Kader Hanım', initials: 'KH', role: 'Arama & Randevu', email: 'kader@nefalix.com' },
    { id: 'demo', name: 'Demo Kullanıcı', initials: 'DK', role: 'Temsilci', email: 'demo@nefalix.com' }
  ];

  function sessionFromKod(kod) {
    const k = String(kod || '').toLowerCase();
    let u = USERS.find(x => x.id === k);
    if (!u && k.indexOf('abd') >= 0) u = USERS.find(x => x.id === 'abdulkadir');
    if (!u && k.indexOf('enes') >= 0) u = USERS.find(x => x.id === 'enes');
    if (!u && k.indexOf('kader') >= 0) u = USERS.find(x => x.id === 'kader');
    if (!u) return null;
    return { id: u.id, name: u.name, initials: u.initials, role: u.role, email: u.email, ts: Date.now() };
  }

  function apiCall(action, method, body, query) {
    let url = API + '?action=' + encodeURIComponent(action);
    if (query) url += '&' + query;
    return fetch(url, {
      method: method || 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: body != null ? JSON.stringify(body) : undefined
    }).then(r => r.json().catch(() => ({})));
  }

  function segLabel(code) {
    if (!_boot || !code) return code || '';
    const s = (_boot.segments || []).find(x => x.code === code);
    return s ? s.label : code;
  }

  function userName(id) {
    if (!_boot || !id) return '';
    const u = (_boot.users || []).find(x => x.id === id);
    return u ? u.ad : '';
  }

  function segCodeFromLabel(label) {
    const l = String(label || '').trim().toLowerCase();
    const s = (_boot.segments || []).find(x => String(x.label || '').trim().toLowerCase() === l);
    return s ? s.code : null;
  }

  function isoToTr(iso) {
    if (!iso) return '';
    const d = new Date(iso);
    if (isNaN(d)) return String(iso).slice(0, 10);
    return fmt(d, false);
  }

  function mapContact(c) {
    return {
      _id: c.id,
      'ID': c.id,
      'Danışan ID': c.file_no || c.id.slice(0, 8),
      'Dosya no': c.file_no || '',
      'Ad': c.ad || '',
      'Telefon': c.telefon || '',
      'Ülke': c.ulke || '',
      'E-Posta': c.email || '',
      'Segment': segLabel(c.segment_code),
      'Satış temsilcisi': userName(c.assigned_to),
      'Referans kaynağı': c.kaynak || '',
      'Danışan tipi': c.stage === 'danisan' ? 'Aktif Hasta' : 'Potansiyel Hasta',
      'Kayıt tarihi': isoToTr(c.created_at),
      'Değişiklik tarihi': isoToTr(c.updated_at),
      'Facebook Kampanyası': c.kampanya || '',
      'Oluşturan': userName(c.created_by) || 'Sistem',
      _raw: c
    };
  }

  function mapDynamic(c) {
    const row = mapContact(c);
    row['Danışan'] = row['Ad'];
    row.nextCallDate = c.next_call_date || '';
    return row;
  }

  function mapAppt(a) {
    const start = a.start_at ? new Date(a.start_at) : new Date();
    const contact = a.contact || {};
    const durumMap = {
      beklemede: 'bekliyor',
      tamamlandi: 'geldi',
      geldi: 'geldi',
      iptal: 'iptal',
      ertelendi: 'ertelendi',
      gelmedi: 'gelmedi',
      onayli: 'onayli'
    };
    return {
      _id: a.id,
      danisanId: a.contact_id,
      ad: contact.ad || '',
      tel: contact.telefon || '',
      tarih: fmt(start, false),
      saat: String(start.getHours()).padStart(2, '0') + ':' + String(start.getMinutes()).padStart(2, '0'),
      tip: a.tip || '',
      oda: a.oda || '',
      doktor: a.personel || '',
      durum: durumMap[a.durum] || a.durum || 'bekliyor',
      notlar: a.not_text || ''
    };
  }

  function mapOffer(o) {
    const c = o.contact || {};
    const stMap = { taslak: 'beklemede', gonderildi: 'gonderildi', kabul: 'kabul', red: 'red', beklemede: 'beklemede' };
    return {
      _id: o.id,
      danisanId: o.contact_id,
      ad: c.ad || '',
      tel: c.telefon || '',
      ref: 'TKF-' + String(o.id || '').slice(0, 8),
      hizmet: o.title || '',
      tutar: Number(o.amount || 0),
      kur: o.currency || 'EUR',
      tarih: isoToTr(o.created_at),
      gecerlilik: '',
      durum: stMap[o.status] || o.status || 'beklemede',
      temsilci: o.temsilci || '',
      hotel: o.hotel || '',
      transfer: o.transfer || ''
    };
  }

  function mapPayment(p) {
    const c = p.contact || {};
    return {
      _id: p.id,
      'Danışan / Firma': c.ad || '',
      'Danışan': c.ad || '',
      'Ödeme tarihi': isoToTr(p.payment_date),
      'Tutar': Number(p.amount || 0),
      'Kur': p.currency || 'EUR',
      'Ödeme Yöntemi': p.method || '',
      'Bilgi': p.description || '',
      'Oluşturan': userName(p.created_by) || 'Sistem',
      'Kayıt tarihi': isoToTr(p.created_at)
    };
  }

  function refreshData() {
    return Promise.all([
      apiCall('clinic-leads', 'GET', null, 'stage=danisan&limit=300'),
      apiCall('clinic-leads', 'GET', null, 'stage=lead&limit=300'),
      apiCall('clinic-dynamic', 'GET'),
      apiCall('clinic-appointments', 'GET'),
      apiCall('clinic-offers', 'GET'),
      apiCall('clinic-payments', 'GET')
    ]).then(([dan, lead, dyn, appt, off, pay]) => {
      const all = [].concat((dan.contacts || []), (lead.contacts || []));
      _contacts = all.map(mapContact);
      _dynamic = (dyn.contacts || []).map(mapDynamic);
      _randevu = (appt.appointments || []).map(mapAppt);
      _teklif = (off.offers || []).map(mapOffer);
      _payments = (pay.payments || []).map(mapPayment);
      _seed = { danisan: _contacts, dinamik: _dynamic, kasa: _payments, bakiye: [] };
      return _seed;
    }).catch(err => {
      console.error('[Nefalix] API refresh failed', err);
      return _seed;
    });
  }

  function login(id, pw) {
    const kod = String(id || '').toLowerCase().trim();
    if (!kod) return null;
    let u = USERS.find(x => x.id === kod);
    if (!u && kod.indexOf('abd') >= 0) u = USERS.find(x => x.id === 'abdulkadir');
    if (!u && kod.indexOf('enes') >= 0) u = USERS.find(x => x.id === 'enes');
    if (!u && kod.indexOf('kader') >= 0) u = USERS.find(x => x.id === 'kader');
    if (!u) return null;
    if (pw != null && String(pw).length > 0 && kod !== 'demo' && String(pw) !== '1234' && String(pw) !== 'demo') return null;
    const sess = sessionFromKod(u.id);
    if (sess) { lsSet(K.auth, sess); lsSet('nfx_auth_id', u.id); }
    return sess;
  }

  function loginAsync(id, pw) {
    const sess = login(id, pw);
    if (!sess) return Promise.resolve(null);
    const kod = sess.id === 'demo' ? 'enes' : sess.id;
    return apiCall('clinic-login', 'POST', { kod }).then(() => sess).catch(() => sess);
  }

  function currentUser() {
    const sess = lsGet(K.auth, null);
    if (sess && sess.id) return sess;
    try {
      const id = LS.getItem('nfx_auth_id');
      if (id) {
        const rebuilt = sessionFromKod(id);
        if (rebuilt) { lsSet(K.auth, rebuilt); return rebuilt; }
      }
    } catch (e) {}
    return null;
  }

  function logout() {
    LS.removeItem(K.auth);
    LS.removeItem('nfx_auth_id');
    apiCall('clinic-logout', 'POST', {}).catch(() => {});
  }

  function restoreServerSession() {
    return apiCall('clinic-me', 'POST', {}).then(j => {
      if (!j || !j.ok || !j.kod) return currentUser();
      const sess = sessionFromKod(j.kod);
      if (sess) { lsSet(K.auth, sess); lsSet('nfx_auth_id', sess.id); }
      return sess || currentUser();
    }).catch(() => currentUser());
  }

  function saveLastRoute(route) {
    try {
      const h = String(route || location.hash || '').replace(/^#/, '');
      if (!h || h.indexOf('Login') === 0) return;
      const u = currentUser();
      lsSet(K.lastRoute, { route: h, userId: u && u.id, ts: Date.now() });
    } catch (e) {}
  }

  function getLastRoute() {
    try {
      const raw = LS.getItem(K.lastRoute);
      if (!raw) return '';
      const o = JSON.parse(raw);
      const route = typeof o === 'string' ? o : (o && o.route);
      return route && String(route).indexOf('Login') !== 0 ? String(route) : '';
    } catch (e) { return ''; }
  }

  function resumeRoute(fallback) { return getLastRoute() || fallback || 'Dashboard'; }

  function loadSeed() {
    if (_readyPromise) return _readyPromise;
    _readyPromise = restoreServerSession()
      .then(() => apiCall('clinic-bootstrap', 'GET'))
      .then(j => { if (j && j.ok) _boot = j; return refreshData(); })
      .catch(() => {
        if (window.__NFX_SEED) _seed = window.__NFX_SEED;
        return _seed;
      });
    return _readyPromise;
  }

  function readyLocal() { return Promise.resolve(_seed); }
  function syncInBackground() { loadSeed().catch(() => {}); }

  function isSingle() { return !!window.__NFX_SEED; }
  function _hashRoute() {
    const h = (location.hash || '').replace(/^#/, '');
    const qi = h.indexOf('?');
    return { page: qi >= 0 ? h.slice(0, qi) : h, query: qi >= 0 ? h.slice(qi + 1) : '' };
  }
  function nav(target) {
    const t = String(target || '').trim();
    if (!isSingle()) { location.href = t; return; }
    if (t.charAt(0) === '#') { location.hash = t; saveLastRoute(t); return; }
    const m = /^([^?#]*)(\?[^#]*)?/.exec(t);
    const name = ((m && m[1]) || t).replace(/\.dc\.html$/i, '').replace(/\.html$/i, '');
    location.hash = '#' + name + ((m && m[2]) ? m[2] : '');
    saveLastRoute(location.hash);
  }
  function param(name) {
    const q = isSingle() ? _hashRoute().query : location.search.replace(/^\?/, '');
    return new URLSearchParams(q).get(name);
  }
  function currentPage(fallback) {
    if (isSingle()) return _hashRoute().page || fallback || 'Dashboard';
    return (location.pathname.split('/').pop() || '').replace(/\.dc\.html$/i, '') || fallback || 'Dashboard';
  }

  function allDanisan() { return _contacts.slice(); }

  function getDanisan(opts) {
    opts = opts || {};
    let list = allDanisan();
    const q = (opts.q || '').toLowerCase().trim();
    if (q) list = list.filter(d => ['Ad', 'Telefon', 'Segment', 'Satış temsilcisi'].some(k => String(d[k] || '').toLowerCase().includes(q)));
    if (opts.tip) list = list.filter(d => (d['Danışan tipi'] || '') === opts.tip);
    if (opts.temsilci) list = list.filter(d => (d['Satış temsilcisi'] || '') === opts.temsilci);
    if (opts.segment) list = list.filter(d => (d['Segment'] || '') === opts.segment);
    const total = list.length;
    const page = opts.page || 1, size = opts.size || 30;
    return { rows: list.slice((page - 1) * size, page * size), total, page, size, pages: Math.max(1, Math.ceil(total / size)) };
  }

  function getDanisanById(id) { return allDanisan().find(d => d._id === id) || null; }
  function findIdByName(name) {
    if (!name) return null;
    const n = String(name).trim().toLowerCase();
    const d = allDanisan().find(x => String(x['Ad'] || '').trim().toLowerCase() === n);
    return d ? d._id : null;
  }
  function hrefForName(name) { const id = findIdByName(name); return id ? 'HastaKarti.dc.html?id=' + encodeURIComponent(id) : null; }

  function updateDanisan(id, patch) {
    const body = { id };
    if (patch['Ad'] != null) body.ad = patch['Ad'];
    if (patch['Telefon'] != null) body.telefon = patch['Telefon'];
    if (patch['Ülke'] != null) body.ulke = patch['Ülke'];
    if (patch['Referans kaynağı'] != null) body.kaynak = patch['Referans kaynağı'];
    const seg = patch['Segment'];
    const tasks = [];
    if (Object.keys(body).length > 1) tasks.push(apiCall('clinic-contact', 'POST', body));
    if (seg) {
      const code = segCodeFromLabel(seg);
      if (code) tasks.push(apiCall('clinic-note-save', 'POST', { contact_id: id, body: 'Segment: ' + seg, segment_code: code }));
    }
    return Promise.all(tasks).then(() => refreshData()).then(() => getDanisanById(id));
  }

  function addDanisan(obj) {
    return apiCall('clinic-leads', 'POST', {
      ad: obj['Ad'] || obj.ad || '',
      telefon: obj['Telefon'] || obj.telefon || '',
      ulke: obj['Ülke'] || obj.ulke || '',
      kaynak: obj['Referans kaynağı'] || obj.kaynak || ''
    }).then(j => refreshData().then(() => mapContact(j.contact || {})));
  }

  // Lead listesi: yalnızca yeni lead segmentleri (veya segmentsiz). Takiptekiler Danışan/Dinamik'te.
  const NEW_LEAD_LABELS = new Set(['yeni data', 'yeni lead', 'yeni gelen', 'yenı data', 'yenı lead', 'yenı gelen']);
  function isNewLeadSegment(label) {
    const s = String(label || '').trim().toLowerCase().replace(/\s+/g, ' ');
    return !s || NEW_LEAD_LABELS.has(s);
  }

  function getLeads(opts) {
    opts = opts || {};
    let list = allDanisan().filter(d => {
      if ((d['Danışan tipi'] || '') === 'Aktif Hasta') return false;
      return isNewLeadSegment(d['Segment']);
    });
    const q = (opts.q || '').toLowerCase().trim();
    if (q) list = list.filter(d => String(d['Ad'] || '').toLowerCase().includes(q) || String(d['Telefon'] || '').toLowerCase().includes(q));
    const total = list.length, page = opts.page || 1, size = opts.size || 30;
    return { rows: list.slice((page - 1) * size, page * size), total, page, size, pages: Math.max(1, Math.ceil(total / size)) };
  }

  function convertLead(id, temsilci) {
    const d = getDanisanById(id);
    const user = (_boot && _boot.users || []).find(u => u.ad === temsilci || u.kod === temsilci);
    const userId = user ? user.id : ((_boot && _boot.user) || {}).id;
    return apiCall('clinic-assign', 'POST', { contact_id: id, user_id: userId }).then(() => refreshData()).then(() => getDanisanById(id));
  }

  function salesSegments() {
    const list = allDanisan();
    const m = {};
    list.forEach(d => { const s = (d['Segment'] || '(Segmentsiz)').trim() || '(Segmentsiz)'; (m[s] = m[s] || []).push(d); });
    const keys = Object.keys(m).sort();
    const grand = list.length || 1;
    return keys.map(k => ({ key: k, count: m[k].length, pct: (m[k].length / grand * 100), items: m[k] }));
  }

  function getNotes(danisanId) { return _notes[danisanId] || []; }

  function getSegments() {
    return ((_boot && _boot.segments) || []).map(s => ({
      code: s.code,
      label: s.label,
      gun_offset: s.gun_offset,
      show_in_dynamic: s.show_in_dynamic
    }));
  }

  function addNote(danisanId, text, segmentLabel) {
    const body = { contact_id: danisanId, body: text || '(not)' };
    if (segmentLabel) {
      const code = segCodeFromLabel(segmentLabel);
      if (code) body.segment_code = code;
    }
    return apiCall('clinic-note-save', 'POST', body).then(j => {
      const note = { text: text, user: (currentUser() || {}).name || 'Sistem', ts: todayStr(true), segment: segmentLabel || '' };
      (_notes[danisanId] = _notes[danisanId] || []).unshift(note);
      return refreshData().then(() => _notes[danisanId]);
    });
  }

  function getDinamik() { return _dynamic.slice(); }
  function getDinamikDue() { return getDinamik(); }

  function setDinamikResult(id, result, notlar, gun) {
    const code = segCodeFromLabel(result);
    const body = notlar || 'Dinamik arama';
    return apiCall('clinic-note-save', 'POST', { contact_id: id, body, segment_code: code }).then(() => refreshData()).then(() => getDinamik().find(x => x._id === id));
  }

  function getKasa() { return _payments.slice(); }
  function addKasa(obj) {
    return apiCall('clinic-payments', 'POST', {
      contact_id: obj.danisanId || obj.contact_id || null,
      amount: obj['Tutar'] || obj.tutar,
      currency: obj['Kur'] || obj.kur || 'EUR',
      method: obj['Ödeme Yöntemi'] || obj.yontem || '',
      description: obj['Bilgi'] || obj.bilgi || obj['Not'] || '',
      payment_date: obj.payment_date || undefined
    }).then(() => refreshData());
  }
  function kasaTotals() {
    const t = { girisEUR: 0, cikisEUR: 0, girisTRY: 0, cikisTRY: 0 };
    getKasa().forEach(k => {
      const v = parseFloat(k['Tutar']) || 0;
      const kur = k['Kur'] || 'EUR';
      if (v >= 0) { if (kur === 'EUR') t.girisEUR += v; else t.girisTRY += v; }
      else { if (kur === 'EUR') t.cikisEUR += -v; else t.cikisTRY += -v; }
    });
    t.netEUR = t.girisEUR - t.cikisEUR; t.netTRY = t.girisTRY - t.cikisTRY;
    return t;
  }
  function getBakiye() {
    const m = {};
    getKasa().forEach(k => {
      const n = k['Danışan / Firma'] || k['Danışan'] || '';
      if (!n) return;
      m[n] = (m[n] || 0) + (parseFloat(k['Tutar']) || 0);
    });
    return Object.keys(m).map((ad, i) => ({ _id: 'bk-' + i, 'Danışan': ad, 'Tutar': m[ad], 'Kur': 'EUR', 'Segment': '-' }));
  }
  function getGelir() { return getKasa().filter(k => (parseFloat(k['Tutar']) || 0) >= 0); }
  function getGider() { return getKasa().filter(k => (parseFloat(k['Tutar']) || 0) < 0); }

  // Renkler Stella/Onat: geldi yeşil, gelmedi kırmızı, bekliyor sarı
  const RND_STATUS = [
    { key: 'bekliyor', label: 'Bekliyor', color: '#f59e0b' },
    { key: 'onayli', label: 'Onaylandı', color: '#2563eb' },
    { key: 'geldi', label: 'Geldi', color: '#16a34a' },
    { key: 'gelmedi', label: 'Gelmedi', color: '#ef4444' },
    { key: 'iptal', label: 'İptal', color: '#9ca3af' },
    { key: 'ertelendi', label: 'Ertelendi', color: '#8b5cf6' }
  ];
  const RND_TYPES = ['Kontrol', 'İşlem', 'Konsültasyon', 'Transfer'];

  function getRandevu() { return _randevu.slice(); }
  function addRandevu(obj) {
    const d = parseDate(obj.tarih) || new Date();
    const [hh, mm] = String(obj.saat || '09:00').split(':');
    d.setHours(+hh || 9, +mm || 0, 0, 0);
    return apiCall('clinic-appointments', 'POST', {
      contact_id: obj.danisanId,
      start_at: d.toISOString(),
      hizmet: obj.hizmet || obj.tip || '',
      personel: obj.doktor || '',
      oda: obj.oda || '',
      tip: obj.tip || '',
      durum: 'beklemede',
      not_text: obj.notlar || ''
    }).then(() => refreshData());
  }
  function setRandevuStatus(id, durum) {
    const rev = {
      bekliyor: 'beklemede',
      onayli: 'beklemede',
      geldi: 'tamamlandi',
      gelmedi: 'gelmedi',
      iptal: 'iptal',
      ertelendi: 'ertelendi'
    };
    return apiCall('clinic-appointments', 'POST', { id, durum: rev[durum] || durum }).then(() => refreshData());
  }

  const TEKLIF_STATUS = [
    { key: 'beklemede', label: 'Beklemede', color: '#f59e0b' },
    { key: 'gonderildi', label: 'Gönderildi', color: '#2563eb' },
    { key: 'kabul', label: 'Kabul Edildi', color: '#16a34a' },
    { key: 'red', label: 'Reddedildi', color: '#ef4444' }
  ];
  const HIZMETLER = ['İmplant Tedavisi', 'Zirkonyum Kaplama', 'Gülüş Tasarımı', 'Diş Beyazlatma', 'Ortodonti', 'Kanal Tedavisi', 'All-on-4', 'Lamina Veneer'];

  function getTeklif() { return _teklif.slice(); }
  function addTeklif(obj) {
    return apiCall('clinic-offers', 'POST', {
      contact_id: obj.danisanId,
      title: obj.hizmet || '',
      amount: obj.tutar,
      currency: obj.kur || 'EUR',
      hotel: obj.hotel || '',
      transfer: obj.transfer || '',
      temsilci: obj.temsilci || (currentUser() || {}).name
    }).then(() => refreshData());
  }
  function setTeklifStatus(id, durum) {
    const rev = { beklemede: 'taslak', gonderildi: 'gonderildi', kabul: 'kabul', red: 'red' };
    return apiCall('clinic-offers', 'POST', { id, status: rev[durum] || durum }).then(() => refreshData());
  }
  function teklifStatusMeta() { return TEKLIF_STATUS; }

  const DEFS = { personel: [], hizmet: [], paket: [], urun: [] };
  function getDefs(kind) { return (DEFS[kind] || []).slice(); }
  function addDef(kind, obj) { return obj; }
  function getDestek() { return []; }
  function addDestek(obj) { return obj; }
  function getFirma() { return []; }
  function addFirma(obj) { return obj; }
  function getGorevler() { return []; }
  function toggleGorev() {}
  function addGorev(obj) { return obj; }

  function patientHistory(id, name) {
    const nm = (name || '').trim().toLowerCase();
    const matchName = v => v && String(v).trim().toLowerCase() === nm;
    const randevular = getRandevu().filter(r => r.danisanId === id || matchName(r.ad));
    const teklifler = getTeklif().filter(t => t.danisanId === id || matchName(t.ad));
    const satislar = getKasa().filter(k => (parseFloat(k['Tutar']) || 0) >= 0 && matchName(k['Danışan / Firma'] || k['Danışan']));
    const bakiyeler = getBakiye().filter(b => matchName(b['Danışan']));
    let bakiyeTop = 0, bakiyeKur = 'EUR', satisTop = 0, satisKur = 'EUR';
    bakiyeler.forEach(b => { bakiyeTop += parseFloat(b['Tutar']) || 0; });
    satislar.forEach(s => { satisTop += parseFloat(s['Tutar']) || 0; if (s['Kur']) satisKur = s['Kur']; });
    // Notları arka planda çek — HastaKarti senkron obje bekler (Promise.slice kırığı)
    apiCall('clinic-contact', 'GET', null, 'id=' + encodeURIComponent(id)).then(j => {
      if (j && j.notes) {
        _notes[id] = (j.notes || []).map(n => ({
          text: n.body,
          user: userName(n.created_by) || 'Sistem',
          ts: isoToTr(n.created_at),
          segment: segLabel(n.segment_code)
        }));
      }
    }).catch(function () {});
    return { randevular, teklifler, satislar, bakiyeler, bakiyeTop, bakiyeKur, satisTop, satisKur };
  }

  function groupCount(list, field) {
    const m = {};
    list.forEach(d => { const k = (d[field] || '(Boş)').trim() || '(Boş)'; m[k] = (m[k] || 0) + 1; });
    return Object.entries(m).map(([k, v]) => ({ key: k, value: v })).sort((a, b) => b.value - a.value);
  }
  function monthTrend(list, field) {
    const m = {};
    list.forEach(d => { const dt = parseDate(d[field]); if (!dt) return; const key = dt.getFullYear() + '-' + String(dt.getMonth() + 1).padStart(2, '0'); m[key] = (m[key] || 0) + 1; });
    return Object.entries(m).map(([k, v]) => ({ key: k, value: v })).sort((a, b) => a.key < b.key ? -1 : 1);
  }
  function reports() {
    const d = allDanisan();
    return {
      total: d.length,
      bySegment: groupCount(d, 'Segment'),
      byTemsilci: groupCount(d, 'Satış temsilcisi'),
      byReferans: groupCount(d, 'Referans kaynağı'),
      byTip: groupCount(d, 'Danışan tipi'),
      byUlke: groupCount(d, 'Ülke'),
      byMonth: monthTrend(d, 'Kayıt tarihi')
    };
  }

  function parseDate(s) {
    if (!s) return null;
    const m = /^(\d{2})\.(\d{2})\.(\d{4})(?:\s+(\d{2}):(\d{2}))?/.exec(s);
    if (m) return new Date(+m[3], +m[2] - 1, +m[1], +(m[4] || 0), +(m[5] || 0));
    const d = new Date(s);
    return isNaN(d) ? null : d;
  }
  function fmt(d, withTime) {
    const p = x => String(x).padStart(2, '0');
    let s = p(d.getDate()) + '.' + p(d.getMonth() + 1) + '.' + d.getFullYear();
    if (withTime) s += ' ' + p(d.getHours()) + ':' + p(d.getMinutes());
    return s;
  }
  function todayStr(withTime) { return fmt(new Date(), withTime); }

  function _esc(v) { return String(v == null ? '' : v).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function _downloadBlob(blob, name) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name; document.body.appendChild(a); a.click();
    setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(url); }, 500);
  }
  function exportExcel(filename, headers, rows) {
    let h = '<html><body><table border="1"><tr>' + headers.map(x => '<th>' + _esc(x) + '</th>').join('') + '</tr>';
    rows.forEach(r => { h += '<tr>' + r.map(c => '<td>' + _esc(c) + '</td>').join('') + '</tr>'; });
    h += '</table></body></html>';
    _downloadBlob(new Blob(['\ufeff' + h], { type: 'application/vnd.ms-excel' }), (filename || 'nefalix') + '.xls');
  }
  function exportPDF(title, headers, rows) {
    const w = window.open('', '_blank');
    if (!w) return;
    let h = '<html><head><title>' + _esc(title) + '</title></head><body><h1>' + _esc(title) + '</h1><table border="1"><tr>';
    h += headers.map(x => '<th>' + _esc(x) + '</th>').join('') + '</tr>';
    rows.forEach(r => { h += '<tr>' + r.map(c => '<td>' + _esc(c) + '</td>').join('') + '</tr>'; });
    h += '</table></body></html>';
    w.document.write(h); w.document.close(); w.print();
  }

  const API_OUT = {
    ready: loadSeed,
    ensureSession: loadSeed,
    readyLocal,
    syncInBackground,
    USERS,
    login,
    loginAsync,
    currentUser,
    logout,
    restoreServerSession,
    saveLastRoute,
    getLastRoute,
    resumeRoute,
    requireAuth: () => { if (!currentUser()) { nav('Login.dc.html'); return false; } return true; },
    nav, param, currentPage, isSingle,
    getDanisan, getDanisanById, updateDanisan, addDanisan,
    findIdByName, hrefForName,
    getLeads, convertLead, salesSegments,
    getNotes, addNote, getSegments,
    getDinamik, getDinamikDue, setDinamikResult,
    getKasa, addKasa, kasaTotals, getBakiye, getGelir, getGider,
    getRandevu, addRandevu, setRandevuStatus, RND_STATUS, RND_TYPES,
    getTeklif, addTeklif, setTeklifStatus, teklifStatusMeta, HIZMETLER,
    getDefs, addDef, getDestek, addDestek,
    getFirma, addFirma, getGorevler, toggleGorev, addGorev,
    patientHistory,
    reports, parseDate, fmt, todayStr,
    exportExcel, exportPDF,
    refreshData,
    resetAll: () => { LS.removeItem(K.auth); LS.removeItem(K.lastRoute); }
  };

  window.Nefalix = API_OUT;

  document.addEventListener('click', function (e) {
    if (!isSingle()) return;
    const a = e.target && e.target.closest ? e.target.closest('a') : null;
    if (!a) return;
    const href = a.getAttribute('href') || '';
    if (/\.dc\.html(\?|#|$)/i.test(href)) { e.preventDefault(); nav(href); }
  }, true);
})();
