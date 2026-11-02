import { handleGetGuest } from '$lib/server/api/guests';
import type { GuestKind } from '$lib/shared/api/types';

function parseKind(value: string): GuestKind | null {
	return value === 'qemu' || value === 'lxc' ? value : null;
}

export const GET = ({ request, params }) => {
	const kind = parseKind(params.kind);
	const vmid = Number(params.vmid);
	if (!kind || !Number.isFinite(vmid)) {
		return Response.json({ code: 'bad_request', message: 'Invalid kind or vmid' }, { status: 400 });
	}
	return handleGetGuest(request, kind, vmid);
};
