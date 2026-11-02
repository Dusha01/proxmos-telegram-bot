import { describe, expect, it } from 'vitest';
import { createHmac } from 'node:crypto';

import { validateInitDataRaw } from '../src/lib/server/telegram/validateInitDataRaw';

function buildInitData(payload: Record<string, string>, botToken: string): string {
	const params = new URLSearchParams(payload);
	const dataCheckString = [...params.entries()]
		.sort(([a], [b]) => a.localeCompare(b))
		.map(([key, value]) => `${key}=${value}`)
		.join('\n');
	const secretKey = createHmac('sha256', 'WebAppData').update(botToken).digest();
	const hash = createHmac('sha256', secretKey).update(dataCheckString).digest('hex');
	params.set('hash', hash);
	return params.toString();
}

describe('validateInitDataRaw', () => {
	it('accepts valid signature', () => {
		const botToken = '123456:ABC-DEF';
		const authDate = String(Math.floor(Date.now() / 1000));
		const raw = buildInitData(
			{
				auth_date: authDate,
				user: JSON.stringify({ id: 42, first_name: 'Test' })
			},
			botToken
		);
		const parsed = validateInitDataRaw(raw, botToken, 86400);
		expect(parsed.user.id).toBe(42);
		expect(parsed.chat).toBeUndefined();
	});

	it('rejects tampered hash', () => {
		const botToken = '123456:ABC-DEF';
		const raw = buildInitData(
			{
				auth_date: String(Math.floor(Date.now() / 1000)),
				user: JSON.stringify({ id: 1 })
			},
			botToken
		);
		expect(() => validateInitDataRaw(`${raw}x`, botToken, 86400)).toThrow();
	});
});
