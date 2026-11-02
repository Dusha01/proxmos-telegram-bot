import { getServerEnv } from '$lib/server/env';

export {
	InitDataError,
	type InitDataChat,
	type InitDataUser,
	type ParsedInitData,
	validateInitDataRaw
} from '$lib/server/telegram/validateInitDataRaw';

import { validateInitDataRaw } from '$lib/server/telegram/validateInitDataRaw';

export function validateInitData(rawInitData: string) {
	const { telegramBotToken, initDataMaxAgeSec } = getServerEnv();
	return validateInitDataRaw(rawInitData, telegramBotToken, initDataMaxAgeSec);
}
