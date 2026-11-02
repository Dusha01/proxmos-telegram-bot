import type { GuestDto, PowerAction } from '$lib/shared/api/types';
import { mapPowerStatusLabel, mapStatusLabel } from './mapStatusLabel';
import { mapActionLabel } from './mapActionLabel';

export function formatActionResultMessage(
	guest: GuestDto,
	action: PowerAction,
	reachedExpected: boolean
): string {
	const kind = guest.kind.toUpperCase();
	const title = `${kind} ${guest.vmid} — ${guest.name}`;
	const power = mapPowerStatusLabel(guest.status);
	const status = mapStatusLabel(guest.status);

	if (reachedExpected) {
		if (action === 'start' || action === 'resume') {
			return `${title}: успешно включена. Статус: ${status} (${power})`;
		}
		if (action === 'stop') {
			return `${title}: успешно остановлена (стоп). Статус: ${status} (${power})`;
		}
		if (action === 'shutdown') {
			return `${title}: успешно выключена. Статус: ${status} (${power})`;
		}
		if (action === 'reboot') {
			return `${title}: успешно перезагружена. Статус: ${status} (${power})`;
		}
		if (action === 'suspend') {
			return `${title}: на паузе. Статус: ${status} (${power})`;
		}
	}

	return `${title}: команда «${mapActionLabel(action)}» отправлена, ожидаемый статус не достигнут. Сейчас: ${status} (${power})`;
}
