import { defineEnvVars } from '@sveltejs/kit/env';

export const variables = defineEnvVars({
	TELEGRAM_BOT_TOKEN: {
		description: 'Telegram bot token (initData HMAC)'
	},
	BOT_API_TOKEN: {
		description: 'Shared secret for FastAPI X-Bot-Token'
	},
	API_BASE_URL: {
		description: 'FastAPI base URL (BFF → backend)'
	},
	INIT_DATA_MAX_AGE_SEC: {
		description: 'Max age of WebApp initData auth_date'
	},
	APP_ENV: {
		description: 'dev | prod (enables Authorization: dev in dev)'
	},
	DEV_ADMIN_USER_ID: {
		description: 'Browser dev auth: Telegram user id'
	},
	DEV_MINI_APP_CHAT_ID: {
		description: 'Browser dev auth: chat id passed to /access'
	}
});
