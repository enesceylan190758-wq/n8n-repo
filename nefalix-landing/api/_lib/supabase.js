/** Supabase service-role client (Vercel env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY) */

const PROXY_URL =
  process.env.N8N_SUPABASE_PROXY_URL ||
  'https://api.nefalix.com/webhook/nefalix/supabase-proxy';

export function sbConfig() {
  const url = (process.env.SUPABASE_URL || '').replace(/\/$/, '');
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY || '';
  if (!url || !key) return null;
  return { url, key };
}

/** Nefalix CRM cloud DB (nefalix_state). Dashboard/VPS proxy’den ayrı. */
export function sbCrmConfig() {
  const url = (
    process.env.SUPABASE_URL_PROD ||
    process.env.SUPABASE_CRM_URL ||
    ''
  ).replace(/\/$/, '');
  const key =
    process.env.SUPABASE_SERVICE_ROLE_KEY_PROD ||
    process.env.SUPABASE_CRM_SERVICE_ROLE_KEY ||
    '';
  if (!url || !key) return null;
  return { url, key };
}

function useProxy() {
  return !sbConfig() && process.env.N8N_SUPABASE_PROXY_URL !== '0';
}

async function sbProxyRequest(method, table, { query = '', body, prefer = 'return=representation' } = {}) {
  const internalKey = process.env.NEFALIX_INTERNAL_KEY;
  if (!internalKey) {
    throw new Error(
      'Supabase proxy yapılandırması eksik (NEFALIX_INTERNAL_KEY — Vercel env).'
    );
  }

  const res = await fetch(PROXY_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      'X-Nefalix-Internal-Key': internalKey,
    },
    body: JSON.stringify({ method, table, query, body, prefer }),
  });

  const text = await res.text();
  let payload = null;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }

  if (!res.ok) {
    const msg = payload?.message || payload?.error || text || `Proxy ${res.status}`;
    throw new Error(msg);
  }

  if (payload?.error) throw new Error(payload.error);
  return payload?.data ?? payload?.json?.data ?? payload;
}

async function sbDirectRequest(cfg, method, table, { query = '', body, prefer = 'return=representation' } = {}) {
  const headers = {
    apikey: cfg.key,
    Authorization: `Bearer ${cfg.key}`,
    'Content-Type': 'application/json',
    Prefer: prefer,
  };

  const res = await fetch(`${cfg.url}/rest/v1/${table}${query ? `?${query}` : ''}`, {
    method,
    headers,
    body: body != null ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const msg = data?.message || data?.error || data?.hint || `Supabase ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

export async function sbRequest(method, table, { query = '', body, prefer = 'return=representation' } = {}) {
  if (useProxy()) {
    return sbProxyRequest(method, table, { query, body, prefer });
  }

  const cfg = sbConfig();
  if (!cfg) {
    throw new Error('Supabase yapılandırması eksik (SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY)');
  }
  return sbDirectRequest(cfg, method, table, { query, body, prefer });
}

/** CRM → cloud Supabase; yoksa mevcut proxy/VPS yolu. */
export async function sbCrmRequest(method, table, opts = {}) {
  const crm = sbCrmConfig();
  if (crm) return sbDirectRequest(crm, method, table, opts);
  return sbRequest(method, table, opts);
}
