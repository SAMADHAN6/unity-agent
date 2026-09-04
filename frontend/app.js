/**
 * Unity Game Dev AI Agent — Frontend Logic
 */

const API_URL = "http://127.0.0.1:8000";

const messagesEl  = document.getElementById("messages");
const inputEl     = document.getElementById("user-input");
const sendBtn     = document.getElementById("send-btn");
const clearBtn    = document.getElementById("clear-btn");
const statusBadge = document.getElementById("status-badge");

// ── Helpers ──────────────────────────────────────────────

/** Convert markdown-ish text to HTML (code blocks + bold + inline code) */
function formatText(text) {
  // Fenced code blocks ```lang ... ```
  text = text.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => {
    const language = lang || "csharp";
    const escaped  = code.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
    return `<pre><code class="language-${language}">${escaped}</code></pre>`;
  });

  // Inline code `...`
  text = text.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Bold **...**
  text = text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

  // Newlines → paragraphs (split on double newline)
  const paras = text.split(/\n{2,}/);
  return paras.map(p => {
    // Single newlines inside a paragraph → <br>
    const inner = p.replace(/\n/g, "<br>");
    if (inner.startsWith("<pre>")) return inner;
    return `<p>${inner}</p>`;
  }).join("");
}

/** Append a message bubble to the chat */
function appendMessage(role, content) {
  const wrap   = document.createElement("div");
  wrap.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "🧑" : "🤖";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = role === "user"
    ? `<p>${content.replace(/</g,"&lt;")}</p>`
    : formatText(content);

  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  messagesEl.appendChild(wrap);

  // Syntax-highlight any code blocks
  wrap.querySelectorAll("pre code").forEach(block => hljs.highlightElement(block));

  scrollToBottom();
  return wrap;
}

/** Show the animated typing indicator */
function showTyping() {
  const wrap = document.createElement("div");
  wrap.className = "message agent typing-indicator";
  wrap.id = "typing";
  wrap.innerHTML = `
    <div class="avatar">🤖</div>
    <div class="bubble">
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
    </div>`;
  messagesEl.appendChild(wrap);
  scrollToBottom();
}

function hideTyping() {
  const el = document.getElementById("typing");
  if (el) el.remove();
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function setStatus(ok) {
  statusBadge.textContent = ok ? "● Connected" : "● Disconnected";
  statusBadge.className   = ok ? "status-badge" : "status-badge error";
}

// ── API Call ─────────────────────────────────────────────

async function sendMessage(text) {
  if (!text.trim()) return;

  appendMessage("user", text);
  inputEl.value = "";
  inputEl.style.height = "auto";
  sendBtn.disabled = true;
  showTyping();

  try {
    const res = await fetch(`${API_URL}/chat`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ message: text }),
    });

    hideTyping();

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      appendMessage("agent", `⚠️ Error: ${err.detail || "Something went wrong."}`);
      setStatus(false);
      return;
    }

    const data = await res.json();
    appendMessage("agent", data.reply);
    setStatus(true);

  } catch (err) {
    hideTyping();
    appendMessage("agent", "⚠️ Could not reach the backend. Make sure the server is running on port 8000.");
    setStatus(false);
  } finally {
    sendBtn.disabled = false;
    inputEl.focus();
  }
}

// ── Clear History ─────────────────────────────────────────

async function clearChat() {
  try {
    await fetch(`${API_URL}/clear-history`, { method: "DELETE" });
  } catch (_) { /* ignore if server is offline */ }

  // Remove all messages except the welcome message (first child)
  while (messagesEl.children.length > 1) {
    messagesEl.removeChild(messagesEl.lastChild);
  }
}

// ── Event Listeners ───────────────────────────────────────

sendBtn.addEventListener("click", () => sendMessage(inputEl.value));

inputEl.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage(inputEl.value);
  }
});

// Auto-resize textarea
inputEl.addEventListener("input", () => {
  inputEl.style.height = "auto";
  inputEl.style.height = Math.min(inputEl.scrollHeight, 140) + "px";
});

clearBtn.addEventListener("click", clearChat);

// Quick prompt buttons
document.querySelectorAll(".quick-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    sendMessage(btn.dataset.prompt);
  });
});

// ── Init: check server health ─────────────────────────────

(async () => {
  try {
    const res = await fetch(`${API_URL}/`);
    setStatus(res.ok);
  } catch (_) {
    setStatus(false);
  }
})();
