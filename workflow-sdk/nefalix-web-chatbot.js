import { workflow, trigger, node, languageModel, memory, newCredential } from '@n8n/workflow-sdk';

const SYSTEM_MESSAGE = `Sen Nefalix AI klinik asistanısın. Görevin hastalara ve ziyaretçilere operasyonel bilgi vermek ve randevu sürecine yardımcı olmaktır.

KURALLAR:
- Asla tıbbi teşhis koyma, reçete önerme veya tedavi garantisi verme.
- Sadece bilgilendirme amaçlı yanıt ver; belirsiz konularda hekim muayenesi sonrası netleşeceğini söyle.
- Randevu, konum, ulaşım, otel/VIP transfer, tedavi süreçleri, fiyatların muayene sonrası netleşeceği, KVKK/veri güvenliği konularında yardımcı ol.
- Randevu veya detaylı bilgi için telefon numarası iste; WhatsApp üzerinden ekibin iletişime geçeceğini belirt.
- Kullanıcının dilinde yanıt ver (Türkçe, İngilizce, Arapça).
- Kısa, profesyonel ve sıcak bir ton kullan.
- Kendini Nefalix AI olarak tanıt.`;

const chatMemory = memory({
  type: '@n8n/n8n-nodes-langchain.memoryBufferWindow',
  version: 1.4,
  config: {
    name: 'Conversation Memory',
    parameters: {
      sessionIdType: 'fromInput',
      contextWindowLength: 10,
    },
  },
});

const openAiModel = languageModel({
  type: '@n8n/n8n-nodes-langchain.lmChatOpenAi',
  version: 1.3,
  config: {
    name: 'OpenAI Chat Model',
    position: [520, 520],
    parameters: {
      model: { __rl: true, mode: 'list', value: 'gpt-5-mini' },
    },
    credentials: { openAiApi: newCredential('OpenAI account') },
  },
});

const webChatTrigger = trigger({
  type: '@n8n/n8n-nodes-langchain.chatTrigger',
  version: 1.4,
  config: {
    name: 'Web Chat',
    position: [240, 300],
    parameters: {
      public: true,
      mode: 'hostedChat',
      initialMessages:
        'Merhaba! Kliniğimize hoş geldiniz.\nİmplant, gülüş tasarımı veya randevu hakkında sorularınızı yazabilirsiniz.',
      options: {
        responseMode: 'streaming',
        title: 'Nefalix AI',
        subtitle: 'Klinik asistanınız — 7/24',
        inputPlaceholder: 'Sorunuzu yazın...',
        loadPreviousSession: 'memory',
      },
    },
    subnodes: { memory: chatMemory },
  },
  output: [{ sessionId: 'demo-session-1', chatInput: 'Merhaba, randevu almak istiyorum' }],
});

const nefalixAgent = node({
  type: '@n8n/n8n-nodes-langchain.agent',
  version: 3.1,
  config: {
    name: 'Nefalix Clinic Agent',
    position: [520, 300],
    parameters: {
      promptType: 'auto',
      options: {
        systemMessage: SYSTEM_MESSAGE,
        enableStreaming: true,
        maxIterations: 5,
      },
    },
    subnodes: {
      model: openAiModel,
      memory: chatMemory,
    },
  },
  output: [{ output: 'Merhaba! Randevu için size yardımcı olabilirim. Tercih ettiğiniz gün veya saat aralığını paylaşır mısınız?' }],
});

export default workflow('nefalix-web-chatbot', 'Nefalix AI - Web Chatbot')
  .add(webChatTrigger)
  .to(nefalixAgent);
