import { requireAuth } from '../_lib/auth.js';

export default async function handler(req, res) {
  const user = requireAuth(req, res);
  if (!user) return;

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const upstream = process.env.N8N_INBOX_CLEAR_URL;
  if (!upstream) {
    res.status(503).json({ error: 'Inbox temizleme API bağlı değil (N8N_INBOX_CLEAR_URL).' });
    return;
  }

  const { clinicId, clearAll } = req.body || {};
  const isAdmin = user.role === 'admin';

  if (clearAll && !isAdmin) {
    res.status(403).json({ error: 'Tüm firmaları temizleme yetkisi yok.' });
    return;
  }

  if (!isAdmin && clinicId && user.clinicId && clinicId !== user.clinicId) {
    res.status(403).json({ error: 'Bu firmayı temizleme yetkisi yok.' });
    return;
  }

  const targetClinicId = isAdmin ? clinicId || null : user.clinicId || clinicId || null;

  try {
    const apiRes = await fetch(upstream, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({
        clinicId: targetClinicId,
        clearAll: Boolean(clearAll && isAdmin),
        clearedBy: user.email,
      }),
    });
    const data = await apiRes.json().catch(() => ({}));
    if (!apiRes.ok) {
      res.status(apiRes.status).json({ error: data.message || 'Temizleme başarısız', detail: data });
      return;
    }
    const body = data?.deleted !== undefined ? data : data?.json ?? data?.[0]?.json ?? data;
    res.status(200).json(body);
  } catch (err) {
    res.status(502).json({ error: 'Inbox temizlenemedi', detail: err.message });
  }
}
