import { beforeAll, afterAll, afterEach } from 'vitest';
import { config } from '@vue/test-utils';

// Global test setup
beforeAll(() => {
  // Setup code
});

// Clean up after each test
afterEach(() => {
  // Reset the Vue Test Utils config
  config.global.plugins = [];
  config.global.mocks = {};
});

// Clean up after all tests
afterAll(() => {
  // Cleanup code
}); 