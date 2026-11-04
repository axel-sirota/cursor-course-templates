#!/usr/bin/env node
// check_stories.mjs
// Checks that each required component ships its co-located files, exports every
// required Storybook story, and has the required test titles. No dependencies. Node 20+.
//
// Usage (run from the repo root):
//   node exercises/designer/02-claim-components/checks/check_stories.mjs
//   node exercises/designer/02-claim-components/checks/check_stories.mjs --root path/to/workspace
//   node exercises/designer/02-claim-components/checks/check_stories.mjs --required path/to/required.json
//
// Defaults:
//   --root      workspaces/designer           (relative to the current directory)
//   --required  required.json next to this script
//
// required.json shape:
//   { "components": [ { "name": "StatusBadge", "dir": "src/components",
//                       "files": [".tsx", ".css", ".stories.tsx", ".test.tsx"],
//                       "stories": ["Draft"], "tests": ["has no axe violations"] } ] }
//   "dir" defaults to src/components, "files" defaults to the four shown.
//
// Exit codes: 0 everything present, 1 something missing, 2 bad input.

import { existsSync, readFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const DEFAULT_FILES = ['.tsx', '.css', '.stories.tsx', '.test.tsx'];

function fail(code, message) {
  console.error(`[stories] ${message}`);
  process.exit(code);
}

function parseArgs(argv) {
  const args = {
    root: resolve(process.cwd(), 'workspaces/designer'),
    required: resolve(HERE, 'required.json'),
  };
  for (let i = 0; i < argv.length; i += 1) {
    const flag = argv[i];
    if (flag === '--root' || flag === '--required') {
      const value = argv[i + 1];
      if (!value) fail(2, `${flag} needs a path`);
      args[flag.slice(2)] = resolve(process.cwd(), value);
      i += 1;
    } else if (flag === '--help' || flag === '-h') {
      console.log('Usage: node check_stories.mjs [--root workspace] [--required required.json]');
      process.exit(0);
    } else {
      fail(2, `unknown argument "${flag}"`);
    }
  }
  return args;
}

// Remove block comments and whole-line or trailing // comments, so a commented-out
// story does not count. Keeps "//" inside strings such as URLs.
export function stripComments(source) {
  return source
    .replace(/\/\*[\s\S]*?\*\//g, '')
    .split('\n')
    .map((line) => line.replace(/(^|\s)\/\/.*$/, '$1'))
    .join('\n');
}

export function storyExports(source) {
  const code = stripComments(source);
  const names = new Set();
  for (const m of code.matchAll(/export\s+(?:const|let|var|function)\s+([A-Za-z_$][\w$]*)/g)) {
    names.add(m[1]);
  }
  for (const m of code.matchAll(/export\s*\{([^}]*)\}/g)) {
    for (const part of m[1].split(',')) {
      const bits = part.trim().split(/\s+as\s+/);
      const name = (bits[1] ?? bits[0]).trim();
      if (name && name !== 'default') names.add(name);
    }
  }
  return {
    names,
    hasDefault: /export\s+default\b/.test(code) || /export\s*\{[^}]*\bas\s+default\b/.test(code),
  };
}

// Titles of it(), test(), it.each(...)(), test.skip() and so on.
export function testTitles(source) {
  const code = stripComments(source);
  const titles = [];
  const pattern =
    /\b(?:it|test)(?:\.(?:each|only|skip|todo|concurrent|fails)(?:\([\s\S]*?\))?)?\(\s*(['"`])((?:\\.|(?!\1)[\s\S])*?)\1/g;
  for (const m of code.matchAll(pattern)) titles.push(m[2]);
  return titles;
}

function readIfExists(path) {
  return existsSync(path) ? readFileSync(path, 'utf8') : null;
}

function pad(text, width) {
  const s = String(text);
  return s.length >= width ? s : s + ' '.repeat(width - s.length);
}

function printTable(rows) {
  const headers = ['component', 'check', 'result', 'detail'];
  const widths = headers.map((h, i) => Math.max(h.length, ...rows.map((r) => String(r[i]).length)));
  const line = (cells) => cells.map((c, i) => pad(c, widths[i])).join(' | ');
  console.log(line(headers));
  console.log(widths.map((w) => '-'.repeat(w)).join('-|-'));
  for (const r of rows) console.log(line(r));
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  let spec;
  try {
    spec = JSON.parse(readFileSync(args.required, 'utf8'));
  } catch (err) {
    fail(2, `cannot read required list at ${args.required}: ${err.message}`);
  }
  if (!Array.isArray(spec.components) || spec.components.length === 0) {
    fail(2, 'required list has no "components" array');
  }

  const rows = [];
  let missing = 0;
  const miss = (row) => {
    rows.push(row);
    missing += 1;
  };

  for (const comp of spec.components) {
    const dir = resolve(args.root, comp.dir ?? 'src/components');
    const files = comp.files ?? DEFAULT_FILES;

    for (const ext of files) {
      const path = join(dir, `${comp.name}${ext}`);
      const shown = relative(args.root, path);
      if (existsSync(path)) rows.push([comp.name, `file ${comp.name}${ext}`, 'ok', shown]);
      else miss([comp.name, `file ${comp.name}${ext}`, 'MISSING', `create ${shown}`]);
    }

    const storySource = readIfExists(join(dir, `${comp.name}.stories.tsx`));
    if (storySource !== null) {
      const { names, hasDefault } = storyExports(storySource);
      if (hasDefault) rows.push([comp.name, 'story meta (export default)', 'ok', '']);
      else miss([comp.name, 'story meta (export default)', 'MISSING', 'add: export default meta']);
      for (const story of comp.stories ?? []) {
        if (names.has(story)) rows.push([comp.name, `story ${story}`, 'ok', '']);
        else miss([comp.name, `story ${story}`, 'MISSING', `add: export const ${story}: Story = { ... }`]);
      }
    } else {
      for (const story of comp.stories ?? []) {
        miss([comp.name, `story ${story}`, 'MISSING', 'no stories file']);
      }
    }

    const testSource = readIfExists(join(dir, `${comp.name}.test.tsx`));
    const titles = testSource === null ? [] : testTitles(testSource).map((t) => t.toLowerCase());
    for (const phrase of comp.tests ?? []) {
      const want = phrase.toLowerCase();
      if (titles.some((t) => t.includes(want))) rows.push([comp.name, `test "${phrase}"`, 'ok', '']);
      else miss([comp.name, `test "${phrase}"`, 'MISSING', testSource === null ? 'no test file' : 'no it()/test() title contains it']);
    }
  }

  console.log(`[stories] root:     ${args.root}`);
  console.log(`[stories] required: ${args.required}`);
  console.log('');
  printTable(rows);
  console.log('');

  const total = rows.length;
  if (missing) {
    console.error(`[stories] ${missing} of ${total} check(s) missing`);
    process.exit(1);
  }
  console.log(`[stories] OK: ${total} check(s) present`);
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main();
}
