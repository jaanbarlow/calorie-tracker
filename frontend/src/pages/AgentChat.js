import React, { useEffect, useRef, useState } from "react";
import { api } from "../api";

/* ── Suggested starter prompts ───────────────────────────────────────────── */
const SUGGESTIONS = [
  "What have I eaten today and am I hitting my protein goal?",
  "Log 200g of chicken breast for me",
  "How has my nutrition looked this week?",
  "Am I on track for my calorie goal today?",
];

export default function AgentChat() {
  const [messages, setMessages] = useState([
    {
      role: "ai",
      content:
        "Hi! I'm your AI nutrition coach 🥗 I can look up foods, log what you've eaten, and analyse your macro trends. What can I help you with?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  /* Auto-scroll to latest message */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  /* ── Send message ──────────────────────────────────────────────────────── */
  const send = async (text) => {
    const userText = (text ?? input).trim();
    if (!userText || loading) return;

    setInput("");
    setError("");

    const updatedMessages = [...messages, { role: "human", content: userText }];
    setMessages(updatedMessages);
    setLoading(true);

    /* Build history — everything except the initial AI greeting and the
       message we just added (which is the current "input") */
    const history = updatedMessages.slice(1, -1).map((m) => ({
      role: m.role,
      content: m.content,
    }));

    try {
      const data = await api("/agent/chat", {
        method: "POST",
        body: JSON.stringify({ message: userText, history }),
      });
      setMessages((prev) => [...prev, { role: "ai", content: data.response }]);
    } catch (err) {
      setError(err.message);
      /* Remove the user message we optimistically added */
      setMessages(messages);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  /* ── Render ────────────────────────────────────────────────────────────── */
  return (
    <div className="chat-container">
      <div className="chat-header">
        <span className="chat-header-icon">🤖</span>
        <div>
          <div className="chat-header-title">AI Nutrition Coach</div>
          <div className="chat-header-subtitle">
            Powered by GPT-4o-mini · LangChain agentic tools
          </div>
        </div>
      </div>

      {/* ── Message list ───────────────────────────────────────────────── */}
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`chat-bubble-row ${msg.role === "human" ? "human" : "ai"}`}
          >
            {msg.role === "ai" && <div className="chat-avatar">🤖</div>}
            <div className={`chat-bubble ${msg.role}`}>
              {/* Render newlines as paragraphs */}
              {msg.content.split("\n").map((line, j) =>
                line === "" ? <br key={j} /> : <span key={j}>{line}<br /></span>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="chat-bubble-row ai">
            <div className="chat-avatar">🤖</div>
            <div className="chat-bubble ai thinking">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </div>
          </div>
        )}

        {error && (
          <div className="chat-error">⚠️ {error}</div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* ── Suggestions (only while conversation is fresh) ─────────────── */}
      {messages.length <= 2 && !loading && (
        <div className="chat-suggestions">
          {SUGGESTIONS.map((s) => (
            <button key={s} className="suggestion-chip" onClick={() => send(s)}>
              {s}
            </button>
          ))}
        </div>
      )}

      {/* ── Input bar ──────────────────────────────────────────────────── */}
      <div className="chat-input-bar">
        <textarea
          className="chat-input"
          rows={1}
          placeholder="Ask your nutrition coach anything…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          disabled={loading}
        />
        <button
          className="chat-send-btn"
          onClick={() => send()}
          disabled={loading || !input.trim()}
        >
          {loading ? "…" : "Send"}
        </button>
      </div>
    </div>
  );
}
