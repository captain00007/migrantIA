/**
 * Módulo de Reconhecimento e Síntese de Voz (Acessibilidade) do MigrantIA.
 */
class SpeechModule {
  constructor() {
    this.synth = window.speechSynthesis || null;
    this.recognition = null;
    this.isListening = false;
    this.currentUtterance = null;
    this.initRecognition();
  }

  initRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = false;
    }
  }

  getLocaleForLanguage(langCode) {
    switch (langCode) {
      case "ht":
        return "ht-HT";
      case "fr":
        return "fr-FR";
      case "es":
        return "es-ES";
      case "en":
        return "en-US";
      case "pt":
      default:
        return "pt-BR";
    }
  }

  speak(text, langCode = "pt", onEndCallback = null) {
    if (!this.synth) return false;

    // Cancela fala anterior se em andamento
    this.stopSpeaking();

    // Remove markdown e links antes da síntese
    const cleanText = text
      .replace(/[#*_`]/g, "")
      .replace(/\[(.*?)\]\(.*?\)/g, "$1")
      .replace(/https?:\/\/\S+/g, "");

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = this.getLocaleForLanguage(langCode);
    utterance.rate = 0.95; // Velocidade confortável

    utterance.onend = () => {
      this.currentUtterance = null;
      if (onEndCallback) onEndCallback();
    };

    utterance.onerror = (e) => {
      console.warn("[Speech] Erro na síntese de voz:", e);
      this.currentUtterance = null;
      if (onEndCallback) onEndCallback();
    };

    this.currentUtterance = utterance;
    this.synth.speak(utterance);
    return true;
  }

  stopSpeaking() {
    if (this.synth && this.synth.speaking) {
      this.synth.cancel();
      this.currentUtterance = null;
    }
  }

  startListening(langCode, onResultCallback, onErrorCallback, onEndCallback) {
    if (!this.recognition) {
      if (onErrorCallback) onErrorCallback("not_supported");
      return false;
    }

    this.recognition.lang = this.getLocaleForLanguage(langCode);

    this.recognition.onstart = () => {
      this.isListening = true;
    };

    this.recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (onResultCallback) onResultCallback(transcript);
    };

    this.recognition.onerror = (event) => {
      this.isListening = false;
      if (onErrorCallback) onErrorCallback(event.error);
    };

    this.recognition.onend = () => {
      this.isListening = false;
      if (onEndCallback) onEndCallback();
    };

    try {
      this.recognition.start();
      return true;
    } catch (err) {
      console.warn("[Speech] Erro ao iniciar escuta:", err);
      return false;
    }
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
      this.isListening = false;
    }
  }
}

const speechModule = new SpeechModule();
