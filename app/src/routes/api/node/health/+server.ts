import { handleNodeHealth } from '$lib/server/api/node';

export const GET = ({ request }: { request: Request }) => handleNodeHealth(request);
