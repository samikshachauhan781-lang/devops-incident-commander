import {
  GUIDE_AMBIGUOUS_CLARIFY,
  GUIDE_CAPABILITIES,
  GUIDE_EMPTY_PROMPT,
  GUIDE_FALLBACK_ANSWER,
  GUIDE_FOLLOWUP_PROMPTS,
  GUIDE_SECURITY_REFUSAL,
  GUIDE_TOPICS,
  type GuideTopicEntry,
} from './guideChatKnowledge';
import type { GuideReply, GuideSessionContext } from './guideChatTypes';

export type { GuideReply, GuideSessionContext } from './guideChatTypes';

const MIN_SCORE = 3;
const CLARIFY_GAP_RATIO = 0.85;

const SECURITY_PATTERNS = [
  /\b(api\s*key|secret|password|token|credential|env\s*var|environment variables?)\b/i,
  /\b(show|print|list|give).{0,20}(environment variables?|env\s*var)/i,
  /\b(bypass|hack|exploit|sql\s*inject|drop\s+table|shell\s+command)\b/i,
  /\b(delete\s+all|wipe\s+database|disable\s+demo\s+mode)\b/i,
];

const FOLLOWUP_PATTERNS = [
  /^tell me more$/i,
  /^more$/i,
  /^continue$/i,
  /^go on$/i,
  /^what else$/i,
  /^and then\??$/i,
  /^explain that$/i,
  /^can you elaborate$/i,
  /^yes$/i,
  /^ok(ay)?\s+(and|then)?/i,
  /^what about that$/i,
  /^how about that$/i,
];

export function normalizeGuideText(text: string): string {
  return text
    .toLowerCase()
    .replace(/['']/g, "'")
    .replace(/[^\w\s'-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

/** Simple Damerau-Levenshtein cap for typo tolerance on tokens length >= 4. */
export function tokenSimilar(a: string, b: string): number {
  if (a === b) return 1;
  if (a.length < 4 || b.length < 4) return a === b ? 1 : 0;
  const maxLen = Math.max(a.length, b.length);
  if (Math.abs(a.length - b.length) > 2) return 0;
  const dist = levenshtein(a, b);
  if (dist > 2) return 0;
  return 1 - dist / maxLen;
}

function levenshtein(a: string, b: string): number {
  const m = a.length;
  const n = b.length;
  const dp: number[] = Array(n + 1).fill(0);
  for (let j = 0; j <= n; j++) dp[j] = j;
  for (let i = 1; i <= m; i++) {
    let prev = dp[0];
    dp[0] = i;
    for (let j = 1; j <= n; j++) {
      const tmp = dp[j];
      dp[j] = Math.min(
        dp[j] + 1,
        dp[j - 1] + 1,
        prev + (a[i - 1] === b[j - 1] ? 0 : 1),
      );
      prev = tmp;
    }
  }
  return dp[n];
}

function queryTokens(query: string): string[] {
  return normalizeGuideText(query).split(' ').filter(Boolean);
}

function scoreTopic(topic: GuideTopicEntry, query: string, tokens: string[]): number {
  const q = normalizeGuideText(query);
  let score = 0;

  for (const phrase of topic.phrases ?? []) {
    const p = normalizeGuideText(phrase);
    if (p.length >= 6 && q.includes(p)) {
      score += 6 + Math.min(p.length / 10, 4);
    }
  }

  for (const keyword of topic.keywords) {
    const k = normalizeGuideText(keyword);
    if (!k) continue;
    if (k.includes(' ') && q.includes(k)) {
      score += 4 + k.length / 8;
      continue;
    }
    if (q.includes(k)) {
      score += k.length >= 10 ? 4 : 2.5;
      continue;
    }
    for (const t of tokens) {
      const sim = tokenSimilar(t, k);
      if (sim >= 0.75) score += 2 * sim;
    }
  }

  const titleNorm = normalizeGuideText(topic.title);
  if (q === titleNorm || q.includes(titleNorm)) score += 7;

  return score;
}

function isSecuritySensitive(query: string): boolean {
  return SECURITY_PATTERNS.some((re) => re.test(query));
}

function isFollowUp(query: string): boolean {
  const q = query.trim();
  return FOLLOWUP_PATTERNS.some((re) => re.test(q));
}

const DIRECT_ROUTES: { pattern: RegExp; topicId: string }[] = [
  { pattern: /what can (you|this platform|this app) (do|help)/i, topicId: 'capabilities' },
  { pattern: /purpose of this (website|app|platform)/i, topicId: 'purpose' },
  { pattern: /where is the timeline/i, topicId: 'navigation' },
  { pattern: /how do i (get to|open) analytics/i, topicId: 'navigation' },
  { pattern: /difference between status and severity/i, topicId: 'status-lifecycle' },
  { pattern: /status vs severity/i, topicId: 'severity' },
  { pattern: /what happens when i click investigate/i, topicId: 'investigate-button' },
  { pattern: /what hapens when i investigate|what happens when i investigate(?!.*how does)/i, topicId: 'investigate-button' },
  { pattern: /start investigat(o|io)n button|investigate button click/i, topicId: 'investigate-button' },
  { pattern: /read investigation output|investigation output/i, topicId: 'investigation-results' },
  { pattern: /what is on the timeline page|timeline page/i, topicId: 'timeline' },
  { pattern: /filter incidents by service/i, topicId: 'analytics' },
  { pattern: /metrics on dashboard|dashboard metrics/i, topicId: 'navigation' },
  { pattern: /page is blank|blank page|failed to load incidents|dashboard not loading/i, topicId: 'troubleshooting' },
  { pattern: /api health check|platform health/i, topicId: 'troubleshooting' },
  { pattern: /will ai fix production|fix production automatically/i, topicId: 'limitations' },
  { pattern: /monitor prod servers auto|can u monitor prod/i, topicId: 'demo' },
  { pattern: /step by step|walk me through/i, topicId: 'how-works' },
  { pattern: /interpret(ation)? results/i, topicId: 'investigation-results' },
  { pattern: /high vs critical|critical vs high|difference between high and critical/i, topicId: 'severity-compare' },
  { pattern: /why am i getting an error/i, topicId: 'troubleshooting' },
  { pattern: /monitor my production servers automatically/i, topicId: 'demo' },
  { pattern: /connect to datadog|prometheus|pagerduty/i, topicId: 'faq-monitoring' },
  { pattern: /limitations|what can this not do/i, topicId: 'limitations' },
  { pattern: /how to get to analytics|get to analytics/i, topicId: 'navigation' },
  { pattern: /walk me through the website/i, topicId: 'how-works' },
  { pattern: /severety|sevrity/i, topicId: 'severity' },
  { pattern: /^start investigation$/i, topicId: 'ai-investigation' },
  { pattern: /what does this project do/i, topicId: 'what-is' },
  { pattern: /devops incident commander/i, topicId: 'what-is' },
  { pattern: /explain devops incid(e|n)et commander/i, topicId: 'what-is' },
  { pattern: /server failure/i, topicId: 'ai-investigation' },
  { pattern: /investigation templates|mock provider|ollama investigation/i, topicId: 'ai-investigation' },
  { pattern: /403 forbidden|why cant i create/i, topicId: 'demo' },
  { pattern: /cors investigate|vite api base/i, topicId: 'troubleshooting' },
  { pattern: /filter timeline events|incident events chronological/i, topicId: 'timeline' },
  { pattern: /severity breakdown|analytics charts|status breakdown/i, topicId: 'analytics' },
  { pattern: /open status mean|investigating status|incident resolved/i, topicId: 'status-lifecycle' },
  { pattern: /trained ai|generative ai chatbot/i, topicId: 'limitations' },
];

function tryInvestigationDisambiguation(query: string): GuideTopicEntry | null {
  const q = normalizeGuideText(query);
  if (/investigation output|read investigation output|interpret investigation results/.test(q)) {
    return topicById('investigation-results') ?? null;
  }
  if (/(investigate button|button click|click investigate)/.test(q)) {
    return topicById('investigate-button') ?? null;
  }
  if (/what hapens when i investigate|what happens when i investigate/.test(q) && !/how does/.test(q)) {
    return topicById('investigate-button') ?? null;
  }
  if (/how does ai investigation|how does investigation work|investigation workflow|server failure/.test(q)) {
    return topicById('ai-investigation') ?? null;
  }
  return null;
}

function tryDirectRoute(query: string): GuideTopicEntry | null {
  for (const route of DIRECT_ROUTES) {
    if (route.pattern.test(query)) {
      return topicById(route.topicId) ?? null;
    }
  }
  return null;
}

function topicById(id: string): GuideTopicEntry | undefined {
  return GUIDE_TOPICS.find((t) => t.id === id);
}

function buildAnswer(topic: GuideTopicEntry): GuideReply {
  return {
    topicId: topic.id,
    answer: topic.answer,
    behavior: 'answer',
    confidence: 0.9,
    followUpSuggestions: topic.followUpSuggestions,
  };
}

/**
 * Core matcher — synchronous, no network. Used by tests and evaluation.
 */
export function findGuideAnswer(
  query: string,
  context: GuideSessionContext = {},
): GuideReply {
  const trimmed = query.trim();

  if (!trimmed) {
    return {
      topicId: 'empty',
      answer: GUIDE_EMPTY_PROMPT,
      behavior: 'fallback',
      confidence: 1,
      followUpSuggestions: GUIDE_FOLLOWUP_PROMPTS.slice(0, 3),
    };
  }

  if (isSecuritySensitive(trimmed)) {
    return {
      topicId: 'security-refuse',
      answer: GUIDE_SECURITY_REFUSAL,
      behavior: 'refuse',
      confidence: 1,
      followUpSuggestions: ['What can this platform do?', 'What is demo mode?'],
    };
  }

  if (isFollowUp(trimmed) && context.lastTopicId) {
    const prev = topicById(context.lastTopicId);
    if (prev) {
      return {
        ...buildAnswer(prev),
        topicId: prev.id,
        confidence: 0.85,
        answer: `Continuing from **${prev.title}**:\n\n${prev.answer}`,
      };
    }
  }

  const tokens = queryTokens(trimmed);

  if (/^(hi|hello|hey|thanks|thank you)\b/i.test(trimmed)) {
    return {
      topicId: 'capabilities',
      answer: GUIDE_CAPABILITIES,
      behavior: 'answer',
      confidence: 0.65,
      followUpSuggestions: GUIDE_FOLLOWUP_PROMPTS.slice(0, 4),
    };
  }

  const direct = tryDirectRoute(trimmed);
  if (direct) {
    return { ...buildAnswer(direct), confidence: 0.92 };
  }

  const invTopic = tryInvestigationDisambiguation(trimmed);
  if (invTopic) {
    return { ...buildAnswer(invTopic), confidence: 0.91 };
  }

  const scored = GUIDE_TOPICS.map((topic) => ({
    topic,
    score: scoreTopic(topic, trimmed, tokens),
  }))
    .filter((s) => s.score > 0)
    .sort((a, b) => b.score - a.score);

  if (scored.length === 0) {
    return {
      topicId: 'fallback',
      answer: GUIDE_FALLBACK_ANSWER,
      behavior: 'fallback',
      confidence: 0.2,
      followUpSuggestions: GUIDE_FOLLOWUP_PROMPTS,
    };
  }

  const top = scored[0];
  const second = scored[1];
  const maxScore = top.score;

  if (
    second &&
    second.score >= MIN_SCORE &&
    top.score > 0 &&
    second.score / top.score >= CLARIFY_GAP_RATIO &&
    top.topic.category !== second.topic.category &&
    top.score < 7
  ) {
    return {
      topicId: 'clarify',
      answer: GUIDE_AMBIGUOUS_CLARIFY,
      behavior: 'clarify',
      confidence: top.score / (top.score + second.score),
      clarificationOptions: [top.topic.title, second.topic.title],
      followUpSuggestions: [top.topic.title, second.topic.title],
    };
  }

  if (maxScore < MIN_SCORE) {
    return {
      topicId: 'fallback',
      answer: GUIDE_FALLBACK_ANSWER,
      behavior: 'fallback',
      confidence: maxScore / MIN_SCORE,
      followUpSuggestions: GUIDE_FOLLOWUP_PROMPTS,
    };
  }

  const confidence = Math.min(0.98, 0.45 + maxScore / 25);
  return {
    ...buildAnswer(top.topic),
    confidence,
  };
}

/** Backward-compatible shape for older tests */
export function findGuideAnswerLegacy(query: string): { topicId: string; answer: string } {
  const r = findGuideAnswer(query);
  return { topicId: r.topicId, answer: r.answer };
}

const MIN_REPLY_MS = 280;
const MAX_REPLY_MS = 520;

export function replyDelayMs(): number {
  return MIN_REPLY_MS + Math.floor(Math.random() * (MAX_REPLY_MS - MIN_REPLY_MS));
}

export async function getGuideReplyLocal(
  query: string,
  context?: GuideSessionContext,
): Promise<GuideReply> {
  await new Promise((resolve) => setTimeout(resolve, replyDelayMs()));
  return findGuideAnswer(query, context);
}
