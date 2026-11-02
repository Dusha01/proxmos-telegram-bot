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
