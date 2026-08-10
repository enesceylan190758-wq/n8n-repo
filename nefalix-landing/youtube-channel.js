(function () {
  const FEATURED_ID = 'I9W_oyS_b1o';
  const CHANNEL_URL = 'https://www.youtube.com/@Nefalixai';

  function escapeHtml(s) {
    return String(s ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function fmtDate(iso) {
    try {
      return new Date(iso).toLocaleDateString('tr-TR', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      });
    } catch {
      return '';
    }
  }

  function cardHtml(v, { featured = false } = {}) {
    const tag = featured ? 'featured' : 'card';
    return `
      <a class="youtube-${tag}" href="${escapeHtml(v.url)}" target="_blank" rel="noopener noreferrer">
        <span class="youtube-thumb-wrap">
          <img src="${escapeHtml(v.thumbnail)}" alt="" loading="lazy" width="480" height="360">
          <span class="youtube-play" aria-hidden="true">▶</span>
        </span>
        <span class="youtube-copy">
          <strong>${escapeHtml(v.title)}</strong>
          ${v.published_at ? `<small>${escapeHtml(fmtDate(v.published_at))}</small>` : ''}
        </span>
      </a>`;
  }

  async function loadGrid(root) {
    const featuredId = root.dataset.featured || FEATURED_ID;
    const limit = parseInt(root.dataset.limit || '6', 10);
    root.innerHTML = '<p class="youtube-loading">Videolar yükleniyor…</p>';
    try {
      const res = await fetch('/api/youtube/list', { headers: { Accept: 'application/json' } });
      const data = await res.json();
      if (!data.ok || !data.videos?.length) throw new Error('empty');
      const videos = data.videos.slice(0, limit);
      const featured = videos.find((v) => v.id === featuredId) || videos[0];
      const rest = videos.filter((v) => v.id !== featured.id);
      root.innerHTML = `
        <div class="youtube-featured-slot">${cardHtml(featured, { featured: true })}</div>
        <div class="youtube-grid-rest">${rest.map((v) => cardHtml(v)).join('')}</div>
        <p class="youtube-channel-cta">
          <a href="${CHANNEL_URL}" target="_blank" rel="noopener noreferrer">Tüm videolar @Nefalixai →</a>
        </p>`;
    } catch {
      root.innerHTML = `
        <p class="youtube-fallback">Videolar şu an yüklenemedi.
          <a href="${CHANNEL_URL}" target="_blank" rel="noopener noreferrer">YouTube kanalımızı ziyaret edin →</a>
        </p>`;
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-youtube-grid]').forEach(loadGrid);
  });
})();
