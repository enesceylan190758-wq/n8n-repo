# Yazılımcı erişim rehberi

Güvenilir geliştirici onboarding için **yapılandırılmış erişim paketi**.

## Tam erişim dosyası (şifreler dahil)

Gerçek kullanıcı adı / şifre / API key'ler **git'e commit edilmez**.

Kurucu şu dosyayı güvenli kanaldan paylaşır:

```
n8n-repo/.tmp/yazilimci-erisim.md
```

Dosya yoksa veya güncel değilse, kurucu Cursor'da şunu söyleyebilir:

> "Yazılımcı erişim paketini güncelle (.tmp/yazilimci-erisim.md)"

## Hızlı linkler (herkese açık)

| Ne | URL |
|----|-----|
| GitHub (backend) | https://github.com/enesceylan190758-wq/n8n-repo |
| Canlı site | https://nefalix.com |
| Dashboard | https://nefalix.com/dashboard/login |
| n8n prod | https://api.nefalix.com |
| Vercel proje | https://vercel.com → `nefalix-landing` |

## Invite checklist (kurucu)

- [ ] GitHub `n8n-repo` → Collaborator
- [ ] Vercel team → Developer (env read)
- [ ] VPS → SSH public key ekle
- [ ] `.tmp/yazilimci-erisim.md` paylaş (1Password / Signal)
- [ ] İş bitince `DEV_DASHBOARD_EMAIL` / `DEV_DASHBOARD_PASSWORD` Vercel'den sil

## Teknik referans

Detaylı mimari: [DEVELOPER_DASHBOARD.md](./DEVELOPER_DASHBOARD.md)
