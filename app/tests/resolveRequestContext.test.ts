import { describe, expect, it } from 'vitest';

import { AuthError, resolveTelegramContext } from '../src/lib/server/auth/resolveRequestContext';
import { resetServerEnvCache } from '../src/lib/server/env';

describe('resolveTelegramContext dev + mini app chat', () => {
	it('dev auth uses DEV_MINI_APP_CHAT_ID as chat', () => {
		process.env.APP_ENV = 'dev';
		process.env.TELEGRAM_BOT_TOKEN = '1:token';
		process.env.BOT_API_TOKEN = 'bot';
		process.env.DEV_ADMIN_USER_ID = '1';
		process.env.DEV_MINI_APP_CHAT_ID = '888';
		resetServerEnvCache();

		const request = new Request('http://local/api/me', {
			headers: { Authorization: 'dev' }
		});
		const ctx = resolveTelegramContext(request);
		expect(ctx.chatId).toBe(888);
	});

	it('dev missing vars throws', () => {
		process.env.APP_ENV = 'dev';
		process.env.TELEGRAM_BOT_TOKEN = '1:token';
		process.env.BOT_API_TOKEN = 'bot';
		process.env.DEV_ADMIN_USER_ID = '0';
		process.env.DEV_MINI_APP_CHAT_ID = '0';
		resetServerEnvCache();

		const request = new Request('http://local/api/me', {
			headers: { Authorization: 'dev' }
		});
		expect(() => resolveTelegramContext(request)).toThrow(AuthError);
	});
});
