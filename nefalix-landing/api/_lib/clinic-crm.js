/**
 * Nefalix Klinik CRM (Stella mantığı) — clinic-* action'ları.
 * Veri: Supabase crm_users / crm_segments / crm_contacts / crm_contact_notes / crm_appointments
 * Çağıran: api/blog.js (Vercel Hobby tek function).
 */
import { createHmac, timingSafeEqual } from 'crypto';
import { sbRequest } from './supabase.js';
import { parseCookies } from './auth.js';

const COOKIE = 'nefalix_clinic';
const MAX_AGE = 60 * 60 * 24 * 90;

function secret() {
  return process.env.DASHBOARD_SESSION_SECRET || process.env.NEFALIX_INTERNAL_KEY || 'nefalix-clinic-local';
}

function signSession(user) {
  const payload = {
    id: user.id,
    kod: user.kod,
    ad: user.ad,
    rol: user.rol,
    exp: Date.now() + MAX_AGE * 1000,
  };
  const body = Buffer.from(JSON.stringify(payload)).toString('base64url');
  const sig = createHmac('sha256', secret()).update(body).digest('base64url');
  return `${body}.${sig}`;
}

function verifySession(token) {
  if (!token) return null;
  const [body, sig] = String(token).split('.');
  if (!body || !sig) return null;
  const expected = createHmac('sha256', secret()).update(body).digest('base64url');
  const a = Buffer.from(sig);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !timingSafeEqual(a, b)) return null;
  try {
    const payload = JSON.parse(Buffer.from(body, 'base64url').toString('utf8'));
    if (!payload.exp || payload.exp < Date.now()) return null;
    return payload;
  } catch {
    return null;
  }
}

function setCookie(res, token, maxAge = MAX_AGE) {
  const secure = process.env.VERCEL === '1' ? '; Secure' : '';
  res.setHeader('Set-Cookie', `${COOKIE}=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${maxAge}${secure}`);
}

function requireSession(req, res) {
  const user = verifySession(parseCookies(req)[COOKIE]);
  if (!user) {
    res.status(401).json({ error: 'Klinik CRM oturumu gerekli' });
    return null;
  }
  return user;
}

function jsonBody(req) {
  return typeof req.body === 'string' ? JSON.parse(req.body || '{}') : req.body || {};
}

/** Bugün (Europe/Istanbul) — YYYY-MM-DD */
function todayTR() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Istanbul' }).format(new Date());
}

function addDays(dateStr, days) {
  const d = new Date(`${dateStr}T12:00:00Z`);
  d.setUTCDate(d.getUTCDate() + Number(days || 0));
  return d.toISOString().slice(0, 10);
}

const CONTACT_COLS =
  'id,file_no,stage,status,ad,telefon,ulke,kaynak,kampanya,email,assigned_to,segment_code,next_call_date,dynamic_attempt_count,stella_customer_id,created_at,updated_at,created_by,updated_by';

const UNREACHABLE_SEGMENTS = new Set([
  'ulasilamadi_tekrar_aranacak',
  '5_kez_ulasilamadi',
  '10_kez_ulasilamadi',
]);

/* ─── Auth ─────────────────────────────────────────────── */

async function login(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST gerekli' });
  const kod = String(jsonBody(req).kod || '').trim().toLowerCase();
  if (!kod) return res.status(400).json({ error: 'Kullanıcı kodu gerekli' });
  const rows = await sbRequest('GET', 'crm_users', {
    query: `kod=eq.${encodeURIComponent(kod)}&aktif=eq.true&select=id,kod,ad,rol&limit=1`,
  });
  const user = Array.isArray(rows) ? rows[0] : null;
  if (!user) return res.status(401).json({ error: 'Kullanıcı adı hatalı' });
  setCookie(res, signSession(user));
  return res.status(200).json({ ok: true, user });
}

async function logout(_req, res) {
  setCookie(res, '', 0);
  return res.status(200).json({ ok: true });
}

async function me(req, res) {
  if (req.method !== 'POST' && req.method !== 'GET') return res.status(405).json({ error: 'GET/POST gerekli' });
  const session = verifySession(parseCookies(req)[COOKIE]);
  if (!session) return res.status(200).json({ ok: false });
  setCookie(res, signSession(session));
  return res.status(200).json({ ok: true, kod: session.kod, id: session.id, ad: session.ad, rol: session.rol });
}

async function sbGetOrEmpty(table, query) {
  try {
    const rows = await sbRequest('GET', table, { query });
    return Array.isArray(rows) ? rows : [];
  } catch {
    return [];
  }
}

/** Oturum + segment kataloğu + kullanıcı listesi — UI açılışında tek çağrı */
async function bootstrap(req, res) {
  const session = requireSession(req, res);
  if (!session) return;
  const [segments, users, refs] = await Promise.all([
    sbGetOrEmpty('crm_segments', 'aktif=eq.true&select=code,label,show_in_dynamic,gun_offset,max_dynamic_attempts&order=sira.asc'),
    sbGetOrEmpty('crm_users', 'aktif=eq.true&select=id,kod,ad,rol&order=ad.asc'),
    sbGetOrEmpty('crm_reference_sources', 'aktif=eq.true&select=id,code,label&order=sira.asc'),
  ]);
  return res.status(200).json({ ok: true, user: session, segments, users, reference_sources: refs });
}

/* ─── Lead / kişi listeleri ────────────────────────────── */

async function leads(req, res) {
  const session = requireSession(req, res);
  if (!session) return;

  if (req.method === 'POST') {
    const b = jsonBody(req);
    const ad = String(b.ad || '').trim();
    if (!ad) return res.status(400).json({ error: 'Ad gerekli' });
    const row = {
      ad,
      telefon: String(b.telefon || '').trim(),
      ulke: String(b.ulke || '').trim(),
      email: String(b.email || '').trim(),
      kaynak: String(b.kaynak || '').trim(),
      kampanya: String(b.kampanya || '').trim(),
      stage: 'lead',
      // Lead listesi yalnızca yeni* segment — manuel kayıt da Stella ile hizalı
      segment_code: String(b.segment_code || 'yeni_lead').trim() || 'yeni_lead',
      created_by: session.id,
      updated_by: session.id,
    };
    if (!row.email) delete row.email;
    if (!row.kampanya) delete row.kampanya;
    const inserted = await sbRequest('POST', 'crm_contacts', {
      body: row,
      prefer: 'return=representation',
    });
    return res.status(200).json({ ok: true, contact: Array.isArray(inserted) ? inserted[0] : inserted });
  }

  const stage = String(req.query.stage || 'lead');
  const q = String(req.query.q || '').trim();
  // Hasta CRM: Stella ~7.5k — PostgREST max-rows genelde 1000; sayfalayarak topla
  const limit = Math.min(Math.max(Number(req.query.limit) || 100, 1), 10000);
  const pageSize = 1000;
  const all = [];
  for (let offset = 0; offset < limit; offset += pageSize) {
    const chunk = Math.min(pageSize, limit - offset);
    const parts = [
      `select=${CONTACT_COLS}`,
      'order=created_at.desc',
      `limit=${chunk}`,
      `offset=${offset}`,
    ];
    if (stage === 'lead' || stage === 'danisan') parts.push(`stage=eq.${stage}`);
    if (q) {
      const enc = encodeURIComponent(`%${q}%`);
      parts.push(`or=(ad.ilike.${enc},telefon.ilike.${enc})`);
    }
    const rows = await sbRequest('GET', 'crm_contacts', { query: parts.join('&') });
    const list = Array.isArray(rows) ? rows : [];
    all.push(...list);
    if (list.length < chunk) break;
  }
  return res.status(200).json({ ok: true, contacts: all });
}

async function assign(req, res) {
  const session = requireSession(req, res);
  if (!session) return;
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST gerekli' });
  const b = jsonBody(req);
  const contactId = String(b.contact_id || '');
  const userId = String(b.user_id || '');
  if (!contactId || !userId) return res.status(400).json({ error: 'contact_id ve user_id gerekli' });
  const updated = await sbRequest('PATCH', 'crm_contacts', {
    query: `id=eq.${encodeURIComponent(contactId)}&select=${CONTACT_COLS}`,
    body: {
      assigned_to: userId,
      stage: 'danisan',
      // Atanan kayıt temsilcinin bugünkü arama listesine düşer
      next_call_date: todayTR(),
      updated_by: session.id,
    },
    prefer: 'return=representation',
  });
  return res.status(200).json({ ok: true, contact: Array.isArray(updated) ? updated[0] : updated });
}

/* ─── Dinamik Arama ────────────────────────────────────── */

async function dynamicList(req, res) {
  const session = requireSession(req, res);
  if (!session) return;
  const today = todayTR();
  const pool = String(req.query.pool || '') === '1';
  const parts = [
    `select=${CONTACT_COLS}`,
    'status=eq.aktif',
    `next_call_date=lte.${today}`,
    'order=next_call_date.asc,updated_at.asc',
    'limit=300',
  ];
  if (pool) {
    parts.push('assigned_to=is.null');
  } else if (session.rol !== 'yonetici' || String(req.query.all || '') !== '1') {
    parts.push(`assigned_to=eq.${encodeURIComponent(session.id)}`);
  }
  const rows = await sbRequest('GET', 'crm_contacts', { query: parts.join('&') });
  return res.status(200).json({ ok: true, today, contacts: rows || [] });
}

/* ─── Not + segment ────────────────────────────────────── */

async function noteSave(req, res) {
  const session = requireSession(req, res);
  if (!session) return;
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST gerekli' });
  const b = jsonBody(req);
  const contactId = String(b.contact_id || '');
  const body = String(b.body || '').trim();
  const segmentCode = String(b.segment_code || '').trim();
  const noteDate = /^\d{4}-\d{2}-\d{2}$/.test(String(b.note_date || '')) ? b.note_date : null;
  if (!contactId || !body) return res.status(400).json({ error: 'contact_id ve not gerekli' });

  let segment = null;
  if (segmentCode) {
    const segRows = await sbRequest('GET', 'crm_segments', {
      query: `code=eq.${encodeURIComponent(segmentCode)}&select=code,label,show_in_dynamic,gun_offset,max_dynamic_attempts&limit=1`,
    });
    segment = Array.isArray(segRows) ? segRows[0] : null;
    if (!segment) return res.status(400).json({ error: 'Geçersiz segment' });
  }

  const existingRows = await sbRequest('GET', 'crm_contacts', {
    query: `id=eq.${encodeURIComponent(contactId)}&select=dynamic_attempt_count,segment_code&limit=1`,
  });
  const existing = Array.isArray(existingRows) ? existingRows[0] : null;
  let attemptCount = Number(existing?.dynamic_attempt_count || 0);

  const note = await sbRequest('POST', 'crm_contact_notes', {
    body: {
      contact_id: contactId,
      body,
      segment_code: segment ? segment.code : null,
      note_date: noteDate,
      created_by: session.id,
    },
    prefer: 'return=representation',
  });

  const patch = { updated_by: session.id };
  if (segment) {
    patch.segment_code = segment.code;
    if (UNREACHABLE_SEGMENTS.has(segment.code) || segment.code === 'ulasilamadi_tekrar_aranacak') {
      attemptCount += 1;
      patch.dynamic_attempt_count = attemptCount;
      const maxAttempts = Number(segment.max_dynamic_attempts || 5);
      if (attemptCount >= maxAttempts && segment.code === 'ulasilamadi_tekrar_aranacak') {
        patch.segment_code = '5_kez_ulasilamadi';
        patch.next_call_date = null;
        patch.status = 'arsiv';
      }
    } else if (!UNREACHABLE_SEGMENTS.has(segment.code)) {
      patch.dynamic_attempt_count = 0;
    }
    if (!patch.next_call_date && patch.status !== 'arsiv') {
      patch.next_call_date = segment.show_in_dynamic
        ? addDays(noteDate || todayTR(), Math.max(1, segment.gun_offset || 1))
        : null;
    }
    if (!segment.show_in_dynamic && ['satildi', 'sureci_biten', 'tedaviye_uygun_degil', '5_kez_ulasilamadi', '10_kez_ulasilamadi'].includes(segment.code)) {
      patch.next_call_date = null;
      patch.status = 'arsiv';
    }
  }
  const updated = await sbRequest('PATCH', 'crm_contacts', {
    query: `id=eq.${encodeURIComponent(contactId)}&select=${CONTACT_COLS}`,
    body: patch,
    prefer: 'return=representation',
  });

  return res.status(200).json({
    ok: true,
    note: Array.isArray(note) ? note[0] : note,
    contact: Array.isArray(updated) ? updated[0] : updated,
  });
}

/* ─── Danışan kartı ────────────────────────────────────── */

async function contact(req, res) {
  const session = requireSession(req, res);
  if (!session) return;

  if (req.method === 'POST') {
    // Kişi bilgisi güncelle
    const b = jsonBody(req);
    const id = String(b.id || '');
    if (!id) return res.status(400).json({ error: 'id gerekli' });
    const patch = { updated_by: session.id };
    for (const k of ['ad', 'telefon', 'ulke', 'email', 'kaynak', 'kampanya', 'status', 'stage']) {
      if (b[k] !== undefined) patch[k] = String(b[k]);
    }
    const updated = await sbRequest('PATCH', 'crm_contacts', {
      query: `id=eq.${encodeURIComponent(id)}&select=${CONTACT_COLS}`,
      body: patch,
      prefer: 'return=representation',
    });
    return res.status(200).json({ ok: true, contact: Array.isArray(updated) ? updated[0] : updated });
  }

  const id = String(req.query.id || '');
  if (!id) return res.status(400).json({ error: 'id gerekli' });
  const [rows, notes, appts] = await Promise.all([
    sbRequest('GET', 'crm_contacts', {
      query: `id=eq.${encodeURIComponent(id)}&select=${CONTACT_COLS}&limit=1`,
    }),
    sbRequest('GET', 'crm_contact_notes', {
      query: `contact_id=eq.${encodeURIComponent(id)}&select=id,body,segment_code,note_date,created_by,created_at&order=created_at.desc&limit=100`,
    }),
    sbRequest('GET', 'crm_appointments', {
      query: `contact_id=eq.${encodeURIComponent(id)}&select=*&order=start_at.desc&limit=50`,
    }),
  ]);
  const row = Array.isArray(rows) ? rows[0] : null;
  if (!row) return res.status(404).json({ error: 'Kayıt bulunamadı' });
  return res.status(200).json({ ok: true, contact: row, notes: notes || [], appointments: appts || [] });
}

/* ─── Randevular ───────────────────────────────────────── */

async function appointments(req, res) {
  const session = requireSession(req, res);
  if (!session) return;

  if (req.method === 'POST') {
    const b = jsonBody(req);
    if (b.id) {
      // Güncelle (durum / saat / alanlar)
      const patch = { updated_by: session.id };
      for (const k of ['start_at', 'end_at', 'hizmet', 'personel', 'oda', 'tip', 'durum', 'not_text']) {
        if (b[k] !== undefined) patch[k] = b[k];
      }
      const updated = await sbRequest('PATCH', 'crm_appointments', {
        query: `id=eq.${encodeURIComponent(String(b.id))}&select=*`,
        body: patch,
        prefer: 'return=representation',
      });
      return res.status(200).json({ ok: true, appointment: Array.isArray(updated) ? updated[0] : updated });
    }
    const contactId = String(b.contact_id || '');
    const startAt = String(b.start_at || '');
    if (!contactId || !startAt) return res.status(400).json({ error: 'contact_id ve start_at gerekli' });
    const inserted = await sbRequest('POST', 'crm_appointments', {
      body: {
        contact_id: contactId,
        start_at: startAt,
        end_at: b.end_at || null,
        hizmet: String(b.hizmet || ''),
        personel: String(b.personel || ''),
        oda: String(b.oda || ''),
        tip: String(b.tip || ''),
        durum: String(b.durum || 'beklemede'),
        not_text: String(b.not_text || ''),
        created_by: session.id,
        updated_by: session.id,
      },
      prefer: 'return=representation',
    });
    return res.status(200).json({ ok: true, appointment: Array.isArray(inserted) ? inserted[0] : inserted });
  }

  const from = String(req.query.from || '');
  const to = String(req.query.to || '');
  const parts = [
    'select=*,contact:crm_contacts(id,ad,telefon,file_no)',
    'order=start_at.asc',
    'limit=500',
  ];
  if (/^\d{4}-\d{2}-\d{2}$/.test(from)) parts.push(`start_at=gte.${from}T00:00:00%2B03:00`);
  if (/^\d{4}-\d{2}-\d{2}$/.test(to)) parts.push(`start_at=lte.${to}T23:59:59%2B03:00`);
  const rows = await sbRequest('GET', 'crm_appointments', { query: parts.join('&') });
  return res.status(200).json({ ok: true, appointments: rows || [] });
}

/* ─── Public lead intake (site formu — oturum yok) ─────── */

async function leadIntake(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST gerekli' });
  const b = jsonBody(req);
  const ad = String(b.ad || b.fullName || '').trim().slice(0, 120);
  const telefon = String(b.telefon || b.phone || '').trim().slice(0, 30);
  if (!ad || !telefon) return res.status(400).json({ error: 'ad ve telefon gerekli' });
  // Basit honeypot: doldurulmuşsa bot
  if (String(b.website || '').trim()) return res.status(200).json({ ok: true });

  const cleanPhone = telefon.replace(/[^\d+]/g, '');
  const enc = encodeURIComponent;
  const existing = await sbRequest('GET', 'crm_contacts', {
    query: `select=id&or=(telefon.eq.${enc(cleanPhone)},telefon.eq.${enc('+' + cleanPhone.replace(/^\+/, ''))})&limit=1`,
  });
  if (Array.isArray(existing) && existing.length) {
    return res.status(200).json({ ok: true, existing: true });
  }
  const extra = [];
  if (b.company) extra.push(`Firma: ${String(b.company).slice(0, 120)}`);
  if (b.email) extra.push(`E-posta: ${String(b.email).slice(0, 120)}`);
  const inserted = await sbRequest('POST', 'crm_contacts', {
    body: {
      ad,
      telefon: cleanPhone,
      kaynak: String(b.kaynak || 'Web Demo Formu').slice(0, 80),
      kampanya: extra.join(' | '),
      stage: 'lead',
      segment_code: 'yeni_lead',
    },
    prefer: 'return=representation',
  });
  const row = Array.isArray(inserted) ? inserted[0] : inserted;
  return res.status(200).json({ ok: true, id: row?.id });
}

/* ─── Teklifler ────────────────────────────────────────── */

async function offers(req, res) {
  const session = requireSession(req, res);
  if (!session) return;

  if (req.method === 'POST') {
    const b = jsonBody(req);
    if (b.id) {
      const patch = { updated_at: new Date().toISOString() };
      for (const k of ['title', 'currency', 'amount', 'hotel', 'transfer', 'lines', 'status', 'temsilci']) {
        if (b[k] !== undefined) patch[k] = b[k];
      }
      const updated = await sbRequest('PATCH', 'crm_offers', {
        query: `id=eq.${encodeURIComponent(String(b.id))}&select=*`,
        body: patch,
        prefer: 'return=representation',
      });
      return res.status(200).json({ ok: true, offer: Array.isArray(updated) ? updated[0] : updated });
    }
    const contactId = String(b.contact_id || '');
    if (!contactId) return res.status(400).json({ error: 'contact_id gerekli' });
    const inserted = await sbRequest('POST', 'crm_offers', {
      body: {
        contact_id: contactId,
        title: String(b.title || b.hizmet || ''),
        currency: String(b.currency || 'EUR'),
        amount: Number(b.amount || b.tutar || 0),
        hotel: String(b.hotel || ''),
        transfer: String(b.transfer || ''),
        lines: b.lines || [],
        status: String(b.status || 'taslak'),
        temsilci: String(b.temsilci || session.ad || ''),
        created_by: session.id,
      },
      prefer: 'return=representation',
    });
    return res.status(200).json({ ok: true, offer: Array.isArray(inserted) ? inserted[0] : inserted });
  }

  const contactId = String(req.query.contact_id || '');
  const parts = ['select=*,contact:crm_contacts(id,ad,telefon)', 'order=created_at.desc', 'limit=300'];
  if (contactId) parts.push(`contact_id=eq.${encodeURIComponent(contactId)}`);
  const rows = await sbRequest('GET', 'crm_offers', { query: parts.join('&') });
  return res.status(200).json({ ok: true, offers: rows || [] });
}

/* ─── Ödemeler (basit kasa) ────────────────────────────── */

async function payments(req, res) {
  const session = requireSession(req, res);
  if (!session) return;

  if (req.method === 'POST') {
    const b = jsonBody(req);
    const amount = Number(b.amount || b.tutar);
    if (!amount) return res.status(400).json({ error: 'amount gerekli' });
    const inserted = await sbRequest('POST', 'crm_payments', {
      body: {
        contact_id: b.contact_id || null,
        payment_date: /^\d{4}-\d{2}-\d{2}$/.test(String(b.payment_date || '')) ? b.payment_date : todayTR(),
        amount,
        currency: String(b.currency || b.kur || 'EUR'),
        method: String(b.method || b.yontem || ''),
        description: String(b.description || b.bilgi || ''),
        appointment_id: b.appointment_id || null,
        created_by: session.id,
      },
      prefer: 'return=representation',
    });
    return res.status(200).json({ ok: true, payment: Array.isArray(inserted) ? inserted[0] : inserted });
  }

  const from = String(req.query.from || '');
  const to = String(req.query.to || '');
  const parts = ['select=*,contact:crm_contacts(id,ad,telefon)', 'order=payment_date.desc', 'limit=500'];
  if (/^\d{4}-\d{2}-\d{2}$/.test(from)) parts.push(`payment_date=gte.${from}`);
  if (/^\d{4}-\d{2}-\d{2}$/.test(to)) parts.push(`payment_date=lte.${to}`);
  const rows = await sbRequest('GET', 'crm_payments', { query: parts.join('&') });
  return res.status(200).json({ ok: true, payments: rows || [] });
}

/* ─── Ay sonu raporu ───────────────────────────────────── */

async function reports(req, res) {
  const session = requireSession(req, res);
  if (!session) return;
  const month = String(req.query.month || todayTR().slice(0, 7));
  const from = `${month}-01`;
  const [y, m] = month.split('-').map(Number);
  const lastDay = new Date(y, m, 0).getDate();
  const to = `${month}-${String(lastDay).padStart(2, '0')}`;

  const [appts, pays, contacts, segments, users] = await Promise.all([
    sbRequest('GET', 'crm_appointments', {
      query: `select=id,start_at,durum,hizmet,contact:crm_contacts(ad)&start_at=gte.${from}T00:00:00%2B03:00&start_at=lte.${to}T23:59:59%2B03:00&limit=1000`,
    }),
    sbRequest('GET', 'crm_payments', {
      query: `select=id,amount,currency,payment_date,description,contact:crm_contacts(ad)&payment_date=gte.${from}&payment_date=lte.${to}&limit=1000`,
    }),
    sbRequest('GET', 'crm_contacts', {
      query: `select=id,segment_code,stage,status,assigned_to,ad&created_at=gte.${from}T00:00:00&created_at=lte.${to}T23:59:59&limit=5000`,
    }),
    sbRequest('GET', 'crm_segments', {
      query: 'select=code,label&limit=200',
    }),
    sbRequest('GET', 'crm_users', {
      query: 'select=id,ad,kod&limit=100',
    }),
  ]);

  const completed = (appts || []).filter((a) => String(a.durum || '').includes('tamam'));
  const paymentTotal = (pays || []).reduce((s, p) => s + Number(p.amount || 0), 0);

  const segLabel = {};
  (segments || []).forEach((s) => { segLabel[s.code] = s.label || s.code; });
  const userName = {};
  (users || []).forEach((u) => { userName[u.id] = u.ad || u.kod || u.id; });

  const bySegmentMap = {};
  const byTemsilciMap = {};
  (contacts || []).forEach((c) => {
    const seg = segLabel[c.segment_code] || c.segment_code || '(Segmentsiz)';
    bySegmentMap[seg] = (bySegmentMap[seg] || 0) + 1;
    const tem = c.assigned_to ? (userName[c.assigned_to] || String(c.assigned_to).slice(0, 8)) : '(Atanmadı)';
    byTemsilciMap[tem] = (byTemsilciMap[tem] || 0) + 1;
  });
  const sortCount = (m) => Object.entries(m)
    .map(([key, count]) => ({ key, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 20);

  return res.status(200).json({
    ok: true,
    month,
    summary: {
      new_contacts: (contacts || []).length,
      appointments_total: (appts || []).length,
      appointments_completed: completed.length,
      payments_count: (pays || []).length,
      payments_total_eur: paymentTotal,
    },
    by_segment: sortCount(bySegmentMap),
    by_temsilci: sortCount(byTemsilciMap),
    appointments: appts || [],
    payments: pays || [],
    contacts: contacts || [],
  });
}

/* ─── Dispatch ─────────────────────────────────────────── */

export const CLINIC_ACTIONS = new Set([
  'clinic-login',
  'clinic-logout',
  'clinic-me',
  'clinic-bootstrap',
  'clinic-leads',
  'clinic-assign',
  'clinic-dynamic',
  'clinic-note-save',
  'clinic-contact',
  'clinic-appointments',
  'clinic-lead-intake',
  'clinic-offers',
  'clinic-payments',
  'clinic-reports',
]);

export async function handleClinicAction(action, req, res) {
  switch (action) {
    case 'clinic-login':
      return login(req, res);
    case 'clinic-logout':
      return logout(req, res);
    case 'clinic-me':
      return me(req, res);
    case 'clinic-bootstrap':
      return bootstrap(req, res);
    case 'clinic-leads':
      return leads(req, res);
    case 'clinic-assign':
      return assign(req, res);
    case 'clinic-dynamic':
      return dynamicList(req, res);
    case 'clinic-note-save':
      return noteSave(req, res);
    case 'clinic-contact':
      return contact(req, res);
    case 'clinic-appointments':
      return appointments(req, res);
    case 'clinic-lead-intake':
      return leadIntake(req, res);
    case 'clinic-offers':
      return offers(req, res);
    case 'clinic-payments':
      return payments(req, res);
    case 'clinic-reports':
      return reports(req, res);
    default:
      return res.status(400).json({ error: 'Geçersiz clinic action' });
  }
}
