/**
 * Nefalix CRM (kurum) — ortak state + login.
 * Tablo: nefalix_state id=2 (Saha id=1 ile karışmaz).
 */
import { sbCrmRequest } from './supabase.js';

export const NFX_CRM_STATE_ID = 2;

export const NFX_CRM_USERS = [
  { id: 'ak', kod: 'abdulkadir', ad: 'Abdülkadir Yaşar', rol: 'Kurucu · Saha' },
  { id: 'ak', kod: 'admin', ad: 'Abdülkadir Yaşar', rol: 'Yönetici' },
  { id: 'en', kod: 'enes', ad: 'Enes Ceylan', rol: 'CTO · Saha' },
  { id: 'kd', kod: 'kader', ad: 'Kader Hanım', rol: 'Arama & Randevu' },
  { id: 'dm', kod: 'demo', ad: 'Demo Kullanıcı', rol: 'Temsilci' },
  { id: 'mi', kod: 'destek', ad: 'Destek', rol: 'Destek' },
];

export function emptyNfxCrmData() {
  return { rev: 0, bag: {}, seedKurum: [] };
}

export async function ensureNfxCrmRow() {
  const rows = await sbCrmRequest('GET', 'nefalix_state', {
    query: `id=eq.${NFX_CRM_STATE_ID}&select=id,data,rev`,
    prefer: 'return=representation',
  });
  if (Array.isArray(rows) && rows[0]) return rows[0];
  await sbCrmRequest('POST', 'nefalix_state', {
    body: { id: NFX_CRM_STATE_ID, data: emptyNfxCrmData(), rev: 0 },
    prefer: 'return=minimal',
  });
  return { id: NFX_CRM_STATE_ID, data: emptyNfxCrmData(), rev: 0 };
}

export async function getNfxCrmData() {
  const row = await ensureNfxCrmRow();
  const data = row?.data && typeof row.data === 'object' ? row.data : emptyNfxCrmData();
  return { ...emptyNfxCrmData(), ...data, rev: row.rev ?? data.rev ?? 0 };
}

export async function saveNfxCrmData(data) {
  const rev = Number(data?.rev) || 1;
  const payload = {
    rev,
    bag: data.bag && typeof data.bag === 'object' ? data.bag : {},
    seedKurum: Array.isArray(data.seedKurum) ? data.seedKurum : [],
  };
  await sbCrmRequest('PATCH', 'nefalix_state', {
    query: `id=eq.${NFX_CRM_STATE_ID}`,
    body: { data: payload, rev },
    prefer: 'return=minimal',
  });
  return rev;
}
