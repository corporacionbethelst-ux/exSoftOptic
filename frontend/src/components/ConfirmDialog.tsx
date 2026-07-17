import type { ReactNode } from 'react';

type ConfirmDialogProps = {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  busy?: boolean;
  children?: ReactNode;
  onConfirm: () => void;
  onCancel: () => void;
};

export function ConfirmDialog({ open, title, description, confirmLabel = 'Confirmar', cancelLabel = 'Cancelar', busy, children, onConfirm, onCancel }: ConfirmDialogProps) {
  if (!open) return null;

  return (
    <div className="dialog-backdrop" role="presentation">
      <section className="confirm-dialog" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
        <h2 id="confirm-title">{title}</h2>
        <p className="muted">{description}</p>
        {children ? <div className="dialog-content">{children}</div> : null}
        <div className="form-actions">
          <button className="danger-button" disabled={busy} onClick={onConfirm}>{busy ? 'Procesando…' : confirmLabel}</button>
          <button className="secondary-button" disabled={busy} onClick={onCancel}>{cancelLabel}</button>
        </div>
      </section>
    </div>
  );
}
