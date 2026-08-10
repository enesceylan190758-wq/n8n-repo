import { createHmac, timingSafeEqual } from 'crypto';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { sbRequest } from './_lib/supabase.js';
import { parseCookies } from './_lib/auth.js';
import { CLINIC_ACTIONS, handleClinicAction } from './_lib/clinic-crm.js';
import firmaBasvuruHandler from './_lib/firma-basvuru-handler.js';
import {
  normalizeInstanceName,
  startQrSession,
  pollConnection,
  connectionState,
  listChats,
  listMessages,
  sendTextMessage,
} from './_lib/evolution.js';
import {
  getNfxCrmData,
  saveNfxCrmData,
  ensureNfxCrmRow,
} from './_lib/nefalix-crm-store.js';
import { OUTREACH, listEmailTemplates, fillOutreach, buildSignatureHtml } from './_lib/outreach-templates.js';

const SITE = 'https://nefalix.com';
const OG_IMAGE = `${SITE}/assets/brand/nefalix-logo-512.png`;
const CRM_COOKIE = 'nefalix_crm';
const CRM_MAX_AGE = 60 * 60 * 24 * 90; // 90 gün — kaldığı yerden devam
const GEO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
const COVER_VERSION = '7';

function brandedCoverUrl(title, tag = 'Rehber', kind = 'blog') {
  const q = new URLSearchParams({
    action: 'cover',
    kind,
    tag: String(tag || 'Rehber').slice(0, 40),
    t: String(title || 'Nefalix').slice(0, 90),
    v: COVER_VERSION,
  });
  return `${SITE}/api/blog?${q}`;
}

/** Saha CRM kullanıcıları (iç ekip — klinik dashboard değil) */
const CRM_USERS = [
  { id: 'ak', kod: 'abdulkadir', sifre: '4X7K0ytgwJ', ad: 'Abdülkadir Yaşar', rol: 'Kurucu · Saha' },
  { id: 'en', kod: 'enes', sifre: '8SOHcroY18', ad: 'Enes Ceylan', rol: 'CTO · Saha' },
  { id: 'kd', kod: 'kader', sifre: 'Xbp1IBfogO', ad: 'Kader Hanım', rol: 'Arama & Randevu' },
  { id: 'mi', kod: 'destek', sifre: 'NXgGYHC7J3', ad: 'Destek / 4. Kişi', rol: 'Destek' },
];

function crmSecret() {
  return process.env.DASHBOARD_SESSION_SECRET || process.env.NEFALIX_INTERNAL_KEY || 'nefalix-crm-local';
}

function signCrmSession(user) {
  const payload = {
    id: user.id,
    kod: user.kod,
    ad: user.ad,
    rol: user.rol,
    exp: Date.now() + CRM_MAX_AGE * 1000,
  };
  const body = Buffer.from(JSON.stringify(payload)).toString('base64url');
  const sig = createHmac('sha256', crmSecret()).update(body).digest('base64url');
  return `${body}.${sig}`;
}

function verifyCrmSession(token) {
  if (!token) return null;
  const [body, sig] = String(token).split('.');
  if (!body || !sig) return null;
  const expected = createHmac('sha256', crmSecret()).update(body).digest('base64url');
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

function setCrmCookie(res, token) {
  const secure = process.env.VERCEL === '1' ? '; Secure' : '';
  res.setHeader(
    'Set-Cookie',
    `${CRM_COOKIE}=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${CRM_MAX_AGE}${secure}`
  );
}

function clearCrmCookie(res) {
  const secure = process.env.VERCEL === '1' ? '; Secure' : '';
  res.setHeader(
    'Set-Cookie',
    `${CRM_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0${secure}`
  );
}

function requireCrm(req, res) {
  const user = verifyCrmSession(parseCookies(req)[CRM_COOKIE]);
  if (!user) {
    res.status(401).json({ error: 'CRM oturumu gerekli' });
    return null;
  }
  return user;
}

async function handleCrmLogin(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST gerekli' });
  const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : req.body || {};
  const kod = String(body.kod || '').trim().toLowerCase();
  const user = CRM_USERS.find((u) => u.kod === kod);
  if (!user) return res.status(401).json({ error: 'Kullanıcı adı hatalı' });
  setCrmCookie(res, signCrmSession(user));
  return res.status(200).json({ ok: true, id: user.id, ad: user.ad, rol: user.rol });
}

async function handleCrmMe(req, res) {
  if (req.method !== 'POST' && req.method !== 'GET') {
    return res.status(405).json({ error: 'GET/POST gerekli' });
  }
  const session = verifyCrmSession(parseCookies(req)[CRM_COOKIE]);
  if (!session) return res.status(200).json({ ok: false });
  const user = CRM_USERS.find((u) => u.kod === session.kod) || {
    id: session.id,
    kod: session.kod,
    ad: session.ad,
    rol: session.rol,
  };
  // Sliding session — her ziyarette süreyi uzat
  setCrmCookie(res, signCrmSession(user));
  return res.status(200).json({
    ok: true,
    id: user.id,
    kod: user.kod,
    ad: user.ad || session.ad,
    rol: user.rol || session.rol,
  });
}

async function handleCrmLogout(req, res) {
  clearCrmCookie(res);
  return res.status(200).json({ ok: true });
}

async function handleCrmGet(req, res) {
  if (!requireCrm(req, res)) return;
  const rows = await sbRequest('GET', 'nefalix_state', {
    query: 'id=eq.1&select=data,rev',
    prefer: 'return=representation',
  });
  const row = Array.isArray(rows) ? rows[0] : null;
  if (!row?.data || !row.data.clinics) {
    return res.status(200).json({ ok: true, data: null });
  }
  const data = { ...row.data, rev: row.rev };
  return res.status(200).json({ ok: true, data });
}

async function handleCrmSave(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST gerekli' });
  if (!requireCrm(req, res)) return;
  const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : req.body || {};
  const data = body.data;
  if (!data || typeof data !== 'object' || !Array.isArray(data.clinics)) {
    return res.status(400).json({ error: 'Geçersiz CRM veri' });
  }
  const rev = Number(data.rev) || 1;
  await sbRequest('PATCH', 'nefalix_state', {
    query: 'id=eq.1',
    body: { data, rev },
    prefer: 'return=minimal',
  });
  return res.status(200).json({ ok: true, rev });
}

async function triggerCrmRandevuMail(payload) {
  const url = (
    process.env.CRM_NOTIFY_WEBHOOK_URL ||
    'https://api.nefalix.com/internal/crm/randevu-mail'
  ).replace(/\/$/, '');
  const internalKey = process.env.NEFALIX_INTERNAL_KEY;
  if (!internalKey) throw new Error('NEFALIX_INTERNAL_KEY eksik (Vercel env)');
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Nefalix-Internal-Key': internalKey,
    },
    body: JSON.stringify(payload),
  });
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { raw: text };
  }
  if (!res.ok) {
    throw new Error(data?.error || data?.message || text || `HTTP ${res.status}`);
  }
  return data;
}

async function handleCrmNotifyRandevu(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST gerekli' });
  const session = requireCrm(req, res);
  if (!session) return;
  const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : req.body || {};
  const event = String(body.event || 'created').toLowerCase();
  if (!['created', 'cancelled'].includes(event)) {
    return res.status(400).json({ error: 'event created|cancelled olmalı' });
  }
  const clinic = String(body.clinic || '').trim();
  if (!clinic) return res.status(400).json({ error: 'clinic gerekli' });
  const payload = {
    event,
    clinic,
    tarih: String(body.tarih || ''),
    saat: String(body.saat || ''),
    adres: String(body.adres || ''),
    tel: String(body.tel || ''),
    notu: String(body.notu || ''),
    olusturan: String(body.olusturan || session.ad || ''),
    katilimcilar: Array.isArray(body.katilimcilar)
      ? body.katilimcilar.map((x) => String(x))
      : [],
  };
  const result = await triggerCrmRandevuMail(payload);
  return res.status(200).json({ ok: true, mail: result });
}

async function triggerCrmOutreachMail(payload) {
  const url = (
    process.env.CRM_OUTREACH_WEBHOOK_URL ||
    'https://api.nefalix.com/internal/crm/outreach-mail'
  ).replace(/\/$/, '');
  const internalKey = process.env.NEFALIX_INTERNAL_KEY;
  if (!internalKey) throw new Error('NEFALIX_INTERNAL_KEY eksik (Vercel env)');
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Nefalix-Internal-Key': internalKey,
    },
    body: JSON.stringify(payload),
  });
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { raw: text };
  }
  if (!res.ok) {
    throw new Error(data?.error || data?.message || text || `HTTP ${res.status}`);
  }
  return data;
}

async function pollCrmOutreachJob(jobId, { timeoutMs = 280000, intervalMs = 2500 } = {}) {
  const base =
    process.env.CRM_OUTREACH_STATUS_URL ||
    'https://api.nefalix.com/internal/crm/outreach-status';
  const internalKey = process.env.NEFALIX_INTERNAL_KEY;
  if (!internalKey) throw new Error('NEFALIX_INTERNAL_KEY eksik (Vercel env)');
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const url = `${base}?jobId=${encodeURIComponent(jobId)}`;
    const res = await fetch(url, {
      headers: { 'X-Nefalix-Internal-Key': internalKey },
    });
    const text = await res.text();
    let data = null;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = { raw: text };
    }
    if (!res.ok) {
      throw new Error(data?.error || data?.message || text || `HTTP ${res.status}`);
    }
    const st = String(data?.status || '');
    if (st === 'done') return data.mail || data;
    if (st === 'error') throw new Error(data?.error || 'outreach job error');
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  throw new Error('Gönderim zaman aşımı — VPS job hâlâ çalışıyor olabilir');
}

function mapSenderKey(session) {
  const kod = String(session?.kod || session?.id || '').toLowerCase();
  if (kod.includes('enes')) return 'enes';
  if (kod.includes('kader')) return 'kader';
  if (kod.includes('abd') || kod.includes('ak') || kod.includes('ay')) return 'kadir';
  return 'kadir';
}

function replyEmailForSession(session) {
  const key = mapSenderKey(session);
  const sender = OUTREACH.senders?.[key];
  return sender?.email || 'abdulkadir@nefalix.com';
}

async function handleCrmOutreachTemplates(req, res) {
  if (req.method !== 'GET' && req.method !== 'POST') {
    return res.status(405).json({ error: 'GET|POST gerekli' });
  }
  if (!requireCrm(req, res)) return;
  const templates = listEmailTemplates().map((t) => ({
    id: t.id,
    title: t.title,
    stage: t.stage,
    subject: t.subject,
    body: t.body || '',
    bodyPreview: String(t.body || '').slice(0, 220),
  }));
  return res.status(200).json({
    ok: true,
    templates,
    senders: OUTREACH.senders,
  });
}

async function handleCrmOutreach(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST gerekli' });
  const session = requireCrm(req, res);
  if (!session) return;
  const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : req.body || {};
  const templateId = String(body.templateId || '').trim();
  const templates = listEmailTemplates();
  const tpl = templates.find((t) => t.id === templateId);
  if (!tpl) return res.status(400).json({ error: 'Geçersiz templateId' });

  let recipients = Array.isArray(body.recipients) ? body.recipients : [];
  recipients = recipients
    .map((r) => ({
      email: String(r?.email || '').trim().toLowerCase(),
      name: String(r?.name || '').trim(),
      firm: String(r?.firm || '').trim(),
      hitap: String(r?.hitap || body.hitap || 'unknown').trim().toLowerCase(),
    }))
    .filter((r) => r.email);
  if (!recipients.length) {
    return res.status(400).json({ error: 'En az bir geçerli e-posta gerekli' });
  }
  if (recipients.length > 50) {
    return res.status(400).json({ error: 'En fazla 50 alıcı' });
  }
  const bad = recipients.filter((r) => !r.name || !r.firm);
  if (bad.length && body.preview !== true) {
    return res.status(400).json({
      error: 'Her alıcı için isim ve firma zorunlu',
      missing: bad.map((r) => r.email),
    });
  }

  let senderKey = String(body.senderKey || mapSenderKey(session)).toLowerCase();
  if (['abdulkadir', 'ak', 'ay', 'admin'].includes(senderKey)) senderKey = 'kadir';
  if (['kader', 'kh', 'kd'].includes(senderKey)) senderKey = 'kader';
  if (['enes', 'ec', 'en'].includes(senderKey)) senderKey = 'enes';
  if (!OUTREACH.senders?.[senderKey]) senderKey = 'kadir';

  const customSubject =
    body.customSubject != null ? String(body.customSubject) : null;
  const customBody = body.customBody != null ? String(body.customBody) : null;
  const draftTpl = {
    subject: customSubject != null ? customSubject : tpl.subject,
    body: customBody != null ? customBody : tpl.body,
  };

  const payload = {
    templateId,
    senderKey,
    replyTo: String(body.replyTo || replyEmailForSession(session)).trim(),
    recipients,
    delaySec: Number(body.delaySec ?? 3),
    maxPerHour: Number(body.maxPerHour ?? 20),
  };
  if (customSubject != null) payload.customSubject = customSubject;
  if (customBody != null) payload.customBody = customBody;
  const includeSignature =
    body.includeSignature === undefined ? true : Boolean(body.includeSignature);
  payload.includeSignature = includeSignature;
  let mailStyle = String(body.mailStyle || 'personal').toLowerCase();
  if (mailStyle === 'marka' || mailStyle === 'card') mailStyle = 'branded';
  if (mailStyle !== 'branded') mailStyle = 'personal';
  payload.mailStyle = mailStyle;

  // Preview-only (no send)
  if (body.preview === true) {
    const sender = OUTREACH.senders[senderKey];
    const sample = recipients[0] || { name: '[İsim]', firm: '[Firma]' };
    const filled = fillOutreach(draftTpl, sender, sample);
    let previewBody = filled.body || '';
    if (includeSignature) {
      const m = previewBody.match(/(^|\n)(Saygılarımla,?)\s*\n/i);
      if (m) previewBody = previewBody.slice(0, m.index + m[0].length).trimEnd();
    }
    const signatureHtml = includeSignature ? buildSignatureHtml(sender) : '';
    return res.status(200).json({
      ok: true,
      preview: true,
      subject: filled.subject,
      body: previewBody,
      signatureHtml,
      includeSignature,
      mailStyle,
      draftSubject: draftTpl.subject,
      draftBody: draftTpl.body,
      senderKey,
      count: recipients.length,
    });
  }

  const queued = await triggerCrmOutreachMail(payload);
  if (queued?.jobId) {
    // Client-side poll preferred (Vercel timeout); return jobId immediately
    if (body.wait === true) {
      const mail = await pollCrmOutreachJob(queued.jobId);
      return res.status(200).json({ ok: true, mail });
    }
    return res.status(200).json({ ok: true, queued: true, jobId: queued.jobId, status: queued.status });
  }
  return res.status(200).json({ ok: true, mail: queued });
}

async function handleCrmOutreachStatus(req, res) {
  if (req.method !== 'GET' && req.method !== 'POST') {
    return res.status(405).json({ error: 'GET|POST gerekli' });
  }
  if (!requireCrm(req, res)) return;
  const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : req.body || {};
  const jobId = String(req.query.jobId || body.jobId || '').trim();
  if (!jobId) return res.status(400).json({ error: 'jobId gerekli' });
  const base =
    process.env.CRM_OUTREACH_STATUS_URL ||
    'https://api.nefalix.com/internal/crm/outreach-status';
  const internalKey = process.env.NEFALIX_INTERNAL_KEY;
  if (!internalKey) throw new Error('NEFALIX_INTERNAL_KEY eksik (Vercel env)');
  const url = `${base}?jobId=${encodeURIComponent(jobId)}`;
  const r = await fetch(url, { headers: { 'X-Nefalix-Internal-Key': internalKey } });
  const text = await r.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { raw: text };
  }
  if (!r.ok) {
    return res.status(r.status).json({ error: data?.error || text || `HTTP ${r.status}` });
  }
  return res.status(200).json(data);
}

async function handleCrmWhatsapp(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST gerekli' });
  if (!requireCrm(req, res)) return;
  const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : req.body || {};
  const action = String(body.action || 'status').toLowerCase();
  let instance;
  try {
    instance = normalizeInstanceName(
      body.instanceName || process.env.CRM_EVOLUTION_INSTANCE || 'nefalix-crm'
    );
  } catch (e) {
    return res.status(400).json({ error: e.message || 'Geçersiz instance' });
  }

  try {
    if (action === 'start' || action === 'refresh') {
      const result = await startQrSession(instance, {
        reset: action === 'refresh' || Boolean(body.reset),
      });
      return res.status(200).json({
        ok: true,
        instance,
        state: result.state,
        connected: result.connected,
        qr: result.qr,
        hint: result.connected
          ? 'WhatsApp bağlı.'
          : 'Telefonda WhatsApp → Bağlı cihazlar → Cihaz bağla → QR okutun (60 sn).',
      });
    }

    if (action === 'status') {
      let result;
      try {
        result = await pollConnection(instance);
      } catch (e) {
        const msg = String(e.message || e);
        if (/not found|404|does not exist/i.test(msg)) {
          return res.status(200).json({
            ok: true,
            instance,
            state: 'missing',
            connected: false,
            qr: null,
            hint: 'Instance yok — “QR başlat” ile oluşturun.',
          });
        }
        throw e;
      }
      return res.status(200).json({
        ok: true,
        instance,
        state: result.state,
        connected: result.connected,
        qr: result.qr,
      });
    }

    if (action === 'chats') {
      const state = await connectionState(instance).catch(() => 'unknown');
      if (state !== 'open') {
        return res.status(200).json({
          ok: true,
          instance,
          connected: false,
          state,
          chats: [],
          hint: 'WhatsApp bağlı değil — önce QR okutun.',
        });
      }
      const chats = await listChats(instance, { limit: Number(body.limit) || 40 });
      return res.status(200).json({ ok: true, instance, connected: true, state, chats });
    }

    if (action === 'messages') {
      const remoteJid = String(body.remoteJid || body.jid || '').trim();
      if (!remoteJid) return res.status(400).json({ error: 'remoteJid gerekli' });
      const messages = await listMessages(instance, remoteJid, {
        limit: Number(body.limit) || 50,
      });
      return res.status(200).json({ ok: true, instance, remoteJid, messages });
    }

    if (action === 'send') {
      const to = String(body.to || body.number || body.remoteJid || '').trim();
      const text = String(body.text || body.message || '').trim();
      const result = await sendTextMessage(instance, to, text);
      return res.status(200).json({ ok: true, instance, result });
    }

    if (action === 'manager-sso' || action === 'inbox-sso') {
      const evoUrl = (
        process.env.EVOLUTION_PUBLIC_URL ||
        process.env.EVOLUTION_API_URL ||
        'https://evo.nefalix.com'
      ).replace(/\/$/, '');
      const publicUrl =
        evoUrl.includes('127.0.0.1') ||
        evoUrl.includes('localhost') ||
        evoUrl.includes('evolution-api')
          ? 'https://evo.nefalix.com'
          : evoUrl;
      const apiKey = process.env.EVOLUTION_API_KEY || '';
      if (!apiKey) {
        return res.status(503).json({ error: 'EVOLUTION_API_KEY eksik' });
      }

      // Varsayılan: Evolution sohbet inbox (tüm chat’ler tek listede + isimler)
      if (action === 'inbox-sso') {
        const hash = new URLSearchParams({
          apiUrl: publicUrl,
          token: apiKey,
          instance,
          label: 'Nefalix CRM',
          next: '/wa-inbox/index.html',
        }).toString();
        return res.status(200).json({
          ok: true,
          instance,
          connected: true,
          state: 'assumed',
          ssoUrl: `${publicUrl}/wa-inbox/sso.html#${hash}`,
          inboxUrl: `${publicUrl}/wa-inbox/`,
          managerUrl: `${publicUrl}/manager/`,
          hint: 'WhatsApp sohbet',
        });
      }

      // Manager chat (gruplar → Grupos sekmesi)
      let version = '2.3.7';
      let instanceId = '';
      try {
        const root = await Promise.race([
          fetch(`${publicUrl}/`, {
            headers: { apikey: apiKey, Accept: 'application/json' },
          }).then((r) => r.json()),
          new Promise((resolve) => setTimeout(() => resolve(null), 400)),
        ]);
        if (root?.version) version = String(root.version);
      } catch {
        /* default */
      }
      try {
        const list = await Promise.race([
          fetch(
            `${publicUrl}/instance/fetchInstances?instanceName=${encodeURIComponent(instance)}`,
            { headers: { apikey: apiKey, Accept: 'application/json' } }
          ).then((r) => r.json()),
          new Promise((resolve) => setTimeout(() => resolve(null), 600)),
        ]);
        const arr = Array.isArray(list) ? list : list ? [list] : [];
        const row =
          arr.find((x) => {
            const n =
              x?.name || x?.instance?.instanceName || x?.instance?.name || '';
            return String(n).toLowerCase() === String(instance).toLowerCase();
          }) || (arr.length === 1 ? arr[0] : null);
        instanceId = String(row?.id || row?.instance?.id || '');
      } catch {
        /* wa-sso çözer */
      }

      const chatPath = instanceId
        ? `/manager/instance/${encodeURIComponent(instanceId)}/chat`
        : '';
      const hash = new URLSearchParams({
        apiUrl: publicUrl,
        token: apiKey,
        version,
        instance,
        ...(chatPath ? { next: chatPath } : {}),
      }).toString();
      return res.status(200).json({
        ok: true,
        instance,
        instanceId: instanceId || null,
        version,
        connected: true,
        state: 'assumed',
        ssoUrl: `${publicUrl}/wa-sso#${hash}`,
        chatUrl: chatPath ? `${publicUrl}${chatPath}` : `${publicUrl}/manager/`,
        managerUrl: `${publicUrl}/manager/`,
        hint: 'Evolution Manager · Grupos sekmesine bakın',
      });
    }

    return res.status(400).json({
      error: 'action start|refresh|status|chats|messages|send|manager-sso|inbox-sso olmalı',
    });
  } catch (e) {
    return res.status(502).json({ error: e.message || 'Evolution hatası', instance });
  }
}

function escapeHtml(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function xmlEscape(s) {
  return escapeHtml(s);
}

function fmtDate(iso) {
  try {
    return new Date(iso).toLocaleDateString('tr-TR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  } catch {
    return '';
  }
}

async function loadBlogPosts(limit = 50) {
  const nowIso = new Date().toISOString();
  const rows = await sbRequest('GET', 'blog_posts', {
    query: `select=slug,title,tag,excerpt,published_at,cover_image_url&status=eq.published&published_at=lte.${encodeURIComponent(nowIso)}&order=published_at.desc&limit=${limit}`,
    prefer: 'return=representation',
  });
  return (Array.isArray(rows) ? rows : []).map((r) => ({
    slug: r.slug,
    title: r.title,
    tag: r.tag || 'Rehber',
    excerpt: r.excerpt,
    published_at: r.published_at,
    cover_image_url:
      r.cover_image_url && !String(r.cover_image_url).includes('unsplash.com')
        ? r.cover_image_url
        : brandedCoverUrl(r.title, r.tag || 'Rehber', 'blog'),
    url: `${SITE}/blog/${r.slug}`,
  }));
}

async function handleList(req, res) {
  res.setHeader('Cache-Control', 'public, s-maxage=120, stale-while-revalidate=300');
  const limit = Math.min(Number(req.query.limit) || 24, 50);
  const posts = await loadBlogPosts(limit);
  res.status(200).json({ ok: true, posts });
}

function fmtIndexDate(iso) {
  try {
    return new Date(iso).toLocaleDateString('tr-TR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return '';
  }
}

function blogIndexCardHtml(p, { featured = false } = {}) {
  const cover = p.cover_image_url
    ? `<img class="${featured ? 'blog-featured-cover' : 'article-card-cover'}" src="${escapeHtml(p.cover_image_url)}" alt="" loading="${featured ? 'eager' : 'lazy'}">`
    : '';
  if (featured) {
    return `
      <a class="blog-featured-card" href="/blog/${escapeHtml(p.slug)}">
        ${cover}
        <div class="blog-featured-copy">
          <span class="article-card-tag">${escapeHtml(p.tag)}</span>
          <h2>${escapeHtml(p.title)}</h2>
          <p>${escapeHtml(p.excerpt)}</p>
          <span class="article-card-meta">${escapeHtml(fmtIndexDate(p.published_at))} · Blog · Okumaya devam et →</span>
        </div>
      </a>`;
  }
  return `
      <a class="article-card article-card-link" href="/blog/${escapeHtml(p.slug)}">
        ${cover}
        <span class="article-card-tag">${escapeHtml(p.tag)}</span>
        <h3>${escapeHtml(p.title)}</h3>
        <p>${escapeHtml(p.excerpt)}</p>
        <span class="article-card-meta">${escapeHtml(fmtIndexDate(p.published_at))} · Blog</span>
      </a>`;
}

function blogIndexTagFiltersHtml(posts) {
  const tags = [];
  const seen = new Set();
  for (const p of posts) {
    const tag = (p.tag || 'Rehber').trim();
    if (!seen.has(tag)) {
      seen.add(tag);
      tags.push(tag);
    }
  }
  const buttons = [
    '<button type="button" class="blog-tag-btn active" data-tag="all">Tümü</button>',
    ...tags.map(
      (tag) =>
        `<button type="button" class="blog-tag-btn" data-tag="${escapeHtml(tag)}">${escapeHtml(tag)}</button>`
    ),
  ];
  return buttons.join('');
}

function readPublicHtml(filename) {
  const full = join(process.cwd(), filename);
  if (!existsSync(full)) return null;
  return readFileSync(full, 'utf8');
}

async function handleBlogIndex(_req, res) {
  const posts = await loadBlogPosts(50);
  let html = readPublicHtml('blog.html');
  if (!html) {
    res.status(500).send('blog.html bulunamadı');
    return;
  }

  const countText = posts.length ? `${posts.length} yazı` : 'Henüz yazı yok';
  let featuredHtml = '';
  let gridHtml = '';
  if (!posts.length) {
    gridHtml =
      '<p class="blog-empty">İlk yazılar yakında burada. Günlük blog otomasyonu aktif.</p>';
  } else {
    const [featured, ...rest] = posts;
    featuredHtml = blogIndexCardHtml(featured, { featured: true });
    gridHtml =
      rest.map((p) => blogIndexCardHtml(p)).join('') ||
      '<p class="blog-empty" style="grid-column:1/-1;">Diğer yazılar yakında eklenecek.</p>';
  }

  const itemList = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: 'Blog — Nefalix',
    url: `${SITE}/blog`,
    description:
      'Nefalix blog: klinik itibarı, NPS, WhatsApp iletişimi, HBYS entegrasyonu ve hasta deneyimi yazıları.',
    mainEntity: {
      '@type': 'ItemList',
      numberOfItems: posts.length,
      itemListElement: posts.map((p, i) => ({
        '@type': 'ListItem',
        position: i + 1,
        url: p.url,
        name: p.title,
      })),
    },
  };
  const jsonLd = `<script type="application/ld+json">${JSON.stringify(itemList)}</script>`;

  html = html
    .replace(
      /<p class="blog-index-count" id="blog-index-count">[^<]*<\/p>/,
      `<p class="blog-index-count" id="blog-index-count">${escapeHtml(countText)}</p>`
    )
    .replace(
      /<div class="blog-tag-filters" id="blog-tag-filters"[^>]*><\/div>/,
      `<div class="blog-tag-filters" id="blog-tag-filters" aria-label="Konu filtreleri">${blogIndexTagFiltersHtml(posts)}</div>`
    )
    .replace(
      /<div id="blog-featured" class="blog-featured" hidden><\/div>/,
      featuredHtml
        ? `<div id="blog-featured" class="blog-featured">${featuredHtml}</div>`
        : `<div id="blog-featured" class="blog-featured" hidden></div>`
    )
    .replace(
      /<div class="article-card-grid blog-index-grid" id="blog-post-grid">[\s\S]*?<\/div>\s*<\/div>\s*<\/section>/,
      `<div class="article-card-grid blog-index-grid" id="blog-post-grid">${gridHtml}</div>\n  </div>\n</section>`
    )
    .replace('</head>', `${jsonLd}\n</head>`);

  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'public, s-maxage=120, stale-while-revalidate=300');
  res.status(200).send(html);
}

async function handleRender(req, res) {
  const slug = String(req.query.slug || '').trim();
  if (!slug || !/^[a-z0-9][a-z0-9-]{0,120}$/.test(slug)) {
    res.status(400).send('Geçersiz slug');
    return;
  }
  const rows = await sbRequest('GET', 'blog_posts', {
    query: `slug=eq.${encodeURIComponent(slug)}&status=eq.published&published_at=lte.${encodeURIComponent(new Date().toISOString())}&select=slug,title,tag,excerpt,body_html,meta_description,published_at,cover_image_url,footer_image_url,youtube_video_id,youtube_title&limit=1`,
    prefer: 'return=representation',
  });
  const post = Array.isArray(rows) ? rows[0] : null;
  if (!post) {
    res.status(404).send('Yazı bulunamadı');
    return;
  }

  const title = escapeHtml(post.title);
  const desc = escapeHtml(post.meta_description || post.excerpt);
  const tag = escapeHtml(post.tag || 'Rehber');
  const date = fmtDate(post.published_at);
  const url = `${SITE}/blog/${post.slug}`;
  const body = post.body_html || '';
  const cover = post.cover_image_url?.includes('unsplash.com')
    ? brandedCoverUrl(post.title, post.tag || 'Rehber', 'blog')
    : post.cover_image_url || brandedCoverUrl(post.title, post.tag || 'Rehber', 'blog');
  const footer = post.footer_image_url?.includes('unsplash.com')
    ? brandedCoverUrl('Nefalix', post.tag || 'Rehber', 'footer')
    : post.footer_image_url || brandedCoverUrl('Nefalix', post.tag || 'Rehber', 'footer');
  const coverEsc = escapeHtml(cover);
  const footerEsc = escapeHtml(footer);
  const videoBlock = post.youtube_video_id
    ? youtubeEmbedHtml(post.youtube_video_id, post.youtube_title || post.title)
    : '';

  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'public, s-maxage=600, stale-while-revalidate=3600');
  const published = post.published_at || new Date().toISOString();
  const jsonGraph = [
    {
      '@type': 'BlogPosting',
      headline: post.title,
      description: post.meta_description || post.excerpt || '',
      image: cover,
      datePublished: published,
      dateModified: published,
      author: { '@type': 'Organization', name: 'Nefalix', url: SITE },
      publisher: {
        '@type': 'Organization',
        name: 'Nefalix',
        url: SITE,
        logo: { '@type': 'ImageObject', url: `${SITE}/assets/brand/nefalix-logo-512.png` },
      },
      mainEntityOfPage: { '@type': 'WebPage', '@id': url },
    },
  ];
  if (post.youtube_video_id) {
    jsonGraph.push({
      '@type': 'VideoObject',
      name: post.youtube_title || post.title,
      description: post.meta_description || post.excerpt || '',
      thumbnailUrl: `https://i.ytimg.com/vi/${post.youtube_video_id}/hqdefault.jpg`,
      uploadDate: published,
      embedUrl: `https://www.youtube.com/embed/${post.youtube_video_id}`,
      url: `https://www.youtube.com/watch?v=${post.youtube_video_id}`,
    });
  }
  const jsonLd = JSON.stringify({ '@context': 'https://schema.org', '@graph': jsonGraph });
  res.status(200).send(`<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="${desc}">
<link rel="canonical" href="${url}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Nefalix">
<meta property="og:title" content="${title}">
<meta property="og:description" content="${desc}">
<meta property="og:url" content="${url}">
<meta property="og:image" content="${coverEsc}">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">${jsonLd}</script>
<title>${title} — Nefalix</title>
<link rel="icon" href="/assets/brand/favicon-192.png" type="image/png">
<link rel="stylesheet" href="/shared.css">
<style>
.blog-article-wrap { max-width: 760px; margin: 0 auto; padding: 48px 20px 80px; }
.blog-hero-img, .blog-footer-img { width:100%; border-radius:18px; object-fit:cover; object-position:center; display:block; background:#eef2f7; }
.blog-hero-img { height:min(380px, 48vw); margin: 0 0 28px; box-shadow:0 18px 48px rgba(15,23,42,0.12); }
.blog-footer-img { height:min(220px, 32vw); margin: 36px 0 0; opacity:.95; }
.blog-article-tag { display:inline-block; font-size:11px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:var(--coral); margin-bottom:12px; }
.blog-article h1 { font-size: clamp(1.75rem, 4vw, 2.35rem); line-height:1.2; margin: 0 0 12px; }
.blog-article-meta { color: var(--muted); font-size: 14px; margin-bottom: 28px; }
.blog-article-body { font-size: 17px; line-height: 1.8; color: var(--ink); }
.blog-article-body p { margin: 0 0 1.15em; }
.blog-article-body h2 { font-size:1.4rem; margin:1.75em 0 0.65em; line-height:1.3; }
.blog-article-body h3 { font-size:1.12rem; margin:1.25em 0 0.45em; }
.blog-article-body .faq-item { margin:0 0 1.1em; padding:14px 16px; border-radius:14px; background:rgba(15,23,42,0.03); }
.blog-lede { font-size:1.08em; line-height:1.75; margin:0 0 1.4em !important; }
.blog-takeaways, .blog-checklist {
  margin: 1.5em 0 1.75em; padding: 20px 22px; border-radius: 16px;
  border: 1px solid rgba(216,231,246,0.95); background: linear-gradient(180deg,#fff,rgba(47,107,255,0.04));
}
.blog-takeaways h2, .blog-checklist h2 { margin-top:0 !important; font-size:1.15rem !important; }
.blog-takeaways ul, .blog-checklist ul { margin:0; padding-left:1.2em; }
.blog-takeaways li, .blog-checklist li { margin:0 0 0.55em; }
.blog-cta { margin-top:1.75em; padding:16px 18px; border-left:4px solid #2F6BFF; background:rgba(47,107,255,0.06); border-radius:0 12px 12px 0; }
.blog-back { display:inline-flex; align-items:center; gap:8px; margin-bottom:28px; color:var(--teal); font-weight:600; text-decoration:none; }
.blog-back:hover { text-decoration:underline; }
</style>
</head>
<body class="site-subpage">
<div class="blog-article-wrap">
  <a href="/blog" class="blog-back">← Tüm yazılar</a>
  <article class="blog-article">
    <img class="blog-hero-img" src="${coverEsc}" alt="" width="1200" height="560" loading="eager">
    <span class="blog-article-tag">${tag}</span>
    <h1>${title}</h1>
    <p class="blog-article-meta">${date} · Blog</p>
    <div class="blog-article-body">${body}</div>
    ${videoBlock}
    <img class="blog-footer-img" src="${footerEsc}" alt="Nefalix" width="1200" height="320" loading="lazy">
  </article>
</div>
<script src="/shared.js"></script>
</body>
</html>`);
}

async function handleSitemap(_req, res) {
  const nowIso = new Date().toISOString();
  const rows = await sbRequest('GET', 'blog_posts', {
    query: `select=slug,published_at&status=eq.published&published_at=lte.${encodeURIComponent(nowIso)}&order=published_at.desc&limit=200`,
    prefer: 'return=representation',
  });
  const posts = Array.isArray(rows) ? rows : [];
  const urls = posts
    .map((p) => {
      const loc = `${SITE}/blog/${xmlEscape(p.slug)}`;
      const lastmod = (p.published_at || '').slice(0, 10);
      return `  <url>\n    <loc>${loc}</loc>\n    <lastmod>${lastmod}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>`;
    })
    .join('\n');

  res.setHeader('Content-Type', 'application/xml; charset=utf-8');
  res.setHeader('Cache-Control', 'public, s-maxage=3600, stale-while-revalidate=7200');
  res.status(200).send(`<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`);
}

/* ─── GEO (public crawlable packs — Hobby: same function as blog) ─── */

function geoPublicUrl(runDate) {
  return `${SITE}/geo/${runDate}`;
}

const GEO_STATIC_COVERS = {
  '2026-07-18': `${SITE}/assets/geo-branded/geo-cover-2026-07-18.jpg`,
  '2026-07-19': `${SITE}/assets/geo-branded/geo-cover-2026-07-19.jpg`,
  '2026-07-20': `${SITE}/assets/geo-branded/geo-cover-2026-07-20.jpg`,
  '2026-07-21': `${SITE}/assets/geo-branded/geo-cover-2026-07-21.jpg`,
  '2026-07-22': `${SITE}/assets/geo-branded/geo-cover-2026-07-22.jpg`,
  '2026-07-23': `${SITE}/assets/geo-branded/geo-cover-2026-07-23.jpg`,
  '2026-07-24': `${SITE}/assets/geo-branded/geo-cover-2026-07-24.jpg`,
  '2026-07-25': `${SITE}/assets/geo-branded/geo-cover-2026-07-25.jpg`,
  '2026-07-26': `${SITE}/assets/geo-branded/geo-cover-2026-07-26.jpg`,
  '2026-07-27': `${SITE}/assets/geo-branded/geo-cover-2026-07-27.jpg`,
};

function geoCoverUrl(row) {
  return GEO_STATIC_COVERS[row.run_date] || brandedCoverUrl(row.prompt, row.bucket || 'GEO', 'geo');
}

function normalizeGeoFaq(faq) {
  if (!Array.isArray(faq)) return [];
  return faq
    .map((item) => ({
      q: String(item?.q || item?.question || '').trim(),
      a: String(item?.a || item?.answer || '').trim(),
    }))
    .filter((x) => x.q && x.a);
}

function normalizeGeoBullets(bullets) {
  if (!Array.isArray(bullets)) return [];
  return bullets.map((b) => String(b || '').trim()).filter(Boolean);
}

function normalizeGeoLinks(links) {
  if (!Array.isArray(links)) return [];
  return links.map((u) => String(u || '').trim()).filter(Boolean).slice(0, 8);
}

function fmtGeoDate(isoOrDate) {
  try {
    const d = String(isoOrDate || '').slice(0, 10);
    if (!d) return '';
    return new Date(`${d}T12:00:00Z`).toLocaleDateString('tr-TR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  } catch {
    return '';
  }
}

function geoLinkLabel(url) {
  const path = String(url || '')
    .replace(/^https?:\/\/(www\.)?nefalix\.com/i, '')
    .split('#')[0]
    .split('?')[0];
  if (!path || path === '/') return 'Ana sayfa';
  if (path === '/blog' || path.startsWith('/blog/')) return 'Blog';
  if (path === '/geo' || path.startsWith('/geo/')) return 'GEO paketleri';
  if (path.startsWith('/fiyatlar')) return 'Fiyatlandırma';
  if (path.startsWith('/sektorler')) return 'Sektörler';
  if (path.startsWith('/urunler')) return 'Ürünler';
  if (path.startsWith('/kaynaklar')) return 'Kaynaklar';
  if (path.startsWith('/hbys')) return 'HBYS entegrasyonu';
  return path.replace(/^\//, '').replace(/-/g, ' ');
}

function youtubeEmbedHtml(videoId, title) {
  const id = String(videoId || '').trim();
  if (!id || !/^[a-zA-Z0-9_-]{6,20}$/.test(id)) return '';
  const t = escapeHtml(title || 'Nefalix video');
  const watch = `https://www.youtube.com/watch?v=${id}`;
  return `<section class="geo-video" aria-label="İlgili video">
<h2>İlgili video</h2>
<div class="youtube-embed-wrap"><iframe src="https://www.youtube.com/embed/${id}?rel=0&modestbranding=1" title="${t}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe></div>
<p class="geo-video-meta"><a href="${watch}" target="_blank" rel="noopener noreferrer">${t}</a> · <a href="https://www.youtube.com/@Nefalixai" target="_blank" rel="noopener noreferrer">@Nefalixai</a></p>
</section>`;
}

async function geoNeighbors(runDate) {
  const rows = await sbRequest('GET', 'geo_daily_runs', {
    query: 'select=run_date,prompt&status=eq.published&order=run_date.desc&limit=120',
    prefer: 'return=representation',
  });
  const packs = Array.isArray(rows) ? rows : [];
  const idx = packs.findIndex((p) => p.run_date === runDate);
  return {
    newer: idx > 0 ? packs[idx - 1] : null,
    older: idx >= 0 && idx < packs.length - 1 ? packs[idx + 1] : null,
  };
}

function buildGeoPager(neighbors) {
  const { newer, older } = neighbors || {};
  if (!newer && !older) return '';
  const prev = older
    ? `<a class="geo-pager-link" href="${geoPublicUrl(older.run_date)}"><span class="geo-pager-kicker">← Önceki</span><span class="geo-pager-title">${escapeHtml(String(older.prompt || '').slice(0, 80))}</span></a>`
    : '<span class="geo-pager-spacer"></span>';
  const next = newer
    ? `<a class="geo-pager-link geo-pager-next" href="${geoPublicUrl(newer.run_date)}"><span class="geo-pager-kicker">Sonraki →</span><span class="geo-pager-title">${escapeHtml(String(newer.prompt || '').slice(0, 80))}</span></a>`
    : '<span class="geo-pager-spacer"></span>';
  return `<nav class="geo-pager" aria-label="Diğer GEO paketleri">${prev}${next}</nav>`;
}

function buildGeoBodyHtml(row, currentUrl) {
  const direct = escapeHtml(row.direct_answer || '');
  const bullets = normalizeGeoBullets(row.bullets);
  const faq = normalizeGeoFaq(row.faq);
  const links = normalizeGeoLinks(row.internal_links).filter((u) => u !== currentUrl);
  const parts = [];
  parts.push(`<p class="geo-answer-first"><strong>${direct}</strong></p>`);
  if (bullets.length) {
    parts.push('<ul class="geo-bullets">');
    for (const b of bullets) parts.push(`<li>${escapeHtml(b)}</li>`);
    parts.push('</ul>');
  }
  if (row.youtube_video_id) {
    parts.push(youtubeEmbedHtml(row.youtube_video_id, row.youtube_title));
  }
  if (faq.length) {
    parts.push('<section class="geo-faq" aria-label="Sık sorulanlar">');
    parts.push('<h2>Sık sorulanlar</h2>');
    for (const item of faq) {
      parts.push(
        `<div class="faq-item"><h3>${escapeHtml(item.q)}</h3><p>${escapeHtml(item.a)}</p></div>`
      );
    }
    parts.push('</section>');
  }
  if (links.length) {
    parts.push('<nav class="geo-links" aria-label="İlgili sayfalar"><h2>İlgili sayfalar</h2><div class="geo-link-chips">');
    for (const u of links) {
      const safe = escapeHtml(u);
      const label = geoLinkLabel(u);
      parts.push(`<a class="geo-link-chip" href="${safe}">${escapeHtml(label)}</a>`);
    }
    parts.push('</div></nav>');
  }
  return parts.join('\n');
}

function geoFaqPageJsonLd(row, url) {
  const faq = normalizeGeoFaq(row.faq);
  const graph = [
    {
      '@type': 'WebPage',
      '@id': url,
      url,
      name: row.prompt,
      description: row.direct_answer || '',
      datePublished: row.run_date,
      dateModified: row.run_date,
      isPartOf: { '@type': 'WebSite', name: 'Nefalix', url: SITE },
      about: { '@type': 'Organization', name: 'Nefalix', url: SITE },
    },
    {
      '@type': 'FAQPage',
      mainEntity: faq.map((item) => ({
        '@type': 'Question',
        name: item.q,
        acceptedAnswer: { '@type': 'Answer', text: item.a },
      })),
    },
  ];
  if (row.youtube_video_id) {
    graph.push({
      '@type': 'VideoObject',
      name: row.youtube_title || row.prompt,
      description: row.direct_answer || '',
      thumbnailUrl: `https://i.ytimg.com/vi/${row.youtube_video_id}/hqdefault.jpg`,
      uploadDate: row.run_date,
      embedUrl: `https://www.youtube.com/embed/${row.youtube_video_id}`,
      url: `https://www.youtube.com/watch?v=${row.youtube_video_id}`,
    });
  }
  return { '@context': 'https://schema.org', '@graph': graph };
}

async function loadGeoPacks(limit = 60) {
  const rows = await sbRequest('GET', 'geo_daily_runs', {
    query: `select=run_date,bucket,prompt,direct_answer,created_at&status=eq.published&order=run_date.desc&limit=${limit}`,
    prefer: 'return=representation',
  });
  return (Array.isArray(rows) ? rows : []).map((r) => ({
    run_date: r.run_date,
    bucket: r.bucket || '',
    prompt: r.prompt,
    excerpt: r.direct_answer,
    created_at: r.created_at,
    url: geoPublicUrl(r.run_date),
    cover_image_url: geoCoverUrl(r),
  }));
}

async function handleGeoList(req, res) {
  res.setHeader('Cache-Control', 'public, s-maxage=120, stale-while-revalidate=300');
  const limit = Math.min(Number(req.query.limit) || 60, 120);
  const packs = await loadGeoPacks(limit);
  res.status(200).json({ ok: true, packs });
}

function geoIndexCardHtml(p, { featured = false } = {}) {
  const tag = escapeHtml(p.bucket || 'GEO');
  const path = `/geo/${escapeHtml(p.run_date)}`;
  const cover = p.cover_image_url
    ? `<img class="${featured ? 'blog-featured-cover' : 'article-card-cover'}" src="${escapeHtml(p.cover_image_url)}" alt="" loading="${featured ? 'eager' : 'lazy'}">`
    : '';
  if (featured) {
    return `
      <a class="blog-featured-card" href="${path}">
        ${cover}
        <div class="blog-featured-copy">
          <span class="article-card-tag">${tag}</span>
          <h2>${escapeHtml(p.prompt)}</h2>
          <p>${escapeHtml(p.excerpt || '')}</p>
          <span class="article-card-meta">${escapeHtml(fmtIndexDate(`${String(p.run_date).slice(0, 10)}T12:00:00Z`))} · GEO · Paketi aç →</span>
        </div>
      </a>`;
  }
  return `
      <a class="article-card article-card-link" href="${path}">
        ${cover}
        <span class="article-card-tag">${tag}</span>
        <h3>${escapeHtml(p.prompt)}</h3>
        <p>${escapeHtml(p.excerpt || '')}</p>
        <span class="article-card-meta">${escapeHtml(fmtIndexDate(`${String(p.run_date).slice(0, 10)}T12:00:00Z`))} · GEO</span>
      </a>`;
}

async function handleGeoIndex(_req, res) {
  const packs = await loadGeoPacks(60);
  let html = readPublicHtml('geo.html');
  if (!html) {
    res.status(500).send('geo.html bulunamadı');
    return;
  }

  const countText = packs.length ? `${packs.length} GEO paketi` : 'Henüz GEO paketi yok';
  let featuredHtml = '';
  let gridHtml = '';
  if (!packs.length) {
    gridHtml =
      '<p style="color:var(--muted);grid-column:1/-1;">Henüz yayınlanmış GEO paketi yok.</p>';
  } else {
    const [featured, ...rest] = packs;
    featuredHtml = geoIndexCardHtml(featured, { featured: true });
    gridHtml = rest.map((p) => geoIndexCardHtml(p)).join('');
  }

  const itemList = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: 'GEO — Nefalix',
    url: `${SITE}/geo`,
    description:
      'Nefalix GEO: AI motorlarının alıntılayabileceği günlük soru-cevap paketleri.',
    mainEntity: {
      '@type': 'ItemList',
      numberOfItems: packs.length,
      itemListElement: packs.map((p, i) => ({
        '@type': 'ListItem',
        position: i + 1,
        url: p.url,
        name: p.prompt,
      })),
    },
  };
  const jsonLd = `<script type="application/ld+json">${JSON.stringify(itemList)}</script>`;

  html = html
    .replace(
      /<p class="blog-index-count" id="geo-index-count">[^<]*<\/p>/,
      `<p class="blog-index-count" id="geo-index-count">${escapeHtml(countText)}</p>`
    )
    .replace(
      /<div id="geo-featured" class="blog-featured" hidden><\/div>/,
      featuredHtml
        ? `<div id="geo-featured" class="blog-featured">${featuredHtml}</div>`
        : `<div id="geo-featured" class="blog-featured" hidden></div>`
    )
    .replace(
      /<div class="article-card-grid blog-index-grid" id="geo-pack-grid">[\s\S]*?<\/div>\s*<\/div>\s*<\/section>/,
      `<div class="article-card-grid blog-index-grid" id="geo-pack-grid">${gridHtml}</div>\n  </div>\n</section>`
    )
    .replace('</head>', `${jsonLd}\n</head>`);

  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'public, s-maxage=120, stale-while-revalidate=300');
  res.status(200).send(html);
}

async function handleGeoRender(req, res) {
  const date = String(req.query.date || req.query.slug || '').trim();
  if (!GEO_DATE_RE.test(date)) {
    res.status(400).send('Geçersiz tarih');
    return;
  }
  const rows = await sbRequest('GET', 'geo_daily_runs', {
    query: `run_date=eq.${encodeURIComponent(date)}&status=eq.published&select=run_date,bucket,prompt,direct_answer,bullets,faq,internal_links,linkedin_one_liner,youtube_video_id,youtube_title,answer_html,created_at&limit=1`,
    prefer: 'return=representation',
  });
  const row = Array.isArray(rows) ? rows[0] : null;
  if (!row) {
    res.status(404).send('GEO paketi bulunamadı');
    return;
  }

  const title = escapeHtml(row.prompt);
  const desc = escapeHtml((row.direct_answer || '').slice(0, 160));
  const bucket = escapeHtml(row.bucket || 'GEO');
  const dateLabel = fmtGeoDate(row.run_date);
  const url = geoPublicUrl(row.run_date);
  const neighbors = await geoNeighbors(row.run_date);
  const body = buildGeoBodyHtml(row, url);
  const pager = buildGeoPager(neighbors);
  const jsonLd = JSON.stringify(geoFaqPageJsonLd(row, url));
  const cover = geoCoverUrl(row);
  const coverEsc = escapeHtml(cover);

  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'public, s-maxage=600, stale-while-revalidate=3600');
  res.status(200).send(`<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="${desc}">
<link rel="canonical" href="${url}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Nefalix">
<meta property="og:title" content="${title}">
<meta property="og:description" content="${desc}">
<meta property="og:url" content="${url}">
<meta property="og:image" content="${coverEsc}">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">${jsonLd}</script>
<title>${title} — Nefalix GEO</title>
<link rel="icon" href="/assets/brand/favicon-192.png" type="image/png">
<link rel="stylesheet" href="/shared.css">
<style>
.geo-hero-img { width:100%; height:min(340px,42vw); object-fit:cover; border-radius:18px; margin:0 0 24px; box-shadow:0 18px 48px rgba(15,23,42,0.12); display:block; background:#0B1220; }
</style>
</head>
<body class="site-subpage geo-detail-body">
<nav class="site-nav-mount" aria-label="Ana menü"></nav>
<main class="geo-article-wrap">
  <a href="/geo" class="geo-back">← Tüm GEO paketleri</a>
  <article class="geo-article">
    <img class="geo-hero-img" src="${coverEsc}" alt="" width="1200" height="630" loading="eager">
    <span class="geo-article-tag">${bucket}</span>
    <h1>${title}</h1>
    <p class="geo-article-meta">${dateLabel} · Nefalix GEO</p>
    <div class="geo-article-body">${body}</div>
    ${pager}
    <footer class="geo-slim-footer">
      <a href="/blog">Blog</a>
      <span aria-hidden="true">·</span>
      <a href="/geo">GEO</a>
      <span aria-hidden="true">·</span>
      <a href="https://www.youtube.com/@Nefalixai" target="_blank" rel="noopener noreferrer">YouTube</a>
    </footer>
  </article>
</main>
<script src="/shared.js"></script>
</body>
</html>`);
}

async function handleGeoSitemap(_req, res) {
  const rows = await sbRequest('GET', 'geo_daily_runs', {
    query: 'select=run_date&status=eq.published&order=run_date.desc&limit=400',
    prefer: 'return=representation',
  });
  const packs = Array.isArray(rows) ? rows : [];
  const indexUrl = `  <url>\n    <loc>${SITE}/geo</loc>\n    <changefreq>daily</changefreq>\n    <priority>0.8</priority>\n  </url>`;
  const urls = packs
    .map((p) => {
      const loc = geoPublicUrl(xmlEscape(p.run_date));
      const lastmod = String(p.run_date || '').slice(0, 10);
      return `  <url>\n    <loc>${loc}</loc>\n    <lastmod>${lastmod}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.7</priority>\n  </url>`;
    })
    .join('\n');

  res.setHeader('Content-Type', 'application/xml; charset=utf-8');
  res.setHeader('Cache-Control', 'public, s-maxage=3600, stale-while-revalidate=7200');
  res.status(200).send(`<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${indexUrl}
${urls}
</urlset>`);
}

function socialPage(title, bodyHtml) {
  return `<!DOCTYPE html>
<html lang="tr"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escapeHtml(title)} — Nefalix</title>
<link rel="stylesheet" href="/shared.css">
</head>
<body class="site-subpage" style="padding:48px 20px;">
<div class="wrap" style="max-width:560px;margin:0 auto;text-align:center;">
<h1 style="font-size:1.75rem;margin-bottom:12px;">${escapeHtml(title)}</h1>
${bodyHtml}
<p style="margin-top:28px;"><a href="/" class="btn-ghost">Ana sayfaya dön</a></p>
</div>
</body></html>`;
}

async function findSocialByToken(token) {
  const rows = await sbRequest('GET', 'social_posts', {
    query: `approval_token=eq.${encodeURIComponent(token)}&select=id,status,approval_token,headline&limit=1`,
  });
  return Array.isArray(rows) && rows[0] ? rows[0] : null;
}

async function triggerSocialPublish(postId, token) {
  const url = (process.env.SOCIAL_PUBLISH_WEBHOOK_URL || 'https://api.nefalix.com/internal/social/publish').replace(/\/$/, '');
  const internalKey = process.env.NEFALIX_INTERNAL_KEY;
  if (!internalKey) throw new Error('NEFALIX_INTERNAL_KEY eksik (Vercel env)');
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Nefalix-Internal-Key': internalKey,
    },
    body: JSON.stringify({ post_id: postId, token }),
  });
  const text = await res.text();
  let payload = null;
  try {
    payload = text ? JSON.parse(text) : null;
  } catch {
    payload = { raw: text };
  }
  if (!res.ok) {
    throw new Error(payload?.error || payload?.message || text || `HTTP ${res.status}`);
  }
  return payload;
}

async function handleSocialApprove(req, res) {
  const token = String(req.query.token || '').trim();
  if (!token) {
    res.status(400).send(socialPage('Geçersiz link', '<p style="color:var(--muted);">Onay bağlantısı eksik veya hatalı.</p>'));
    return;
  }
  const post = await findSocialByToken(token);
  if (!post) {
    res.status(404).send(socialPage('Post bulunamadı', '<p style="color:var(--muted);">Bu onay linki artık geçerli değil.</p>'));
    return;
  }
  if (post.status === 'published') {
    res.status(200).send(socialPage('Zaten yayınlandı', '<p style="color:var(--muted);">Bu post daha önce yayınlanmış.</p>'));
    return;
  }
  if (post.status === 'rejected') {
    res.status(409).send(socialPage('Reddedilmiş', '<p style="color:var(--muted);">Bu post reddedilmiş; tekrar onaylanamaz.</p>'));
    return;
  }
  await sbRequest('PATCH', 'social_posts', {
    query: `id=eq.${post.id}`,
    body: { status: 'approved', updated_at: new Date().toISOString() },
    prefer: 'return=minimal',
  });
  const publishResult = await triggerSocialPublish(post.id, token);
  const row = publishResult?.results?.[0] || publishResult;
  const status = row?.status;
  let detail = '<p style="color:var(--muted);">Instagram ve LinkedIn paylaşımı tetiklendi.</p>';
  if (status === 'published') {
    detail = '<p style="color:#0d9488;font-weight:600;">Yayın tamamlandı (veya kısmen tamamlandı).</p>';
  } else if (status === 'failed') {
    detail = '<p style="color:#b45309;">Yayın sırasında hata oluştu. Yöneticilere mail gitti.</p>';
  } else if (status === 'approved') {
    detail = '<p style="color:#b45309;">API anahtarları eksik olabilir — post onaylandı ama otomatik yayın yapılamadı.</p>';
  }
  const ig = row?.instagram;
  const li = row?.linkedin;
  const extras = [];
  if (ig?.instagram_post_id) extras.push(`Instagram: ${escapeHtml(ig.instagram_post_id)}`);
  if (li?.linkedin_post_id) extras.push(`LinkedIn: ${escapeHtml(li.linkedin_post_id)}`);
  if (extras.length) detail += `<p style="font-size:13px;color:var(--muted);">${extras.join('<br>')}</p>`;
  res.status(200).send(socialPage('Onaylandı', detail));
}

async function handleSocialReject(req, res) {
  const token = String(req.query.token || '').trim();
  if (!token) {
    res.status(400).send(socialPage('Geçersiz link', '<p style="color:var(--muted);">Reddetme bağlantısı eksik.</p>'));
    return;
  }
  const post = await findSocialByToken(token);
  if (!post) {
    res.status(404).send(socialPage('Post bulunamadı', '<p style="color:var(--muted);">Bu link artık geçerli değil.</p>'));
    return;
  }
  if (post.status === 'pending_approval') {
    await sbRequest('PATCH', 'social_posts', {
      query: `id=eq.${post.id}`,
      body: { status: 'rejected', updated_at: new Date().toISOString() },
      prefer: 'return=minimal',
    });
  }
  res.status(200).send(socialPage('Paylaşım reddedildi', '<p style="color:var(--muted);">Bugünkü sosyal medya paylaşımı iptal edildi.</p>'));
}

const YOUTUBE_CHANNEL_ID = 'UCw8fkrtG_vSCXpA5-8KjHHg';
const YOUTUBE_RSS = `https://www.youtube.com/feeds/videos.xml?channel_id=${YOUTUBE_CHANNEL_ID}`;

function youtubeXmlDecode(s) {
  return String(s ?? '')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function parseYoutubeEntries(xml) {
  const entries = [];
  for (const block of xml.split('<entry>').slice(1)) {
    const id = (block.match(/<yt:videoId>([^<]+)<\/yt:videoId>/) || [])[1];
    const title = (block.match(/<title>([^<]+)<\/title>/) || [])[1];
    const published = (block.match(/<published>([^<]+)<\/published>/) || [])[1];
    const thumb = (block.match(/<media:thumbnail url="([^"]+)"/) || [])[1];
    if (!id || !title) continue;
    entries.push({
      id,
      title: youtubeXmlDecode(title),
      published_at: published || null,
      thumbnail: thumb || `https://i.ytimg.com/vi/${id}/hqdefault.jpg`,
      url: `https://www.youtube.com/watch?v=${id}`,
      embed_url: `https://www.youtube.com/embed/${id}?rel=0&modestbranding=1`,
    });
  }
  return entries;
}

async function handleYoutubeList(_req, res) {
  res.setHeader('Cache-Control', 'public, s-maxage=3600, stale-while-revalidate=86400');
  const r = await fetch(YOUTUBE_RSS, { headers: { 'User-Agent': 'NefalixSite/1' } });
  if (!r.ok) throw new Error(`RSS ${r.status}`);
  const videos = parseYoutubeEntries(await r.text());
  res.status(200).json({
    ok: true,
    channel_id: YOUTUBE_CHANNEL_ID,
    channel_url: 'https://www.youtube.com/@Nefalixai',
    videos,
  });
}

function coverHash(s) {
  let h = 2166136261;
  const str = String(s || '');
  for (let i = 0; i < str.length; i += 1) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

/**
 * Logolu, konuya özel üretilmiş kapak havuzu. Blog, GEO ve footer kapakları
 * aynı premium görsel setini tekrar kullanır; yeni üretim gerekirse buraya eklenir.
 */
const GENERATED_COVER_PHOTOS = [
  `${SITE}/assets/geo-branded/geo-cover-2026-07-18.jpg`,
  `${SITE}/assets/geo-branded/geo-cover-2026-07-19.jpg`,
  `${SITE}/assets/geo-branded/geo-cover-2026-07-20.jpg`,
  `${SITE}/assets/geo-branded/geo-cover-2026-07-21.jpg`,
  `${SITE}/assets/geo-branded/geo-cover-2026-07-22.jpg`,
  `${SITE}/assets/geo-branded/geo-cover-2026-07-23.jpg`,
  `${SITE}/assets/geo-branded/geo-cover-2026-07-24.jpg`,
  `${SITE}/assets/geo-branded/geo-cover-2026-07-25.jpg`,
  `${SITE}/assets/geo-branded/geo-cover-2026-07-26.jpg`,
  `${SITE}/assets/geo-branded/geo-cover-2026-07-27.jpg`,
];

function handleCover(req, res) {
  const kind = String(req.query.kind || 'blog');
  const tagRaw = String(req.query.tag || 'Rehber').slice(0, 40);
  const titleRaw = String(req.query.t || 'Nefalix').slice(0, 100);
  const seed = coverHash(`${tagRaw}|${titleRaw}|${kind}`);
  const photo = GENERATED_COVER_PHOTOS[seed % GENERATED_COVER_PHOTOS.length];

  res.setHeader('Cache-Control', 'public, s-maxage=86400, stale-while-revalidate=604800');
  res.setHeader('Location', photo);
  res.status(302).end();
}

const CRM_PAGE_FILES = {
  iletisim: 'iletisim.html',
  imza: 'iletisim-imza.html',
  kilavuz: 'iletisim-kilavuz.html',
  onizleme: 'iletisim-mail-onizleme.html',
  'toplu-mail': 'toplu-mail.html',
};

function crmLoginHtml(nextPath) {
  const next = String(nextPath || '/toplu-mail').replace(/"/g, '');
  return `<!DOCTYPE html><html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>CRM giriş · Nefalix</title>
<style>body{margin:0;font-family:Segoe UI,system-ui,sans-serif;background:#f2f2f9;color:#241854;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.box{max-width:400px;width:100%;background:#fff;border:1px solid #ece9f7;border-radius:14px;padding:28px;box-shadow:0 2px 10px rgba(20,20,60,.06)}
h1{margin:0 0 8px;font-size:20px}p{color:#8b87a8;font-size:13px;line-height:1.5}input{width:100%;padding:10px 12px;border:1px solid #d9d5ee;border-radius:9px;font-size:14px;box-sizing:border-box}
button{margin-top:12px;width:100%;border:none;border-radius:9px;padding:12px;font-weight:700;color:#fff;background:linear-gradient(135deg,#7c3aed,#2563eb);cursor:pointer}
a{color:#7c3aed;font-weight:600;text-decoration:none;font-size:13px}.err{color:#b91c1c;font-size:13px;margin-top:8px;display:none}</style></head><body>
<div class="box"><div style="font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:#8b87a8;font-weight:700;margin-bottom:8px">Nefalix CRM</div>
<h1>İç araç — giriş gerekli</h1>
<p>Mail / iletişim sayfaları dışarıya açık değil. CRM kullanıcı kodu ile girin.</p>
<label style="font-size:12px;font-weight:600;display:block;margin-bottom:6px">Kullanıcı kodu</label>
<input id="kod" placeholder="enes / abdulkadir / kader" autocomplete="username"/>
<div class="err" id="err"></div>
<button type="button" id="go">Giriş</button>
<p style="margin-top:16px"><a href="/nefalix-crm">← CRM’e git</a></p></div>
<script>
const next=${JSON.stringify(next)};
document.getElementById('go').onclick=async()=>{
  const kod=document.getElementById('kod').value.trim();
  const err=document.getElementById('err');
  err.style.display='none';
  try{
    const r=await fetch('/api/blog?action=crm-login',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({kod})});
    const d=await r.json().catch(()=>({}));
    if(!r.ok) throw new Error(d.error||'Giriş başarısız');
    location.href=next;
  }catch(e){err.textContent=e.message||'Hata';err.style.display='block';}
};
document.getElementById('kod').addEventListener('keydown',(e)=>{if(e.key==='Enter')document.getElementById('go').click();});
</script></body></html>`;
}

async function handleCrmPage(req, res) {
  const page = String(req.query.page || '').trim();
  const file = CRM_PAGE_FILES[page];
  if (!file) {
    res.status(404).send('Sayfa yok');
    return;
  }
  const session = verifyCrmSession(parseCookies(req)[CRM_COOKIE]);
  const nextPath =
    page === 'imza'
      ? '/iletisim/imza'
      : page === 'kilavuz'
        ? '/iletisim/kilavuz'
        : page === 'onizleme'
          ? '/iletisim/onizleme'
          : page === 'toplu-mail'
            ? '/toplu-mail'
            : page === 'iletisim'
              ? '/mail'
              : '/' + page;
  if (!session) {
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.setHeader('Cache-Control', 'private, no-store');
    res.status(401).send(crmLoginHtml(nextPath));
    return;
  }
  const full = join(process.cwd(), file);
  if (!existsSync(full)) {
    res.status(404).send('Dosya bulunamadı');
    return;
  }
  const html = readFileSync(full, 'utf8');
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Cache-Control', 'private, no-store');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  res.status(200).send(html);
}

/** Tek endpoint — Vercel Hobby function limiti */
export default async function handler(req, res) {
  const action = String(req.query.action || 'list');

  // Public başvuru + admin kuyruk (ayrı serverless function yok — Hobby limiti)
  if (action === 'firma-basvuru') {
    await firmaBasvuruHandler(req, res);
    return;
  }

  const crmActions = new Set([
    'crm-login',
    'crm-logout',
    'crm-me',
    'crm-get',
    'crm-save',
    'crm-notify-randevu',
    'crm-outreach',
    'crm-outreach-templates',
    'crm-outreach-status',
    'crm-whatsapp',
    'crm-page',
    'nfx-crm-get',
    'nfx-crm-save',
  ]);

  if (!crmActions.has(action) && !CLINIC_ACTIONS.has(action) && req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    if (action === 'list') {
      await handleList(req, res);
      return;
    }
    if (action === 'blog-index') {
      await handleBlogIndex(req, res);
      return;
    }
    if (action === 'render') {
      await handleRender(req, res);
      return;
    }
    if (action === 'sitemap') {
      await handleSitemap(req, res);
      return;
    }
    if (action === 'geo-list') {
      await handleGeoList(req, res);
      return;
    }
    if (action === 'geo-index') {
      await handleGeoIndex(req, res);
      return;
    }
    if (action === 'geo-render') {
      await handleGeoRender(req, res);
      return;
    }
    if (action === 'geo-sitemap') {
      await handleGeoSitemap(req, res);
      return;
    }
    if (action === 'social-approve') {
      await handleSocialApprove(req, res);
      return;
    }
    if (action === 'social-reject') {
      await handleSocialReject(req, res);
      return;
    }
    if (action === 'youtube-list') {
      await handleYoutubeList(req, res);
      return;
    }
    if (action === 'cover') {
      handleCover(req, res);
      return;
    }
    if (action === 'crm-login') {
      await handleCrmLogin(req, res);
      return;
    }
    if (action === 'crm-me') {
      await handleCrmMe(req, res);
      return;
    }
    if (action === 'crm-logout') {
      await handleCrmLogout(req, res);
      return;
    }
    if (action === 'crm-get') {
      await handleCrmGet(req, res);
      return;
    }
    if (action === 'crm-save') {
      await handleCrmSave(req, res);
      return;
    }
    if (action === 'crm-notify-randevu') {
      await handleCrmNotifyRandevu(req, res);
      return;
    }
    if (action === 'crm-outreach-templates') {
      await handleCrmOutreachTemplates(req, res);
      return;
    }
    if (action === 'crm-outreach') {
      await handleCrmOutreach(req, res);
      return;
    }
    if (action === 'crm-outreach-status') {
      await handleCrmOutreachStatus(req, res);
      return;
    }
    if (action === 'crm-whatsapp') {
      await handleCrmWhatsapp(req, res);
      return;
    }
    if (action === 'crm-page') {
      await handleCrmPage(req, res);
      return;
    }
    if (action === 'nfx-crm-get') {
      const session = verifyCrmSession(parseCookies(req)[CRM_COOKIE]);
      if (session) {
        const user = CRM_USERS.find((u) => u.kod === session.kod);
        if (user) setCrmCookie(res, signCrmSession(user));
      }
      await ensureNfxCrmRow();
      const data = await getNfxCrmData();
      if (!session) {
        return res.status(200).json({
          ok: true,
          data: { rev: data.rev, bag: {}, seedKurum: data.seedKurum || [] },
        });
      }
      return res.status(200).json({ ok: true, data });
    }
    if (action === 'nfx-crm-save') {
      if (req.method !== 'POST') return res.status(405).json({ error: 'POST gerekli' });
      if (!requireCrm(req, res)) return;
      const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : req.body || {};
      const data = body.data;
      if (!data || typeof data !== 'object') return res.status(400).json({ error: 'Geçersiz data' });
      const existing = await getNfxCrmData();
      const merged = {
        rev: Number(data.rev) || (existing.rev || 0) + 1,
        bag: data.bag && typeof data.bag === 'object' ? data.bag : existing.bag || {},
        seedKurum: Array.isArray(data.seedKurum) ? data.seedKurum : existing.seedKurum || [],
      };
      const rev = await saveNfxCrmData(merged);
      return res.status(200).json({ ok: true, rev });
    }
    if (CLINIC_ACTIONS.has(action)) {
      await handleClinicAction(action, req, res);
      return;
    }
    res.status(400).json({ error: 'Geçersiz action' });
  } catch (err) {
    if (action === 'render' || action === 'geo-render' || action === 'blog-index' || action === 'geo-index') {
      res.status(502).send(
        action === 'geo-render' || action === 'geo-index'
          ? `GEO yüklenemedi: ${escapeHtml(err.message)}`
          : `Blog yüklenemedi: ${escapeHtml(err.message)}`
      );
      return;
    }
    if (action === 'sitemap' || action === 'geo-sitemap') {
      res.status(502).send(`<!-- ${escapeHtml(err.message)} -->`);
      return;
    }
    if (action === 'social-approve' || action === 'social-reject') {
      res.status(502).send(
        socialPage('Yayın hatası', `<p style="color:#b45309;">${escapeHtml(err.message)}</p>`)
      );
      return;
    }
    if (crmActions.has(action) || CLINIC_ACTIONS.has(action)) {
      res.status(502).json({ error: 'CRM isteği başarısız', detail: err.message });
      return;
    }
    res.status(502).json({ error: 'Blog isteği başarısız', detail: err.message });
  }
}
