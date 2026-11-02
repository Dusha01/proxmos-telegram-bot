import type { ParsedInitData } from '$lib/server/telegram/validateInitData';

export type TelegramContext = {
	userId: number;
	chatId: number;
	displayName: string;
};

/** Telegram uses user id as chat id in private chats; initData `chat.id` can differ from Message.chat.id. */
export function resolveChatIdFromInitData(parsed: ParsedInitData): number {
	const userId = Number(parsed.user.id);
	if (!Number.isFinite(userId)) {
		throw new Error('initData: invalid user.id');
	}
	const chatType = (parsed.chat?.type ?? parsed.chatType ?? '').toLowerCase();
	if (!parsed.chat || chatType === 'private' || chatType === 'sender') {
		return userId;
	}
	const chatId = Number(parsed.chat.id);
	if (!Number.isFinite(chatId)) {
		throw new Error('initData: invalid chat.id');
	}
	return chatId;
}

export function contextFromInitData(parsed: ParsedInitData): TelegramContext {
	const userId = Number(parsed.user.id);
	const chatId = resolveChatIdFromInitData(parsed);
	const parts = [parsed.user.first_name, parsed.user.last_name].filter(Boolean);
	const displayName =
		parts.join(' ').trim() || parsed.user.username || String(parsed.user.id);
	return {
		userId,
		chatId,
		displayName
	};
}
