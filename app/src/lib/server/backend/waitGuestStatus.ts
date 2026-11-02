import type { GuestKind, GuestStatus, PowerAction } from '$lib/shared/api/types';
import { backendRequest } from '$lib/server/backend/client';
import type { TelegramContext } from '$lib/server/telegram/resolveContext';
import type { GuestDto } from '$lib/shared/api/types';

const ACTION_EXPECTED_STATUS: Record<PowerAction, GuestStatus> = {
	start: 'running',
	stop: 'stopped',
	shutdown: 'stopped',
	reboot: 'running',
	suspend: 'paused',
	resume: 'running'
};

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export async function waitForGuestStatus(
	ctx: TelegramContext,
	kind: GuestKind,
	vmid: number,
	expectedStatus: GuestStatus,
	timeoutMs = 90_000,
	intervalMs = 2_000
): Promise<{ guest: GuestDto; reachedExpected: boolean }> {
	const deadline = Date.now() + timeoutMs;
	let lastGuest: GuestDto | null = null;
	while (Date.now() < deadline) {
		lastGuest = await backendRequest<GuestDto>(ctx, `/guests/${kind}/${vmid}`);
		if (lastGuest.status === expectedStatus) {
			return { guest: lastGuest, reachedExpected: true };
		}
		await sleep(intervalMs);
	}
	if (!lastGuest) {
		lastGuest = await backendRequest<GuestDto>(ctx, `/guests/${kind}/${vmid}`);
	}
	return { guest: lastGuest, reachedExpected: lastGuest.status === expectedStatus };
}

export function expectedStatusForAction(action: PowerAction): GuestStatus {
	return ACTION_EXPECTED_STATUS[action];
}
