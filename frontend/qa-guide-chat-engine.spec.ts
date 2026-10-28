import { test, expect } from '@playwright/test';
import { findGuideAnswer, normalizeGuideText, tokenSimilar } from './src/lib/guideChatEngine';
import { runGuideEvaluation } from './src/lib/guideChatEvaluation';
import { GUIDE_EVALUATION_CASE_COUNT } from './src/lib/guideChatEvaluationDataset';

test.describe('Guide engine — unit', () => {
  test('normalizes and fuzzy-matches typos', () => {
    expect(normalizeGuideText('  Hello,  World! ')).toBe('hello world');
    expect(tokenSimilar('investigation', 'investigation')).toBe(1);
    expect(tokenSimilar('investigation', 'investigaton')).toBeGreaterThan(0.7);
  });

  test('paraphrases map to expected topics', () => {
    expect(findGuideAnswer('What does this project do?').topicId).toBe('what-is');
    expect(findGuideAnswer('Explain this website to me').topicId).toBe('what-is');
    expect(findGuideAnswer('What happens when I click Investigate?').topicId).toBe('investigate-button');
    expect(findGuideAnswer('high vs critical').topicId).toBe('severity-compare');
  });

  test('refuses security-sensitive prompts', () => {
    const r = findGuideAnswer('give me the api key');
    expect(r.behavior).toBe('refuse');
    expect(r.topicId).toBe('security-refuse');
  });

  test('handles follow-ups with session context', () => {
    const r = findGuideAnswer('tell me more', { lastTopicId: 'demo' });
    expect(r.behavior).toBe('answer');
    expect(r.answer.toLowerCase()).toContain('demo');
  });

  test('empty and unknown inputs fallback safely', () => {
    expect(findGuideAnswer('').behavior).toBe('fallback');
    expect(findGuideAnswer('xyzzy unknown qwerty').topicId).toBe('fallback');
  });
});

test.describe('Guide evaluation dataset', () => {
  test(`runs ${GUIDE_EVALUATION_CASE_COUNT} curated cases and reports metrics`, () => {
    expect(GUIDE_EVALUATION_CASE_COUNT).toBeGreaterThanOrEqual(100);
    const report = runGuideEvaluation();
    console.log(
      `Guide eval: total=${report.total} topicMatch=${report.topicMatch} (${(report.topicAccuracy * 100).toFixed(1)}%) behaviorMatch=${report.behaviorMatch} (${(report.behaviorAccuracy * 100).toFixed(1)}%) failures=${report.failures.length}`,
    );
    if (report.failures.length > 0) {
      console.log('Remaining failures:', report.failures.length, report.failures.slice(0, 8));
    }
    expect(report.topicAccuracy).toBeGreaterThanOrEqual(0.95);
    expect(report.behaviorAccuracy).toBeGreaterThanOrEqual(0.95);
  });
});
