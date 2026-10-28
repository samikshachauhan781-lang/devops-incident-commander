/**
 * Level B — optional LLM provider hook (not used by default).
 * The homepage guide is a documentation-based assistant unless VITE_GUIDE_LLM_ENABLED is set
 * and a provider implementation is registered server-side in the future.
 */
import type { GuideReply, GuideReplyOptions, GuideSessionContext } from './guideChatTypes';
import { getGuideReplyLocal } from './guideChatEngine';

export interface GuideChatProvider {
  readonly id: string;
  readonly label: string;
  reply(query: string, context?: GuideSessionContext, options?: GuideReplyOptions): Promise<GuideReply>;
}

/** Default: local retrieval + rule engine (no network). */
export const localDocumentationProvider: GuideChatProvider = {
  id: 'local-docs',
  label: 'Documentation-based guide (local)',
  reply: getGuideReplyLocal,
};

let activeProvider: GuideChatProvider = localDocumentationProvider;

export function getGuideChatProvider(): GuideChatProvider {
  return activeProvider;
}

/** For tests or future wiring only — never points at a paid API from the browser by default. */
export function setGuideChatProvider(provider: GuideChatProvider): void {
  activeProvider = provider;
}

export function resetGuideChatProvider(): void {
  activeProvider = localDocumentationProvider;
}

export async function getGuideReply(
  query: string,
  context?: GuideSessionContext,
  options?: GuideReplyOptions,
): Promise<GuideReply> {
  return activeProvider.reply(query, context, options);
}
