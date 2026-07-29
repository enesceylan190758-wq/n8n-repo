/** GEO sitemap — yalnızca run_date <= bugün (future-dated URL yok). HEAD destekli. */
const SITE = "https://nefalix.com";

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

async function fetchRuns(req) {
  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey =
    process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;

  if (supabaseUrl && supabaseKey) {
    const url = new URL(`${supabaseUrl.replace(/\/$/, "")}/rest/v1/geo_daily_runs`);
    url.searchParams.set("select", "run_date");
    url.searchParams.set("status", "eq.published");
    url.searchParams.set("order", "run_date.desc");
    url.searchParams.set("limit", "500");
    const resp = await fetch(url, {
      headers: {
        apikey: supabaseKey,
        Authorization: `Bearer ${supabaseKey}`,
      },
    });
    if (!resp.ok) {
      throw new Error(`Supabase ${resp.status}`);
    }
    return resp.json();
  }

  const proto = req.headers["x-forwarded-proto"] || "https";
  const host = req.headers.host || "nefalix.com";
  const resp = await fetch(`${proto}://${host}/api/geo/list?limit=500`);
  if (!resp.ok) {
    throw new Error(`geo list ${resp.status}`);
  }
  const data = await resp.json();
  return Array.isArray(data) ? data : data.items || data.runs || [];
}

function buildXml(rows, today) {
  const urls = rows
    .filter((row) => row.run_date && row.run_date <= today)
    .map(
      (row) =>
        `  <url><loc>${SITE}/geo/${row.run_date}</loc><changefreq>weekly</changefreq></url>`
    );
  return (
    '<?xml version="1.0" encoding="UTF-8"?>\n' +
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    urls.join("\n") +
    "\n</urlset>"
  );
}

module.exports = async (req, res) => {
  res.setHeader("Content-Type", "application/xml; charset=utf-8");
  res.setHeader("Cache-Control", "s-maxage=3600, stale-while-revalidate");

  if (req.method === "HEAD") {
    res.status(200).end();
    return;
  }
  if (req.method !== "GET") {
    res.status(405).end();
    return;
  }

  try {
    const today = todayIso();
    const rows = await fetchRuns(req);
    res.status(200).send(buildXml(rows, today));
  } catch (err) {
    res.status(500).send(`<!-- geo-sitemap error: ${err.message} -->`);
  }
};
