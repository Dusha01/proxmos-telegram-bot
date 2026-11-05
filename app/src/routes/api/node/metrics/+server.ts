import { handleNodeMetrics } from '$lib/server/api/node';

export const GET = ({ request }: { request: Request }) => handleNodeMetrics(request);
