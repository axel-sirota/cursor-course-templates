// ClaimSummaryCard: built in a hurry for the October demo. Review before it ships.
import './ClaimSummaryCard.css';

type ClaimStatus = 'draft' | 'submitted' | 'approved' | 'rejected' | 'paid';

export type ClaimSummaryCardProps = {
  title: string;
  claimId: string;
  total: number;
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
  total,
  status,
  expenseCount,
  flagCount,
  submittedLabel,
  receiptThumbUrl,
  onOpen,
  onMoreActions,
}: ClaimSummaryCardProps) {
  return (
    <div className="claim-card" style={{ marginTop: 12 }}>
      <div className="claim-card__header">
        <h3 className="claim-card__title">{title}</h3>
        <button className="claim-card__menu" onClick={onMoreActions}>
          <svg className="claim-card__menu-icon" viewBox="0 0 16 16">
            <circle cx="8" cy="3" r="1.5" fill="currentColor" />
            <circle cx="8" cy="8" r="1.5" fill="currentColor" />
            <circle cx="8" cy="13" r="1.5" fill="currentColor" />
          </svg>
        </button>
      </div>
      <p className="claim-card__id">{claimId}</p>
      <p className="claim-card__total">${total.toFixed(2)}</p>
      <div className="claim-card__status">
        <span className={`claim-card__dot claim-card__dot--${status}`} />
      </div>
      <p className="claim-card__meta">
        {expenseCount} expenses · {flagCount} flags · {submittedLabel}
      </p>
      {receiptThumbUrl && <img className="claim-card__thumb" src={receiptThumbUrl} />}
      <div className="claim-card__open" onClick={onOpen}>
        View details
      </div>
    </div>
  );
}
