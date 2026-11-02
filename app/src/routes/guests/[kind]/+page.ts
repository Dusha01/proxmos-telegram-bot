import { error } from '@sveltejs/kit';
import type { GuestKind } from '$lib/shared/api/types';

export function load({ params }) {
	const kind = params.kind;
	if (kind !== 'qemu' && kind !== 'lxc') {
		error(404, 'Unknown guest kind');
	}
	return { kind: kind as GuestKind };
}
