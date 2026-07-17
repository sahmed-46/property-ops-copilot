import { useEffect, useMemo, useRef, useState } from "react";
import { checkHealth, fetchUnits, sendChat } from "./api/client";
import { MessageList } from "./components/MessageList";
import { Sidebar } from "./components/Sidebar";
import type { ChatMessage, Unit } from "./types";
import { extractReplyMeta, formatAssistantReply } from "./utils/formatReply";
import "./App.css";

function newId(): string {
  return crypto.randomUUID();
}

export default function App() {
  const [units, setUnits] = useState<Unit[]>([]);
  const [unitId, setUnitId] = useState("");
  const [sessionId, setSessionId] = useState("demo-session");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<"checking" | "online" | "offline">("checking");
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        await checkHealth();
        const loadedUnits = await fetchUnits();
        if (cancelled) return;
        setUnits(loadedUnits);
        setUnitId(loadedUnits[0]?.id ?? "");
        setApiStatus("online");
      } catch {
        if (!cancelled) setApiStatus("offline");
      }
    }

    bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  const selectedUnit = useMemo(
    () => units.find((unit) => unit.id === unitId),
    [units, unitId],
  );

  async function handleSend(event?: React.FormEvent) {
    event?.preventDefault();
    const text = draft.trim();
    if (!text || loading || !unitId) return;

    const userMessage: ChatMessage = {
      id: newId(),
      role: "user",
      content: text,
    };

    setMessages((prev) => [...prev, userMessage]);
    setDraft("");
    setLoading(true);
    setError(null);

    try {
      const result = await sendChat({
        session_id: sessionId,
        message: text,
        unit_id: unitId,
      });

      const assistantMessage: ChatMessage = {
        id: newId(),
        role: "assistant",
        content: formatAssistantReply(result),
        meta: extractReplyMeta(result),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to reach API";
      setError(message);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handleSend();
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <p className="eyebrow">PropTech · Multi-agent demo</p>
          <h1>Property Ops Copilot</h1>
          <p className="subtitle">
            Lease Q&amp;A with citations · Maintenance tickets · Compliance guardrails
          </p>
        </div>
        <div className={`status-pill status-${apiStatus}`}>
          API {apiStatus === "checking" ? "connecting" : apiStatus}
        </div>
      </header>

      <main className="layout">
        <Sidebar
          units={units}
          unitId={unitId}
          sessionId={sessionId}
          selectedUnit={selectedUnit}
          onUnitChange={setUnitId}
          onSessionChange={setSessionId}
        />

        <section className="chat-panel">
          <MessageList messages={messages} loading={loading} />

          {error ? <div className="error-banner">{error}</div> : null}

          <form className="composer" onSubmit={handleSend}>
            <textarea
              ref={inputRef}
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about your lease or report a maintenance issue..."
              rows={3}
              disabled={loading || apiStatus !== "online" || !unitId}
            />
            <div className="composer-actions">
              <span className="hint">Enter to send · Shift+Enter for newline</span>
              <button type="submit" disabled={loading || !draft.trim() || !unitId}>
                {loading ? "Sending..." : "Send"}
              </button>
            </div>
          </form>
        </section>
      </main>
    </div>
  );
}
