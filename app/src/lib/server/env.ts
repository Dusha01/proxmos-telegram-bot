import {
	API_BASE_URL,
	APP_ENV,
	BOT_API_TOKEN,
	DEV_ADMIN_USER_ID,
	DEV_MINI_APP_CHAT_ID,
	INIT_DATA_MAX_AGE_SEC,
	TELEGRAM_BOT_TOKEN
} from '$app/env/private';

export type ServerEnv = {
	telegramBotToken: string;
	botApiToken: string;
	apiBaseUrl: string;
	initDataMaxAgeSec: number;
	appEnv: string;
	devAdminUserId: number;
	devMiniAppChatId: number;
};

let cached: ServerEnv | null = null;

/** Kit env first; Vitest sets `process.env` without regenerating `$app/env/private`. */
function envString(kitValue: string | undefined, name: string): string | undefined {
	const fromKit = kitValue?.trim();
	if (fromKit) {
		return fromKit;
	}
	return process.env[name]?.trim();
}

export function getServerEnv(): ServerEnv {
	if (cached) {
		return cached;
	}
	const telegramBotToken = envString(TELEGRAM_BOT_TOKEN, 'TELEGRAM_BOT_TOKEN');
	const botApiToken = envString(BOT_API_TOKEN, 'BOT_API_TOKEN');
	const apiBaseUrl = (
		envString(API_BASE_URL, 'API_BASE_URL') ?? 'http://127.0.0.1:8000'
	).replace(/\/$/, '');
	if (!telegramBotToken || !botApiToken) {
		throw new Error('TELEGRAM_BOT_TOKEN and BOT_API_TOKEN are required');
	}
	const appEnv = envString(APP_ENV, 'APP_ENV') ?? 'dev';
	const initRaw = envString(INIT_DATA_MAX_AGE_SEC, 'INIT_DATA_MAX_AGE_SEC');
	const devUserRaw = envString(DEV_ADMIN_USER_ID, 'DEV_ADMIN_USER_ID');
	const devChatRaw = envString(DEV_MINI_APP_CHAT_ID, 'DEV_MINI_APP_CHAT_ID');
	cached = {
		telegramBotToken,
		botApiToken,
		apiBaseUrl,
		initDataMaxAgeSec: Number(initRaw ?? 86400),
		appEnv,
		devAdminUserId: Number(devUserRaw ?? 0),
		devMiniAppChatId: Number(devChatRaw ?? 0)
	};
	return cached;
}

/** @internal test helper */
export function resetServerEnvCache(): void {
	cached = null;
}
