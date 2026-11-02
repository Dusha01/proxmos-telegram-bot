import { building } from '$app/env';
import { defineEnvVars } from '@sveltejs/kit/env';

/** Dev-only or injected at container start — not required during `vite build` in Docker. */
function optionalString(value: string | undefined): string | undefined {
	return value;
}

function requiredAtRuntime(name: string) {
	return (value: string | undefined): string | undefined => {
		if (building) {
			return value;
		}
		if (value === undefined || value.trim() === '') {
			throw new Error(`${name} is required`);
		}
		return value;
	};
}

export const variables = defineEnvVars({
	TELEGRAM_BOT_TOKEN: {
		description: 'Telegram bot token (initData HMAC)',
		schema: requiredAtRuntime('TELEGRAM_BOT_TOKEN')
	},
	BOT_API_TOKEN: {
		description: 'Shared secret for FastAPI X-Bot-Token',
		schema: requiredAtRuntime('BOT_API_TOKEN')
	},
	API_BASE_URL: {
		description: 'FastAPI base URL (BFF → backend)',
		schema: optionalString
	},
	INIT_DATA_MAX_AGE_SEC: {
		description: 'Max age of WebApp initData auth_date',
		schema: optionalString
	},
	APP_ENV: {
		description: 'dev | prod (enables Authorization: dev in dev)',
		schema: optionalString
	},
	DEV_ADMIN_USER_ID: {
		description: 'Browser dev auth: Telegram user id (dev only)',
		schema: optionalString
	},
	DEV_MINI_APP_CHAT_ID: {
		description: 'Browser dev auth: chat id passed to /access (dev only)',
		schema: optionalString
	}
});
