import type { ApiClientError } from '$lib/shared/api/client';

export const ACCESS_DENIED_USER_MESSAGE = 'Нет доступа.';

export function userMessageForAccessError(error: ApiClientError): string {
	if (error.status === 401 || error.status === 403) {
		return ACCESS_DENIED_USER_MESSAGE;
	}
	if (error.status >= 500) {
		return 'Сервис временно недоступен. Попробуйте позже.';
	}
	return error.message || ACCESS_DENIED_USER_MESSAGE;
}
