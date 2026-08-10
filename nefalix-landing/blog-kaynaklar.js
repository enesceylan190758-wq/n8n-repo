(function () {
  const grid = document.getElementById('blog-post-grid');
  if (!grid) return;

  const featuredEl = document.getElementById('blog-featured');
  const countEl = document.getElementById('blog-index-count');
  const filtersEl = document.getElementById('blog-tag-filters');
  const isBlogIndex = document.body.classList.contains('blog-index-body');
  const homeLimit = parseInt(grid.dataset.limit || '0', 10);
  const isHomeBlog = homeLimit > 0;

  let allPosts = [];
  let activeTag = 'all';

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

  function cardHtml(p, { featured = false } = {}) {
    const cover = p.cover_image_url
      ? `<img class="${featured ? 'blog-featured-cover' : 'article-card-cover'}" src="${escapeHtml(p.cover_image_url)}" alt="" loading="${featured ? 'eager' : 'lazy'}">`
      : '';
    if (featured) {
      return `
      <a class="blog-featured-card" href="/blog/${escapeHtml(p.slug)}">
        ${cover}
        <div class="blog-featured-copy">
          <span class="article-card-tag">${escapeHtml(p.tag)}</span>
          <h2>${escapeHtml(p.title)}</h2>
          <p>${escapeHtml(p.excerpt)}</p>
          <span class="article-card-meta">${escapeHtml(fmtDate(p.published_at))} · Blog · Okumaya devam et →</span>
        </div>
      </a>`;
    }
    return `
      <a class="article-card article-card-link" href="/blog/${escapeHtml(p.slug)}">
        ${cover}
        <span class="article-card-tag">${escapeHtml(p.tag)}</span>
        <h3>${escapeHtml(p.title)}</h3>
        <p>${escapeHtml(p.excerpt)}</p>
        <span class="article-card-meta">${escapeHtml(fmtDate(p.published_at))} · Blog</span>
      </a>`;
  }

  function uniqueTags(posts) {
    const tags = [];
    const seen = new Set();
    posts.forEach((p) => {
      const tag = (p.tag || 'Rehber').trim();
      if (!seen.has(tag)) {
        seen.add(tag);
        tags.push(tag);
      }
    });
    return tags;
  }

  function renderFilters(posts) {
    if (!filtersEl || !isBlogIndex || isHomeBlog) return;
    const tags = uniqueTags(posts);
    const buttons = [
      `<button type="button" class="blog-tag-btn ${activeTag === 'all' ? 'active' : ''}" data-tag="all">Tümü</button>`,
      ...tags.map(
        (tag) =>
          `<button type="button" class="blog-tag-btn ${activeTag === tag ? 'active' : ''}" data-tag="${escapeHtml(tag)}">${escapeHtml(tag)}</button>`
      ),
    ];
    filtersEl.innerHTML = buttons.join('');
    filtersEl.querySelectorAll('.blog-tag-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        activeTag = btn.getAttribute('data-tag') || 'all';
        render();
      });
    });
  }

  function render() {
    const filtered =
      activeTag === 'all'
        ? allPosts
        : allPosts.filter((p) => (p.tag || 'Rehber') === activeTag);

    if (countEl) {
      countEl.textContent = filtered.length
        ? `${filtered.length} yazı${activeTag !== 'all' ? ` · ${activeTag}` : ''}`
        : 'Yazı bulunamadı';
    }

    renderFilters(allPosts);

    if (!filtered.length) {
      if (featuredEl) {
        featuredEl.hidden = true;
        featuredEl.innerHTML = '';
      }
      grid.innerHTML =
        '<p class="blog-empty">Bu konuda henüz yazı yok. <a href="/blog">Tüm yazılara dön</a>.</p>';
      return;
    }

    if (isHomeBlog) {
      if (featuredEl) {
        featuredEl.hidden = true;
        featuredEl.innerHTML = '';
      }
      grid.innerHTML = filtered.slice(0, homeLimit).map((p) => cardHtml(p)).join('');
      if (!filtered.length) {
        grid.innerHTML =
          '<p class="blog-empty" style="grid-column:1/-1;">İlk yazılar yakında burada.</p>';
      }
      return;
    }

    if (isBlogIndex && featuredEl && activeTag === 'all') {
      const [featured, ...rest] = filtered;
      featuredEl.hidden = false;
      featuredEl.innerHTML = cardHtml(featured, { featured: true });
      grid.innerHTML = rest.map((p) => cardHtml(p)).join('') || '';
      if (!rest.length) {
        grid.innerHTML = '<p class="blog-empty" style="grid-column:1/-1;">Diğer yazılar yakında eklenecek.</p>';
      }
      return;
    }

    if (featuredEl) {
      featuredEl.hidden = true;
      featuredEl.innerHTML = '';
    }
    grid.innerHTML = filtered.map((p) => cardHtml(p)).join('');
  }

  const listLimit = isHomeBlog ? homeLimit : 50;
  fetch(`/api/blog/list?limit=${listLimit}`)
    .then((r) => r.json())
    .then((data) => {
      allPosts = data.posts || [];
      if (!allPosts.length) {
        if (countEl) countEl.textContent = 'Henüz yazı yok';
        if (featuredEl) featuredEl.hidden = true;
        grid.innerHTML =
          '<p class="blog-empty">İlk yazılar yakında burada. Günlük blog otomasyonu aktif.</p>';
        return;
      }
      render();
    })
    .catch(() => {
      // Keep SSR cards if present (no-JS / crawlable first paint).
      if (grid.querySelector('a.article-card-link, a.blog-featured-card')) return;
      if (countEl) countEl.textContent = '';
      grid.innerHTML =
        '<p class="blog-empty">Yazılar yüklenemedi. <a href="/blog">Sayfayı yenileyin</a>.</p>';
    });
})();
