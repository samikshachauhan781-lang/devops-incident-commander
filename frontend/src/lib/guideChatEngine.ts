import {
  GUIDE_AMBIGUOUS_CLARIFY,
  GUIDE_ACK,
  GUIDE_ACK_NO_CONTEXT,
  GUIDE_CLOSING,
  GUIDE_CLOSING_SOFT,
  GUIDE_EMPTY_PROMPT,
  GUIDE_FALLBACK_ANSWER,
  GUIDE_FOLLOWUP_NO_CONTEXT,
  GUIDE_FOLLOWUP_PROMPTS,
  GUIDE_GREETING_DEFAULT,
  GUIDE_GREETING_REPEAT,
  GUIDE_GREETING_RETURN,
  GUIDE_GREETING_TIME,
  GUIDE_INTRO_WHO,
  GUIDE_SECURITY_REFUSAL,
  GUIDE_THANKS,
  GUIDE_THANKS_HELPFUL,
  GUIDE_TOPICS,
  type GuideTopicEntry,
} from './guideChatKnowledge';
import type { GuideReply, GuideSessionContext } from './guideChatTypes';

export type { GuideReply, GuideSessionContext } from './guideChatTypes';

/** Topic IDs that should not replace session `lastTopicId` (social turns). */
export const CONVERSATIONAL_TOPIC_IDS = new Set([
  'conv-greeting',
  'conv-thanks',
  'conv-ack',
  'conv-closing',
  'conv-intro',
]);

export function isConversationalTopicId(topicId: string): boolean {
  return CONVERSATIONAL_TOPIC_IDS.has(topicId);
}

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
  /^what('s| is) next\??$/i,
  /^and then\??$/i,
  /^explain that$/i,
  /^can you explain that\??$/i,
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

const GREETING_PATTERNS = [
  /^good\s+(morning|afternoon|evening)\b[\s!.?,]*$/i,
];

function isGreetingOnly(query: string): boolean {
  const q = normalizeGuideText(query);
  if (/^good (morning|afternoon|evening)\b/.test(q)) {
    return q.split(' ').length <= 4;
  }
  if (/^(hi|hello|hey|howdy|greetings)\b/.test(q)) {
    const rest = q.replace(/^(hi|hello|hey|howdy|greetings)\b\s*/, '').trim();
    if (!rest) return true;
    return /^(there|again|you|folks|team)[\s!.?,]*$/.test(rest);
  }
  return GREETING_PATTERNS.some((re) => re.test(query.trim()));
}

const THANKS_PATTERNS = [
  /^thanks?\b/i,
  /^thank\s+you\b/i,
  /^that('s| is)\s+(helpful|useful)\b/i,
  /^appreciate\s+it\b/i,
];

const ACK_PATTERNS = [
  /^(okay|ok|k)\b[\s!.?,]*$/i,
  /^(got it|understood)\b[\s!.?,]*$/i,
  /^(great|cool|perfect|sounds good|alright|nice)\b[\s!.?,]*$/i,
];

const CLOSING_PATTERNS = [
  /^(bye|goodbye|see you( later)?|talk to you later)\b[\s!.?,]*$/i,
  /^that('s| is)\s+all(\s+for\s+now)?\b[\s!.?,]*$/i,
  /^(done|finished)\s+for\s+now\b[\s!.?,]*$/i,
  /^have a good (one|day|night)\b[\s!.?,]*$/i,
];

const INTRO_PATTERNS = [
  /^who are you\??$/i,
  /^what are you\??$/i,
  /^(introduce yourself|tell me who you are)\b/i,
];

function matchesAny(patterns: RegExp[], text: string): boolean {
  const t = text.trim();
  return patterns.some((re) => re.test(t));
}

function greetingReply(query: string, context: GuideSessionContext): GuideReply {
  const q = normalizeGuideText(query);
  let answer = GUIDE_GREETING_DEFAULT;
  if (/good morning/.test(q)) answer = GUIDE_GREETING_TIME.morning;
  else if (/good afternoon/.test(q)) answer = GUIDE_GREETING_TIME.afternoon;
  else if (/good evening/.test(q)) answer = GUIDE_GREETING_TIME.evening;
  else if (context.lastTopicId && !isConversationalTopicId(context.lastTopicId)) {
    answer = GUIDE_GREETING_RETURN;
  } else if (context.lastUserQuestion && isGreetingOnly(context.lastUserQuestion)) {
    answer = GUIDE_GREETING_REPEAT;
  }
  return {
    topicId: 'conv-greeting',
    answer,
    behavior: 'answer',
    confidence: 0.95,
    followUpSuggestions: GUIDE_FOLLOWUP_PROMPTS.slice(0, 3),
  };
}

function tryConversationalTurn(
  query: string,
  context: GuideSessionContext,
): GuideReply | null {
  const trimmed = query.trim();
  if (isGreetingOnly(trimmed)) {
    return greetingReply(trimmed, context);
  }
  if (matchesAny(INTRO_PATTERNS, trimmed)) {
    return {
      topicId: 'conv-intro',
      answer: GUIDE_INTRO_WHO,
      behavior: 'answer',
      confidence: 0.95,
      followUpSuggestions: ['What can this platform do?', 'What is demo mode?', 'How does AI investigation work?'],
    };
  }
  if (matchesAny(THANKS_PATTERNS, trimmed)) {
    const hasTopic = context.lastTopicId && !isConversationalTopicId(context.lastTopicId);
    return {
      topicId: 'conv-thanks',
      answer: hasTopic ? GUIDE_THANKS_HELPFUL : GUIDE_THANKS,
      behavior: 'answer',
      confidence: 0.95,
      followUpSuggestions: hasTopic
        ? ['Tell me more', 'What else?', 'What is demo mode?']
        : GUIDE_FOLLOWUP_PROMPTS.slice(0, 3),
    };
  }
  if (matchesAny(ACK_PATTERNS, trimmed)) {
    const hasTopic = context.lastTopicId && !isConversationalTopicId(context.lastTopicId);
    return {
      topicId: 'conv-ack',
      answer: hasTopic ? GUIDE_ACK : GUIDE_ACK_NO_CONTEXT,
      behavior: 'answer',
      confidence: 0.95,
      followUpSuggestions: hasTopic
        ? ['Tell me more', 'What\'s next?', 'What else?']
        : GUIDE_FOLLOWUP_PROMPTS.slice(0, 3),
    };
  }
  if (matchesAny(CLOSING_PATTERNS, trimmed)) {
    return {
      topicId: 'conv-closing',
      answer: /all for now|done for now|finished for now/i.test(trimmed)
        ? GUIDE_CLOSING_SOFT
        : GUIDE_CLOSING,
      behavior: 'answer',
      confidence: 0.95,
      followUpSuggestions: [],
    };
  }
  return null;
}

function buildFollowUpReply(prev: GuideTopicEntry, query: string): GuideReply {
  const q = normalizeGuideText(query);
  const isWhatNext = /what(?:'s| is) next/.test(q);

  if (isWhatNext && prev.relatedTopicIds?.length) {
    const related = prev.relatedTopicIds
      .map((id) => topicById(id))
      .filter((t): t is GuideTopicEntry => Boolean(t));
    if (related.length > 0) {
      const bullets = related.map((t) => `- **${t.title}** — ask me about "${t.title.toLowerCase()}"`).join('\n');
      return {
        topicId: prev.id,
        answer: `After **${prev.title}**, good next steps:\n\n${bullets}\n\nOr say **tell me more** to revisit the previous answer.`,
        behavior: 'answer',
        confidence: 0.88,
        followUpSuggestions: related.map((t) => t.title).slice(0, 3),
      };
    }
  }

  const lead =
    /^(yes|ok|okay)\b/.test(q) || /explain that|can you explain/.test(q)
      ? `Sure — more on **${prev.title}**:`
      : `Continuing **${prev.title}**:`;

  return {
    topicId: prev.id,
    answer: `${lead}\n\n${prev.answer}`,
    behavior: 'answer',
    confidence: 0.85,
    followUpSuggestions: prev.followUpSuggestions ?? GUIDE_FOLLOWUP_PROMPTS.slice(0, 3),
  };
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
      return buildFollowUpReply(prev, trimmed);
    }
  }

  if (isFollowUp(trimmed) && !context.lastTopicId) {
    return {
      topicId: 'clarify',
      answer: GUIDE_FOLLOWUP_NO_CONTEXT,
      behavior: 'clarify',
      confidence: 0.5,
      followUpSuggestions: GUIDE_FOLLOWUP_PROMPTS.slice(0, 4),
    };
  }

  const conversational = tryConversationalTurn(trimmed, context);
  if (conversational) {
    return conversational;
  }

  const tokens = queryTokens(trimmed);

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
