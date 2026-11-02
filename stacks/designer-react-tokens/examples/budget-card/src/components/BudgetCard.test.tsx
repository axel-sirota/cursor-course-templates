import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import axe from 'axe-core';
import { BudgetCard, type BudgetCardProps } from './BudgetCard';

const onTrack: BudgetCardProps = {
  label: 'Groceries',
  spentLabel: '$420',
  limitLabel: '$600',
  percentUsed: 70,
  status: 'on-track',
  statusLabel: '$180 left',
};

describe('BudgetCard', () => {
  it('renders the category, amounts and status text', () => {
    render(<BudgetCard {...onTrack} />);

    expect(screen.getByRole('heading', { name: 'Groceries' })).toBeInTheDocument();
    expect(screen.getByText('$420')).toBeInTheDocument();
    expect(screen.getByText(/of \$600/)).toBeInTheDocument();
    expect(screen.getByText('$180 left')).toBeInTheDocument();
  });

  it('exposes progress as an accessible progressbar', () => {
    render(<BudgetCard {...onTrack} />);

    const bar = screen.getByRole('progressbar', { name: 'Groceries budget used' });
    expect(bar).toHaveAttribute('value', '70');
    expect(bar).toHaveAttribute('max', '100');
  });

  it('names the card region after its category', () => {
    render(<BudgetCard {...onTrack} />);

    expect(screen.getByRole('article', { name: 'Groceries' })).toBeInTheDocument();
  });

  it.each(['on-track', 'near-limit', 'over'] as const)('maps status %s to data-status', (status) => {
    render(<BudgetCard {...onTrack} status={status} />);

    expect(screen.getByRole('article')).toHaveAttribute('data-status', status);
  });

  it('has no axe violations in any state', async () => {
    for (const status of ['on-track', 'near-limit', 'over'] as const) {
      const { container, unmount } = render(<BudgetCard {...onTrack} status={status} />);
      // jsdom has no layout or canvas, so contrast is checked on token pairs instead.
      const results = await axe.run(container, { rules: { 'color-contrast': { enabled: false } } });
      expect(results.violations).toEqual([]);
      unmount();
    }
  });
});

describe('BudgetCard.css style guard', () => {
  // Pass import.meta.url as a string: jsdom replaces the global URL class.
  const cssPath = resolve(dirname(fileURLToPath(import.meta.url)), 'BudgetCard.css');
  const css = readFileSync(cssPath, 'utf8').replace(/\/\*[\s\S]*?\*\//g, '');

  it('uses no hardcoded colors', () => {
    expect(css).not.toMatch(/#[0-9a-fA-F]{3,8}\b/);
    expect(css).not.toMatch(/\b(rgb|rgba|hsl|hsla)\(/);
  });

  it('uses no pixel values other than 1px', () => {
    const pixels = css.match(/\d*\.?\d+px/g) ?? [];
    expect(pixels.filter((p) => p !== '1px')).toEqual([]);
  });

  it('reads semantic tokens only, never primitives', () => {
    expect(css).not.toContain('--primitive-');
  });
});
