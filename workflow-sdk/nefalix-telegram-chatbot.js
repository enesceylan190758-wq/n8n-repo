import { workflow, trigger, node, languageModel, memory, expr, newCredential, nodeJson } from '@n8n/workflow-sdk';

const SYSTEM_MESSAGE = `Sen Nefalix AI klinik asistanısın. Görevin hastalara ve ziyaretçilere operasyonel bilgi vermek ve randevu sürecine yardımcı olmaktır.

KURALLAR:
- Asla tıbbi teşhis koyma, reçete önerme veya tedavi garantisi verme.
- Sadece bilgilendirme amaçlı yanıt ver; belirsiz konularda hekim muayenesi sonrası netleşeceğini söyle.
- Randevu, konum, ulaşım, otel/VIP transfer, tedavi süreçleri, fiyatların muayene sonrası netleşeceği, KVKK/veri güvenliği konularında yardımcı ol.
- Randevu veya detaylı bilgi için telefon numarası iste; WhatsApp üzerinden ekibin iletişime geçeceğini belirt.
- Kullanıcının dilinde yanıt ver (Türkçe, İngilizce, Arapça).
- Kısa, profesyonel ve sıcak bir ton kullan.
- Kendini Nefalix AI olarak tanıt.`;

const telegramTrigger = trigger({
  type: 'n8n-nodes-base.telegramTrigger',
  version: 1.3,
  config: {
    name: 'Telegram Trigger',
    position: [240, 300],
    parameters: {
      updates: ['message'],
    },
    credentials: { telegramApi: newCredential('Telegram Bot') },
  },
  output: [
    {
      message: {
        message_id: 1,
        text: 'Merhaba, implant tedavisi hakkında bilgi alabilir miyim?',
        chat: { id: 8801497174, type: 'private' },
        from: { id: 8801497174, first_name: 'Test' },
      },
    },
  ],
});

const telegramMemory = memory({
  type: '@n8n/n8n-nodes-langchain.memoryBufferWindow',
  version: 1.4,
  config: {
    name: 'Telegram Memory',
    parameters: {
      sessionIdType: 'customKey',
      sessionKey: nodeJson(telegramTrigger, 'message.chat.id'),
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

const nefalixAgent = node({
  type: '@n8n/n8n-nodes-langchain.agent',
  version: 3.1,
  config: {
    name: 'Nefalix Clinic Agent',
    position: [520, 300],
    parameters: {
      promptType: 'define',
      text: expr('{{ $json.message.text }}'),
      options: {
        systemMessage: SYSTEM_MESSAGE,
        enableStreaming: false,
        maxIterations: 5,
      },
    },
    subnodes: {
      model: openAiModel,
      memory: telegramMemory,
    },
  },
  output: [{ output: 'Merhaba! İmplant tedavileri hakkında genel bilgi verebilirim. Detaylı planlama için ön muayene gereklidir.' }],
});

const sendTelegramReply = node({
  type: 'n8n-nodes-base.telegram',
  version: 1.2,
  config: {
    name: 'Send Telegram Reply',
    position: [800, 300],
    parameters: {
      resource: 'message',
      operation: 'sendMessage',
      chatId: expr('{{ $("Telegram Trigger").item.json.message.chat.id }}'),
      text: expr('{{ $json.output }}'),
      additionalFields: {
        appendAttribution: false,
        parse_mode: 'HTML',
      },
    },
    credentials: { telegramApi: newCredential('Telegram Bot') },
  },
  output: [{ ok: true }],
});

export default workflow('nefalix-telegram-chatbot', 'Nefalix AI - Telegram Chatbot')
  .add(telegramTrigger)
  .to(nefalixAgent)
  .to(sendTelegramReply);
