import { requireAuth } from '../_lib/auth.js';

export default async function handler(req, res) {
  const user = requireAuth(req, res);
  if (!user) return;

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const { reviewId, replyText } = req.body || {};
  if (!reviewId || !replyText?.trim()) {
    res.status(400).json({ error: 'Yorum ID ve yanıt metni gerekli' });
    return;
  }

  const upstream = process.env.N8N_GOOGLE_REVIEW_APPROVE_URL;
  if (!upstream) {
    res.status(503).json({ error: 'Google yorum onay API bağlı değil (N8N_GOOGLE_REVIEW_APPROVE_URL).' });
    return;
  }

  try {
    const apiRes = await fetch(upstream, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({
        reviewId,
        replyText: replyText.trim(),
        sentBy: user.email,
      }),
    });
    const data = await apiRes.json().catch(() => ({}));
    if (!apiRes.ok) {
      res.status(apiRes.status).json({ error: data.message || data.error || 'Onay başarısız', detail: data });
      return;
    }
    const body = data?.ok !== undefined ? data : data?.json ?? data?.[0]?.json ?? data;
    res.status(200).json(body);
  } catch (err) {
    res.status(502).json({ error: 'Yanıt onaylanamadı', detail: err.message });
  }
}
