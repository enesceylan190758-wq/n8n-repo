#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { en, ar } = require('./i18n-data');

const LANG_SWITCHER = `            <div class="flex items-center gap-1 text-[11px] font-bold border border-slate-200 rounded-full p-0.5 bg-slate-50 shrink-0">
                <a href="/" class="lang-link px-2.5 py-1 rounded-full transition-colors">TR</a>
                <a href="/en" class="lang-link px-2.5 py-1 rounded-full transition-colors">EN</a>
                <a href="/ar" class="lang-link px-2.5 py-1 rounded-full transition-colors">AR</a>
            </div>`;

const RTL_CSS = `
        [dir="rtl"] { text-align: right; }
        [dir="rtl"] .text-center { text-align: center; }
        [dir="rtl"] .lg\\:text-left { text-align: right; }
        [dir="rtl"] .fa-arrow-right { transform: scaleX(-1); }
        [dir="rtl"] .rounded-tl-none { border-top-left-radius: 1rem; border-top-right-radius: 0; }
        [dir="rtl"] .rounded-tr-none { border-top-right-radius: 1rem; border-top-left-radius: 0; }
        [dir="rtl"] .self-start { align-self: flex-end; }
        [dir="rtl"] .self-end { align-self: flex-start; }
        [dir="rtl"] .border-l-2 { border-left: 0; border-right: 2px solid; }
`;

function stripSwitcher(html) {
  return html
    .replace(/\s*<!-- Language Switcher -->\s*<div class="hidden md:flex items-center">[\s\S]*?<\/div>\s*\n\s*<!-- Action Button/g, '\n            <!-- Action Button')
    .replace(/\s*<div class="flex justify-center pb-2">\s*<div class="flex items-center gap-1[\s\S]*?<\/div>\s*<\/div>\s*<div class="pt-4 border-t/g, '\n            <div class="pt-4 border-t')
    .replace(/ class="lang-link[^"]*"/g, ' class="lang-link px-2.5 py-1 rounded-full transition-colors"');
}

function injectChat(html) {
  const snippet = `
    <!-- Nefalix AI — canlı chatbot (n8n + OpenAI) -->
    <link href="https://cdn.jsdelivr.net/npm/@n8n/chat/dist/style.css" rel="stylesheet" />
    <link href="/nefalix-chat.css" rel="stylesheet" />
    <script type="module" src="/nefalix-chat.js"></script>`;
  if (html.includes('nefalix-chat.js')) return html;
  return html.replace('</body>', `${snippet}\n</body>`);
}

function injectSwitcher(html) {
  return stripSwitcher(html)
    .replace(
      '            <!-- Action Button Linked to Cal.com -->\n            <div class="hidden sm:flex items-center gap-4">',
      `            <!-- Language Switcher -->\n            <div class="hidden md:flex items-center">\n${LANG_SWITCHER}\n            </div>\n\n            <!-- Action Button Linked to Cal.com -->\n            <div class="hidden sm:flex items-center gap-4">`
    )
    .replace(
      '            <div class="pt-4 border-t border-slate-100 flex flex-col gap-3">',
      `            <div class="flex justify-center pb-2">\n${LANG_SWITCHER}\n            </div>\n            <div class="pt-4 border-t border-slate-100 flex flex-col gap-3">`
    );
}

function applyPairs(html, pairs) {
  const sorted = [...pairs].sort((a, b) => b[0].length - a[0].length);
  let out = html;
  for (const [from, to] of sorted) {
    out = out.split(from).join(to);
  }
  return out;
}

function highlightLang(html, lang) {
  const links = { tr: '/', en: '/en', ar: '/ar' };
  for (const [l, href] of Object.entries(links)) {
    const active = l === lang ? 'bg-brand-teal text-white' : 'text-slate-600 hover:text-brand-teal';
    const base = `href="${href}" class="lang-link px-2.5 py-1 rounded-full transition-colors`;
    const re = new RegExp(base.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '[^"]*"', 'g');
    html = html.replace(re, `${base} ${active}"`);
  }
  return html;
}

function buildAr(html) {
  let out = applyPairs(html, ar);
  if (!out.includes('dir="rtl"')) {
    out = out.replace('<html lang="tr"', '<html lang="ar" dir="rtl"');
  }
  if (!out.includes('[dir="rtl"]')) {
    out = out.replace('</style>', RTL_CSS + '\n    </style>');
  }
  out = out.replace(
    'family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap',
    'family=Noto+Sans+Arabic:wght@300;400;500;600;700;800&display=swap'
  );
  return out;
}

const raw = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const trBase = stripSwitcher(raw).replace(/<html[^>]*>/, '<html lang="tr" class="scroll-smooth">');

let trHtml = injectSwitcher(trBase);
trHtml = injectChat(trHtml);
trHtml = highlightLang(trHtml, 'tr');
fs.writeFileSync(path.join(__dirname, 'index.html'), trHtml);

let enHtml = injectSwitcher(trBase);
enHtml = injectChat(enHtml);
enHtml = applyPairs(enHtml, en);
enHtml = highlightLang(enHtml, 'en');
fs.writeFileSync(path.join(__dirname, 'en.html'), enHtml);

let arHtml = injectSwitcher(trBase);
arHtml = injectChat(arHtml);
arHtml = buildAr(arHtml);
arHtml = highlightLang(arHtml, 'ar');
fs.writeFileSync(path.join(__dirname, 'ar.html'), arHtml);

console.log('Built: index.html (TR), en.html, ar.html');
