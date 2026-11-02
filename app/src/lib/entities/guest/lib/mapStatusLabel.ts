import type { GuestStatus } from '$lib/shared/api/types';

const STATUS_LABELS: Record<GuestStatus, string> = {
	running: 'работает',
	stopped: 'остановлен',
	paused: 'на паузе',
	unknown: 'неизвестно'
};

const POWER_LABELS: Record<GuestStatus, string> = {
	running: 'включена',
	stopped: 'выключена',
	paused: 'на паузе',
	unknown: 'неизвестно'
};

export function mapStatusLabel(status: GuestStatus): string {
	return STATUS_LABELS[status] ?? status;
}

export function mapPowerStatusLabel(status: GuestStatus): string {
	return POWER_LABELS[status] ?? status;
}

export function statusButtonLabel(status: GuestStatus): string {
	return `Статус: ${mapPowerStatusLabel(status)}`;
}
