import { handlePowerAction, isPowerAction } from '$lib/server/api/powerAction';
import type { GuestKind } from '$lib/shared/api/types';

function parseKind(value: string): GuestKind | null {
	return value === 'qemu' || value === 'lxc' ? value : null;
}

export const POST = ({ request, params }) => {
	const kind = parseKind(params.kind);
	const vmid = Number(params.vmid);
	const action = params.action;
	if (!kind || !Number.isFinite(vmid) || !isPowerAction(action)) {
		return Response.json({ code: 'bad_request', message: 'Invalid parameters' }, { status: 400 });
	}
	return handlePowerAction(request, kind, vmid, action);
};
