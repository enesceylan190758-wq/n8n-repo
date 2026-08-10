import { createHmac, randomBytes, scryptSync, timingSafeEqual } from 'crypto';
import { sbRequest } from './supabase.js';

export const COOKIE_NAME = 'nefalix_session';
const MAX_AGE_SEC = 60 * 60 * 24 * 7;

function b64url(input) {
  return Buffer.from(input).toString('base64url');
}

function fromB64url(str) {
  return Buffer.from(str, 'base64url').toString('utf8');
}

export function getUsers() {
  try {
    const parsed = JSON.parse(process.env.DASHBOARD_USERS || '[]');
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function verifyPassword(password, user) {
  const hash = scryptSync(password, user.salt, 64);
  const expected = Buffer.from(user.hash, 'base64');
  if (hash.length !== expected.length) return false;
  return timingSafeEqual(hash, expected);
}

export function hashPassword(password, salt = randomBytes(16).toString('base64')) {
  const hash = scryptSync(password, salt, 64).toString('base64');
  return { salt, hash };
}

export function setupToken() {
  return randomBytes(32).toString('base64url');
}

export function tokenHash(token) {
  const secret = process.env.DASHBOARD_SESSION_SECRET || 'nefalix-local';
  return createHmac('sha256', secret).update(String(token || '')).digest('base64url');
}

function publicUser(user) {
  return {
    email: user.email,
    role: user.role,
    firstName: user.firstName || user.first_name || '',
    lastName: user.lastName || user.last_name || '',
    phone: user.phone,
    clinicId: user.clinicId || user.clinic_id || null,
  };
}

async function findDbUser(normalized, password) {
  const rows = await sbRequest('GET', 'dashboard_users', {
    query: `email=eq.${encodeURIComponent(normalized)}&status=eq.active&select=email,role,first_name,last_name,phone,clinic_id,salt,password_hash&limit=1`,
  }).catch(() => []);
  const user = Array.isArray(rows) ? rows[0] : null;
  if (!user?.salt || !user?.password_hash) return null;
  const hash = scryptSync(password, user.salt, 64);
  const expected = Buffer.from(user.password_hash, 'base64');
  if (hash.length !== expected.length || !timingSafeEqual(hash, expected)) return null;
  return publicUser(user);
}

function findDevUser(normalized, password) {
  const devEmail = String(process.env.DEV_DASHBOARD_EMAIL || '').trim().toLowerCase();
  const devPassword = process.env.DEV_DASHBOARD_PASSWORD || '';
  if (!devEmail || !devPassword) return null;
  if (normalized !== devEmail || password !== devPassword) return null;
  return {
    email: devEmail,
    role: process.env.DEV_DASHBOARD_ROLE || 'admin',
    firstName: 'Geliştirici',
    lastName: 'Erişim',
    phone: '',
    clinicId: null,
  };
}

export async function findUser(email, password) {
  const normalized = String(email || '').trim().toLowerCase();
  const devUser = findDevUser(normalized, password);
  if (devUser) return devUser;
  // Klinik yöneticileri (clinic_id) Supabase'te — env JSON'dan önce dene
  const dbUser = await findDbUser(normalized, password);
  if (dbUser) return dbUser;
  const user = getUsers().find((u) => u.email.toLowerCase() === normalized);
  if (user && verifyPassword(password, user)) return publicUser(user);
  return null;
}

export function signSession(user) {
  const secret = process.env.DASHBOARD_SESSION_SECRET;
  if (!secret) throw new Error('DASHBOARD_SESSION_SECRET missing');
  const payload = {
    ...user,
    exp: Date.now() + MAX_AGE_SEC * 1000,
  };
  const body = b64url(JSON.stringify(payload));
  const sig = createHmac('sha256', secret).update(body).digest('base64url');
  return `${body}.${sig}`;
}

export function verifySession(token) {
  if (!token) return null;
  const secret = process.env.DASHBOARD_SESSION_SECRET;
  if (!secret) return null;
  const [body, sig] = token.split('.');
  if (!body || !sig) return null;
  const expected = createHmac('sha256', secret).update(body).digest('base64url');
  const a = Buffer.from(sig);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !timingSafeEqual(a, b)) return null;
  try {
    const payload = JSON.parse(fromB64url(body));
    if (!payload.exp || payload.exp < Date.now()) return null;
    return {
      email: payload.email,
      role: payload.role,
      firstName: payload.firstName,
      lastName: payload.lastName,
      phone: payload.phone,
      clinicId: payload.clinicId || null,
    };
  } catch {
    return null;
  }
}

export function parseCookies(req) {
  const raw = req.headers.cookie || '';
  return Object.fromEntries(
    raw.split(';').map((c) => {
      const [k, ...v] = c.trim().split('=');
      return [k, decodeURIComponent(v.join('='))];
    })
  );
}

export function setSessionCookie(res, token) {
  const secure = process.env.VERCEL === '1' ? '; Secure' : '';
  res.setHeader(
    'Set-Cookie',
    `${COOKIE_NAME}=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${MAX_AGE_SEC}${secure}`
  );
}

export function clearSessionCookie(res) {
  const secure = process.env.VERCEL === '1' ? '; Secure' : '';
  res.setHeader(
    'Set-Cookie',
    `${COOKIE_NAME}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0${secure}`
  );
}

export function requireAuth(req, res) {
  const cookies = parseCookies(req);
  const user = verifySession(cookies[COOKIE_NAME]);
  if (!user) {
    res.status(401).json({ error: 'Oturum gerekli. Lütfen giriş yapın.' });
    return null;
  }
  return user;
}
