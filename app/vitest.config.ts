import path from 'node:path';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	resolve: {
		alias: {
			$lib: path.resolve('src/lib'),
			'$app/env/private': path.resolve('tests/mocks/app-env-private.ts')
		}
	},
	test: {
		include: ['tests/**/*.test.ts']
	}
});
