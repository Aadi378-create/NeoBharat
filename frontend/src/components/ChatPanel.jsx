import React, { useState } from 'react';
import { SendIcon, SparklesIcon, AlertCircleIcon, ShieldIcon } from './Icons';
import { sendChatMessage } from '../api/client';

const SUGGESTIONS = [
  'Why am I seeing this?',
  'What should I do next?',
  'Why didn\'t you recommend a loan?',
  'Is this transaction suspicious?',
];

export function ChatPanel({ customerId, customerName }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hello ${customerName || 'there'}! I am NeoBharat's explanation assistant. I can explain the decisions, risk scores, and guidance provided by our financial engines. What would you like to know?`,
      responseType: 'FINANCIAL_GUIDANCE',
      safety: {
        financial_decision_made_by: 'DETERMINISTIC_ENGINE',
        llm_role: 'EXPLANATION_ONLY',
      },
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSend = async (textToSend) => {
    const text = (textToSend || inputText).trim();
    if (!text || loading) return;

    // Reject message over 4000 characters before making request
    if (text.length > 4000) {
      setError('Message exceeds the maximum allowed length of 4000 characters.');
      return;
    }

    setError(null);
    setInputText('');

    // Append user message to history
    const userMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      // POST /api/chat with strictly customer_id and message
      const response = await sendChatMessage(customerId, text);

      const assistantMsg = {
        role: 'assistant',
        content: response.message,
        responseType: response.response_type,
        decisionAck: response.decision_acknowledgement,
        evidence: response.evidence,
        nextStep: response.next_step,
        safety: response.safety,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setError(err.message || 'Failed to receive explanation from server.');
      // Append error message to chat
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          isError: true,
          content: `Error: ${err.message || 'Unable to connect to NeoBharat explanation service.'}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card chat-card" aria-label="Ask NeoBharat Chat Panel">
      <div className="card-header" style={{ marginBottom: '0.75rem' }}>
        <div className="card-title-group">
          <div className="brand-icon" style={{ width: 32, height: 32, background: '#0284c7' }}>
            <SparklesIcon className="w-4 h-4" />
          </div>
          <div>
            <h2 className="card-title" style={{ fontSize: '1rem' }}>Ask NeoBharat</h2>
            <p className="card-subtitle" style={{ fontSize: '0.75rem' }}>
              Conversational explanation layer powered by OpenAI
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.6875rem', color: 'var(--text-muted)' }}>
          <ShieldIcon className="w-3.5 h-3.5" />
          <span>LLM Explains · Engine Decides</span>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="chat-messages" role="log" aria-live="polite">
        {messages.map((m, idx) => (
          <div key={idx} className={`message-bubble ${m.role} ${m.isError ? 'error-bubble' : ''}`}>
            {m.responseType && (
              <div style={{ fontSize: '0.6875rem', fontWeight: 700, textTransform: 'uppercase', opacity: 0.8, marginBottom: '0.25rem' }}>
                {m.responseType.replace(/_/g, ' ')}
              </div>
            )}

            <div>{m.content}</div>

            {/* Next Step if present */}
            {m.nextStep && (
              <div className="next-step-box">
                <strong>Next Step:</strong> {m.nextStep.label}
              </div>
            )}

            {/* Evidence chips if present */}
            {Array.isArray(m.evidence) && m.evidence.length > 0 && (
              <div className="evidence-tags-container">
                {m.evidence.map((ev, eIdx) => (
                  <span key={eIdx} className="evidence-chip">
                    {ev.metric}: {typeof ev.value === 'number' ? ev.value.toLocaleString() : String(ev.value)}
                  </span>
                ))}
              </div>
            )}

            {/* Safety metadata tag */}
            {m.safety && (
              <div style={{ fontSize: '0.625rem', opacity: 0.6, marginTop: '0.375rem', fontStyle: 'italic' }}>
                Decision: {m.safety.financial_decision_made_by} · Role: {m.safety.llm_role}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="message-bubble assistant">
            <div className="loading-indicator" style={{ padding: '0.5rem 0', justifyContent: 'flex-start' }}>
              <div className="spinner" />
              <span>NeoBharat is composing an explanation...</span>
            </div>
          </div>
        )}
      </div>

      {/* Error alert if client error */}
      {error && (
        <div className="error-banner" style={{ padding: '0.5rem 0.75rem', margin: '0.5rem 0', fontSize: '0.75rem' }}>
          <AlertCircleIcon className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {/* Suggested prompts */}
      <div className="chat-suggestions" aria-label="Suggested questions">
        {SUGGESTIONS.map((s, idx) => (
          <button
            key={idx}
            type="button"
            className="suggestion-pill"
            onClick={() => handleSend(s)}
            disabled={loading}
          >
            {s}
          </button>
        ))}
      </div>

      {/* Input Form */}
      <form
        className="chat-input-form"
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
      >
        <input
          type="text"
          className="chat-input"
          placeholder="Ask a question about your financial status..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={loading}
          maxLength={4000}
        />
        <button
          type="submit"
          className="chat-send-btn"
          disabled={loading || !inputText.trim()}
          aria-label="Send message"
        >
          <SendIcon className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
