import {
  GUIDE_FALLBACK_ANSWER,
  GUIDE_TOPICS,
  type GuideTopic,
} from './guideChatKnowledge';

export type GuideAnswer = {
  topicId: string;
  answer: string;
};

function normalize(text: string): string {
  return text.toLowerCase().replace(/\s+/g, ' ').trim();
}

function scoreTopic(topic: GuideTopic, query: string): number {
  const q = normalize(query);
  let score = 0;
  for (const keyword of topic.keywords) {
    const k = normalize(keyword);
    if (q.includes(k)) {
      score += k.length >= 12 ? 4 : 2;
    }
  }
  if (normalize(topic.title) === q || q.includes(normalize(topic.title))) {
    score += 6;
  }
  return score;
}

/**
 * Match user text to the best documentation topic. Purely local—no network calls.
 * Designed so a future LLM can replace this function behind the same interface.
 */
export function findGuideAnswer(query: string): GuideAnswer {
  const trimmed = query.trim();
  if (!trimmed) {
    return { topicId: 'empty', answer: GUIDE_FALLBACK_ANSWER };
  }

  let best: GuideTopic | null = null;
  let bestScore = 0;

  for (const topic of GUIDE_TOPICS) {
    const s = scoreTopic(topic, trimmed);
    if (s > bestScore) {
      bestScore = s;
      best = topic;
    }
  }

  if (!best || bestScore < 2) {
    return { topicId: 'fallback', answer: GUIDE_FALLBACK_ANSWER };
  }

  return { topicId: best.id, answer: best.answer };
}

const MIN_REPLY_MS = 380;
const MAX_REPLY_MS = 720;

/** Simulated think time so the UI can show a loading state. */
export function replyDelayMs(): number {
  return MIN_REPLY_MS + Math.floor(Math.random() * (MAX_REPLY_MS - MIN_REPLY_MS));
}

export async function getGuideReply(query: string): Promise<GuideAnswer> {
  const delay = replyDelayMs();
  await new Promise((resolve) => setTimeout(resolve, delay));
  return findGuideAnswer(query);
}
