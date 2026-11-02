import { browser } from '$app/env';

type TelegramWebApp = {
	initData?: string;
	ready?: () => void;
	expand?: () => void;
	BackButton?: {
		show: () => void;
		hide: () => void;
		onClick: (cb: () => void) => void;
		offClick: (cb: () => void) => void;
	};
	themeParams?: Record<string, string>;
	HapticFeedback?: {
		notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
	};
};

declare global {
	interface Window {
		Telegram?: { WebApp?: TelegramWebApp };
	}
}

export function getTelegramWebApp(): TelegramWebApp | null {
	if (!browser) {
		return null;
	}
	return window.Telegram?.WebApp ?? null;
}

export function getTelegramInitData(): string {
	return getTelegramWebApp()?.initData?.trim() ?? '';
}

export function getDevAuthHeader(): string {
	return 'dev';
}

export function initTelegramChrome(): void {
	const webApp = getTelegramWebApp();
	if (!webApp) {
		return;
	}
	webApp.ready?.();
	webApp.expand?.();
	applyThemeParams(webApp.themeParams);
}

function applyThemeParams(params?: Record<string, string>): void {
	if (!params || !browser) {
		return;
	}
	const root = document.documentElement;
	for (const [key, value] of Object.entries(params)) {
		const cssKey = key.replace(/_/g, '-');
		root.style.setProperty(`--tg-theme-${cssKey}`, value);
	}
}

export function hapticSuccess(): void {
	getTelegramWebApp()?.HapticFeedback?.notificationOccurred('success');
}

export function hapticError(): void {
	getTelegramWebApp()?.HapticFeedback?.notificationOccurred('error');
}
