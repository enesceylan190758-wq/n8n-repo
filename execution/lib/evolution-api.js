/**
 * Evolution API helpers — Node (Vercel) ve dokümantasyon için ortak mantık.
 * Instance adı: küçük harf, rakam, tire; 3–50 karakter.
 */

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

export function evolutionConfig() {
  const base = (process.env.EVOLUTION_API_URL || 'https://evo.nefalixai.com').replace(/\/$/, '');
  const apiKey = process.env.EVOLUTION_API_KEY;
  if (!apiKey) throw new Error('EVOLUTION_API_KEY tanımlı değil (Vercel env)');
  const inboxWebhook =
    process.env.N8N_INBOX_INCOMING_URL ||
    'https://api.nefalixai.com/webhook/nefalix/inbox/incoming';
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

export async function fetchQrBase64(instance) {
  const data = await evoFetch(`/instance/connect/${encodeURIComponent(instance)}`);
  const b64 = data?.base64 || data?.qrcode?.base64 || data?.code || '';
  if (!b64 || b64 === 'null') {
    throw new Error('QR alınamadı — birkaç saniye sonra yenileyin');
  }
  const src = b64.startsWith('data:') ? b64 : `data:image/png;base64,${b64}`;
  return src;
}

export async function ensureInstance(instance) {
  try {
    await evoFetch(`/instance/connectionState/${encodeURIComponent(instance)}`);
    return;
  } catch {
    /* yoksa oluştur */
  }
  await evoFetch('/instance/create', {
    method: 'POST',
    body: {
      instanceName: instance,
      integration: 'WHATSAPP-BAILEYS',
      qrcode: true,
    },
  });
}

export async function resetInstance(instance) {
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
