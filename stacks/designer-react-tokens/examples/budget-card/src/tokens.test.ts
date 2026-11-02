import { execFileSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

// Pass import.meta.url as a string: jsdom replaces the global URL class.
const script = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'scripts', 'build-tokens.mjs');

describe('tokens/tokens.json', () => {
  it('passes the schema and reference check', () => {
    const output = execFileSync(process.execPath, [script, '--check'], { encoding: 'utf8' });
    expect(output).toMatch(/\[tokens\] OK/);
  });
});
