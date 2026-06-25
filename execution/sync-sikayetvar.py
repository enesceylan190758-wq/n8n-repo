#!/usr/bin/env python3
"""Şikayetvar marka sayfası → yeni şikayetleri Sentinel webhook'a ilet.

KVKK: yalnızca şikayet başlığı, kısa özet ve public URL saklanır; kişisel veri çekilmez.

Gereksinim: clinics.sikayetvar_url dolu olmalı.

Kullanım:
  python3 execution/sync-sikayetvar.py
  python3 execution/sync-sikayetvar.py --clinic-id UUID
  python3 execution/sync-sikayetvar.py --dry-run
"""

from __future__ import annotations

import argparse
import html as htmlmod
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (compatible; NefalixSikayetvarSync/1.0)"
BRAND_COMPLAINT_RE = re.compile(
    r'title\\":\\"([^\\]+)\\",\\"href\\":\\"([^\\]+)\\"[^}]*complaintId\\":(\d+)'
)
EXCERPT_RE = re.compile(r'lg:inline">([^<]{40,4000})</span>')
CHILDREN_RE = re.compile(r'children\\":\\"([^\\]{80,4000})\\"')
DATE_RE = re.compile(r"(\d{1,2} [A-Za-zğüşıöçĞÜŞİÖÇ]+ \d{4}(?: \d{2}:\d{2})?)")
JINA_LINK_RE = re.compile(
    r"\[([^\]]+)\]\((https://www\.sikayetvar\.com/[^)\s]+)\s*(?:\"[^\"]*\")?\)"
)


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


REQUEST_DELAY_SEC = float(os.environ.get("SIKAYETVAR_REQUEST_DELAY_SEC", "2"))


def use_jina_mode() -> bool:
    mode = env("SIKAYETVAR_USE_JINA", "auto").lower()
    if mode in ("1", "true", "yes", "jina"):
        return True
    if mode in ("0", "false", "no", "direct"):
        return False
    return False  # auto: try direct first, 403 → jina in fetch_page


def http_get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode("utf-8", "ignore")


def fetch_page(url: str) -> tuple[str, str]:
    """Return (body, mode) where mode is direct or jina."""
    if use_jina_mode():
        return http_get(f"https://r.jina.ai/{url}"), "jina"
    try:
        return http_get(url), "direct"
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 429, 503):
            return http_get(f"https://r.jina.ai/{url}"), "jina"
        raise


def parse_brand_jina(text: str, profile_url: str) -> list[dict]:
    brand_path = urllib.parse.urlparse(profile_url).path.strip("/")
    seen: set[str] = set()
    out: list[dict] = []
    for title, url in JINA_LINK_RE.findall(text):
        path = urllib.parse.urlparse(url).path.strip("/")
        if not path.startswith(f"{brand_path}/") or path == brand_path:
            continue
        slug = path.rsplit("/", 1)[-1]
        ext_id = slug
        if ext_id in seen:
            continue
        seen.add(ext_id)
        clean_title = re.sub(r"\s+", " ", title).strip()
        excerpt = ""
        pos = text.find(url)
        if pos >= 0:
            tail = text[pos : pos + 1200]
            lines = [ln.strip() for ln in tail.splitlines() if ln.strip()]
            for ln in lines[2:6]:
                if ln.startswith("[") or ln.startswith("!") or "şikayet" in ln.lower()[:20]:
                    continue
                if len(ln) > 60:
                    excerpt = ln
                    break
        out.append(
            {
                "external_id": ext_id,
                "title": clean_title,
                "href": "/" + path,
                "url": url.split()[0],
                "excerpt": excerpt,
            }
        )
    return out


def supabase_key() -> str:
    return env(
        "SUPABASE_SERVICE_ROLE_KEY",
        env(
            "SUPABASE_ANON_KEY",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU",
        ),
    )


def supabase_base() -> str:
    return env("SUPABASE_URL", "http://127.0.0.1:54321").rstrip("/")


def webhook_base() -> str:
    return env("N8N_WEBHOOK_URL", env("WEBHOOK_URL", "http://127.0.0.1:5678/")).rstrip("/")


def sb_request(method: str, path: str, body: dict | list | None = None) -> object:
    url = f"{supabase_base()}/rest/v1/{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "apikey": supabase_key(),
            "Authorization": f"Bearer {supabase_key()}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode()
        raise RuntimeError(f"{method} {path}: {exc.code} {detail}") from exc


def parse_brand_complaints(html: str, profile_url: str = "", mode: str = "direct") -> list[dict]:
    if mode == "jina" or "Markdown Content:" in html:
        return parse_brand_jina(html, profile_url)
    seen: set[str] = set()
    out: list[dict] = []
    for title, href, cid in BRAND_COMPLAINT_RE.findall(html):
        if cid in seen:
            continue
        seen.add(cid)
        if not href.startswith("/"):
            href = "/" + href.lstrip("/")
        out.append(
            {
                "external_id": cid,
                "title": htmlmod.unescape(title),
                "href": href,
                "url": f"https://www.sikayetvar.com{href}",
            }
        )
    if not out and profile_url:
        return parse_brand_jina(html, profile_url)
    return out


def parse_complaint_excerpt(html: str, title: str, mode: str = "direct") -> tuple[str, str | None]:
    if mode == "jina" or "Markdown Content:" in html:
        for ln in html.splitlines():
            ln = ln.strip()
            if len(ln) < 80:
                continue
            low = ln.lower()
            if any(k in low for k in ("markdown content", "url source", "title:", "şikayetvar")):
                continue
            if title.lower()[:30] in low and len(ln) < len(title) + 30:
                continue
            if re.search(r"\d{2}\.\d{2}\.\d{4}", ln) or any(
                k in low for k in ("dolgu", "ağrı", "diş", "klinik", "mağdur", "işlem")
            ):
                return ln, None
        return title, None
    m = EXCERPT_RE.search(html)
    if m:
        text = htmlmod.unescape(m.group(1)).strip()
        if text and not text.startswith("..."):
            return text, None

    title_low = title.lower()
    for chunk in CHILDREN_RE.findall(html):
        text = htmlmod.unescape(chunk).strip()
        low = text.lower()
        if len(text) < 80:
            continue
        if title_low[:40] in low and len(text) < len(title) + 20:
            continue
        if any(k in low for k in ("şikayetvar", "tüm markalar", "404", "aydınlatma")):
            continue
        if any(k in low for k in ("dolgu", "ağrı", "diş", "klinik", "doktor", "hasta", "mağdur")):
            date_m = DATE_RE.search(html)
            return text, date_m.group(1) if date_m else None

    date_m = DATE_RE.search(html)
    return title, date_m.group(1) if date_m else None


def already_synced(clinic_id: str, external_id: str, url: str) -> bool:
    for query in (
        f"reputation_mentions?clinic_id=eq.{clinic_id}&source=eq.sikayetvar"
        f"&external_id=eq.{urllib.parse.quote(external_id)}&select=id&limit=1",
        f"reputation_mentions?clinic_id=eq.{clinic_id}&source=eq.sikayetvar"
        f"&url=eq.{urllib.parse.quote(url, safe='')}&select=id&limit=1",
    ):
        rows = sb_request("GET", query)
        if isinstance(rows, list) and rows:
            return True
    events = sb_request(
        "GET",
        "automation_events?"
        + urllib.parse.urlencode(
            {
                "clinic_id": f"eq.{clinic_id}",
                "event_type": "eq.sikayetvar_forwarded",
                "payload->>complaintId": f"eq.{external_id}",
                "select": "id",
                "limit": "1",
            }
        ),
    )
    return isinstance(events, list) and bool(events)


def forward_sentinel(clinic: dict, complaint: dict, content: str) -> None:
    payload = {
        "source": "sikayetvar",
        "platform": "sikayetvar",
        "clinic_id": clinic["id"],
        "brandName": clinic.get("name") or "Klinik",
        "text": content,
        "content": content,
        "url": complaint["url"],
        "external_id": complaint["external_id"],
    }
    req = urllib.request.Request(
        f"{webhook_base()}/webhook/nefalix/sentinel/mention",
        data=json.dumps(payload).encode(),
        method="POST",
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        resp.read()


def log_event(clinic_id: str, complaint: dict) -> None:
    sb_request(
        "POST",
        "automation_events",
        {
            "clinic_id": clinic_id,
            "workflow_name": "nefalix-14-sikayetvar-sync",
            "event_type": "sikayetvar_forwarded",
            "payload": {
                "complaintId": complaint["external_id"],
                "url": complaint["url"],
                "title": complaint.get("title"),
            },
        },
    )


def load_clinics(clinic_id: str | None) -> list[dict]:
    query = "select=id,name,sikayetvar_url,sikayetvar_synced_at&order=name.asc"
    if clinic_id:
        query += f"&id=eq.{clinic_id}"
    else:
        query += "&sikayetvar_url=not.is.null"
    rows = sb_request("GET", f"clinics?{query}")
    return rows or []


def sync_clinic(clinic: dict, dry_run: bool = False) -> dict:
    clinic_id = clinic["id"]
    name = clinic.get("name") or clinic_id
    profile_url = (clinic.get("sikayetvar_url") or "").strip()
    if not profile_url:
        return {"clinic_id": clinic_id, "name": name, "ok": False, "error": "sikayetvar_url yok"}

    print(f"▶ {name}")
    brand_html, fetch_mode = fetch_page(profile_url)
    complaints = parse_brand_complaints(brand_html, profile_url, fetch_mode)
    print(f"  {len(complaints)} şikayet listelendi ({fetch_mode})")

    new_count = 0
    skipped = 0
    errors: list[str] = []
    details: list[dict] = []

    for i, complaint in enumerate(complaints):
        if already_synced(clinic_id, complaint["external_id"], complaint["url"]):
            skipped += 1
            continue

        if i > 0:
            time.sleep(REQUEST_DELAY_SEC)

        try:
            if complaint.get("excerpt"):
                excerpt = complaint["excerpt"]
                posted_at = None
            else:
                detail_html, detail_mode = fetch_page(complaint["url"])
                excerpt, posted_at = parse_complaint_excerpt(
                    detail_html, complaint["title"], detail_mode
                )
            content = complaint["title"]
            if excerpt and excerpt != complaint["title"]:
                content = f"{complaint['title']}\n\n{excerpt}"
            complaint["posted_at"] = posted_at
            complaint["excerpt"] = excerpt

            if dry_run:
                print(f"  [dry-run] yeni: {complaint['external_id']} — {complaint['title'][:60]}")
                new_count += 1
                details.append({"id": complaint["external_id"], "dry_run": True})
                continue

            forward_sentinel(clinic, complaint, content)
            log_event(clinic_id, complaint)
            new_count += 1
            print(f"  ✓ Sentinel: {complaint['external_id']} — {complaint['title'][:50]}")
            details.append({"id": complaint["external_id"], "forwarded": True})
            time.sleep(REQUEST_DELAY_SEC)
        except Exception as exc:
            msg = f"{complaint['external_id']}: {exc}"
            errors.append(msg)
            print(f"  ✗ {msg}", file=sys.stderr)

    if not dry_run:
        sb_request(
            "PATCH",
            f"clinics?id=eq.{clinic_id}",
            {"sikayetvar_synced_at": datetime.now(timezone.utc).isoformat()},
        )

    return {
        "clinic_id": clinic_id,
        "name": name,
        "ok": True,
        "listed": len(complaints),
        "new": new_count,
        "skipped": skipped,
        "errors": errors,
        "details": details,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Şikayetvar → Sentinel senkron")
    parser.add_argument("--clinic-id", default=None, help="Tek klinik UUID")
    parser.add_argument("--dry-run", action="store_true", help="Sentinel çağırma, sadece listele")
    args = parser.parse_args()

    clinics = load_clinics(args.clinic_id)
    if not clinics:
        print("sikayetvar_url olan klinik bulunamadı", file=sys.stderr)
        return 1

    results = []
    for clinic in clinics:
        try:
            results.append(sync_clinic(clinic, dry_run=args.dry_run))
        except Exception as exc:
            print(f"  ✗ {exc}", file=sys.stderr)
            results.append(
                {
                    "clinic_id": clinic.get("id"),
                    "name": clinic.get("name"),
                    "ok": False,
                    "error": str(exc),
                }
            )

    ok = sum(1 for r in results if r.get("ok"))
    total_new = sum(r.get("new", 0) for r in results)
    print(f"\n{'═' * 50}")
    print(f"Şikayetvar senkron: {ok}/{len(results)} klinik | yeni iletilen: {total_new}")
    print(f"{'═' * 50}")

    summary = Path(__file__).resolve().parent.parent / ".tmp" / "sikayetvar-sync.json"
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    return 0 if ok == len(results) else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
