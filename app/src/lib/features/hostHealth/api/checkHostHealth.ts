import { apiFetch } from '$lib/shared/api/client';
import type { HostHealthDto } from '$lib/shared/api/types';

export async function checkHostHealth(): Promise<HostHealthDto> {
	return apiFetch<HostHealthDto>('/api/node/health');
}
