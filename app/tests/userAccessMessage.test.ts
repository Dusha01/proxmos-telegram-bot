import { describe, expect, it } from 'vitest';

import {
	ACCESS_DENIED_USER_MESSAGE,
	userMessageForAccessError
} from '$lib/features/accessGate/lib/userAccessMessage';
import { ApiClientError } from '$lib/shared/api/client';

function err(status: number, message = 'x'): ApiClientError {
	return new ApiClientError(status, 'test', message);
}

describe('userMessageForAccessError', () => {
	it('maps 401/403 to short access denied text', () => {
		expect(userMessageForAccessError(err(401))).toBe(ACCESS_DENIED_USER_MESSAGE);
		expect(userMessageForAccessError(err(403))).toBe(ACCESS_DENIED_USER_MESSAGE);
	});

	it('maps 5xx to service unavailable', () => {
		expect(userMessageForAccessError(err(503))).toBe(
			'Сервис временно недоступен. Попробуйте позже.'
		);
	});

	it('falls back to error message or default', () => {
		expect(userMessageForAccessError(err(404, 'Not found'))).toBe('Not found');
		expect(userMessageForAccessError(err(418, ''))).toBe(ACCESS_DENIED_USER_MESSAGE);
	});
});
