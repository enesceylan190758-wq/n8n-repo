#!/usr/bin/env python3
"""nefalix-10 workflow jsCode — Vertex Gemini (OpenAI yerine)."""
import json
from pathlib import Path

JS = r'''const token = $env.GCP_ACCESS_TOKEN;
if (!token) throw new Error('GCP_ACCESS_TOKEN eksik — VPS: WRITE_GCP_TOKEN_TO_ENV=1 python3 execution/refresh-gcp-access-token.py');

const project = $env.GCP_PROJECT_ID || 'project-860dace6-d98e-44e1-994';
const region = $env.GCP_REGION || 'europe-west1';
const model = $env.VERTEX_GEMINI_MODEL || 'gemini-1.5-flash';

const sbBase = ($env.SUPABASE_URL || 'http://host.docker.internal:54321').replace(/\/$/, '');
const sbKey = $env.SUPABASE_SERVICE_ROLE_KEY;
const sbH = { apikey: sbKey, Authorization: `Bearer ${sbKey}`, 'Content-Type': 'application/json', Prefer: 'return=minimal' };

async function vertexJson(prompt, system) {
  const url = `https://${region}-aiplatform.googleapis.com/v1/projects/${project}/locations/${region}/publishers/google/models/${model}:generateContent`;
  const body = {
    contents: [{ role: 'user', parts: [{ text: prompt }] }],
    systemInstruction: { parts: [{ text: system || 'Sadece geçerli JSON döndür.' }] },
    generationConfig: { temperature: 0.4, maxOutputTokens: 2048, responseMimeType: 'application/json' },
  };
  const res = await this.helpers.httpRequest({
    method: 'POST',
    url,
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body,
    json: true,
  });
  const text = (res.candidates?.[0]?.content?.parts || []).map((p) => p.text || '').join('');
  if (!text.trim()) throw new Error('Vertex boş yanıt');
  return JSON.parse(text);
}

const clinics = await this.helpers.httpRequest({ method: 'GET', url: `${sbBase}/rest/v1/clinics?select=id,name`, headers: sbH, json: true });
const clinicMap = Object.fromEntries(clinics.map((c) => [c.id, c.name]));

const reviews = await this.helpers.httpRequest({
  method: 'GET',
  url: `${sbBase}/rest/v1/google_reviews?select=id,clinic_id,author_name,rating,review_text,draft_reply&status=eq.pending_approval&or=(draft_reply.is.null,draft_reply.eq.)&order=created_at.desc&limit=20`,
  headers: sbH,
  json: true,
});

let done = 0;
const errors = [];
for (const r of reviews) {
  if ((r.draft_reply || '').trim()) continue;
  const clinic = clinicMap[r.clinic_id] || 'Klinik';
  const prompt = `Google yorumu için klinik yanıt taslağı yaz.\n\nKlinik: ${clinic}\nYazar: ${r.author_name}\nPuan: ${r.rating}/5\nYorum: ${r.review_text}\n\nKVKK uyumlu, teşhis yok, max 80 kelime. Yorum dilinde yanıt ver.\nJSON: sentiment, themes[], draftReply, urgency`;
  try {
    const out = await vertexJson.call(this, prompt, 'Sen klinik itibar yöneticisisin. Sadece geçerli JSON döndür.');
    await this.helpers.httpRequest({
      method: 'PATCH',
      url: `${sbBase}/rest/v1/google_reviews?id=eq.${r.id}`,
      headers: sbH,
      body: { draft_reply: out.draftReply || '', sentiment: out.sentiment, themes: out.themes || [], urgency: out.urgency || 'low' },
      json: true,
    });
    done++;
  } catch (e) {
    errors.push({ id: r.id, error: e.message });
  }
}
return [{ json: { ok: true, drafted: done, total: reviews.length, errors, provider: 'vertex', model } }];
'''

def main():
    path = Path(__file__).resolve().parent.parent / "workflows" / "nefalix-10-google-review-drafts.json"
    data = json.loads(path.read_text())
    for node in data["nodes"]:
        if node.get("name") == "AI Taslak Üret":
            node["parameters"]["jsCode"] = JS.strip()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(f"✓ {path.name} → Vertex Gemini")


if __name__ == "__main__":
    main()
