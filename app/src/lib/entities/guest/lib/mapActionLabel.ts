import type { PowerAction } from '$lib/shared/api/types';

const LABELS: Record<PowerAction, string> = {
	start: 'Запуск',
	stop: 'Стоп',
	shutdown: 'Выключить (ACPI)',
	suspend: 'Пауза',
	resume: 'Продолжить',
	reboot: 'Перезагрузить'
};

export function mapActionLabel(action: PowerAction): string {
	return LABELS[action];
}
