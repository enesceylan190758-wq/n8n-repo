const params = new URLSearchParams(window.location.search);
const token = params.get('token') || '';
const form = document.getElementById('setup-form');
const errEl = document.getElementById('setup-error');
const btn = document.getElementById('setup-btn');
const emailEl = document.getElementById('setup-email');

function showError(message) {
  errEl.textContent = message;
  errEl.classList.remove('hidden');
}

async function loadInvite() {
  if (!token) {
    showError('Kurulum linki eksik.');
    btn.disabled = true;
    return;
  }
  try {
    const res = await fetch(`/api/auth?action=setup&token=${encodeURIComponent(token)}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Kurulum linki geçersiz');
    emailEl.textContent = `${data.email} hesabı için şifre belirleyin.`;
  } catch (err) {
    showError(err.message);
    btn.disabled = true;
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  errEl.classList.add('hidden');
  const password = document.getElementById('password').value;
  const password2 = document.getElementById('password2').value;
  if (password !== password2) {
    showError('Şifreler eşleşmiyor.');
    return;
  }
  btn.disabled = true;
  btn.textContent = 'Kaydediliyor…';
  try {
    const res = await fetch('/api/auth?action=setup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Şifre oluşturulamadı');
    window.location.href = '/dashboard';
  } catch (err) {
    showError(err.message);
    btn.disabled = false;
    btn.textContent = 'Şifreyi oluştur';
  }
});

loadInvite();
