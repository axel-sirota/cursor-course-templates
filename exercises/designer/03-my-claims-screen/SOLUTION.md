# Solution Key: Exercise 3, My Claims Screen (instructor only)

The reference fix and screen below were run in a clean copy of the stack example: `npm test` (38 tests in 6 files, all pass, axe zero violations in all 5 screen states), `tsc --noEmit` clean, `check_card.mjs` 12 of 12 fixed, `check_stories.mjs` 34 of 34 (exercise 3) and 53 of 53 (exercise 2), `check_contrast.mjs` 18 + 10 + 9 pairs pass.

## Seeded defects in `inputs/flawed/`

Line numbers are for the files as shipped. `check_card.mjs --dir exercises/designer/03-my-claims-screen/inputs/flawed` reports the same lines.

| ID | File:line | Code | Problem | Fix |
|---|---|---|---|---|
| D1 | `ClaimSummaryCard.tsx:32` | `style={{ marginTop: 12 }}` | Inline style, hardcoded spacing, breaks the stack rule | Remove it. Spacing between cards belongs to the parent grid gap (`space.stack.md`) |
| D2 | `ClaimSummaryCard.tsx:35` | `<button className="claim-card__menu" onClick={onMoreActions}>` + bare `<svg>` | Icon-only button with no accessible name. Also no `type="button"` and the svg is not `aria-hidden` | `aria-label={\`More actions for ${title}\`}`, `type="button"`, `aria-hidden="true" focusable="false"` on the svg |
| D3 | `ClaimSummaryCard.tsx:44` | `${total.toFixed(2)}` | Money formatted inside a presentational component, `$` hardcoded: wrong for EUR and GBP, ambiguous for CAD | Props become `totalLabel` + `currency`, render with `AmountCell`. Flag the props change for engineering in the handoff |
| D4 | `ClaimSummaryCard.tsx:46` | `<span className={\`claim-card__dot claim-card__dot--${status}\`} />` | Status shown by color only. No text, invisible to screen readers and to color-blind users | Replace the dot with `<StatusBadge status={status} />`, delete the dot CSS |
| D5 | `ClaimSummaryCard.tsx:51` | `<img className="claim-card__thumb" src={receiptThumbUrl} />` | Image with no `alt` | `alt={\`First receipt for ${title}\`}` (or `alt=""` if the team decides it is decorative, but then say so) |
| D6 | `ClaimSummaryCard.tsx:52` | `<div className="claim-card__open" onClick={onOpen}>` | `div` as a button: no keyboard focus, no Enter / Space, no role | `<button type="button">View details<span class="visually-hidden"> for {title}</span></button>` |
| D7 | `ClaimSummaryCard.css:7` | `width: 400px;` | Fixed width wider than a 360 px screen, so the page scrolls sideways | Remove it. Let the grid size the card (`minmax(var(--size-card-min), 1fr)`), add `min-width: 0` |
| D8 | `ClaimSummaryCard.css:10` | `solid #d0d7de;` | Hardcoded hex, and not even one of the brief's colors | `var(--color-border-subtle)` |
| D9 | `ClaimSummaryCard.css:25` | `font-size: 18px;` | Hardcoded px font size, off the type scale (18 is not a step) | `var(--font-size-title)` (20px step) |
| D10 | `ClaimSummaryCard.css:57` | `color: var(--primitive-color-navy-700);` | Component reads a primitive token, skipping the semantic layer | Remove, AmountCell owns the amount color (`color.text.default`) |
| D11 | `ClaimSummaryCard.css:77` | `opacity: 0.6;` | Muted text at 60% opacity on white is 2.66:1, below 4.5:1 | Remove. `color.text.muted` alone is 6.46:1 |
| D12 | `ClaimSummaryCard.css:39` | `outline: none;` on `:focus` | Keyboard users lose the focus indicator on the menu button | Delete the rule, add `:focus-visible` with `border-width.focus` solid `color.focus.ring` for the menu and View details buttons |

Bonus finds worth credit (not counted by the check):

| File:line | Problem |
|---|---|
| `ClaimSummaryCard.tsx:32` | Card root is a `div`. An `<article aria-labelledby={titleId}>` gives each card a name in the screen's region list |
| `ClaimSummaryCard.tsx:52` | "View details" repeated 8 times has the same accessible name. The visually hidden "for {title}" fixes it |
| `ClaimSummaryCard.css:60` to `:71` | The dot rules use `color.status.*.text` as a fill. Dead once D4 is fixed: delete them |
| `ClaimSummaryCard.css:80` to `:83` | Thumbnail sized with an icon token. Fine for now, worth a `size.thumb` token if the design grows |

## How the check matches each defect

| ID | Pattern in `check_card.mjs` |
|---|---|
| D1 | `style={{` |
| D2 | a `<button>` whose children are only an svg (no text) and no `aria-label` / `aria-labelledby` |
| D3 | `.toFixed(`, `.toLocaleString(` or `Intl.NumberFormat` |
| D4 | no `<StatusBadge`, no status word, no `STATUS_TEXT` map |
| D5 | `<img` without `alt=` |
| D6 | `<div`, `<span`, `<p` or `<li` with `onClick=` |
| D7 | `width:` followed by a 2+ digit px value (`min-width` and `max-width` do not match) |
| D8 | hex, `rgb()`, `rgba()`, `hsl()` or `hsla()` |
| D9 | `font-size:` followed by px, rem or em |
| D10 | `--primitive-` |
| D11 | `opacity:` below 1 |
| D12 | no `:focus-visible` rule that sets `outline` or `box-shadow` with `--color-focus-ring` |

Comments are ignored, so a note like `/* was #d0d7de */` does not count as a defect. Patterns can be gamed (for example `aria-label=""` passes D2). The axe `button-name` rule in the card's test catches that one.

## Reference fix: `ClaimSummaryCard.tsx`

```tsx
// ClaimSummaryCard: one claim at a glance. Presentational only.
import { useId } from 'react';
import { AmountCell, type Currency } from './AmountCell';
import { StatusBadge, type ClaimStatus } from './StatusBadge';
import './ClaimSummaryCard.css';

export type ClaimSummaryCardProps = {
  title: string;
  claimId: string;
  /** Formatted by the parent, e.g. "$1,234.50". Replaces the old numeric `total` (see handoff). */
  totalLabel: string;
  currency: Currency;
  status: ClaimStatus;
  expenseCount: number;
  flagCount: number;
  submittedLabel: string;
  receiptThumbUrl?: string;
  onOpen: () => void;
  onMoreActions: () => void;
};

export function ClaimSummaryCard({
  title,
  claimId,
  totalLabel,
  currency,
  status,
  expenseCount,
  flagCount,
  submittedLabel,
  receiptThumbUrl,
  onOpen,
  onMoreActions,
}: ClaimSummaryCardProps) {
  const titleId = useId();

  return (
    <article className="claim-card" aria-labelledby={titleId}>
      <div className="claim-card__header">
        <h3 id={titleId} className="claim-card__title">
          {title}
        </h3>
        <button
          type="button"
          className="claim-card__menu"
          aria-label={`More actions for ${title}`}
          onClick={onMoreActions}
        >
          <svg className="claim-card__menu-icon" viewBox="0 0 16 16" aria-hidden="true" focusable="false">
            <circle cx="8" cy="3" r="1.5" fill="currentColor" />
            <circle cx="8" cy="8" r="1.5" fill="currentColor" />
            <circle cx="8" cy="13" r="1.5" fill="currentColor" />
          </svg>
        </button>
      </div>
      <p className="claim-card__id">{claimId}</p>
      <div className="claim-card__total">
        <AmountCell amountLabel={totalLabel} currency={currency} />
      </div>
      <div className="claim-card__status">
        <StatusBadge status={status} />
      </div>
      <p className="claim-card__meta">
        {expenseCount} expenses · {flagCount} flags · {submittedLabel}
      </p>
      {receiptThumbUrl && (
        <img className="claim-card__thumb" src={receiptThumbUrl} alt={`First receipt for ${title}`} />
      )}
      <button type="button" className="claim-card__open" onClick={onOpen}>
        View details<span className="claim-card__visually-hidden"> for {title}</span>
      </button>
    </article>
  );
}
```

## Reference fix: `ClaimSummaryCard.css`

```css
/* ClaimSummaryCard: semantic tokens only. */

.claim-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-stack-sm);
  min-width: 0;
  max-width: 100%;
  padding: var(--space-inset-md);
  background: var(--color-surface-card);
  border: var(--border-width-default) solid var(--color-border-subtle);
  border-radius: var(--radius-card);
  font-family: var(--font-family-base);
  color: var(--color-text-default);
}

.claim-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-inline-sm);
}

.claim-card__title {
  margin: 0;
  font-size: var(--font-size-title);
  font-weight: var(--font-weight-semibold);
  line-height: var(--font-line-height-tight);
  overflow-wrap: anywhere;
}

.claim-card__menu {
  padding: var(--space-inset-xs);
  border: none;
  border-radius: var(--radius-control);
  background: none;
  color: var(--color-text-muted);
  cursor: pointer;
}

.claim-card__menu:focus-visible,
.claim-card__open:focus-visible {
  outline: var(--border-width-focus) solid var(--color-focus-ring);
  outline-offset: var(--border-width-focus);
}

.claim-card__menu-icon {
  width: var(--size-icon-md);
  height: var(--size-icon-md);
}

.claim-card__id {
  margin: 0;
  font-size: var(--font-size-caption);
  color: var(--color-text-muted);
}

.claim-card__total {
  color: var(--color-text-default);
}

.claim-card__meta {
  margin: 0;
  font-size: var(--font-size-label);
  color: var(--color-text-muted);
}

.claim-card__thumb {
  width: var(--size-icon-md);
  height: var(--size-icon-md);
  border-radius: var(--radius-control);
}

.claim-card__open {
  align-self: flex-start;
  padding: 0;
  border: none;
  border-radius: var(--radius-control);
  background: none;
  color: var(--color-text-link);
  font: inherit;
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
}

.claim-card__visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}
```

## Tokens added for the screen

```json
{
  "primitive": {
    "size": {
      "70": {
        "$value": "280px",
        "$type": "dimension"
      },
      "90": {
        "$value": "360px",
        "$type": "dimension"
      },
      "192": {
        "$value": "768px",
        "$type": "dimension"
      },
      "300": {
        "$value": "1200px",
        "$type": "dimension"
      },
      "320": {
        "$value": "1280px",
        "$type": "dimension"
      }
    }
  },
  "semantic": {
    "breakpoint": {
      "sm": {
        "$value": "{primitive.size.90}",
        "$type": "dimension"
      },
      "md": {
        "$value": "{primitive.size.192}",
        "$type": "dimension"
      },
      "lg": {
        "$value": "{primitive.size.320}",
        "$type": "dimension"
      }
    },
    "size": {
      "page": {
        "max": {
          "$value": "{primitive.size.300}",
          "$type": "dimension"
        }
      },
      "card": {
        "min": {
          "$value": "{primitive.size.70}",
          "$type": "dimension"
        }
      }
    },
    "color": {
      "surface": {
        "skeleton": {
          "$value": "{primitive.color.gray.200}",
          "$type": "color"
        }
      },
      "feedback": {
        "danger": {
          "bg": {
            "$value": "{primitive.color.red.100}",
            "$type": "color"
          },
          "border": {
            "$value": "{primitive.color.red.700}",
            "$type": "color"
          }
        }
      }
    }
  }
}
```

Contrast for the screen pairs (real output): error text on danger bg 6.40:1, focus ring on danger bg 3.51:1, control border on page 3.41:1, link on page 6.46:1. All 9 pass.

## Grading the screen

| Look for | Pass | Common miss |
|---|---|---|
| Screen is arrangement only | Props in, components out, stubs marked `// TODO: engineering` | Filtering `rows` by `activeStatus` inside the screen |
| Summary grid | `repeat(auto-fill, minmax(var(--size-card-min), 1fr))`: 1 / 2 / 4 columns at 360 / 768 / 1280 | Three media queries with hardcoded column counts |
| 360 px | Page never scrolls sideways, table scrolls in a focusable region | `overflow-x: auto` on `body`, or the table squeezed until text overlaps |
| Media queries | px literal + `/* breakpoint.md */` comment | `var(--breakpoint-md)` inside `@media` (silently ignored by the browser) |
| Loading | `aria-busy`, hidden "Loading claims" text, placeholders `aria-hidden` | Spinner with no text |
| Error | `role="alert"`, danger tokens, Try again button | Red text only |
| Toggles | `aria-pressed` + check icon or weight change | Pressed state shown by fill color only |
| Table | `<caption>`, `th scope="col"`, select-all labelled | Header row built from `div`s |
| Card props change | In the handoff under "needs engineering" | Silently changed, or left formatting money |

Why 1 / 2 / 4 columns works out: content width is `min(viewport - 2 x padding, 1200px)`. At 360: 328 px, one 280 px column. At 768: 720 px, two columns (three need 864). At 1280: 1200 px, four columns need 4 x 280 + 3 x 12 = 1156.

## Reference screen: `src/screens/MyClaimsScreen.tsx`

```tsx
// MyClaimsScreen: arranges components only. No fetching, filtering or sorting here.
import { useId } from 'react';
import { ClaimSummaryCard, type ClaimSummaryCardProps } from '../components/ClaimSummaryCard';
import { ExpenseRow, type ExpenseRowProps } from '../components/ExpenseRow';
import type { ClaimStatus } from '../components/StatusBadge';
import './MyClaimsScreen.css';

export type ClaimSummary = Omit<ClaimSummaryCardProps, 'onOpen' | 'onMoreActions'>;
export type ExpenseRowData = Omit<ExpenseRowProps, 'selected' | 'onSelectedChange' | 'onOpen'> & { id: string };
export type ScreenState = 'ready' | 'loading' | 'empty' | 'error' | 'no-results';

export type MyClaimsScreenProps = {
  state: ScreenState;
  claims: ClaimSummary[];
  rows: ExpenseRowData[];
  selectedIds: string[];
  activeStatus: 'all' | ClaimStatus;
  flaggedOnly: boolean;
};

const STATUS_FILTERS: { value: 'all' | ClaimStatus; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'draft', label: 'Draft' },
  { value: 'submitted', label: 'Submitted' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'paid', label: 'Paid' },
];

const stub = () => {}; // TODO: engineering

export function MyClaimsScreen({ state, claims, rows, selectedIds, activeStatus, flaggedOnly }: MyClaimsScreenProps) {
  const claimsHeadingId = useId();
  const expensesHeadingId = useId();
  const captionId = useId();
  const searchId = useId();

  return (
    <main className="my-claims">
      <div className="my-claims__inner">
        <header className="my-claims__header">
          <div>
            <h1 className="my-claims__title">My claims</h1>
            <p className="my-claims__subtitle">October 2026 · {rows.length} expenses</p>
          </div>
          <button type="button" className="my-claims__primary" onClick={stub}>
            New claim
          </button>
        </header>

        {state === 'error' && (
          <div className="my-claims__error" role="alert">
            <p className="my-claims__error-text">We could not load your claims.</p>
            <button type="button" className="my-claims__primary" onClick={stub}>
              Try again
            </button>
          </div>
        )}

        {state === 'loading' && (
          <section className="my-claims__loading" aria-busy="true">
            <span className="my-claims__visually-hidden">Loading claims</span>
            <div className="my-claims__grid" aria-hidden="true">
              {[1, 2, 3, 4].map((n) => (
                <div key={n} className="my-claims__skeleton my-claims__skeleton--card" />
              ))}
            </div>
            <div className="my-claims__skeleton-rows" aria-hidden="true">
              {[1, 2, 3, 4, 5].map((n) => (
                <div key={n} className="my-claims__skeleton my-claims__skeleton--row" />
              ))}
            </div>
          </section>
        )}

        {state === 'empty' && (
          <section className="my-claims__empty">
            <h2 className="my-claims__section-title">No expenses yet</h2>
            <p className="my-claims__subtitle">Start a claim and add your first receipt.</p>
            <button type="button" className="my-claims__primary" onClick={stub}>
              New claim
            </button>
          </section>
        )}

        {(state === 'ready' || state === 'no-results') && (
          <>
            <section aria-labelledby={claimsHeadingId}>
              <h2 id={claimsHeadingId} className="my-claims__section-title">
                Claims
              </h2>
              <ul className="my-claims__grid">
                {claims.map((claim) => (
                  <li key={claim.claimId}>
                    <ClaimSummaryCard {...claim} onOpen={stub} onMoreActions={stub} />
                  </li>
                ))}
              </ul>
            </section>

            <section aria-labelledby={expensesHeadingId} className="my-claims__expenses">
              <h2 id={expensesHeadingId} className="my-claims__section-title">
                Expenses
              </h2>

              <div className="my-claims__filters">
                <div className="my-claims__toggles" role="group" aria-label="Filter by status">
                  {STATUS_FILTERS.map((f) => (
                    <button
                      key={f.value}
                      type="button"
                      className="my-claims__toggle"
                      aria-pressed={activeStatus === f.value}
                      onClick={stub}
                    >
                      {activeStatus === f.value && (
                        <svg className="my-claims__check" viewBox="0 0 16 16" aria-hidden="true" focusable="false">
                          <path d="M3 8.5 6.5 12 13 4.5" fill="none" stroke="currentColor" strokeWidth="2" />
                        </svg>
                      )}
                      {f.label}
                    </button>
                  ))}
                </div>
                <label className="my-claims__flagged">
                  <input type="checkbox" checked={flaggedOnly} onChange={stub} /> Flagged only
                </label>
                <div className="my-claims__search">
                  <label htmlFor={searchId}>Search merchant</label>
                  <input id={searchId} type="search" className="my-claims__search-input" onChange={stub} />
                </div>
              </div>

              {selectedIds.length > 0 && (
                <div className="my-claims__bulk">
                  <p className="my-claims__bulk-count">{selectedIds.length} selected</p>
                  <button type="button" className="my-claims__primary" onClick={stub}>
                    Submit selected
                  </button>
                </div>
              )}

              {state === 'no-results' ? (
                <div className="my-claims__no-results">
                  <p className="my-claims__subtitle">No expenses match these filters</p>
                  <button type="button" className="my-claims__text-button" onClick={stub}>
                    Clear filters
                  </button>
                </div>
              ) : (
                <div className="my-claims__table-region" role="region" aria-labelledby={captionId} tabIndex={0}>
                  <table className="my-claims__table">
                    <caption id={captionId} className="my-claims__caption">
                      Expenses, October 2026
                    </caption>
                    <thead>
                      <tr>
                        <th scope="col">
                          <input type="checkbox" aria-label="Select all expenses" onChange={stub} />
                        </th>
                        <th scope="col">Merchant</th>
                        <th scope="col">Date</th>
                        <th scope="col">Category</th>
                        <th scope="col" className="my-claims__th--amount">
                          Amount
                        </th>
                        <th scope="col">Status</th>
                        <th scope="col">Flags</th>
                        <th scope="col">Receipt</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map(({ id, ...row }) => (
                        <ExpenseRow key={id} {...row} selected={selectedIds.includes(id)} />
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </main>
  );
}
```

## Reference screen: `src/screens/MyClaimsScreen.css`

```css
/* MyClaimsScreen: semantic tokens only. Media queries are the one place px literals
   appear, because CSS variables do not work inside @media. Each one names its token. */

.my-claims {
  min-height: 100%;
  padding: var(--space-inset-md);
  background: var(--color-surface-page);
  color: var(--color-text-default);
  font-family: var(--font-family-base);
  font-size: var(--font-size-body);
  line-height: var(--font-line-height-normal);
}

.my-claims__inner {
  display: flex;
  flex-direction: column;
  gap: var(--space-stack-lg);
  max-width: var(--size-page-max);
  margin: 0 auto;
}

.my-claims__header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-stack-md);
}

.my-claims__title {
  margin: 0;
  font-size: var(--font-size-page);
  font-weight: var(--font-weight-bold);
  line-height: var(--font-line-height-tight);
}

.my-claims__section-title {
  margin: 0 0 var(--space-stack-md);
  font-size: var(--font-size-heading);
  font-weight: var(--font-weight-semibold);
  line-height: var(--font-line-height-tight);
}

.my-claims__subtitle {
  margin: 0;
  font-size: var(--font-size-label);
  color: var(--color-text-muted);
}

.my-claims__primary {
  padding: var(--space-inset-sm) var(--space-inline-md);
  border: none;
  border-radius: var(--radius-control);
  background: var(--color-action-primary-bg);
  color: var(--color-text-inverse);
  font: inherit;
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
}

.my-claims__primary:hover {
  background: var(--color-action-primary-bg-hover);
}

.my-claims__text-button {
  padding: 0;
  border: none;
  background: none;
  color: var(--color-text-link);
  font: inherit;
  font-weight: var(--font-weight-semibold);
  text-decoration: underline;
  cursor: pointer;
}

.my-claims__primary:focus-visible,
.my-claims__text-button:focus-visible,
.my-claims__toggle:focus-visible,
.my-claims__search-input:focus-visible,
.my-claims__table-region:focus-visible {
  outline: var(--border-width-focus) solid var(--color-focus-ring);
  outline-offset: var(--border-width-focus);
}

.my-claims__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(var(--size-card-min), 1fr));
  gap: var(--space-stack-md);
  margin: 0;
  padding: 0;
  list-style: none;
}

.my-claims__expenses {
  display: flex;
  flex-direction: column;
  gap: var(--space-stack-md);
}

.my-claims__expenses .my-claims__section-title {
  margin: 0;
}

.my-claims__filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-stack-md);
}

.my-claims__toggles {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-inline-xs);
}

.my-claims__toggle {
  display: inline-flex;
  align-items: center;
  gap: var(--space-inline-xs);
  padding: var(--space-inset-xs) var(--space-inline-sm);
  border: var(--border-width-default) solid var(--color-border-control);
  border-radius: var(--radius-control);
  background: var(--color-surface-card);
  color: var(--color-text-default);
  font: inherit;
  font-size: var(--font-size-label);
  cursor: pointer;
}

.my-claims__toggle[aria-pressed='true'] {
  border-color: var(--color-action-primary-bg);
  background: var(--color-action-primary-bg);
  color: var(--color-text-inverse);
  font-weight: var(--font-weight-semibold);
}

.my-claims__check {
  width: var(--size-icon-sm);
  height: var(--size-icon-sm);
}

.my-claims__flagged {
  display: inline-flex;
  align-items: center;
  gap: var(--space-inline-xs);
  font-size: var(--font-size-label);
}

.my-claims__search {
  display: flex;
  flex-direction: column;
  gap: var(--space-stack-xs);
  font-size: var(--font-size-label);
}

.my-claims__search-input {
  padding: var(--space-inset-xs) var(--space-inline-sm);
  border: var(--border-width-default) solid var(--color-border-control);
  border-radius: var(--radius-control);
  background: var(--color-surface-card);
  color: var(--color-text-default);
  font: inherit;
}

.my-claims__bulk {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-stack-md);
  padding: var(--space-inset-sm) var(--space-inline-md);
  border-radius: var(--radius-card);
  background: var(--color-surface-selected);
}

.my-claims__bulk-count {
  margin: 0;
  font-weight: var(--font-weight-semibold);
}

.my-claims__table-region {
  overflow-x: auto;
  border: var(--border-width-default) solid var(--color-border-subtle);
  border-radius: var(--radius-card);
  background: var(--color-surface-card);
}

.my-claims__table {
  width: 100%;
  border-collapse: collapse;
}

.my-claims__caption {
  padding: var(--space-inset-sm) var(--space-inline-md);
  text-align: start;
  font-size: var(--font-size-label);
  color: var(--color-text-muted);
}

.my-claims__table th {
  padding: var(--space-inset-sm) var(--space-inline-md);
  border-bottom: var(--border-width-default) solid var(--color-border-subtle);
  text-align: start;
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  white-space: nowrap;
}

.my-claims__table .my-claims__th--amount {
  text-align: end;
}

.my-claims__error {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-stack-md);
  padding: var(--space-inset-md);
  border: var(--border-width-default) solid var(--color-feedback-danger-border);
  border-radius: var(--radius-card);
  background: var(--color-feedback-danger-bg);
}

.my-claims__error-text {
  margin: 0;
  color: var(--color-text-danger);
  font-weight: var(--font-weight-semibold);
}

.my-claims__empty,
.my-claims__no-results {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--space-stack-sm);
  padding: var(--space-inset-lg);
  border-radius: var(--radius-card);
  background: var(--color-surface-card);
}

.my-claims__loading {
  display: flex;
  flex-direction: column;
  gap: var(--space-stack-lg);
}

.my-claims__skeleton-rows {
  display: flex;
  flex-direction: column;
  gap: var(--space-stack-sm);
}

.my-claims__skeleton {
  border-radius: var(--radius-card);
  background: var(--color-surface-skeleton);
}

.my-claims__skeleton--card {
  min-height: var(--size-card-min);
}

.my-claims__skeleton--row {
  min-height: var(--space-stack-xxl);
}

.my-claims__visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}

@media (min-width: 768px) { /* breakpoint.md */
  .my-claims {
    padding: var(--space-inset-lg);
  }
}
```

## Reference: `src/data/sample.ts` (typed view of the sample JSON)

```ts
// Typed view of sample-claims.json (copied from exercises/designer/assets/).
// JSON imports widen literal unions to string, so cast once here.
import raw from './sample-claims.json';
import type { Currency } from '../components/AmountCell';
import type { ClaimStatus, PolicyFlag } from '../components/StatusBadge';
import type { ClaimSummary, ExpenseRowData } from '../screens/MyClaimsScreen';

export const sampleRows: ExpenseRowData[] = raw.rows.map((r) => ({
  ...r,
  currency: r.currency as Currency,
  kind: r.kind as 'charge' | 'refund',
  status: r.status as ClaimStatus,
  flags: r.flags as PolicyFlag[],
}));

export const sampleClaims: ClaimSummary[] = raw.claims.map((c) => ({
  ...c,
  currency: c.currency as Currency,
  status: c.status as ClaimStatus,
}));
```

## Reference: `.storybook/preview.ts` viewports

```ts
import type { Preview } from '@storybook/react';
import '../src/styles/tokens.css';

// Viewports match breakpoint.sm / breakpoint.md / breakpoint.lg in tokens/tokens.json.
const viewports = {
  nw360: { name: 'Northwind 360', styles: { width: '360px', height: '800px' }, type: 'mobile' },
  nw768: { name: 'Northwind 768', styles: { width: '768px', height: '1024px' }, type: 'tablet' },
  nw1280: { name: 'Northwind 1280', styles: { width: '1280px', height: '900px' }, type: 'desktop' },
};

const preview: Preview = {
  parameters: {
    layout: 'centered',
    viewport: { viewports },
  },
};

export default preview;
```
