import { apiFetch } from '$lib/shared/api/client';
import type { HostPowerAction } from '$lib/shared/api/types';

export async function runHostAction(action: HostPowerAction): Promise<{ message: string }> {
	const path = action === 'shutdown' ? '/api/node/shutdown' : '/api/node/reboot';
	return apiFetch<{ message: string }>(path, { method: 'POST' });
}
