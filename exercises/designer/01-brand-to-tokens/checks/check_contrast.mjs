#!/usr/bin/env node
// check_contrast.mjs
// WCAG 2.x contrast check for the Northwind Expenses token set. No dependencies. Node 20+.
//
// Reads a tokens.json (primitive + semantic layers, W3C-style $value / $type),
// resolves every semantic reference down to a hex color, and computes the
// contrast ratio for each foreground / background pair listed in pairs.json.
//
// Usage (run from the repo root):
//   node exercises/designer/01-brand-to-tokens/checks/check_contrast.mjs
//   node exercises/designer/01-brand-to-tokens/checks/check_contrast.mjs --tokens path/to/tokens.json
//   node exercises/designer/01-brand-to-tokens/checks/check_contrast.mjs --pairs path/to/pairs.json
//
// Defaults:
//   --tokens  workspaces/designer/tokens/tokens.json   (relative to the current directory)
//   --pairs   pairs.json next to this script
//
// Exit codes: 0 every pair passes, 1 a pair fails or a token is missing, 2 bad input.

import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const REF_PATTERN = /^\{([A-Za-z0-9.-]+)\}$/;
const HEX_PATTERN = /^#([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$/i;
const MAX_DEPTH = 10;

function parseArgs(argv) {
  const args = {
    tokens: resolve(process.cwd(), 'workspaces/designer/tokens/tokens.json'),
    pairs: resolve(HERE, 'pairs.json'),
  };
  for (let i = 0; i < argv.length; i += 1) {
    const flag = argv[i];
    if (flag === '--tokens' || flag === '--pairs') {
      const value = argv[i + 1];
      if (!value) fail(2, `${flag} needs a path`);
      args[flag.slice(2)] = resolve(process.cwd(), value);
      i += 1;
    } else if (flag === '--help' || flag === '-h') {
      console.log('Usage: node check_contrast.mjs [--tokens tokens.json] [--pairs pairs.json]');
      process.exit(0);
    } else {
      fail(2, `unknown argument "${flag}"`);
    }
  }
  return args;
}

function fail(code, message) {
  console.error(`[contrast] ${message}`);
  process.exit(code);
}

function readJson(path, label) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (err) {
    fail(2, `cannot read ${label} at ${path}: ${err.message}`);
  }
}

// "color.text.default" means semantic.color.text.default.
// A name that already starts with a layer is used as written.
function fullPath(name) {
  return name.startsWith('semantic.') || name.startsWith('primitive.') ? name : `semantic.${name}`;
}

function lookup(tokens, path) {
  let node = tokens;
  for (const key of path.split('.')) {
    if (node === null || typeof node !== 'object' || !Object.hasOwn(node, key)) return undefined;
    node = node[key];
  }
  return node;
}

// Follow references until a raw value. Returns { hex } or { error }.
export function resolveColor(tokens, name) {
  let path = fullPath(name);
  const seen = [];
  for (let depth = 0; depth < MAX_DEPTH; depth += 1) {
    seen.push(path);
    const node = lookup(tokens, path);
    if (node === undefined) {
      return { error: depth === 0 ? 'token not found' : `reference ${path} not found` };
    }
    if (node === null || typeof node !== 'object' || !Object.hasOwn(node, '$value')) {
      return { error: `${path} is a group, not a token` };
    }
    if (node.$type !== undefined && node.$type !== 'color') {
      return { error: `${path} has $type "${node.$type}", expected "color"` };
    }
    const value = node.$value;
    const ref = typeof value === 'string' ? value.match(REF_PATTERN) : null;
    if (ref) {
      path = ref[1];
      if (seen.includes(path)) return { error: `reference loop: ${[...seen, path].join(' -> ')}` };
      continue;
    }
    if (typeof value !== 'string' || !HEX_PATTERN.test(value)) {
      return { error: `${path} value ${JSON.stringify(value)} is not a hex color` };
    }
    if (value.length === 9 && value.slice(7).toLowerCase() !== 'ff') {
      return { error: `${path} has alpha (${value}); contrast needs opaque colors` };
    }
    return { hex: value.toLowerCase() };
  }
  return { error: `more than ${MAX_DEPTH} references deep` };
}

function hexToRgb(hex) {
  let h = hex.slice(1);
  if (h.length === 3) h = h.split('').map((c) => c + c).join('');
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
}

// WCAG 2.x relative luminance.
function luminance(hex) {
  const [r, g, b] = hexToRgb(hex).map((c) => {
    const s = c / 255;
    return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

export function contrastRatio(fgHex, bgHex) {
  const a = luminance(fgHex);
  const b = luminance(bgHex);
  const [hi, lo] = a > b ? [a, b] : [b, a];
  return (hi + 0.05) / (lo + 0.05);
}

function pad(text, width) {
  const s = String(text);
  return s.length >= width ? s : s + ' '.repeat(width - s.length);
}

function printTable(rows) {
  const headers = ['#', 'foreground', 'background', 'ratio', 'needs', 'result', 'use'];
  const widths = headers.map((h, i) => Math.max(h.length, ...rows.map((r) => String(r[i]).length)));
  const line = (cells) => cells.map((c, i) => pad(c, widths[i])).join(' | ');
  console.log(line(headers));
  console.log(widths.map((w) => '-'.repeat(w)).join('-|-'));
  for (const r of rows) console.log(line(r));
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const tokens = readJson(args.tokens, 'tokens');
  const pairsFile = readJson(args.pairs, 'pairs');
  const pairs = Array.isArray(pairsFile) ? pairsFile : pairsFile.pairs;
  if (!Array.isArray(pairs) || pairs.length === 0) fail(2, 'pairs file has no "pairs" array');

  const rows = [];
  const problems = [];

  pairs.forEach((pair, index) => {
    const n = index + 1;
    const min = Number(pair.min ?? 4.5);
    const fg = resolveColor(tokens, pair.fg);
    const bg = resolveColor(tokens, pair.bg);
    const fgLabel = fg.hex ? `${pair.fg} (${fg.hex})` : pair.fg;
    const bgLabel = bg.hex ? `${pair.bg} (${bg.hex})` : pair.bg;

    if (fg.error || bg.error) {
      rows.push([n, fgLabel, bgLabel, '-', `${min}:1`, 'MISSING', pair.use ?? '']);
      if (fg.error) problems.push(`#${n} ${pair.fg}: ${fg.error}`);
      if (bg.error) problems.push(`#${n} ${pair.bg}: ${bg.error}`);
      return;
    }

    const ratio = contrastRatio(fg.hex, bg.hex);
    // WCAG thresholds are not rounded: 4.499 fails 4.5.
    const ok = ratio >= min;
    rows.push([n, fgLabel, bgLabel, `${ratio.toFixed(2)}:1`, `${min}:1`, ok ? 'PASS' : 'FAIL', pair.use ?? '']);
    if (!ok) problems.push(`#${n} ${pair.fg} on ${pair.bg}: ${ratio.toFixed(2)}:1 is below ${min}:1`);
  });

  console.log(`[contrast] tokens: ${args.tokens}`);
  console.log(`[contrast] pairs:  ${args.pairs}`);
  console.log('');
  printTable(rows);
  console.log('');

  if (problems.length) {
    console.error(`[contrast] ${problems.length} problem(s):`);
    for (const p of problems) console.error(`  - ${p}`);
    process.exit(1);
  }
  console.log(`[contrast] OK: ${pairs.length} pair(s) meet WCAG AA`);
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main();
}
