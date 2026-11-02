import {
	authErrorResponse,
	resolveTelegramContext,
	AuthError
} from '$lib/server/auth/resolveRequestContext';
import { backendErrorResponse, BackendError, backendRequest } from '$lib/server/backend/client';
import {
	expectedStatusForAction,
	waitForGuestStatus
} from '$lib/server/backend/waitGuestStatus';
import type { GuestKind, PowerAction, PowerActionResultDto } from '$lib/shared/api/types';

const POWER_ACTIONS = new Set<PowerAction>([
	'start',
	'stop',
	'shutdown',
	'reboot',
	'suspend',
	'resume'
]);

export function isPowerAction(value: string): value is PowerAction {
	return POWER_ACTIONS.has(value as PowerAction);
}

export async function handlePowerAction(
	request: Request,
	kind: GuestKind,
	vmid: number,
	action: PowerAction
): Promise<Response> {
	try {
		const ctx = resolveTelegramContext(request);
		await backendRequest<{ message: string }>(
			ctx,
			`/guests/${kind}/${vmid}/${action}`,
			{ method: 'POST' }
		);
		const expected = expectedStatusForAction(action);
		const { guest, reachedExpected } = await waitForGuestStatus(ctx, kind, vmid, expected);
		const body: PowerActionResultDto = {
			guest,
			reachedExpected,
			action
		};
		return Response.json(body);
	} catch (error) {
		if (error instanceof AuthError) {
			return authErrorResponse(error);
		}
		if (error instanceof BackendError) {
			return backendErrorResponse(error);
		}
		throw error;
	}
}
