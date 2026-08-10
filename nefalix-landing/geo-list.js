(function () {
  const grid = document.getElementById('geo-pack-grid');
  if (!grid) return;

  const featuredEl = document.getElementById('geo-featured');
  const countEl = document.getElementById('geo-index-count');
  const limit = parseInt(grid.dataset.limit || '0', 10) || 60;

  function escapeHtml(s) {
    return String(s ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function fmtDate(iso) {
    try {
      const d = String(iso || '').slice(0, 10);
      return new Date(`${d}T12:00:00Z`).toLocaleDateString('tr-TR', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      });
    } catch {
      return '';
    }
  }

  function cardHtml(p, { featured = false } = {}) {
    const tag = escapeHtml(p.bucket || 'GEO');
    const cover = p.cover_image_url
      ? `<img class="${featured ? 'blog-featured-cover' : 'article-card-cover'}" src="${escapeHtml(p.cover_image_url)}" alt="" loading="${featured ? 'eager' : 'lazy'}">`
      : '';
    if (featured) {
      return `
      <a class="blog-featured-card" href="${escapeHtml(p.url)}">
        ${cover}
        <div class="blog-featured-copy">
          <span class="article-card-tag">${tag}</span>
          <h2>${escapeHtml(p.prompt)}</h2>
          <p>${escapeHtml(p.excerpt || '')}</p>
          <span class="article-card-meta">${escapeHtml(fmtDate(p.run_date))} · GEO · Paketi aç →</span>
        </div>
      </a>`;
    }
    return `
      <a class="article-card article-card-link" href="${escapeHtml(p.url)}">
        ${cover}
        <span class="article-card-tag">${tag}</span>
        <h3>${escapeHtml(p.prompt)}</h3>
        <p>${escapeHtml(p.excerpt || '')}</p>
        <span class="article-card-meta">${escapeHtml(fmtDate(p.run_date))} · GEO</span>
      </a>`;
  }

  fetch(`/api/geo/list?limit=${limit}`)
    .then((r) => r.json())
    .then((data) => {
      const packs = Array.isArray(data?.packs) ? data.packs : [];
      if (countEl) {
        countEl.textContent = packs.length
          ? `${packs.length} GEO paketi`
          : 'Henüz GEO paketi yok';
      }
      if (!packs.length) {
        if (featuredEl) {
          featuredEl.hidden = true;
          featuredEl.innerHTML = '';
        }
        grid.innerHTML =
          '<p style="color:var(--muted);grid-column:1/-1;">Henüz yayınlanmış GEO paketi yok.</p>';
        return;
      }
      if (featuredEl) {
        featuredEl.hidden = false;
        featuredEl.innerHTML = cardHtml(packs[0], { featured: true });
        grid.innerHTML = packs.slice(1).map((p) => cardHtml(p)).join('');
      } else {
        grid.innerHTML = packs.map((p) => cardHtml(p)).join('');
      }
    })
    .catch(() => {
      // Keep SSR cards if present (no-JS / crawlable first paint).
      if (grid.querySelector('a.article-card-link, a.blog-featured-card')) return;
      if (countEl) countEl.textContent = 'Paketler yüklenemedi';
      grid.innerHTML =
        '<p style="color:var(--muted);grid-column:1/-1;">GEO paketleri şu an yüklenemedi. <a href="/kaynaklar">Kaynaklar</a> sayfasına bakın.</p>';
    });
})();
