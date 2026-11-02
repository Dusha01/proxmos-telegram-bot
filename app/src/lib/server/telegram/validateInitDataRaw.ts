import { createHmac, timingSafeEqual } from 'node:crypto';

export type InitDataUser = {
	id: number;
	first_name?: string;
	last_name?: string;
	username?: string;
};

export type InitDataChat = {
	id: number;
	type?: string;
	title?: string;
};

export type ParsedInitData = {
	user: InitDataUser;
	chat?: InitDataChat;
	/** From initData `chat_type` when `chat` is absent or for disambiguation. */
	chatType?: string;
	authDate: number;
};

export class InitDataError extends Error {
	constructor(message: string) {
		super(message);
		this.name = 'InitDataError';
	}
}

export function validateInitDataRaw(
	rawInitData: string,
	botToken: string,
	maxAgeSec: number
): ParsedInitData {
	const params = new URLSearchParams(rawInitData);
	const hash = params.get('hash');
	if (!hash) {
		throw new InitDataError('initData: missing hash');
	}
	params.delete('hash');
	const dataCheckString = [...params.entries()]
		.sort(([a], [b]) => a.localeCompare(b))
		.map(([key, value]) => `${key}=${value}`)
		.join('\n');
	const secretKey = createHmac('sha256', 'WebAppData').update(botToken).digest();
	const calculated = createHmac('sha256', secretKey).update(dataCheckString).digest('hex');
	const a = Buffer.from(calculated, 'utf8');
	const b = Buffer.from(hash, 'utf8');
	if (a.length !== b.length || !timingSafeEqual(a, b)) {
		throw new InitDataError('initData: invalid signature');
	}
	const authDate = Number(params.get('auth_date'));
	if (!Number.isFinite(authDate)) {
		throw new InitDataError('initData: missing auth_date');
	}
	const now = Math.floor(Date.now() / 1000);
	if (now - authDate > maxAgeSec) {
		throw new InitDataError('initData: expired');
	}
	const userRaw = params.get('user');
	if (!userRaw) {
		throw new InitDataError('initData: missing user');
	}
	let user: InitDataUser;
	try {
		user = JSON.parse(userRaw) as InitDataUser;
	} catch {
		throw new InitDataError('initData: invalid user json');
	}
	if (!user.id) {
		throw new InitDataError('initData: missing user.id');
	}
	let chat: InitDataChat | undefined;
	const chatRaw = params.get('chat');
	if (chatRaw) {
		try {
			chat = JSON.parse(chatRaw) as InitDataChat;
		} catch {
			throw new InitDataError('initData: invalid chat json');
		}
	}
	const chatType = params.get('chat_type') ?? undefined;
	return { user, chat, chatType, authDate };
}
