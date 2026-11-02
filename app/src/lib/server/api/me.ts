import {
	authErrorResponse,
	resolveTelegramContext,
	AuthError
} from '$lib/server/auth/resolveRequestContext';
import { backendErrorResponse, BackendError, backendRequest } from '$lib/server/backend/client';
import type { MeDto } from '$lib/shared/api/types';

export async function handleMe(request: Request): Promise<Response> {
	try {
		const ctx = resolveTelegramContext(request);
		await backendRequest<void>(ctx, '/access');
		const body: MeDto = {
			userId: ctx.userId,
			chatId: ctx.chatId,
			displayName: ctx.displayName
		};
		return Response.json(body);
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
