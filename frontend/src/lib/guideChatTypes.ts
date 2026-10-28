/** Shared types for the documentation-based guide assistant (Level A + optional Level B). */

export type GuideCategory =
  | 'overview'
  | 'navigation'
  | 'incidents'
  | 'severity'
  | 'status'
  | 'investigation'
  | 'results'
  | 'timeline'
  | 'analytics'
  | 'demo'
  | 'troubleshooting'
  | 'faq'
  | 'limitations'
  | 'security';

export type GuideReplyBehavior = 'answer' | 'clarify' | 'refuse' | 'fallback';

export type GuideTopic = {
  id: string;
  title: string;
  category: GuideCategory;
  /** Short tokens and phrases for matching */
  keywords: string[];
  /** Longer natural-language triggers */
  phrases?: string[];
  answer: string;
  followUpSuggestions?: string[];
  relatedTopicIds?: string[];
};

export type GuideSessionContext = {
  lastTopicId?: string;
  lastUserQuestion?: string;
};

/** Optional engine / provider inputs (not persisted in chat session). */
export type GuideReplyOptions = {
  /** Clock for time-of-day greetings; defaults to `new Date()` (browser local time). */
  now?: Date;
};

export type GuideReply = {
  topicId: string;
  answer: string;
  behavior: GuideReplyBehavior;
  /** 0–1 match confidence for the selected topic (not ML model probability). */
  confidence: number;
  followUpSuggestions?: string[];
  clarificationOptions?: string[];
};

export type GuideEvaluationExpectation = 'answer' | 'clarify' | 'refuse' | 'fallback';

export type GuideEvaluationCase = {
  id: string;
  question: string;
  expectedTopicId: string;
  /** When multiple topics are acceptable (paraphrase overlap). */
  acceptableTopicIds?: string[];
  expectedBehavior: GuideEvaluationExpectation;
  context?: GuideSessionContext;
  notes?: string;
};

export type GuideEvaluationReport = {
  total: number;
  topicMatch: number;
  behaviorMatch: number;
  topicAccuracy: number;
  behaviorAccuracy: number;
  failures: { id: string; question: string; expectedTopicId: string; gotTopicId: string; expectedBehavior: string; gotBehavior: string }[];
};
