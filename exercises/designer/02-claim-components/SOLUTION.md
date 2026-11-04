# Solution Key: Exercise 2, Claim Components (instructor only)

The reference code below was run in a clean copy of the stack example: `npm test` (27 tests, 4 files, all pass, axe zero violations), `tsc --noEmit` (clean), `check_stories.mjs` (53 of 53), `check_contrast.mjs --pairs pairs-rows.json` (10 of 10).

## Token additions (on top of the exercise 1 reference)

```json
"primitive": {
  "size": {
    "3": { "$value": "12px", "$type": "dimension" },
    "4": { "$value": "16px", "$type": "dimension" }
  }
},
"semantic": {
  "color": {
    "surface": {
      "hover":    { "$value": "{primitive.color.gray.100}", "$type": "color" },
      "selected": { "$value": "{primitive.color.navy.100}", "$type": "color" }
    },
    "border": {
      "selected": { "$value": "{primitive.color.navy.700}", "$type": "color" }
    }
  },
  "size": {
    "icon": {
      "sm": { "$value": "{primitive.size.3}", "$type": "dimension" },
      "md": { "$value": "{primitive.size.4}", "$type": "dimension" }
    }
  }
}
```

Contrast proof for the new fills (real output):

| Pair | Ratio | Needs |
|---|---|---|
| text.muted on surface.selected | 5.41:1 | 4.5 |
| text.link on surface.selected | 5.81:1 | 4.5 |
| focus.ring on surface.selected | 3.45:1 | 3 |
| border.control on surface.selected | **3.07:1** | 3 |
| border.selected on surface.card | 11.63:1 | 3 |

The checkbox border on a selected row is the tightest pair in the course. A student who picks navy 500 or teal 100 for `surface.selected` fails it. Good discussion point.

## Decisions to look for

| Topic | Expected | Common miss |
|---|---|---|
| StatusBadge props | Discriminated union, `status` xor `flag` | Two booleans or `variant` + `value: string` |
| Flag vs status | Flag has an icon, so it differs by shape | Same pill, color only |
| Copy | Fixed map inside the badge (presentation, not logic) | Passing the label in, so stories drift |
| AmountCell currency | Code always visible (USD and CAD both use `$`) | Symbol only |
| Refund | Minus in `amountLabel`, success color, visible "Refund" | Color only, or `toFixed` inside the component |
| Alignment | `text-align: end` + `font-variant-numeric: tabular-nums` | `float: right`, proportional digits |
| ExpenseRow root | `<tr>`, stories wrap in a decorator | `<div>` grid that breaks table semantics |
| Checkbox name | "Select Harbor Grill, Fri 16 Oct 2026" | 20 checkboxes all named "Select" |
| Merchant | `<button type="button">` | Clickable `<td onClick>` |
| Receipt | Two icon shapes + visually hidden text | One icon in red / green |
| Disabled | `color.text.muted`, checkbox disabled, merchant still opens | `opacity: 0.5` (muted text drops to 2.19:1, default text to 3.06:1) |
| Focus | `:focus-visible` outline with `color.focus.ring` | `outline: none` |
| Reuse | ExpenseRow imports StatusBadge and AmountCell | Copy-pasted badge markup |

## Check behaviour on a broken workspace

Seeded misses (AmountCell.css deleted, `FlagAlcohol` removed, `export default meta` removed, `Hover` commented out, axe test renamed) give:

```
StatusBadge | story meta (export default) | MISSING | add: export default meta
StatusBadge | story FlagAlcohol           | MISSING | add: export const FlagAlcohol: Story = { ... }
AmountCell  | file AmountCell.css         | MISSING | create src/components/AmountCell.css
ExpenseRow  | story Hover                 | MISSING | add: export const Hover: Story = { ... }
ExpenseRow  | test "has no axe violations"| MISSING | no it()/test() title contains it

[stories] 5 of 53 check(s) missing      (exit 1)
```

## Limits of the automated checks

- `check_stories.mjs` proves the names exist, not that a story shows the right state. Open Storybook and click through.
- axe in jsdom does not check contrast. That is what `check_contrast.mjs` is for.
- The grep sweep misses px values in TSX attributes and named colors. The `token-validator` agent covers those.

## Reference code

### `src/components/StatusBadge.tsx`

```tsx
import './StatusBadge.css';

export type ClaimStatus = 'draft' | 'submitted' | 'approved' | 'rejected' | 'paid';
export type PolicyFlag = 'RECEIPT_REQUIRED' | 'OVER_MEAL_LIMIT' | 'WEEKEND_REVIEW' | 'ALCOHOL';

export type StatusBadgeProps =
  | { status: ClaimStatus; flag?: never }
  | { flag: PolicyFlag; status?: never };

const STATUS_TEXT: Record<ClaimStatus, string> = {
  draft: 'Draft',
  submitted: 'Submitted',
  approved: 'Approved',
  rejected: 'Rejected',
  paid: 'Paid',
};

const FLAG_TEXT: Record<PolicyFlag, string> = {
  RECEIPT_REQUIRED: 'Receipt required',
  OVER_MEAL_LIMIT: 'Over meal limit',
  WEEKEND_REVIEW: 'Weekend review',
  ALCOHOL: 'Alcohol',
};

export function StatusBadge(props: StatusBadgeProps) {
  if (props.flag !== undefined) {
    return (
      <span className="status-badge" data-variant="flag" data-flag={props.flag}>
        <svg className="status-badge__icon" viewBox="0 0 16 16" aria-hidden="true" focusable="false">
          <path d="M8 1 15 14H1L8 1Zm-.75 5v4h1.5V6h-1.5Zm0 5v1.5h1.5V11h-1.5Z" fill="currentColor" />
        </svg>
        {FLAG_TEXT[props.flag]}
      </span>
    );
  }
  return (
    <span className="status-badge" data-variant="status" data-status={props.status}>
      {STATUS_TEXT[props.status]}
    </span>
  );
}
```

### `src/components/StatusBadge.css`

```css
/* StatusBadge: semantic tokens only. */

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-inline-xs);
  padding: var(--space-inset-xs) var(--space-inline-sm);
  border-radius: var(--radius-badge);
  font-family: var(--font-family-base);
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-semibold);
  line-height: var(--font-line-height-tight);
  white-space: nowrap;
}

.status-badge[data-status='draft'] {
  color: var(--color-status-draft-text);
  background: var(--color-status-draft-bg);
}

.status-badge[data-status='submitted'] {
  color: var(--color-status-submitted-text);
  background: var(--color-status-submitted-bg);
}

.status-badge[data-status='approved'] {
  color: var(--color-status-approved-text);
  background: var(--color-status-approved-bg);
}

.status-badge[data-status='rejected'] {
  color: var(--color-status-rejected-text);
  background: var(--color-status-rejected-bg);
}

.status-badge[data-status='paid'] {
  color: var(--color-status-paid-text);
  background: var(--color-status-paid-bg);
}

.status-badge[data-variant='flag'] {
  color: var(--color-flag-text);
  background: var(--color-flag-bg);
}

.status-badge__icon {
  width: var(--size-icon-sm);
  height: var(--size-icon-sm);
  flex: none;
}
```

### `src/components/StatusBadge.stories.tsx`

```tsx
import type { Meta, StoryObj } from '@storybook/react';
import { StatusBadge } from './StatusBadge';

const meta: Meta<typeof StatusBadge> = {
  title: 'Components/StatusBadge',
  component: StatusBadge,
};

export default meta;

type Story = StoryObj<typeof StatusBadge>;

export const Draft: Story = { args: { status: 'draft' } };
export const Submitted: Story = { args: { status: 'submitted' } };
export const Approved: Story = { args: { status: 'approved' } };
export const Rejected: Story = { args: { status: 'rejected' } };
export const Paid: Story = { args: { status: 'paid' } };

export const FlagReceiptRequired: Story = { args: { flag: 'RECEIPT_REQUIRED' } };
export const FlagOverMealLimit: Story = { args: { flag: 'OVER_MEAL_LIMIT' } };
export const FlagWeekendReview: Story = { args: { flag: 'WEEKEND_REVIEW' } };
export const FlagAlcohol: Story = { args: { flag: 'ALCOHOL' } };
```

### `src/components/StatusBadge.test.tsx`

```tsx
import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import axe from 'axe-core';
import { StatusBadge, type ClaimStatus, type PolicyFlag } from './StatusBadge';

const STATUSES: [ClaimStatus, string][] = [
  ['draft', 'Draft'],
  ['submitted', 'Submitted'],
  ['approved', 'Approved'],
  ['rejected', 'Rejected'],
  ['paid', 'Paid'],
];

const FLAGS: [PolicyFlag, string][] = [
  ['RECEIPT_REQUIRED', 'Receipt required'],
  ['OVER_MEAL_LIMIT', 'Over meal limit'],
  ['WEEKEND_REVIEW', 'Weekend review'],
  ['ALCOHOL', 'Alcohol'],
];

describe('StatusBadge', () => {
  it.each(STATUSES)('renders the label for each status: %s', (status, text) => {
    render(<StatusBadge status={status} />);
    expect(screen.getByText(text)).toBeInTheDocument();
  });

  it.each(STATUSES)('maps status to data-status: %s', (status, text) => {
    render(<StatusBadge status={status} />);
    const badge = screen.getByText(text);
    expect(badge).toHaveAttribute('data-status', status);
    expect(badge).toHaveAttribute('data-variant', 'status');
  });

  it.each(FLAGS)('renders policy flags with text: %s', (flag, text) => {
    render(<StatusBadge flag={flag} />);
    const badge = screen.getByText(text);
    expect(badge).toHaveAttribute('data-flag', flag);
    expect(badge.querySelector('svg')).toHaveAttribute('aria-hidden', 'true');
  });

  it('has no axe violations', async () => {
    const { container } = render(
      <div>
        {STATUSES.map(([s]) => (
          <StatusBadge key={s} status={s} />
        ))}
        {FLAGS.map(([f]) => (
          <StatusBadge key={f} flag={f} />
        ))}
      </div>,
    );
    // jsdom cannot compute color, so contrast is proven by check_contrast.mjs instead.
    const results = await axe.run(container, { rules: { 'color-contrast': { enabled: false } } });
    expect(results.violations).toEqual([]);
  });
});
```

### `src/components/AmountCell.tsx`

```tsx
import './AmountCell.css';

export type Currency = 'USD' | 'EUR' | 'GBP' | 'CAD';

export type AmountCellProps = {
  /** Formatted by the parent, sign included, e.g. "$1,234.50" or "−$45.00". */
  amountLabel: string;
  currency: Currency;
  kind?: 'charge' | 'refund';
};

export function AmountCell({ amountLabel, currency, kind = 'charge' }: AmountCellProps) {
  return (
    <span className="amount-cell" data-kind={kind}>
      <span className="amount-cell__value">{amountLabel}</span>
      <span className="amount-cell__currency">{currency}</span>
      {kind === 'refund' && <span className="amount-cell__kind">Refund</span>}
    </span>
  );
}
```

### `src/components/AmountCell.css`

```css
/* AmountCell: semantic tokens only. */

.amount-cell {
  display: flex;
  justify-content: flex-end;
  align-items: baseline;
  flex-wrap: wrap;
  column-gap: var(--space-inline-xs);
  text-align: end;
  font-family: var(--font-family-base);
  color: var(--color-text-default);
}

.amount-cell__value {
  font-size: var(--font-size-label);
  font-weight: var(--font-weight-semibold);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.amount-cell[data-kind='refund'] .amount-cell__value {
  color: var(--color-text-success);
}

.amount-cell__currency,
.amount-cell__kind {
  font-size: var(--font-size-caption);
  color: var(--color-text-muted);
}
```

### `src/components/AmountCell.stories.tsx`

```tsx
import type { Meta, StoryObj } from '@storybook/react';
import { AmountCell } from './AmountCell';

const meta: Meta<typeof AmountCell> = {
  title: 'Components/AmountCell',
  component: AmountCell,
  argTypes: {
    currency: { control: 'inline-radio', options: ['USD', 'EUR', 'GBP', 'CAD'] },
    kind: { control: 'inline-radio', options: ['charge', 'refund'] },
  },
};

export default meta;

type Story = StoryObj<typeof AmountCell>;

export const Usd: Story = { args: { amountLabel: '$86.40', currency: 'USD' } };
export const Eur: Story = { args: { amountLabel: '€1,150.00', currency: 'EUR' } };
export const Gbp: Story = { args: { amountLabel: '£42.75', currency: 'GBP' } };
export const Cad: Story = { args: { amountLabel: '$310.20', currency: 'CAD' } };
export const Refund: Story = { args: { amountLabel: '−$45.00', currency: 'USD', kind: 'refund' } };
export const LargeAmount: Story = { args: { amountLabel: '$12,480.00', currency: 'USD' } };
```

### `src/components/AmountCell.test.tsx`

```tsx
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import axe from 'axe-core';
import { AmountCell } from './AmountCell';

describe('AmountCell', () => {
  it('renders the amount and currency code', () => {
    render(<AmountCell amountLabel="$310.20" currency="CAD" />);
    expect(screen.getByText('$310.20')).toBeInTheDocument();
    expect(screen.getByText('CAD')).toBeInTheDocument();
    expect(screen.queryByText('Refund')).not.toBeInTheDocument();
  });

  it('marks refunds with text', () => {
    const { container } = render(<AmountCell amountLabel="−$45.00" currency="USD" kind="refund" />);
    expect(screen.getByText('Refund')).toBeInTheDocument();
    expect(container.firstChild).toHaveAttribute('data-kind', 'refund');
  });

  it('uses tabular numbers', () => {
    const cssPath = resolve(dirname(fileURLToPath(import.meta.url)), 'AmountCell.css');
    expect(readFileSync(cssPath, 'utf8')).toMatch(/font-variant-numeric:\s*tabular-nums/);
  });

  it('has no axe violations', async () => {
    const { container } = render(
      <div>
        <AmountCell amountLabel="€1,150.00" currency="EUR" />
        <AmountCell amountLabel="−$45.00" currency="USD" kind="refund" />
      </div>,
    );
    const results = await axe.run(container, { rules: { 'color-contrast': { enabled: false } } });
    expect(results.violations).toEqual([]);
  });
});
```

### `src/components/ExpenseRow.tsx`

```tsx
import { AmountCell, type Currency } from './AmountCell';
import { StatusBadge, type ClaimStatus, type PolicyFlag } from './StatusBadge';
import './ExpenseRow.css';

export type ExpenseRowProps = {
  merchant: string;
  dateLabel: string;
  dateTime: string;
  category: string;
  amountLabel: string;
  currency: Currency;
  kind?: 'charge' | 'refund';
  status: ClaimStatus;
  flags: PolicyFlag[];
  hasReceipt: boolean;
  selected?: boolean;
  disabled?: boolean;
  onSelectedChange?: (selected: boolean) => void;
  onOpen?: () => void;
};

export function ExpenseRow({
  merchant,
  dateLabel,
  dateTime,
  category,
  amountLabel,
  currency,
  kind = 'charge',
  status,
  flags,
  hasReceipt,
  selected = false,
  disabled = false,
  onSelectedChange = () => {}, // TODO: engineering
  onOpen = () => {}, // TODO: engineering
}: ExpenseRowProps) {
  return (
    <tr
      className="expense-row"
      data-selected={selected ? 'true' : undefined}
      data-disabled={disabled ? 'true' : undefined}
    >
      <td className="expense-row__cell expense-row__cell--select">
        <input
          type="checkbox"
          className="expense-row__checkbox"
          aria-label={`Select ${merchant}, ${dateLabel}`}
          checked={selected}
          disabled={disabled}
          onChange={(event) => onSelectedChange(event.target.checked)}
        />
      </td>
      <td className="expense-row__cell">
        <button type="button" className="expense-row__open" onClick={onOpen}>
          {merchant}
        </button>
      </td>
      <td className="expense-row__cell expense-row__cell--muted">
        <time dateTime={dateTime}>{dateLabel}</time>
      </td>
      <td className="expense-row__cell expense-row__cell--muted">{category}</td>
      <td className="expense-row__cell expense-row__cell--amount">
        <AmountCell amountLabel={amountLabel} currency={currency} kind={kind} />
      </td>
      <td className="expense-row__cell">
        <StatusBadge status={status} />
      </td>
      <td className="expense-row__cell">
        {flags.length > 0 && (
          <ul className="expense-row__flags" aria-label="Policy flags">
            {flags.map((flag) => (
              <li key={flag}>
                <StatusBadge flag={flag} />
              </li>
            ))}
          </ul>
        )}
      </td>
      <td className="expense-row__cell expense-row__cell--receipt" data-receipt={hasReceipt ? 'attached' : 'missing'}>
        <svg className="expense-row__receipt-icon" viewBox="0 0 16 16" aria-hidden="true" focusable="false">
          {hasReceipt ? (
            <path d="M10.5 3.5 5 9a1.5 1.5 0 0 0 2.1 2.1L12 6.2a3 3 0 0 0-4.2-4.2L3 6.8" fill="none" stroke="currentColor" />
          ) : (
            <path d="M10.5 3.5 5 9a1.5 1.5 0 0 0 2.1 2.1L12 6.2M2 2l12 12" fill="none" stroke="currentColor" />
          )}
        </svg>
        <span className="expense-row__visually-hidden">{hasReceipt ? 'Receipt attached' : 'No receipt'}</span>
      </td>
    </tr>
  );
}
```

### `src/components/ExpenseRow.css`

```css
/* ExpenseRow: semantic tokens only. */

.expense-row {
  background: var(--color-surface-card);
  color: var(--color-text-default);
  font-family: var(--font-family-base);
  font-size: var(--font-size-label);
  line-height: var(--font-line-height-normal);
}

.expense-row:hover,
.expense-row:focus-within {
  background: var(--color-surface-hover);
}

.expense-row[data-selected='true'] {
  background: var(--color-surface-selected);
}

.expense-row[data-selected='true'] .expense-row__cell--select {
  box-shadow: inset var(--border-width-focus) 0 0 var(--color-border-selected);
}

.expense-row[data-disabled='true'] {
  color: var(--color-text-muted);
}

.expense-row__cell {
  padding: var(--space-inset-sm) var(--space-inline-md);
  border-bottom: var(--border-width-default) solid var(--color-border-subtle);
  vertical-align: middle;
}

.expense-row__cell--muted {
  color: var(--color-text-muted);
}

.expense-row__cell--amount {
  text-align: end;
}

.expense-row__checkbox {
  accent-color: var(--color-action-primary-bg);
  border: var(--border-width-default) solid var(--color-border-control);
  border-radius: var(--radius-control);
  margin: 0;
}

.expense-row__open {
  padding: 0;
  border: none;
  background: none;
  color: var(--color-text-link);
  font: inherit;
  font-weight: var(--font-weight-semibold);
  text-align: start;
  cursor: pointer;
}

.expense-row__open:hover {
  text-decoration: underline;
}

.expense-row__checkbox:focus-visible,
.expense-row__open:focus-visible {
  outline: var(--border-width-focus) solid var(--color-focus-ring);
  outline-offset: var(--border-width-focus);
  border-radius: var(--radius-control);
}

.expense-row__flags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-inline-xs);
  margin: 0;
  padding: 0;
  list-style: none;
}

.expense-row__receipt-icon {
  width: var(--size-icon-sm);
  height: var(--size-icon-sm);
}

.expense-row__cell--receipt[data-receipt='missing'] {
  color: var(--color-text-danger);
}

.expense-row__visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}
```

### `src/components/ExpenseRow.stories.tsx`

```tsx
import type { Meta, StoryObj } from '@storybook/react';
import { within } from '@storybook/test';
import { ExpenseRow } from './ExpenseRow';

const meta: Meta<typeof ExpenseRow> = {
  title: 'Components/ExpenseRow',
  component: ExpenseRow,
  decorators: [
    (Story) => (
      <table>
        <tbody>
          <Story />
        </tbody>
      </table>
    ),
  ],
  args: {
    merchant: 'Harbor Grill',
    dateLabel: 'Fri 16 Oct 2026',
    dateTime: '2026-10-16',
    category: 'Meals',
    amountLabel: '$86.40',
    currency: 'USD',
    status: 'submitted',
    flags: [],
    hasReceipt: true,
  },
};

export default meta;

type Story = StoryObj<typeof ExpenseRow>;

export const Default: Story = {};

export const Hover: Story = {
  parameters: {
    docs: {
      description: {
        story: 'CSS :hover cannot be set from a script. Point at the row: the fill changes to color.surface.hover.',
      },
    },
  },
};

export const Focused: Story = {
  play: async ({ canvasElement }) => {
    within(canvasElement).getByRole('checkbox').focus();
  },
};

export const Selected: Story = { args: { selected: true } };

export const Disabled: Story = { args: { disabled: true, status: 'paid' } };

export const WithPolicyFlags: Story = {
  args: { flags: ['OVER_MEAL_LIMIT', 'ALCOHOL'], amountLabel: '$148.90' },
};

export const MissingReceipt: Story = {
  args: { hasReceipt: false, flags: ['RECEIPT_REQUIRED'], merchant: 'Lakeside Hotel', category: 'Lodging' },
};

export const Refund: Story = {
  args: { kind: 'refund', amountLabel: '−$45.00', merchant: 'Northwind Air', category: 'Airfare', status: 'approved' },
};
```

### `src/components/ExpenseRow.test.tsx`

```tsx
import { describe, expect, it } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import axe from 'axe-core';
import { ExpenseRow, type ExpenseRowProps } from './ExpenseRow';

const base: ExpenseRowProps = {
  merchant: 'Harbor Grill',
  dateLabel: 'Fri 16 Oct 2026',
  dateTime: '2026-10-16',
  category: 'Meals',
  amountLabel: '$86.40',
  currency: 'USD',
  status: 'submitted',
  flags: [],
  hasReceipt: true,
};

function renderRow(props: Partial<ExpenseRowProps> = {}) {
  return render(
    <table>
      <tbody>
        <ExpenseRow {...base} {...props} />
      </tbody>
    </table>,
  );
}

describe('ExpenseRow', () => {
  it('renders merchant, date, category and amount', () => {
    renderRow();
    expect(screen.getByRole('button', { name: 'Harbor Grill' })).toBeInTheDocument();
    expect(screen.getByText('Fri 16 Oct 2026')).toHaveAttribute('datetime', '2026-10-16');
    expect(screen.getByText('Meals')).toBeInTheDocument();
    expect(screen.getByText('$86.40')).toBeInTheDocument();
    expect(screen.getByText('USD')).toBeInTheDocument();
  });

  it('renders the status badge', () => {
    renderRow({ status: 'rejected' });
    expect(screen.getByText('Rejected')).toHaveAttribute('data-status', 'rejected');
  });

  it('renders each policy flag', () => {
    renderRow({ flags: ['OVER_MEAL_LIMIT', 'ALCOHOL'] });
    const list = screen.getByRole('list', { name: 'Policy flags' });
    expect(within(list).getAllByRole('listitem')).toHaveLength(2);
    expect(within(list).getByText('Over meal limit')).toBeInTheDocument();
    expect(within(list).getByText('Alcohol')).toBeInTheDocument();
  });

  it('announces receipt status', () => {
    const { unmount } = renderRow({ hasReceipt: true });
    expect(screen.getByText('Receipt attached')).toBeInTheDocument();
    unmount();
    renderRow({ hasReceipt: false });
    expect(screen.getByText('No receipt')).toBeInTheDocument();
  });

  it('selected row checks the checkbox', () => {
    renderRow({ selected: true });
    expect(screen.getByRole('checkbox', { name: 'Select Harbor Grill, Fri 16 Oct 2026' })).toBeChecked();
    expect(screen.getByRole('row')).toHaveAttribute('data-selected', 'true');
  });

  it('disabled row disables the checkbox', () => {
    renderRow({ disabled: true, status: 'paid' });
    expect(screen.getByRole('checkbox')).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Harbor Grill' })).toBeEnabled();
  });

  it('has no axe violations', async () => {
    const states: Partial<ExpenseRowProps>[] = [
      {},
      { selected: true },
      { disabled: true, status: 'paid' },
      { flags: ['RECEIPT_REQUIRED', 'WEEKEND_REVIEW'], hasReceipt: false },
      { kind: 'refund', amountLabel: '−$45.00' },
    ];
    for (const state of states) {
      const { container, unmount } = renderRow(state);
      const results = await axe.run(container, { rules: { 'color-contrast': { enabled: false } } });
      expect(results.violations).toEqual([]);
      unmount();
    }
  });
});
```

