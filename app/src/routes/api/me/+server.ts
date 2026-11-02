import { handleMe } from '$lib/server/api/me';

export const GET = (event) => handleMe(event.request);
