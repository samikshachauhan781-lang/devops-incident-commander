import React, { useCallback, useEffect, useId, useRef, useState } from 'react';
import { MessageCircle, Send, X, Loader2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { GUIDE_SUGGESTED_QUESTIONS, GUIDE_WELCOME } from '../../lib/guideChatKnowledge';
import { getGuideReply } from '../../lib/guideChatProvider';
import { isConversationalTopicId } from '../../lib/guideChatEngine';
import type { GuideSessionContext } from '../../lib/guideChatTypes';
import { cn } from '@utils/cn';

const MAX_INPUT_LENGTH = 500;

type ChatMessage = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
};

function renderAssistantText(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    const lines = part.split('\n');
    return lines.map((line, j) => (
      <React.Fragment key={`${i}-${j}`}>
        {j > 0 && <br />}
        {line}
      </React.Fragment>
    ));
  });
}

let messageSeq = 0;
function nextMessageId(): string {
  messageSeq += 1;
  return `guide-msg-${messageSeq}`;
}

type GuideChatbotProps = {
  active?: boolean;
};

export default function GuideChatbot({ active = true }: GuideChatbotProps) {
  const panelId = useId();
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [welcomed, setWelcomed] = useState(false);
  const [dynamicSuggestions, setDynamicSuggestions] = useState<string[]>([]);
  const listRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const sessionRef = useRef<GuideSessionContext>({});

  const scrollToBottom = useCallback(() => {
    const el = listRef.current;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }, []);

  useEffect(() => {
    if (open && !welcomed) {
      setMessages([{ id: nextMessageId(), role: 'assistant', content: GUIDE_WELCOME }]);
      setWelcomed(true);
    }
  }, [open, welcomed]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, scrollToBottom]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open]);

  useEffect(() => {
    if (open) {
      const t = window.setTimeout(() => inputRef.current?.focus(), 100);
      return () => window.clearTimeout(t);
    }
  }, [open]);

  const sendQuestion = async (text: string) => {
    const question = text.trim().slice(0, MAX_INPUT_LENGTH);
    if (!question || loading) return;

    setInput('');
    setDynamicSuggestions([]);
    setMessages((prev) => [
      ...prev,
      { id: nextMessageId(), role: 'user', content: question },
    ]);
    setLoading(true);

    try {
      const reply = await getGuideReply(question, sessionRef.current, { now: new Date() });
      const preserveTopic = isConversationalTopicId(reply.topicId);
      if (reply.behavior === 'answer' && reply.topicId !== 'empty' && reply.topicId !== 'fallback') {
        sessionRef.current = {
          lastTopicId: preserveTopic ? sessionRef.current.lastTopicId : reply.topicId,
          lastUserQuestion: question,
        };
      }
      setMessages((prev) => [
        ...prev,
        { id: nextMessageId(), role: 'assistant', content: reply.answer },
      ]);
      if (reply.followUpSuggestions?.length) {
        setDynamicSuggestions(reply.followUpSuggestions.slice(0, 4));
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: nextMessageId(),
          role: 'assistant',
          content:
            'Something went wrong while generating a reply. Please try again — this guide does not modify incidents.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendQuestion(input);
  };

  const showInitialSuggestions = messages.length <= 1 && !loading && dynamicSuggestions.length === 0;

  return (
    <div
      className={cn('guide-chat-root', !active && 'hidden')}
      data-testid="guide-chat-root"
      aria-hidden={!active}
    >
      {open && (
        <div
          className="guide-chat-panel"
          role="dialog"
          aria-labelledby={`${panelId}-title`}
          aria-modal="false"
          data-testid="guide-chat-panel"
        >
          <header className="guide-chat-header">
            <div>
              <h2 id={`${panelId}-title`} className="guide-chat-title">
                Guide
              </h2>
              <p className="guide-chat-subtitle">Documentation-based assistant</p>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="guide-chat-close"
              aria-label="Close guide chat"
              data-testid="guide-chat-header-close"
              onClick={() => setOpen(false)}
            >
              <X className="h-5 w-5" />
            </Button>
          </header>

          <div className="guide-chat-messages" ref={listRef} data-testid="guide-chat-messages">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={cn(
                  'guide-chat-bubble',
                  msg.role === 'user' ? 'guide-chat-bubble-user' : 'guide-chat-bubble-assistant',
                )}
                data-testid={msg.role === 'user' ? 'guide-chat-user-msg' : 'guide-chat-bot-msg'}
              >
                {msg.role === 'assistant' ? renderAssistantText(msg.content) : msg.content}
              </div>
            ))}
            {loading && (
              <div
                className="guide-chat-bubble guide-chat-bubble-assistant guide-chat-loading"
                aria-live="polite"
                data-testid="guide-chat-loading"
              >
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                <span>Thinking…</span>
              </div>
            )}
          </div>

          {showInitialSuggestions && (
            <div className="guide-chat-suggestions" data-testid="guide-chat-suggestions">
              {GUIDE_SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  type="button"
                  className="guide-chat-suggestion"
                  onClick={() => sendQuestion(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          {!showInitialSuggestions && dynamicSuggestions.length > 0 && !loading && (
            <div className="guide-chat-suggestions" data-testid="guide-chat-followups">
              {dynamicSuggestions.map((q) => (
                <button
                  key={q}
                  type="button"
                  className="guide-chat-suggestion"
                  onClick={() => sendQuestion(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          <form className="guide-chat-form" onSubmit={handleSubmit}>
            <label className="sr-only" htmlFor={`${panelId}-input`}>
              Your question
            </label>
            <input
              id={`${panelId}-input`}
              ref={inputRef}
              type="text"
              className="guide-chat-input"
              placeholder="Ask a question…"
              value={input}
              onChange={(e) => setInput(e.target.value.slice(0, MAX_INPUT_LENGTH))}
              disabled={loading}
              autoComplete="off"
              maxLength={MAX_INPUT_LENGTH}
              data-testid="guide-chat-input"
            />
            <Button
              type="submit"
              size="icon"
              className="guide-chat-send"
              disabled={loading || !input.trim()}
              aria-label="Send message"
              data-testid="guide-chat-send"
            >
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      )}

      <Button
        type="button"
        className="guide-chat-fab !transition-none"
        aria-expanded={open}
        aria-controls={open ? `${panelId}-panel` : undefined}
        aria-label={open ? 'Hide guide chat panel' : 'Open guide chat'}
        onClick={() => setOpen((v) => !v)}
        data-testid="guide-chat-fab"
      >
        {open ? <X className="h-6 w-6" /> : <MessageCircle className="h-6 w-6" />}
      </Button>
    </div>
  );
}
