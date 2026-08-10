/**
 * Nefalix Modül 1: Feedback & Reviews Loop
 * HBYS randevu bitti → WhatsApp NPS → Promoter/Detractor yönlendirme
 */
import {
  workflow,
  trigger,
  node,
  languageModel,
  ifElse,
  sticky,
  newCredential,
  expr,
} from '@n8n/workflow-sdk';

const openAiModel = languageModel({
  type: '@n8n/n8n-nodes-langchain.lmChatOpenAi',
  version: 1.3,
  config: {
    name: 'OpenAI Chat Model',
    position: [640, 520],
    parameters: {
      model: { __rl: true, mode: 'list', value: 'gpt-4o-mini' },
    },
    credentials: { openAiApi: newCredential('OpenAI account') },
  },
});

const hbysWebhook = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2.1,
  config: {
    name: 'HBYS Randevu Bitti',
    position: [240, 300],
    parameters: {
      path: 'nefalix/hbys/appointment-completed',
      httpMethod: 'POST',
      responseMode: 'onReceived',
      options: {},
    },
  },
  output: [
    {
      body: {
        patientName: 'Ayşe Yılmaz',
        patientPhone: '+905551234567',
        clinicId: 'medident-kartal',
        clinicName: 'MediDent İstanbul',
        doctorName: 'Dr. Mehmet Kaya',
        treatment: 'implant muayenesi',
        appointmentId: 'APT-2026-001',
        googleReviewUrl: 'https://g.page/r/example/review',
        complaintFormUrl: 'https://nefalix.com/sikayet',
      },
    },
  ],
});

const normalizePayload = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Normalize HBYS Payload',
    position: [460, 300],
    parameters: {
      mode: 'manual',
      includeOtherFields: false,
      assignments: {
        assignments: [
          { id: '1', name: 'patientName', value: expr('{{ $json.body?.patientName ?? $json.patientName }}'), type: 'string' },
          { id: '2', name: 'patientPhone', value: expr('{{ $json.body?.patientPhone ?? $json.patientPhone }}'), type: 'string' },
          { id: '3', name: 'clinicName', value: expr('{{ $json.body?.clinicName ?? $json.clinicName ?? "Klinik" }}'), type: 'string' },
          { id: '4', name: 'doctorName', value: expr('{{ $json.body?.doctorName ?? $json.doctorName ?? "" }}'), type: 'string' },
          { id: '5', name: 'treatment', value: expr('{{ $json.body?.treatment ?? $json.treatment ?? "" }}'), type: 'string' },
          { id: '6', name: 'googleReviewUrl', value: expr('{{ $json.body?.googleReviewUrl ?? $json.googleReviewUrl }}'), type: 'string' },
          { id: '7', name: 'complaintFormUrl', value: expr('{{ $json.body?.complaintFormUrl ?? $json.complaintFormUrl }}'), type: 'string' },
          { id: '8', name: 'appointmentId', value: expr('{{ $json.body?.appointmentId ?? $json.appointmentId }}'), type: 'string' },
        ],
      },
    },
  },
  output: [
    {
      patientName: 'Ayşe Yılmaz',
      patientPhone: '+905551234567',
      clinicName: 'MediDent İstanbul',
      doctorName: 'Dr. Mehmet Kaya',
      treatment: 'implant muayenesi',
      googleReviewUrl: 'https://g.page/r/example/review',
      complaintFormUrl: 'https://nefalix.com/sikayet',
      appointmentId: 'APT-2026-001',
    },
  ],
});

const npsMessageAgent = node({
  type: '@n8n/n8n-nodes-langchain.agent',
  version: 3.1,
  config: {
    name: 'AI NPS Mesajı Üret',
    position: [680, 300],
    parameters: {
      promptType: 'define',
      text: expr(
        'Hasta: {{ $json.patientName }}, Klinik: {{ $json.clinicName }}, Doktor: {{ $json.doctorName }}, Tedavi: {{ $json.treatment }}. WhatsApp ile KVKK uyumlu, samimi bir NPS anketi yaz. 1-10 arası puan iste. Türkçe, max 3 cümle. Sadece mesaj metnini döndür.'
      ),
      options: { maxIterations: 3, enableStreaming: false },
    },
    subnodes: { model: openAiModel },
  },
  output: [{ output: 'Merhaba Ayşe Hanım, MediDent deneyiminizi 1-10 arası puanlar mısınız?' }],
});

const sendWhatsAppNps = node({
  type: 'n8n-nodes-base.httpRequest',
  version: 4.2,
  config: {
    name: 'WhatsApp NPS Gönder',
    position: [900, 300],
    parameters: {
      method: 'POST',
      url: placeholder('WhatsApp Business API URL (Meta Cloud API)'),
      sendBody: true,
      specifyBody: 'json',
      jsonBody: expr(
        '{"to":"{{ $("Normalize HBYS Payload").item.json.patientPhone }}","type":"text","text":{"body":"{{ $json.output }}"}}'
      ),
      options: {},
    },
  },
  output: [{ success: true }],
});

const npsResponseWebhook = trigger({
  type: 'n8n-nodes-base.webhook',
  version: 2.1,
  config: {
    name: 'NPS Yanıtı Al',
    position: [240, 620],
    parameters: {
      path: 'nefalix/nps/response',
      httpMethod: 'POST',
      responseMode: 'lastNode',
      options: {},
    },
  },
  output: [{ body: { score: 9, patientPhone: '+905551234567', patientName: 'Ayşe Yılmaz' } }],
});

const parseNpsScore = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'NPS Skorunu Parse Et',
    position: [460, 620],
    parameters: {
      mode: 'manual',
      includeOtherFields: false,
      assignments: {
        assignments: [
          { id: '1', name: 'score', value: expr('{{ Number($json.body?.score ?? $json.score ?? 0) }}'), type: 'number' },
          { id: '2', name: 'patientName', value: expr('{{ $json.body?.patientName ?? $json.patientName }}'), type: 'string' },
          { id: '3', name: 'patientPhone', value: expr('{{ $json.body?.patientPhone ?? $json.patientPhone }}'), type: 'string' },
          { id: '4', name: 'googleReviewUrl', value: expr('{{ $json.body?.googleReviewUrl ?? $json.googleReviewUrl }}'), type: 'string' },
          { id: '5', name: 'complaintFormUrl', value: expr('{{ $json.body?.complaintFormUrl ?? $json.complaintFormUrl }}'), type: 'string' },
        ],
      },
    },
  },
  output: [{ score: 9, patientName: 'Ayşe Yılmaz', patientPhone: '+905551234567', googleReviewUrl: 'https://g.page/r/example/review', complaintFormUrl: 'https://nefalix.com/sikayet' }],
});

const promoterCheck = ifElse({
  version: 2.2,
  config: {
    name: 'Promoter mi? (8-10)',
    position: [680, 620],
    parameters: {
      conditions: {
        options: { caseSensitive: true, leftValue: '', typeValidation: 'loose' },
        conditions: [
          {
            leftValue: expr('{{ $json.score }}'),
            operator: { type: 'number', operation: 'gte' },
            rightValue: 8,
          },
        ],
        combinator: 'and',
      },
    },
  },
});

const promoterMessage = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Promoter: Google Yorum Linki',
    position: [920, 520],
    parameters: {
      mode: 'manual',
      includeOtherFields: true,
      assignments: {
        assignments: [
          {
            id: '1',
            name: 'whatsappMessage',
            value: expr(
              'Teşekkürler {{ $json.patientName }}! Deneyiminizi Google\'da paylaşır mısınız? {{ $json.googleReviewUrl }}'
            ),
            type: 'string',
          },
          { id: '2', name: 'flow', value: 'promoter', type: 'string' },
        ],
      },
    },
  },
  output: [{ flow: 'promoter', whatsappMessage: 'Teşekkürler! Google linki...' }],
});

const detractorMessage = node({
  type: 'n8n-nodes-base.set',
  version: 3.4,
  config: {
    name: 'Detractor: Şikayet Formu',
    position: [920, 720],
    parameters: {
      mode: 'manual',
      includeOtherFields: true,
      assignments: {
        assignments: [
          {
            id: '1',
            name: 'whatsappMessage',
            value: expr(
              'Üzgünüz {{ $json.patientName }}. Geri bildiriminizi önemsiyoruz: {{ $json.complaintFormUrl }}'
            ),
            type: 'string',
          },
          { id: '2', name: 'flow', value: 'detractor', type: 'string' },
          { id: '3', name: 'alertMessage', value: expr('KRİZ: {{ $json.patientName }} NPS {{ $json.score }}/10 — acil müdahale'), type: 'string' },
        ],
      },
    },
  },
  output: [{ flow: 'detractor', alertMessage: 'KRİZ: NPS 4/10' }],
});

const slackAlert = node({
  type: 'n8n-nodes-base.slack',
  version: 2.3,
  config: {
    name: 'Slack Kriz Alarmı',
    position: [1140, 720],
    parameters: {
      select: 'channel',
      channelId: { __rl: true, mode: 'list', value: '' },
      text: expr('{{ $json.alertMessage }}'),
      otherOptions: {},
    },
    credentials: { slackApi: newCredential('Slack account') },
  },
  output: [{ ok: true }],
});

const note1 = sticky(
  '## Modül 1: Feedback & Reviews Loop\nHBYS webhook → WhatsApp NPS → 8-10 Google link / 1-7 şikayet + Slack alarm\n\nCredential: OpenAI, WhatsApp API, Slack',
  [hbysWebhook, normalizePayload, npsMessageAgent]
);

export default workflow('nefalix-feedback-reviews-loop', 'Nefalix - Feedback & Reviews Loop')
  .add(note1)
  .add(hbysWebhook)
  .to(normalizePayload)
  .to(npsMessageAgent)
  .to(sendWhatsAppNps)
  .add(npsResponseWebhook)
  .to(parseNpsScore)
  .to(
    promoterCheck
      .onTrue(promoterMessage)
      .onFalse(detractorMessage.to(slackAlert))
  );
