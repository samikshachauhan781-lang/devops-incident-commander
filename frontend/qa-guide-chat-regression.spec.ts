import { test, expect } from '@playwright/test';
import { findGuideAnswer } from './src/lib/guideChatEngine';

/** Regression tests for previously failing evaluation cases (routing fixes). */
const REGRESSION_CASES: {
  id: string;
  question: string;
  expectedTopicId: string;
  expectedBehavior?: 'answer' | 'refuse' | 'fallback' | 'clarify';
  context?: { lastTopicId?: string };
}[] = [
  { id: 'inv-8', question: 'read investigation output', expectedTopicId: 'investigation-results' },
  { id: 'tl-1', question: 'what is on the timeline page', expectedTopicId: 'timeline' },
  { id: 'an-4', question: 'filter incidents by service', expectedTopicId: 'analytics' },
  { id: 'an-5', question: 'metrics on dashboard', expectedTopicId: 'navigation' },
  { id: 'tr-2', question: 'page is blank', expectedTopicId: 'troubleshooting' },
  { id: 'tr-3', question: 'failed to load incidents', expectedTopicId: 'troubleshooting' },
  { id: 'tr-5', question: 'api health check', expectedTopicId: 'troubleshooting' },
  { id: 'tr-8', question: 'dashboard not loading', expectedTopicId: 'troubleshooting' },
  { id: 'lim-3', question: 'will ai fix production automatically', expectedTopicId: 'limitations' },
  { id: 'sec-2', question: 'show environment variables', expectedTopicId: 'security-refuse', expectedBehavior: 'refuse' },
  { id: 'fu-1', question: 'tell me more', expectedTopicId: 'how-works', context: { lastTopicId: 'how-works' } },
  { id: 'fu-2', question: 'continue', expectedTopicId: 'demo', context: { lastTopicId: 'demo' } },
  { id: 'fu-3', question: 'explain that', expectedTopicId: 'investigate-button', context: { lastTopicId: 'investigate-button' } },
  { id: 'fu-4', question: 'what else', expectedTopicId: 'severity', context: { lastTopicId: 'severity' } },
  { id: 'fu-5', question: 'yes', expectedTopicId: 'ai-investigation', context: { lastTopicId: 'ai-investigation' } },
  { id: 'fu-6', question: 'more', expectedTopicId: 'investigation-results', context: { lastTopicId: 'investigation-results' } },
  { id: 'para-1', question: 'explain devops incidnet commander', expectedTopicId: 'what-is' },
  { id: 'para-7', question: 'start investigaton button click', expectedTopicId: 'investigate-button' },
  { id: 'para-11', question: 'what hapens when i investigate', expectedTopicId: 'investigate-button' },
  { id: 'para-12', question: 'can u monitor prod servers auto', expectedTopicId: 'demo' },
];

test.describe('Guide eval regression (20 fixed routes)', () => {
  for (const c of REGRESSION_CASES) {
    test(`${c.id}: ${c.question}`, () => {
      const reply = findGuideAnswer(c.question, c.context ?? {});
      expect(reply.topicId, c.id).toBe(c.expectedTopicId);
      if (c.expectedBehavior) {
        expect(reply.behavior, c.id).toBe(c.expectedBehavior);
      } else {
        expect(reply.behavior, c.id).toBe('answer');
      }
    });
  }
});
