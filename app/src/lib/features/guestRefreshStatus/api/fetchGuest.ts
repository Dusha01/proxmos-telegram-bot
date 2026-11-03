import { apiFetch } from '$lib/shared/api/client';
import type { GuestDto, GuestKind } from '$lib/shared/api/types';

export async function fetchGuest(kind: GuestKind, vmid: number): Promise<GuestDto> {
	return apiFetch<GuestDto>(`/api/guests/${kind}/${vmid}`);
}
