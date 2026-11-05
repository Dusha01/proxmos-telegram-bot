import { handleNodePowerAction } from '$lib/server/api/node';

export const POST = ({ request }: { request: Request }) =>
	handleNodePowerAction(request, 'reboot');
