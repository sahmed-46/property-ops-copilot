import type { ChatMessage } from "../types";

interface MessageListProps {
  messages: ChatMessage[];
  loading: boolean;
}

export function MessageList({ messages, loading }: MessageListProps) {
  return (
    <div className="message-list">
      {messages.length === 0 ? (
        <div className="empty-state">
          <p>Start a conversation for the selected unit.</p>
          <p className="muted">
            Lease questions route to the retrieval agent; maintenance issues create work orders.
          </p>
        </div>
      ) : null}

      {messages.map((message) => (
        <article key={message.id} className={`message message-${message.role}`}>
          <div className="message-role">{message.role === "user" ? "You" : "Copilot"}</div>
          <div className="message-body">
            <p>{message.content}</p>

            {message.meta?.citation ? (
              <p className="citation">
                <strong>Source:</strong> Section {message.meta.citation.section} —{" "}
                {message.meta.citation.title}
              </p>
            ) : null}

            {message.meta?.workOrderId ? (
              <p className="work-order">
                <strong>Work order:</strong> {message.meta.workOrderId}
              </p>
            ) : null}

            {message.meta?.agent ? (
              <div className="message-meta">
                <span>Agent: {message.meta.agent}</span>
                {message.meta.routeReason ? <span>{message.meta.routeReason}</span> : null}
                {message.meta.requiresApproval ? <span className="flag">Needs approval</span> : null}
                {message.meta.flags?.map((flag) => (
                  <span key={flag} className="flag">
                    {flag}
                  </span>
                ))}
              </div>
            ) : null}
          </div>
        </article>
      ))}

      {loading ? (
        <article className="message message-assistant loading">
          <div className="message-role">Copilot</div>
          <div className="message-body">
            <p>Routing request and calling tools...</p>
          </div>
        </article>
      ) : null}
    </div>
  );
}
