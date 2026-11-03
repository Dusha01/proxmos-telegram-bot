import { apiFetch } from '$lib/shared/api/client';
import type { GuestListDto, GuestKind } from '$lib/shared/api/types';

export async function fetchGuestList(kind: GuestKind): Promise<GuestListDto> {
	return apiFetch<GuestListDto>(`/api/guests?kind=${kind}`);
}
