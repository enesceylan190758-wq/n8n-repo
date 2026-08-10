import { createChat } from 'https://cdn.jsdelivr.net/npm/@n8n/chat/dist/chat.bundle.es.js';

const WEBHOOK_URL =
  'https://api.nefalix.com/webhook/f34b5627-5f5a-4033-963c-5e51067eb141/chat';

const lang = (document.documentElement.lang || 'tr').split('-')[0];

const copy = {
  tr: {
    title: 'Nefalix',
    subtitle: 'Diş kliniği asistanınız — 7/24',
    inputPlaceholder: 'Sorunuzu yazın...',
    getStarted: 'Sohbeti başlat',
    footer: 'KVKK uyumlu · Tıbbi teşhis koymaz',
    initialMessages: [
      'Merhaba! 👋',
      'İmplant, gülüş tasarımı, diş beyazlatma veya randevu hakkında sorularınızı yazabilirsiniz.',
    ],
  },
  en: {
    title: 'Nefalix',
    subtitle: 'Your dental clinic assistant — 24/7',
    inputPlaceholder: 'Type your question...',
    getStarted: 'Start chat',
    footer: 'KVKK compliant · No medical diagnosis',
    initialMessages: [
      'Hello! 👋',
      'Ask about implants, smile design, whitening, or booking an appointment.',
    ],
  },
  ar: {
    title: 'Nefalix',
    subtitle: 'مساعد عيادة الأسنان — على مدار الساعة',
    inputPlaceholder: 'اكتب سؤالك...',
    getStarted: 'ابدأ المحادثة',
    footer: 'متوافق مع KVKK · لا تشخيص طبي',
    initialMessages: [
      'مرحباً! 👋',
      'اسأل عن الزراعة أو تصميم الابتسامة أو التبييض أو حجز موعد.',
    ],
  },
};

const t = copy[lang] || copy.tr;

createChat({
  webhookUrl: WEBHOOK_URL,
  mode: 'window',
  loadPreviousSession: false,
  enableStreaming: false,
  showWelcomeScreen: false,
  defaultLanguage: lang === 'ar' ? 'ar' : lang === 'en' ? 'en' : 'tr',
  initialMessages: t.initialMessages,
  i18n: {
    [lang]: {
      title: t.title,
      subtitle: t.subtitle,
      footer: t.footer,
      getStarted: t.getStarted,
      inputPlaceholder: t.inputPlaceholder,
    },
  },
  metadata: {
    source: 'nefalix.com',
    clinicType: 'dental',
    lang,
  },
});
