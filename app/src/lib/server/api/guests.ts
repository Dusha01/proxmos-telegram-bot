import {
	authErrorResponse,
	resolveTelegramContext,
	AuthError
} from '$lib/server/auth/resolveRequestContext';
import { backendErrorResponse, BackendError, backendRequest } from '$lib/server/backend/client';
import type { GuestDto, GuestKind, GuestListDto } from '$lib/shared/api/types';

export async function handleListGuests(request: Request, kind: GuestKind): Promise<Response> {
	try {
		const ctx = resolveTelegramContext(request);
		const data = await backendRequest<GuestListDto>(ctx, `/guests?kind=${kind}`);
		return Response.json(data);
	} catch (error) {
		if (error instanceof AuthError) {
			return authErrorResponse(error);
		}
		if (error instanceof BackendError) {
			return backendErrorResponse(error);
		}
		throw error;
	}
}

export async function handleGetGuest(
	request: Request,
	kind: GuestKind,
	vmid: number
): Promise<Response> {
	try {
		const ctx = resolveTelegramContext(request);
		const guest = await backendRequest<GuestDto>(ctx, `/guests/${kind}/${vmid}`);
		return Response.json(guest);
	} catch (error) {
		if (error instanceof AuthError) {
			return authErrorResponse(error);
		}
		if (error instanceof BackendError) {
			return backendErrorResponse(error);
		}
		throw error;
	}
}
