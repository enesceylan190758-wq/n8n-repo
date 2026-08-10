const form = document.getElementById('login-form');
const errEl = document.getElementById('login-error');
const btn = document.getElementById('login-btn');

async function checkSession() {
  const res = await fetch('/api/auth?action=me');
  if (res.ok) window.location.href = '/dashboard';
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  errEl.classList.add('hidden');
  btn.disabled = true;
  btn.textContent = 'Giriş yapılıyor…';

  try {
    const res = await fetch('/api/auth?action=login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: document.getElementById('email').value.trim(),
        password: document.getElementById('password').value,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Giriş başarısız');
    window.location.href = '/dashboard';
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
    btn.disabled = false;
    btn.textContent = 'Giriş yap';
  }
});

checkSession();
