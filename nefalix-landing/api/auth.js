import { clearSessionCookie, findUser, parseCookies, setSessionCookie, signSession, verifySession } from './_lib/auth.js';
import { hashPassword, tokenHash } from './_lib/auth.js';
import { sbRequest } from './_lib/supabase.js';

async function findInvite(token) {
  const hash = tokenHash(token);
  const rows = await sbRequest('GET', 'dashboard_users', {
    query: `setup_token_hash=eq.${encodeURIComponent(hash)}&status=eq.pending&select=id,email,role,first_name,last_name,phone,clinic_id,setup_token_expires_at&limit=1`,
  });
  const user = Array.isArray(rows) ? rows[0] : null;
  if (!user) return null;
  if (!user.setup_token_expires_at || new Date(user.setup_token_expires_at).getTime() < Date.now()) return null;
  return user;
}

export default async function handler(req, res) {
  const action = String(req.query?.action || '').trim();

  if (action === 'me') {
    const user = verifySession(parseCookies(req).nefalix_session);
    if (!user) return res.status(401).json({ error: 'Oturum gerekli. Lütfen giriş yapın.' });
    return res.status(200).json({ user });
  }

  if (action === 'logout') {
    clearSessionCookie(res);
    return res.status(200).json({ ok: true });
  }

  if (action === 'demo') {
    if (req.method !== 'GET') return res.status(405).json({ error: 'Method not allowed' });
    const expected = process.env.DASHBOARD_DEMO_TOKEN;
    if (!expected) return res.status(503).json({ error: 'Demo giriş şu an kapalı.' });
    const token = String(req.query?.token || '').trim();
    if (!token || token !== expected) return res.status(403).json({ error: 'Geçersiz demo bağlantısı.' });
    const user = {
      email: 'demo@nefalix.com',
      role: 'admin',
      firstName: 'Demo',
      lastName: 'Erişim',
      phone: '',
      clinicId: null,
    };
    setSessionCookie(res, signSession(user));
    res.writeHead(302, { Location: '/dashboard' });
    return res.end();
  }

  if (action === 'setup') {
    const token = String(req.query?.token || req.body?.token || '').trim();
    if (!token) return res.status(400).json({ error: 'Kurulum token gerekli' });
    try {
      const invite = await findInvite(token);
      if (!invite) return res.status(404).json({ error: 'Kurulum linki geçersiz veya süresi dolmuş' });
      if (req.method === 'GET') {
        return res.status(200).json({ email: invite.email, firstName: invite.first_name, lastName: invite.last_name });
      }
      if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
      const password = req.body?.password;
      if (!password || password.length < 8) return res.status(400).json({ error: 'Şifre en az 8 karakter olmalı' });
      const { salt, hash } = hashPassword(password);
      const updated = await sbRequest('PATCH', 'dashboard_users', {
        query: `id=eq.${invite.id}`,
        body: {
          salt,
          password_hash: hash,
          setup_token_hash: null,
          setup_token_expires_at: null,
          status: 'active',
          password_set_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        prefer: 'return=representation',
      });
      const row = Array.isArray(updated) ? updated[0] : updated;
      const user = {
        email: row.email,
        role: row.role,
        firstName: row.first_name || '',
        lastName: row.last_name || '',
        phone: row.phone || '',
        clinicId: row.clinic_id || null,
      };
      setSessionCookie(res, signSession(user));
      return res.status(200).json({ ok: true, user });
    } catch (err) {
      return res.status(500).json({ error: err.message || 'Şifre oluşturulamadı' });
    }
  }

  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  const { email, password } = req.body || {};
  if (!email || !password) return res.status(400).json({ error: 'E-posta ve şifre gerekli' });
  const user = await findUser(email, password);
  if (!user) return res.status(401).json({ error: 'E-posta veya şifre hatalı' });
  setSessionCookie(res, signSession(user));
  return res.status(200).json({ user });
}
