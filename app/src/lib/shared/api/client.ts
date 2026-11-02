import type { ApiErrorDto } from '$lib/shared/api/types';
import { getTelegramInitData, getDevAuthHeader } from '$lib/shared/lib/telegram/authHeader';

export class ApiClientError extends Error {
	status: number;
	code: string;

	constructor(status: number, code: string, message: string) {
		super(message);
		this.status = status;
		this.code = code;
	}
}

function authorizationHeader(): string {
	const initData = getTelegramInitData();
	if (initData) {
		return `tma ${initData}`;
	}
	return getDevAuthHeader();
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
	const response = await fetch(path, {
		...init,
		headers: {
			Authorization: authorizationHeader(),
			'Content-Type': 'application/json',
			...(init.headers as Record<string, string> | undefined)
		}
	});
	const text = await response.text();
	if (!response.ok) {
		let code = 'error';
		let message = text;
		try {
			const body = JSON.parse(text) as ApiErrorDto;
			code = body.code ?? code;
			message = body.message ?? message;
		} catch {
			/* raw */
		}
		throw new ApiClientError(response.status, code, message);
	}
	if (!text) {
		return undefined as T;
	}
	return JSON.parse(text) as T;
}
