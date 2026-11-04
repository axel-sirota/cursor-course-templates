#!/usr/bin/env node
// check_card.mjs
// Scans ClaimSummaryCard.tsx and ClaimSummaryCard.css for the 12 defect patterns
// seeded in exercises/designer/03-my-claims-screen/inputs/flawed/. No dependencies. Node 20+.
//
// These are pattern checks, not proof. A clean run means none of the known
// mistakes are left. Storybook, axe and a human still review the result.
//
// Usage (run from the repo root):
//   node exercises/designer/03-my-claims-screen/checks/check_card.mjs
//   node exercises/designer/03-my-claims-screen/checks/check_card.mjs --dir path/to/components
//
// Default --dir: workspaces/designer/src/components (relative to the current directory).
// Exit codes: 0 no defect pattern found, 1 at least one found, 2 bad input.

import { existsSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

function fail(code, message) {
  console.error(`[card] ${message}`);
  process.exit(code);
}

function parseArgs(argv) {
  const args = { dir: resolve(process.cwd(), 'workspaces/designer/src/components') };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--dir') {
      if (!argv[i + 1]) fail(2, '--dir needs a path');
      args.dir = resolve(process.cwd(), argv[i + 1]);
      i += 1;
    } else if (argv[i] === '--help' || argv[i] === '-h') {
      console.log('Usage: node check_card.mjs [--dir components-folder]');
      process.exit(0);
    } else {
      fail(2, `unknown argument "${argv[i]}"`);
    }
  }
  return args;
}

// Blank out comments but keep their newlines, so reported line numbers stay true.
const blank = (m) => m.replace(/[^\n]/g, ' ');
const stripCssComments = (s) => s.replace(/\/\*[\s\S]*?\*\//g, blank);
const stripTsComments = (s) =>
  s
    .replace(/\{\s*\/\*[\s\S]*?\*\/\s*\}/g, blank)
    .replace(/\/\*[\s\S]*?\*\//g, blank)
    .split('\n')
    .map((line) => line.replace(/(^|\s)\/\/.*$/, '$1'))
    .join('\n');

// Line number (1-based) of a match index, for the report.
function lineOf(source, index) {
  return source.slice(0, index).split('\n').length;
}

function firstMatch(source, pattern) {
  const m = pattern.exec(source);
  pattern.lastIndex = 0;
  return m ? lineOf(source, m.index) : null;
}

// <button ...>children</button> with no visible text and no aria-label / aria-labelledby.
function unlabeledButton(tsx) {
  const pattern = /<button\b([^>]*)>([\s\S]*?)<\/button>/g;
  for (const m of tsx.matchAll(pattern)) {
    const attrs = m[1];
    if (/aria-label(ledby)?\s*=/.test(attrs)) continue;
    const text = m[2]
      .replace(/<svg[\s\S]*?<\/svg>/g, '')
      .replace(/<[^>]+>/g, '')
      .replace(/\s+/g, '');
    if (text.length === 0) return lineOf(tsx, m.index);
  }
  return null;
}

function imgWithoutAlt(tsx) {
  for (const m of tsx.matchAll(/<img\b[^>]*>/g)) {
    if (!/\balt\s*=/.test(m[0])) return lineOf(tsx, m.index);
  }
  return null;
}

function colorOnlyStatus(tsx) {
  const usesBadge = /<StatusBadge\b/.test(tsx);
  const hasWord = /\b(Draft|Submitted|Approved|Rejected|Paid)\b/.test(tsx);
  const hasLabelMap = /STATUS_(TEXT|LABEL)/.test(tsx);
  if (usesBadge || hasWord || hasLabelMap) return null;
  return firstMatch(tsx, /\$\{status\}|data-status=|__dot/g) ?? firstMatch(tsx, /status/g) ?? 1;
}

function noFocusStyle(css) {
  const focusRule = /:focus-visible[^{]*\{[^}]*(outline|box-shadow)[^}]*--color-focus-ring/;
  if (focusRule.test(css)) return null;
  return firstMatch(css, /outline\s*:\s*(none|0)\b/g) ?? 1;
}

const DEFECTS = [
  { id: 'D1', file: 'tsx', name: 'inline style attribute', find: (t) => firstMatch(t, /style=\{\{/g) },
  { id: 'D2', file: 'tsx', name: 'icon button without an accessible name', find: unlabeledButton },
  { id: 'D3', file: 'tsx', name: 'money formatted inside the component', find: (t) => firstMatch(t, /\.toFixed\(|\.toLocaleString\(|Intl\.NumberFormat/g) },
  { id: 'D4', file: 'tsx', name: 'status shown by color only', find: colorOnlyStatus },
  { id: 'D5', file: 'tsx', name: 'image without alt', find: imgWithoutAlt },
  { id: 'D6', file: 'tsx', name: 'div or span used as a button', find: (t) => firstMatch(t, /<(div|span|p|li)\b[^>]*\bonClick=/g) },
  { id: 'D7', file: 'css', name: 'fixed px width (breaks at 360px)', find: (c) => firstMatch(c, /(^|[\s;{])width\s*:\s*\d{2,}px/g) },
  { id: 'D8', file: 'css', name: 'hardcoded color value', find: (c) => firstMatch(c, /#[0-9a-fA-F]{3,8}\b|\b(rgba?|hsla?)\(/g) },
  { id: 'D9', file: 'css', name: 'hardcoded font size', find: (c) => firstMatch(c, /font-size\s*:\s*[\d.]+(px|rem|em)\b/g) },
  { id: 'D10', file: 'css', name: 'primitive token used in a component', find: (c) => firstMatch(c, /--primitive-/g) },
  { id: 'D11', file: 'css', name: 'opacity lowers text contrast', find: (c) => firstMatch(c, /opacity\s*:\s*0?\.\d+/g) },
  { id: 'D12', file: 'css', name: 'focus outline removed, no :focus-visible ring', find: noFocusStyle },
];

function main() {
  const { dir } = parseArgs(process.argv.slice(2));
  const paths = { tsx: join(dir, 'ClaimSummaryCard.tsx'), css: join(dir, 'ClaimSummaryCard.css') };
  for (const p of Object.values(paths)) if (!existsSync(p)) fail(2, `missing ${p}`);

  const tsx = stripTsComments(readFileSync(paths.tsx, 'utf8'));
  const css = stripCssComments(readFileSync(paths.css, 'utf8'));
  const sources = { tsx, css };

  console.log(`[card] scanning ${dirname(paths.tsx)}`);
  console.log('');
  const rows = DEFECTS.map((d) => {
    const line = d.find(sources[d.file]);
    return { ...d, line, ok: line === null };
  });

  const w = Math.max(...rows.map((r) => r.name.length));
  console.log(`id  | ${'defect'.padEnd(w)} | result  | where`);
  console.log(`----|-${'-'.repeat(w)}-|---------|------`);
  for (const r of rows) {
    const where = r.ok ? '' : `ClaimSummaryCard.${r.file}:${r.line}`;
    console.log(`${r.id.padEnd(3)} | ${r.name.padEnd(w)} | ${r.ok ? 'fixed  ' : 'PRESENT'} | ${where}`);
  }
  console.log('');

  const present = rows.filter((r) => !r.ok).length;
  if (present) {
    console.error(`[card] ${present} of ${rows.length} defect pattern(s) still present`);
    process.exit(1);
  }
  console.log(`[card] OK: none of the ${rows.length} defect patterns found`);
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main();
}
