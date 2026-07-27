# Stella discovery (Git LFS)

Mac’teki ekran/Excel/ses paketi buraya zip olarak gider; cloud agent `git lfs pull` ile çeker.

## Mac’ten yükle (tek sefer)

```bash
cd ~/n8n-repo
# zip yoksa üret:
# cd .tmp && zip -r stella-discovery-2026-07-27.zip stella-discovery -x '*.DS_Store'
mkdir -p discovery
cp -f .tmp/stella-discovery-2026-07-27.zip discovery/
git lfs install
git add .gitattributes discovery/README.md discovery/stella-discovery-2026-07-27.zip
git commit -m "chore: Stella discovery zip via Git LFS (Mac → cloud)"
git push -u origin HEAD
```

## Cloud’da aç

```bash
git lfs pull
unzip -n discovery/stella-discovery-2026-07-27.zip -d .tmp/
# → .tmp/stella-discovery/
```

VPS kopyası hâlâ geçerli: `/opt/nefalix/.tmp/stella-discovery/`
