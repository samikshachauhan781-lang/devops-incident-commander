import { test, expect } from '@playwright/test';
import { findGuideAnswer, isConversationalTopicId } from './src/lib/guideChatEngine';

test.describe('Guide engine — conversational turns', () => {
  test('greetings use conv-greeting without dumping full capabilities', () => {
    const r = findGuideAnswer('hello');
    expect(r.topicId).toBe('conv-greeting');
    expect(r.behavior).toBe('answer');
    expect(r.answer.length).toBeLessThan(400);
    expect(r.answer.toLowerCase()).toMatch(/hello|guide|incident/);
    expect(r.answer).not.toContain('I **cannot** access your servers');
  });

  test('time-of-day greetings', () => {
    expect(findGuideAnswer('good evening').topicId).toBe('conv-greeting');
    expect(findGuideAnswer('good evening').answer.toLowerCase()).toContain('evening');
  });

  test('introduction who are you', () => {
    const r = findGuideAnswer('who are you?');
    expect(r.topicId).toBe('conv-intro');
    expect(r.answer.toLowerCase()).toContain('documentation');
    expect(r.answer.toLowerCase()).toContain('read-only');
  });

  test('thanks and acknowledgements', () => {
    expect(findGuideAnswer('thank you').topicId).toBe('conv-thanks');
    expect(findGuideAnswer('got it').topicId).toBe('conv-ack');
    expect(findGuideAnswer('understood').topicId).toBe('conv-ack');
  });

  test('closing messages', () => {
    expect(findGuideAnswer('bye').topicId).toBe('conv-closing');
    expect(findGuideAnswer("that's all for now").answer.toLowerCase()).toMatch(/set for now|goodbye/);
  });

  test('follow-up without context clarifies instead of guessing', () => {
    const r = findGuideAnswer('tell me more');
    expect(r.behavior).toBe('clarify');
    expect(r.topicId).toBe('clarify');
  });

  test('acknowledgement preserves session topic for follow-ups', () => {
    const ctx = { lastTopicId: 'demo', lastUserQuestion: 'is this demo mode?' };
    expect(findGuideAnswer('okay', ctx).topicId).toBe('conv-ack');
    const more = findGuideAnswer('tell me more', ctx);
    expect(more.topicId).toBe('demo');
    expect(more.answer.toLowerCase()).toContain('demo');
  });

  test('repeat greeting after prior topic uses return wording', () => {
    const r = findGuideAnswer('hello', { lastTopicId: 'severity', lastUserQuestion: 'critical severity' });
    expect(r.topicId).toBe('conv-greeting');
    expect(r.answer.toLowerCase()).toContain('welcome back');
  });

  test('technical troubleshooting unchanged', () => {
    expect(findGuideAnswer('page is blank').topicId).toBe('troubleshooting');
    expect(findGuideAnswer('give me the api key').behavior).toBe('refuse');
  });

  test('conversational topic ids are flagged', () => {
    expect(isConversationalTopicId('conv-greeting')).toBe(true);
    expect(isConversationalTopicId('demo')).toBe(false);
  });
});

test.describe('Guide chatbot — conversational UI', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/health', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'healthy', demo_mode: true, database: 'incidents_demo.db' }),
      });
    });
    await page.route('**/incidents?**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ incidents: [], page: 1, page_size: 8, total: 0 }),
      });
    });
    await page.route('**/analytics/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          overview: {
            total_incidents: 0,
            critical_incidents: 0,
            investigating_incidents: 0,
            resolved_incidents: 0,
            resolution_rate_percent: 0,
          },
          severity: [],
          status: [],
        }),
      });
    });
  });

  test('sends hello and gets a short friendly reply', async ({ page }) => {
    await page.goto('/');
    await page.getByTestId('guide-chat-fab').evaluate((el) => (el as HTMLButtonElement).click());
    await page.getByTestId('guide-chat-input').fill('hello');
    await page.getByTestId('guide-chat-send').click();
    await expect(page.getByTestId('guide-chat-bot-msg').last()).toContainText(/guide|Hello/i, {
      timeout: 8000,
    });
    const text = await page.getByTestId('guide-chat-bot-msg').last().innerText();
    expect(text.length).toBeLessThan(500);
  });
});
