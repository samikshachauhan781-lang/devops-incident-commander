import { GUIDE_GREETING_TIME } from './guideChatKnowledge';

/** Local time-of-day bucket for guide social greetings. */
export type GuideGreetingPeriod = 'morning' | 'afternoon' | 'evening' | 'night';

/**
 * Maps a clock instant to a greeting period using **local** calendar fields
 * (`Date#getHours()` / `#getMinutes()`), matching the browser timezone.
 *
 * | Period    | Local time (inclusive start, inclusive end) |
 * |-----------|-----------------------------------------------|
 * | Morning   | 5:00 AM – 11:59 AM                            |
 * | Afternoon | 12:00 PM – 4:59 PM                            |
 * | Evening   | 5:00 PM – 8:59 PM                             |
 * | Night     | 9:00 PM – 4:59 AM                             |
 */
export function getGuideGreetingPeriod(date: Date): GuideGreetingPeriod {
  const hour = date.getHours();
  if (hour >= 5 && hour <= 11) return 'morning';
  if (hour >= 12 && hour <= 16) return 'afternoon';
  if (hour >= 17 && hour <= 20) return 'evening';
  return 'night';
}

/** Curated reply for the period — not derived from the user's typed phrase. */
export function getGuideGreetingAnswerForPeriod(period: GuideGreetingPeriod): string {
  switch (period) {
    case 'morning':
      return GUIDE_GREETING_TIME.morning;
    case 'afternoon':
      return GUIDE_GREETING_TIME.afternoon;
    case 'evening':
      return GUIDE_GREETING_TIME.evening;
    case 'night':
      return GUIDE_GREETING_TIME.night;
    default: {
      const _exhaustive: never = period;
      return _exhaustive;
    }
  }
}

/** Build a local `Date` at hour:minute on a fixed calendar day (tests / injectable clock). */
export function localGuideTime(hour: number, minute = 0, year = 2026, monthIndex = 9, day = 28): Date {
  return new Date(year, monthIndex, day, hour, minute, 0, 0);
}
