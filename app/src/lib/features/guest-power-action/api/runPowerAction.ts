import { apiFetch } from '$lib/shared/api/client';
import type { GuestKind, PowerAction, PowerActionResultDto } from '$lib/shared/api/types';

export async function runPowerAction(
	kind: GuestKind,
	vmid: number,
	action: PowerAction
): Promise<PowerActionResultDto> {
	return apiFetch<PowerActionResultDto>(`/api/guests/${kind}/${vmid}/${action}`, {
		method: 'POST'
	});
}
