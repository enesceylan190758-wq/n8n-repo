/** Evolution API — Vercel serverless (EVOLUTION_API_KEY sunucuda kalır) */

export const INSTANCE_RE = /^[a-z0-9][a-z0-9-]{1,48}[a-z0-9]$/;

export function normalizeInstanceName(raw) {
  const s = String(raw || '')
    .toLowerCase()
    .replace(/[^a-z0-9-]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 50);
  if (!INSTANCE_RE.test(s)) {
    throw new Error('Geçersiz instance adı (ör. medident-pilot)');
  }
  return s;
}

function evolutionConfig() {
  const base = (process.env.EVOLUTION_API_URL || 'https://evo.nefalix.com').replace(/\/$/, '');
  const apiKey = process.env.EVOLUTION_API_KEY;
  if (!apiKey) {
    throw new Error('WhatsApp bağlantısı yapılandırılmamış (EVOLUTION_API_KEY).');
  }
  const inboxWebhook =
    process.env.N8N_INBOX_INCOMING_URL ||
    'https://api.nefalix.com/webhook/nefalix/inbox/incoming';
  return { base, apiKey, inboxWebhook };
}

export async function evoFetch(path, { method = 'GET', body } = {}) {
  const { base, apiKey } = evolutionConfig();
  const res = await fetch(`${base}${path}`, {
    method,
    headers: {
      apikey: apiKey,
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { raw: text };
  }
  if (!res.ok) {
    const msg = data?.message || data?.error || text || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

export async function connectionState(instance) {
  const data = await evoFetch(`/instance/connectionState/${encodeURIComponent(instance)}`);
  const state =
    data?.instance?.state || data?.state || data?.connectionStatus?.state || 'unknown';
  return String(state).toLowerCase();
}

async function fetchQrBase64(instance) {
  const data = await evoFetch(`/instance/connect/${encodeURIComponent(instance)}`);
  const b64 = data?.base64 || data?.qrcode?.base64 || data?.code || '';
  if (!b64 || b64 === 'null') {
    throw new Error('QR alınamadı — Yenile\'ye basın');
  }
  return b64.startsWith('data:') ? b64 : `data:image/png;base64,${b64}`;
}

async function ensureInstance(instance) {
  try {
    await evoFetch(`/instance/connectionState/${encodeURIComponent(instance)}`);
  } catch {
    await evoFetch('/instance/create', {
      method: 'POST',
      body: {
        instanceName: instance,
        integration: 'WHATSAPP-BAILEYS',
        qrcode: true,
      },
    });
  }
}

async function resetInstance(instance) {
  await evoFetch(`/instance/logout/${encodeURIComponent(instance)}`, { method: 'DELETE' }).catch(
    () => {}
  );
  await evoFetch(`/instance/delete/${encodeURIComponent(instance)}`, { method: 'DELETE' }).catch(
    () => {}
  );
  await ensureInstance(instance);
}

export async function configureInboxWebhook(instance) {
  const { inboxWebhook } = evolutionConfig();
  await evoFetch(`/webhook/set/${encodeURIComponent(instance)}`, {
    method: 'POST',
    body: {
      webhook: {
        enabled: true,
        url: inboxWebhook,
        webhookByEvents: false,
        webhookBase64: false,
        events: ['MESSAGES_UPSERT'],
      },
    },
  });
}

export async function fetchConnectedPhone(instance) {
  try {
    const rows = await evoFetch(
      `/instance/fetchInstances?instanceName=${encodeURIComponent(instance)}`
    );
    const list = Array.isArray(rows) ? rows : rows ? [rows] : [];
    const row = list[0] || {};
    const inst = row.instance && typeof row.instance === 'object' ? row.instance : row;
    const owner =
      row.ownerJid ||
      row.owner ||
      inst.ownerJid ||
      inst.owner ||
      row.number ||
      inst.number ||
      '';
    const digits = String(owner).split('@')[0].replace(/\D/g, '');
    if (digits.length >= 10) return `+${digits}`;
  } catch {
    /* optional */
  }
  return null;
}

export async function startQrSession(instance, { reset = false } = {}) {
  if (reset) await resetInstance(instance);
  else await ensureInstance(instance);

  const state = await connectionState(instance);
  if (state === 'open') {
    await configureInboxWebhook(instance);
    return { state: 'open', qr: null, connected: true };
  }

  const qr = await fetchQrBase64(instance);
  return { state, qr, connected: false };
}

export async function pollConnection(instance) {
  const state = await connectionState(instance);
  if (state === 'open') {
    await configureInboxWebhook(instance);
    return { state: 'open', connected: true, qr: null };
  }
  let qr = null;
  try {
    qr = await fetchQrBase64(instance);
  } catch {
    /* QR süresi dolmuş olabilir */
  }
  return { state, connected: false, qr };
}

function tsMs(v) {
  if (v == null) return 0;
  if (typeof v === 'number') return v < 1e12 ? v * 1000 : v;
  if (typeof v === 'object' && v.low != null) return Number(v.low) * 1000;
  const n = Date.parse(String(v));
  return Number.isFinite(n) ? n : 0;
}

export function extractMessageText(msg) {
  const m = msg?.message || {};
  if (typeof m.conversation === 'string' && m.conversation) return m.conversation;
  if (m.extendedTextMessage?.text) return String(m.extendedTextMessage.text);
  if (m.imageMessage) return m.imageMessage.caption || '[Fotoğraf]';
  if (m.videoMessage) return m.videoMessage.caption || '[Video]';
  if (m.audioMessage || m.pttMessage) return '[Ses]';
  if (m.documentMessage) return m.documentMessage.fileName || '[Dosya]';
  if (m.stickerMessage) return '[Sticker]';
  if (m.contactMessage) return '[Kişi kartı]';
  if (m.locationMessage) return '[Konum]';
  if (m.buttonsResponseMessage?.selectedDisplayText) {
    return String(m.buttonsResponseMessage.selectedDisplayText);
  }
  if (m.listResponseMessage?.title) return String(m.listResponseMessage.title);
  const t = String(msg?.messageType || '').replace(/Message$/, '');
  return t ? `[${t}]` : '';
}

function chatPreview(last) {
  if (!last) return '';
  return extractMessageText(last).slice(0, 120);
}

function displayName(chat) {
  const name = String(chat?.pushName || chat?.name || '').trim();
  if (name) return name;
  const jid = String(chat?.remoteJid || '');
  if (jid.endsWith('@g.us')) return 'Grup';
  if (jid.includes('@s.whatsapp.net')) return jid.split('@')[0];
  return jid || 'Sohbet';
}

export async function listChats(instance, { limit = 40 } = {}) {
  const data = await evoFetch(`/chat/findChats/${encodeURIComponent(instance)}`, {
    method: 'POST',
    body: {},
  });
  const rows = Array.isArray(data) ? data : [];
  const chats = rows
    .map((c) => {
      const remoteJid = String(c.remoteJid || c.id || '');
      if (!remoteJid) return null;
      const last = c.lastMessage || null;
      const updatedAt = c.updatedAt || last?.messageTimestamp;
      return {
        remoteJid,
        name: displayName(c),
        preview: chatPreview(last),
        updatedAt: updatedAt || null,
        updatedMs: tsMs(updatedAt),
        unread: Number(c.unreadCount || 0) || 0,
        isGroup: remoteJid.endsWith('@g.us'),
      };
    })
    .filter(Boolean)
    .sort((a, b) => b.updatedMs - a.updatedMs)
    .slice(0, Math.min(Number(limit) || 40, 80));
  return chats;
}

export async function listMessages(instance, remoteJid, { limit = 40 } = {}) {
  const jid = String(remoteJid || '').trim();
  if (!jid) throw new Error('remoteJid gerekli');
  const data = await evoFetch(`/chat/findMessages/${encodeURIComponent(instance)}`, {
    method: 'POST',
    body: {
      where: { key: { remoteJid: jid } },
      limit: Math.min(Number(limit) || 40, 100),
    },
  });
  let rows = [];
  if (Array.isArray(data)) rows = data;
  else if (Array.isArray(data?.messages)) rows = data.messages;
  else if (Array.isArray(data?.messages?.records)) rows = data.messages.records;
  else if (Array.isArray(data?.records)) rows = data.records;

  const messages = rows
    .map((m) => {
      const key = m.key || {};
      const fromMe = Boolean(key.fromMe);
      const text = extractMessageText(m);
      const ms = tsMs(m.messageTimestamp);
      return {
        id: key.id || m.id || `${ms}-${fromMe}`,
        fromMe,
        text,
        pushName: m.pushName || '',
        timestamp: ms || null,
        timeLabel: ms
          ? new Date(ms).toLocaleString('tr-TR', {
              day: '2-digit',
              month: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
            })
          : '',
      };
    })
    .filter((m) => m.text)
    .sort((a, b) => (a.timestamp || 0) - (b.timestamp || 0));
  return messages;
}

/** number: 905xxxxxxxxx veya remoteJid */
export async function sendTextMessage(instance, numberOrJid, text) {
  const raw = String(numberOrJid || '').trim();
  const bodyText = String(text || '').trim();
  if (!raw) throw new Error('Alıcı gerekli');
  if (!bodyText) throw new Error('Mesaj boş olamaz');

  let number = raw;
  if (raw.includes('@')) {
    number = raw.split('@')[0];
  } else {
    number = raw.replace(/\D/g, '');
    if (number.startsWith('0')) number = `90${number.slice(1)}`;
    if (number.length === 10) number = `90${number}`;
  }

  const data = await evoFetch(`/message/sendText/${encodeURIComponent(instance)}`, {
    method: 'POST',
    body: {
      number,
      text: bodyText,
    },
  });
  return data;
}
