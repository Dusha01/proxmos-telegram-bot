export type GuestKind = 'qemu' | 'lxc';

export type GuestStatus = 'running' | 'stopped' | 'paused' | 'unknown';

export type PowerAction = 'start' | 'stop' | 'shutdown' | 'suspend' | 'resume' | 'reboot';

export type GuestDto = {
	vmid: number;
	name: string;
	kind: GuestKind;
	status: GuestStatus;
};

export type GuestListDto = {
	items: GuestDto[];
	total: number;
};

export type PowerActionResultDto = {
	guest: GuestDto;
	reachedExpected: boolean;
	action: PowerAction;
};

export type ApiErrorDto = {
	code: string;
	message: string;
};

export type MeDto = {
	userId: number;
	chatId: number;
	displayName: string;
};

export type MetricPointDto = {
	timestamp: number;
	value: number;
};

export type MetricSeriesDto = {
	label: string;
	unit: string;
	points: MetricPointDto[];
};

export type StorageVolumeDto = {
	id: string;
	name: string;
	type: string | null;
	used: number;
	total: number;
	avail: number;
	usedPercent: number;
};

export type RootDiskUsageDto = {
	used: number;
	total: number;
	usedPercent: number;
};

export type NodeMetricsDto = {
	node: string;
	uptime: number | null;
	loadSeries: MetricSeriesDto[];
	memorySeries: MetricSeriesDto | null;
	temperatureSeries: MetricSeriesDto[];
	temperatureAvailable: boolean;
	diskTemperatureSeries: MetricSeriesDto[];
	diskTemperatureAvailable: boolean;
	storages: StorageVolumeDto[];
	rootDisk: RootDiskUsageDto | null;
	loadavg: number[];
	cpuPercent: number | null;
	memoryPercent: number | null;
};

export type HostHealthDto = {
	ok: boolean;
	node: string;
	uptime: number | null;
	warnings: string[];
	checkedAt: string;
};

export type HostPowerAction = 'shutdown' | 'reboot';
