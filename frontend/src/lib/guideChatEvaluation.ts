import { findGuideAnswer } from './guideChatEngine';
import type { GuideEvaluationCase, GuideEvaluationReport } from './guideChatTypes';
import { GUIDE_EVALUATION_CASES } from './guideChatEvaluationDataset';

export function runGuideEvaluation(
  cases: GuideEvaluationCase[] = GUIDE_EVALUATION_CASES,
): GuideEvaluationReport {
  const failures: GuideEvaluationReport['failures'] = [];
  let topicMatch = 0;
  let behaviorMatch = 0;

  for (const c of cases) {
    const reply = findGuideAnswer(c.question, c.context ?? {});
    const allowed = new Set([c.expectedTopicId, ...(c.acceptableTopicIds ?? [])]);
    const topicOk =
      allowed.has(reply.topicId) ||
      (c.expectedTopicId === 'fallback' && reply.behavior === 'fallback') ||
      (c.expectedTopicId === 'clarify' && reply.behavior === 'clarify') ||
      (c.expectedTopicId === 'security-refuse' && reply.behavior === 'refuse');
    const behaviorOk = reply.behavior === c.expectedBehavior;
    if (topicOk) topicMatch += 1;
    if (behaviorOk) behaviorMatch += 1;
    if (!topicOk || !behaviorOk) {
      failures.push({
        id: c.id,
        question: c.question,
        expectedTopicId: c.expectedTopicId,
        gotTopicId: reply.topicId,
        expectedBehavior: c.expectedBehavior,
        gotBehavior: reply.behavior,
      });
    }
  }

  const total = cases.length;
  return {
    total,
    topicMatch,
    behaviorMatch,
    topicAccuracy: total ? topicMatch / total : 0,
    behaviorAccuracy: total ? behaviorMatch / total : 0,
    failures,
  };
}
