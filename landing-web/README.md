# Canlı site review-gating metin düzeltmesi

Google işletme politikası: memnuniyet skoruna göre yorum davetini filtrelemek (review gating) yasak.

Bu klasördeki `index.html` ve `urunler.html`, canlı `nefalix.com` içeriğinin **policy-safe** sürümüdür.

## nefalix-landing'e uygula

```bash
cp landing-web/index.html   ~/nefalix-landing/index.html
cp landing-web/urunler.html ~/nefalix-landing/urunler.html
cd ~/nefalix-landing && npx vercel --prod
```

Veya tekrar üret:

```bash
python3 execution/patch-review-gating-site-copy.py --write landing-web
```

## Kaldırılan mantık (site metni)

- "memnunsa Google'a yönlendirir, değilse bildirim" (skora göre dallanma)
- "yorum öncesi insan müdahalesi" (yorumu engelleme ima eden dil)
- "Memnun hasta → yorum daveti" (eşit erişim vurgusu yok)

## Not

NPS workflow (promoter/detractor) ayrı kanal; site metni eşit yorum daveti ilkesini yansıtır.
