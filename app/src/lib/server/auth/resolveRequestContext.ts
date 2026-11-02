import { getServerEnv } from '$lib/server/env';
import { contextFromInitData } from '$lib/server/telegram/resolveContext';
import { InitDataError, validateInitData } from '$lib/server/telegram/validateInitData';
import type { TelegramContext } from '$lib/server/telegram/resolveContext';

export class AuthError extends Error {
	status: number;
	code: string;

	constructor(status: number, code: string, message: string) {
		super(message);
		this.status = status;
		this.code = code;
	}
}

export function resolveTelegramContext(request: Request): TelegramContext {
	const authorization = request.headers.get('Authorization')?.trim() ?? '';
	const { appEnv, devAdminUserId, devMiniAppChatId } = getServerEnv();

	if ((authorization === 'dev' || authorization.startsWith('dev ')) && appEnv === 'dev') {
		if (!devAdminUserId || !devMiniAppChatId) {
			throw new AuthError(
				403,
				'dev_admin_missing',
				'Set DEV_ADMIN_USER_ID and DEV_MINI_APP_CHAT_ID for dev auth'
			);
		}
		return {
			userId: devAdminUserId,
			chatId: devMiniAppChatId,
			displayName: 'Dev admin'
		};
	}

	if (!authorization.startsWith('tma ')) {
		throw new AuthError(401, 'unauthorized', 'Missing Authorization: tma …');
	}
	const rawInitData = authorization.slice(4).trim();
	if (!rawInitData) {
		throw new AuthError(401, 'unauthorized', 'Empty initData');
	}
	try {
		return contextFromInitData(validateInitData(rawInitData));
	} catch (error) {
		if (error instanceof AuthError) {
			throw error;
		}
		if (error instanceof InitDataError) {
			throw new AuthError(401, 'invalid_init_data', error.message);
		}
		throw error;
	}
}

export function authErrorResponse(error: AuthError): Response {
	return Response.json(
		{ code: error.code, message: error.message },
		{ status: error.status }
	);
}
