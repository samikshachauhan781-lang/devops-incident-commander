import { test, expect } from '@playwright/test';
import { findGuideAnswer } from './src/lib/guideChatEngine';
import {
  getGuideGreetingAnswerForPeriod,
  getGuideGreetingPeriod,
  localGuideTime,
} from './src/lib/guideGreetingTime';

test.describe('Guide greeting — local time periods', () => {
  test('period boundaries (local clock fields)', () => {
    expect(getGuideGreetingPeriod(localGuideTime(0, 0))).toBe('night');
    expect(getGuideGreetingPeriod(localGuideTime(4, 59))).toBe('night');
    expect(getGuideGreetingPeriod(localGuideTime(5, 0))).toBe('morning');
    expect(getGuideGreetingPeriod(localGuideTime(11, 59))).toBe('morning');
    expect(getGuideGreetingPeriod(localGuideTime(12, 0))).toBe('afternoon');
    expect(getGuideGreetingPeriod(localGuideTime(16, 59))).toBe('afternoon');
    expect(getGuideGreetingPeriod(localGuideTime(17, 0))).toBe('evening');
    expect(getGuideGreetingPeriod(localGuideTime(20, 59))).toBe('evening');
    expect(getGuideGreetingPeriod(localGuideTime(21, 0))).toBe('night');
  });

  test('each period maps to distinct greeting copy', () => {
    const morning = getGuideGreetingAnswerForPeriod('morning').toLowerCase();
    const afternoon = getGuideGreetingAnswerForPeriod('afternoon').toLowerCase();
    const evening = getGuideGreetingAnswerForPeriod('evening').toLowerCase();
    const night = getGuideGreetingAnswerForPeriod('night').toLowerCase();
    expect(morning).toContain('good morning');
    expect(afternoon).toContain('good afternoon');
    expect(evening).toContain('good evening');
    expect(night).toContain('late');
  });

  test('hello uses injectable local time, not wall clock', () => {
    const afternoon = localGuideTime(14, 0);
    const r = findGuideAnswer('hello', {}, { now: afternoon });
    expect(r.topicId).toBe('conv-greeting');
    expect(r.answer.toLowerCase()).toContain('good afternoon');
  });

  test('good morning in the afternoon uses actual local period', () => {
    const afternoon = localGuideTime(15, 30);
    const r = findGuideAnswer('good morning', {}, { now: afternoon });
    expect(r.answer.toLowerCase()).toContain('good afternoon');
    expect(r.answer.toLowerCase()).not.toMatch(/^good morning/);
  });

  test('good evening at night uses night copy, not evening echo', () => {
    const late = localGuideTime(22, 0);
    const r = findGuideAnswer('good evening', {}, { now: late });
    expect(r.answer.toLowerCase()).toContain('late');
    expect(r.answer.toLowerCase()).not.toContain('good evening');
  });

  test('timezone uses Date local fields (same instant, different local hour)', () => {
    const utcNoon = new Date('2026-10-28T12:00:00.000Z');
    const period = getGuideGreetingPeriod(utcNoon);
    const expectedHour = utcNoon.getHours();
    if (expectedHour >= 12 && expectedHour <= 16) {
      expect(period).toBe('afternoon');
    } else if (expectedHour >= 5 && expectedHour <= 11) {
      expect(period).toBe('morning');
    }
    const r = findGuideAnswer('hi', {}, { now: utcNoon });
    expect(r.topicId).toBe('conv-greeting');
    expect(r.answer).toBe(getGuideGreetingAnswerForPeriod(period));
  });
});
