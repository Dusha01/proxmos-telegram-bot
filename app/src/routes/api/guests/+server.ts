import { handleListGuests } from '$lib/server/api/guests';
import type { GuestKind } from '$lib/shared/api/types';

export const GET = ({ request, url }) => {
	const kind = url.searchParams.get('kind');
	if (kind !== 'qemu' && kind !== 'lxc') {
		return Response.json({ code: 'bad_request', message: 'kind must be qemu or lxc' }, { status: 400 });
	}
	return handleListGuests(request, kind as GuestKind);
};
