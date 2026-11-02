import { APP_ENV as KIT_APP_ENV } from '$app/env/private';

function appEnv(): string {
	return (KIT_APP_ENV?.trim() || process.env.APP_ENV?.trim()) ?? 'dev';
}

export const POST = () => {
	if (appEnv() !== 'dev') {
		return Response.json({ code: 'forbidden', message: 'Dev only' }, { status: 403 });
	}
	return Response.json({
		hint: 'Use Authorization: dev (empty) header in API client when APP_ENV=dev'
	});
};
