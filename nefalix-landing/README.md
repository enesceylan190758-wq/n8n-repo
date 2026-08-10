# nefalix-landing (kaynak — n8n-repo)

nefalix.com site + dashboard kaynak kodu. Arif / ekip buradan çalışır.

## Deploy (kritik)

Production **Git push ile basılmaz**. Canlı deploy yalnızca Mac CLI:

```bash
cd ~/nefalix-landing && npx vercel --prod --yes
```

`vercel.json` → `"git": { "deploymentEnabled": false }`

Vercel’i bu klasöre Production Git ile bağlama — geçmişte eksik tree siteyi silmişti (`directives/vercel_prod_safety.md`).

## Patch kit

Kartvizit vb. küçük patch’ler: `../landing-kit/` → sync script ile `~/nefalix-landing`.
