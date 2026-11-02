import { getServerEnv } from '$lib/server/env';
import type { TelegramContext } from '$lib/server/telegram/resolveContext';

export class BackendError extends Error {
	status: number;
	body: string;

	constructor(status: number, body: string) {
		super(`Backend ${status}: ${body.slice(0, 200)}`);
		this.status = status;
		this.body = body;
	}
}

type BackendRequestInit = Omit<RequestInit, 'headers'> & {
	headers?: Record<string, string>;
};

export async function backendRequest<T>(
	ctx: TelegramContext,
	path: string,
	init: BackendRequestInit = {}
): Promise<T> {
	const { botApiToken, apiBaseUrl } = getServerEnv();
	const url = `${apiBaseUrl}${path.startsWith('/') ? path : `/${path}`}`;
	const headers: Record<string, string> = {
		'X-Bot-Token': botApiToken,
		'X-Telegram-User-Id': String(ctx.userId),
		'X-Telegram-Chat-Id': String(ctx.chatId),
		...(init.headers ?? {})
	};
	const response = await fetch(url, { ...init, headers });
	if (response.status === 204) {
		return undefined as T;
	}
	const text = await response.text();
	if (response.status >= 400) {
		throw new BackendError(response.status, text);
	}
	if (!text) {
		return undefined as T;
	}
	return JSON.parse(text) as T;
}

type FastApiErrorBody = { detail?: string };

export function backendErrorResponse(error: BackendError): Response {
	let detail = error.body;
	try {
		const parsed = JSON.parse(error.body) as FastApiErrorBody;
		if (parsed.detail) {
			detail = parsed.detail;
		}
	} catch {
		/* keep raw */
	}
	const code =
		error.status === 403
			? 'forbidden'
			: error.status === 404
				? 'not_found'
				: error.status === 400
					? 'bad_request'
					: error.status === 502
						? 'proxmox_error'
						: 'backend_error';
	return Response.json({ code, message: detail }, { status: error.status });
}
