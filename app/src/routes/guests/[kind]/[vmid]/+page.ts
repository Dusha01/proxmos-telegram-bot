import { error } from '@sveltejs/kit';
import type { GuestKind } from '$lib/shared/api/types';

export function load({ params }) {
	const kind = params.kind;
	const vmid = Number(params.vmid);
	if (kind !== 'qemu' && kind !== 'lxc') {
		error(404, 'Unknown guest kind');
	}
	if (!Number.isFinite(vmid)) {
		error(404, 'Invalid vmid');
	}
	return { kind: kind as GuestKind, vmid };
}
