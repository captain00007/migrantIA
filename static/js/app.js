/**
 * Controlador Principal do Frontend PWA do MigrantIA.
 */
document.addEventListener("DOMContentLoaded", () => {
  // State
  let currentLanguage = localStorage.getItem("migrantia_lang") || "pt";
  let currentPillar = null;
  let currentSessionId = localStorage.getItem("migrantia_session_id") || null;
  let activeFeedbackMessageId = null;

  // DOM Elements
  const langSelector = document.getElementById("lang-selector");
  const chatMessages = document.getElementById("chat-messages");
  const chatForm = document.getElementById("chat-form");
  const messageInput = document.getElementById("message-input");
  const sendBtn = document.getElementById("send-btn");
  const micBtn = document.getElementById("mic-btn");
  const typingIndicator = document.getElementById("typing-indicator");
  const feedbackModal = document.getElementById("feedback-modal");
  const btnCloseModal = document.getElementById("btn-close-modal");
  const btnSubmitFeedback = document.getElementById("btn-submit-feedback");
  const pillarChips = document.querySelectorAll(".pillar-chip");

  // Initialize Language
  if (langSelector) {
    langSelector.value = currentLanguage;
    applyLanguage(currentLanguage);
    langSelector.addEventListener("change", (e) => {
      currentLanguage = e.target.value;
      localStorage.setItem("migrantia_lang", currentLanguage);
      applyLanguage(currentLanguage);
    });
  }

  // Initialize Session
  initSession();

  // Pillar Filter Chips
  pillarChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      pillarChips.forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      currentPillar = chip.getAttribute("data-pillar") || null;
    });
  });

  // Auto-resize textarea
  messageInput.addEventListener("input", () => {
    messageInput.style.height = "auto";
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
  });

  // Quick Prompt buttons
  document.querySelectorAll(".quick-prompt-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const query = btn.getAttribute("data-query");
      if (query) {
        messageInput.value = query;
        handleSendMessage();
      }
    });
  });

  // Form Submit
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    handleSendMessage();
  });

  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });

  // Microphone (Speech-to-Text)
  if (micBtn) {
    micBtn.addEventListener("click", () => {
      if (speechModule.isListening) {
        speechModule.stopListening();
        micBtn.classList.remove("recording");
      } else {
        const started = speechModule.startListening(
          currentLanguage,
          (transcript) => {
            messageInput.value = transcript;
            messageInput.focus();
            micBtn.classList.remove("recording");
          },
          (err) => {
            console.warn("[Speech] Erro:", err);
            micBtn.classList.remove("recording");
            if (err === "not-allowed") {
              alert(getTranslation("micPermissionDenied", currentLanguage));
            }
          },
          () => {
            micBtn.classList.remove("recording");
          }
        );
        if (started) {
          micBtn.classList.add("recording");
        }
      }
    });
  }

  // Modal Handlers
  if (btnCloseModal) {
    btnCloseModal.addEventListener("click", closeFeedbackModal);
  }
  if (btnSubmitFeedback) {
    btnSubmitFeedback.addEventListener("click", submitModalFeedback);
  }

  // --------------------------------------------------------------------------
  // Core Functions
  // --------------------------------------------------------------------------

  async function initSession() {
    try {
      if (!currentSessionId) {
        const session = await apiClient.createSession(currentLanguage, currentPillar);
        currentSessionId = session.id;
        localStorage.setItem("migrantia_session_id", currentSessionId);
      }
    } catch (err) {
      console.warn("[App] Falha ao inicializar sessão:", err);
    }
  }

  function applyLanguage(lang) {
    document.getElementById("txt-app-title").textContent = getTranslation("appTitle", lang);
    document.getElementById("txt-app-subtitle").textContent = getTranslation("appSubtitle", lang);
    document.getElementById("txt-welcome-title").textContent = getTranslation("welcomeTitle", lang);
    document.getElementById("txt-welcome-subtitle").textContent = getTranslation("welcomeSubtitle", lang);
    document.getElementById("chip-all").textContent = getTranslation("pillarAll", lang);
    document.getElementById("chip-imm").textContent = getTranslation("pillarImmigration", lang);
    document.getElementById("chip-edu").textContent = getTranslation("pillarEducation", lang);
    document.getElementById("chip-nat").textContent = getTranslation("pillarNationality", lang);
    document.getElementById("chip-com").textContent = getTranslation("pillarCommunity", lang);
    document.getElementById("txt-thinking").textContent = getTranslation("thinkingText", lang);
    messageInput.placeholder = getTranslation("inputPlaceholder", lang);

    // Update Quick Prompts
    const qp1 = document.querySelector("#qp-1 .qp-text");
    const qp2 = document.querySelector("#qp-2 .qp-text");
    const qp3 = document.querySelector("#qp-3 .qp-text");
    const qp4 = document.querySelector("#qp-4 .qp-text");
    if (qp1) qp1.textContent = getTranslation("quickPrompt1", lang);
    if (qp2) qp2.textContent = getTranslation("quickPrompt2", lang);
    if (qp3) qp3.textContent = getTranslation("quickPrompt3", lang);
    if (qp4) qp4.textContent = getTranslation("quickPrompt4", lang);
  }

  async function handleSendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    // Reset input
    messageInput.value = "";
    messageInput.style.height = "auto";
    sendBtn.disabled = true;

    // Hide welcome card after first message
    const welcomeCard = document.getElementById("welcome-card");
    if (welcomeCard) {
      welcomeCard.style.display = "none";
    }

    // Append User Bubble
    appendMessageBubble("user", text);
    showTyping(true);

    try {
      if (!currentSessionId) {
        await initSession();
      }

      const resp = await apiClient.sendMessage(
        currentSessionId,
        text,
        currentLanguage,
        currentPillar
      );

      showTyping(false);
      appendAssistantBubble(resp.assistant_message);
    } catch (err) {
      showTyping(false);
      appendMessageBubble(
        "assistant",
        getTranslation("errorNetwork", currentLanguage)
      );
    } finally {
      sendBtn.disabled = false;
    }
  }

  function appendMessageBubble(sender, content) {
    const row = document.createElement("div");
    row.className = `message-row ${sender}`;

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.textContent = content;

    row.appendChild(bubble);
    chatMessages.appendChild(row);
    scrollToBottom();
  }

  function appendAssistantBubble(assistantMsg) {
    const row = document.createElement("div");
    row.className = "message-row assistant";
    row.setAttribute("data-message-id", assistantMsg.id);

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.innerHTML = formatMarkdown(assistantMsg.content);

    // Golden Rule Alert Box
    if (assistantMsg.golden_rule_triggered) {
      const goldenBox = document.createElement("div");
      goldenBox.className = "golden-rule-box";
      goldenBox.innerHTML = `
        <div class="golden-rule-header">
          <span>⚠️</span> <span>${getTranslation("goldenRuleAlertTitle", currentLanguage)}</span>
        </div>
        <div class="golden-rule-contacts">
          <strong>Canais Oficiais Gratuitos:</strong><br>
          • <strong>DPU (Defensoria Pública da União):</strong> Ligue 129 ou (61) 3318-4300<br>
          • <strong>Missão Paz / CRAI SP:</strong> (11) 3340-6950 | (11) 2361-3780<br>
          • <strong>Cáritas Arquidiocesana:</strong> (11) 3274-1033
        </div>
      `;
      bubble.appendChild(goldenBox);
    }

    // Sources Cited Section
    if (assistantMsg.sources_cited && assistantMsg.sources_cited.length > 0) {
      const sourcesCard = document.createElement("div");
      sourcesCard.className = "sources-card";

      const toggle = document.createElement("div");
      toggle.className = "sources-toggle";
      toggle.innerHTML = `<span>🏛️</span> <span>${getTranslation("sourcesTitle", currentLanguage)} (${assistantMsg.sources_cited.length})</span>`;

      const list = document.createElement("div");
      list.className = "sources-list";

      assistantMsg.sources_cited.forEach((src) => {
        const item = document.createElement("a");
        item.className = "source-item";
        item.href = src.url || "#";
        item.target = "_blank";
        item.rel = "noopener noreferrer";

        let pageBadge = "";
        if (src.pages && src.pages.length > 0) {
          pageBadge = src.pages.length === 1 ? ` (Pág. ${src.pages[0]})` : ` (Págs. ${src.pages.join(", ")})`;
        } else if (src.page) {
          pageBadge = ` (Pág. ${src.page})`;
        }

        const titleText = (src.title || "Portal Oficial") + pageBadge;
        item.innerHTML = `<span>🔗 ${escapeHtml(titleText)}</span> <span>↗</span>`;
        list.appendChild(item);
      });

      sourcesCard.appendChild(toggle);
      sourcesCard.appendChild(list);
      bubble.appendChild(sourcesCard);
    }

    row.appendChild(bubble);

    // Action toolbar (Audio TTS, Feedback 👍 / 👎)
    const actions = document.createElement("div");
    actions.className = "message-actions";

    // Audio Button
    const audioBtn = document.createElement("button");
    audioBtn.className = "action-btn";
    audioBtn.innerHTML = `<span>🔊</span> <span>${getTranslation("listenAudio", currentLanguage)}</span>`;
    audioBtn.addEventListener("click", () => {
      speechModule.speak(assistantMsg.content, currentLanguage, () => {
        audioBtn.innerHTML = `<span>🔊</span> <span>${getTranslation("listenAudio", currentLanguage)}</span>`;
      });
    });

    // Thumbs Up
    const thumbsUpBtn = document.createElement("button");
    thumbsUpBtn.className = "action-btn";
    thumbsUpBtn.innerHTML = `<span>👍</span>`;
    thumbsUpBtn.title = getTranslation("feedbackHelpful", currentLanguage);
    thumbsUpBtn.addEventListener("click", async () => {
      try {
        await apiClient.submitFeedback(assistantMsg.id, 1);
        thumbsUpBtn.classList.add("active-positive");
        thumbsDownBtn.classList.remove("active-negative");
      } catch (err) {
        console.warn("[Feedback] Erro:", err);
      }
    });

    // Thumbs Down
    const thumbsDownBtn = document.createElement("button");
    thumbsDownBtn.className = "action-btn";
    thumbsDownBtn.innerHTML = `<span>👎</span>`;
    thumbsDownBtn.title = getTranslation("feedbackUnhelpful", currentLanguage);
    thumbsDownBtn.addEventListener("click", () => {
      activeFeedbackMessageId = assistantMsg.id;
      openFeedbackModal();
    });

    actions.appendChild(audioBtn);
    actions.appendChild(thumbsUpBtn);
    actions.appendChild(thumbsDownBtn);
    row.appendChild(actions);

    chatMessages.appendChild(row);
    scrollToBottom();
  }

  function showTyping(show) {
    if (typingIndicator) {
      typingIndicator.style.display = show ? "flex" : "none";
      if (show) scrollToBottom();
    }
  }

  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function openFeedbackModal() {
    feedbackModal.classList.add("active");
  }

  function closeFeedbackModal() {
    feedbackModal.classList.remove("active");
    activeFeedbackMessageId = null;
    document.getElementById("feedback-comment").value = "";
  }

  async function submitModalFeedback() {
    if (!activeFeedbackMessageId) return;

    const selectedReason = document.querySelector('input[name="feedback-reason"]:checked')?.value || "OTHER";
    const comment = document.getElementById("feedback-comment").value;

    try {
      await apiClient.submitFeedback(activeFeedbackMessageId, -1, selectedReason, comment);
      closeFeedbackModal();
    } catch (err) {
      console.warn("[Feedback Modal] Erro:", err);
      closeFeedbackModal();
    }
  }

  function formatMarkdown(text) {
    if (!text) return "";
    let html = escapeHtml(text);
    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    // Bullet points
    html = html.replace(/^[•\-] (.*)$/gm, "<li>$1</li>");
    html = html.replace(/(<li>.*<\/li>)/s, "<ul>$1</ul>");
    // Line breaks to paragraphs
    html = html.split("\n\n").map(p => `<p>${p.replace(/\n/g, "<br>")}</p>`).join("");
    return html;
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
