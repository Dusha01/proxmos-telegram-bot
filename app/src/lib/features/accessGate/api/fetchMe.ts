import { apiFetch } from '$lib/shared/api/client';
import type { MeDto } from '$lib/shared/api/types';

export async function fetchMe(): Promise<MeDto> {
	return apiFetch<MeDto>('/api/me');
}
