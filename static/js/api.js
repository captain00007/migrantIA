/**
 * Cliente de API do MigrantIA.
 * Conecta o frontend aos endpoints REST do backend Django.
 */
class MigrantIAClient {
  constructor(baseUrl = "") {
    this.baseUrl = baseUrl;
  }

  async createSession(uiLanguage = "pt", primaryPillar = null, metadata = {}) {
    const response = await fetch(`${this.baseUrl}/api/chat/sessions/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ui_language: uiLanguage,
        primary_pillar: primaryPillar,
        metadata: {
          ...metadata,
          userAgent: navigator.userAgent,
          platform: navigator.platform,
        },
      }),
    });
    if (!response.ok) {
      throw new Error(`Erro ao criar sessão: ${response.statusText}`);
    }
    return await response.json();
  }

  async getSessionMessages(sessionId) {
    const response = await fetch(`${this.baseUrl}/api/chat/sessions/${sessionId}/messages/`);
    if (!response.ok) {
      throw new Error(`Erro ao carregar mensagens: ${response.statusText}`);
    }
    return await response.json();
  }

  async sendMessage(sessionId, content, uiLanguage = null, pillar = null) {
    const payload = { content };
    if (uiLanguage) payload.ui_language = uiLanguage;
    if (pillar) payload.pillar = pillar;

    const response = await fetch(`${this.baseUrl}/api/chat/sessions/${sessionId}/messages/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`Erro ao enviar mensagem: ${response.statusText}`);
    }
    return await response.json();
  }

  async submitFeedback(messageId, rating, reason = null, comment = "") {
    const payload = { rating, comment };
    if (reason) payload.reason = reason;

    const response = await fetch(`${this.baseUrl}/api/chat/messages/${messageId}/feedback/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`Erro ao enviar feedback: ${response.statusText}`);
    }
    return await response.json();
  }
}

const apiClient = new MigrantIAClient();
