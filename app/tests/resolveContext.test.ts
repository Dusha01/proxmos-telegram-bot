import { describe, expect, it } from 'vitest';

import {
	contextFromInitData,
	resolveChatIdFromInitData
} from '../src/lib/server/telegram/resolveContext';
import type { ParsedInitData } from '../src/lib/server/telegram/validateInitDataRaw';

describe('resolveChatIdFromInitData', () => {
	const user = { id: 1258984724, first_name: 'A' };

	it('uses user id when chat is missing', () => {
		const parsed: ParsedInitData = { user, authDate: 0 };
		expect(resolveChatIdFromInitData(parsed)).toBe(1258984724);
	});

	it('uses user id for private chat even if chat.id differs', () => {
		const parsed: ParsedInitData = {
			user,
			authDate: 0,
			chat: { id: 7521966293, type: 'private' }
		};
		expect(resolveChatIdFromInitData(parsed)).toBe(1258984724);
	});

	it('uses group chat id for supergroup', () => {
		const parsed: ParsedInitData = {
			user,
			authDate: 0,
			chat: { id: -1003086131623, type: 'supergroup' }
		};
		expect(resolveChatIdFromInitData(parsed)).toBe(-1003086131623);
	});

	it('uses chat_type sender without chat object', () => {
		const parsed: ParsedInitData = {
			user,
			authDate: 0,
			chatType: 'sender'
		};
		expect(contextFromInitData(parsed).chatId).toBe(1258984724);
	});
});
