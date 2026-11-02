import { useId } from 'react';
import './BudgetCard.css';

export type BudgetStatus = 'on-track' | 'near-limit' | 'over';

export type BudgetCardProps = {
  /** Category name, e.g. "Groceries". */
  label: string;
  /** Amount spent, already formatted by the parent, e.g. "$420". */
  spentLabel: string;
  /** Monthly limit, already formatted by the parent, e.g. "$600". */
  limitLabel: string;
  /** Share of the limit used, 0 to 100. The parent clamps it. */
  percentUsed: number;
  /** Drives color through data-status. The parent decides it. */
  status: BudgetStatus;
  /** Status sentence, e.g. "$180 left". The parent writes it. */
  statusLabel: string;
};

export function BudgetCard({
  label,
  spentLabel,
  limitLabel,
  percentUsed,
  status,
  statusLabel,
}: BudgetCardProps) {
  const titleId = useId();

  return (
    <article className="budget-card" data-status={status} aria-labelledby={titleId}>
      <h3 id={titleId} className="budget-card__title">
        {label}
      </h3>
      <p className="budget-card__amount">
        <span className="budget-card__spent">{spentLabel}</span>
        <span className="budget-card__limit"> of {limitLabel}</span>
      </p>
      <progress
        className="budget-card__bar"
        max={100}
        value={percentUsed}
        aria-label={`${label} budget used`}
      />
      <p className="budget-card__status">{statusLabel}</p>
    </article>
  );
}
