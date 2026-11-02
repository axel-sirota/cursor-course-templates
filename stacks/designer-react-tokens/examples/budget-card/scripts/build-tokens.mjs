#!/usr/bin/env node
// build-tokens.mjs
// Reads tokens/tokens.json (primitive + semantic layers) and writes src/styles/tokens.css.
// No dependencies. Node 20+.
//
// Usage:
//   node scripts/build-tokens.mjs           validate, then write src/styles/tokens.css
//   node scripts/build-tokens.mjs --check   validate only, write nothing
//
// Rules enforced:
//   - top level holds exactly "primitive" and "semantic"
//   - every leaf has $value and a known $type
//   - primitive leaves hold raw values that match their $type
//   - semantic leaves hold a single reference "{primitive.x.y}" that resolves
//     to a primitive leaf of the same $type

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const TOKENS_PATH = resolve(ROOT, 'tokens', 'tokens.json');
const CSS_PATH = resolve(ROOT, 'src', 'styles', 'tokens.css');

const LAYERS = ['primitive', 'semantic'];
const KNOWN_TYPES = new Set(['color', 'dimension', 'fontFamily', 'fontWeight', 'number', 'shadow']);
const KEY_PATTERN = /^[A-Za-z0-9-]+$/;
const REF_PATTERN = /^\{([A-Za-z0-9.-]+)\}$/;

const RAW_CHECKS = {
  color: (v) => typeof v === 'string' && /^#([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$/i.test(v),
  dimension: (v) => typeof v === 'string' && /^(0|-?\d+(\.\d+)?(px|rem|em|%))$/.test(v),
  fontFamily: (v) => typeof v === 'string' && v.trim().length > 0,
  fontWeight: (v) => Number.isInteger(v) && v >= 100 && v <= 900,
  number: (v) => typeof v === 'number' && Number.isFinite(v),
  shadow: (v) => typeof v === 'string' && v.trim().length > 0,
};

function isLeaf(node) {
  return node !== null && typeof node === 'object' && Object.hasOwn(node, '$value');
}

// Walk a layer and collect leaves as { path: ['color','text','default'], token }.
function collectLeaves(node, path, out, errors) {
  if (node === null || typeof node !== 'object' || Array.isArray(node)) {
    errors.push(`${path.join('.')}: group must be an object`);
    return;
  }
  if (isLeaf(node)) {
    out.push({ path, token: node });
    return;
  }
  const keys = Object.keys(node).filter((k) => !k.startsWith('$'));
  if (keys.length === 0) {
    errors.push(`${path.join('.')}: empty group`);
  }
  for (const key of keys) {
    if (!KEY_PATTERN.test(key)) {
      errors.push(`${[...path, key].join('.')}: key must match ${KEY_PATTERN}`);
      continue;
    }
    collectLeaves(node[key], [...path, key], out, errors);
  }
}

export function validateTokens(tokens) {
  const errors = [];
  if (tokens === null || typeof tokens !== 'object' || Array.isArray(tokens)) {
    return { errors: ['root: must be an object'], primitives: [], semantics: [] };
  }
  for (const key of Object.keys(tokens)) {
    if (!LAYERS.includes(key)) errors.push(`root: unknown layer "${key}" (allowed: ${LAYERS.join(', ')})`);
  }
  for (const layer of LAYERS) {
    if (!tokens[layer]) errors.push(`root: missing layer "${layer}"`);
  }
  if (errors.length) return { errors, primitives: [], semantics: [] };

  const primitives = [];
  const semantics = [];
  collectLeaves(tokens.primitive, ['primitive'], primitives, errors);
  collectLeaves(tokens.semantic, ['semantic'], semantics, errors);

  const primitiveByPath = new Map(primitives.map((p) => [p.path.join('.'), p.token]));

  for (const { path, token } of primitives) {
    const name = path.join('.');
    if (!KNOWN_TYPES.has(token.$type)) {
      errors.push(`${name}: unknown $type "${token.$type}"`);
      continue;
    }
    if (typeof token.$value === 'string' && REF_PATTERN.test(token.$value)) {
      errors.push(`${name}: primitive tokens hold raw values, not references`);
      continue;
    }
    if (!RAW_CHECKS[token.$type](token.$value)) {
      errors.push(`${name}: value ${JSON.stringify(token.$value)} is not a valid ${token.$type}`);
    }
  }

  for (const { path, token } of semantics) {
    const name = path.join('.');
    if (!KNOWN_TYPES.has(token.$type)) {
      errors.push(`${name}: unknown $type "${token.$type}"`);
      continue;
    }
    const match = typeof token.$value === 'string' ? token.$value.match(REF_PATTERN) : null;
    if (!match) {
      errors.push(`${name}: semantic tokens must reference a primitive, got ${JSON.stringify(token.$value)}`);
      continue;
    }
    const target = primitiveByPath.get(match[1]);
    if (!target) {
      errors.push(`${name}: reference ${token.$value} does not resolve to a primitive token`);
      continue;
    }
    if (target.$type !== token.$type) {
      errors.push(`${name}: $type "${token.$type}" does not match referenced $type "${target.$type}"`);
    }
  }

  return { errors, primitives, semantics };
}

const kebab = (s) => s.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase();

// primitive.color.slate.900 → --primitive-color-slate-900
// semantic.color.text.muted → --color-text-muted
export function cssVarName(path) {
  const [layer, ...rest] = path;
  const body = rest.map(kebab).join('-');
  return layer === 'primitive' ? `--primitive-${body}` : `--${body}`;
}

export function buildCss({ primitives, semantics }) {
  const lines = [
    '/* GENERATED by scripts/build-tokens.mjs from tokens/tokens.json. Do not edit by hand. */',
    ':root {',
    '  /* primitive layer: raw values, not for use in components */',
  ];
  for (const { path, token } of primitives) {
    lines.push(`  ${cssVarName(path)}: ${token.$value};`);
  }
  lines.push('', '  /* semantic layer: use these in components */');
  for (const { path, token } of semantics) {
    const refPath = token.$value.match(REF_PATTERN)[1].split('.');
    lines.push(`  ${cssVarName(path)}: var(${cssVarName(refPath)});`);
  }
  lines.push('}', '');
  return lines.join('\n');
}

function main() {
  const checkOnly = process.argv.includes('--check');
  let tokens;
  try {
    tokens = JSON.parse(readFileSync(TOKENS_PATH, 'utf8'));
  } catch (err) {
    console.error(`[tokens] cannot read ${relative(ROOT, TOKENS_PATH)}: ${err.message}`);
    process.exit(1);
  }

  const result = validateTokens(tokens);
  if (result.errors.length) {
    console.error(`[tokens] ${result.errors.length} error(s) in ${relative(ROOT, TOKENS_PATH)}:`);
    for (const e of result.errors) console.error(`  - ${e}`);
    process.exit(1);
  }

  const summary = `${result.primitives.length} primitive, ${result.semantics.length} semantic`;
  if (checkOnly) {
    console.log(`[tokens] OK: ${summary}`);
    return;
  }

  mkdirSync(dirname(CSS_PATH), { recursive: true });
  writeFileSync(CSS_PATH, buildCss(result));
  console.log(`[tokens] wrote ${relative(ROOT, CSS_PATH)} (${summary})`);
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main();
}
