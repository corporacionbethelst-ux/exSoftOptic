import type { ReactNode } from 'react';

type SectionPanelProps = {
  title: ReactNode;
  children: ReactNode;
  className?: string;
  description?: string;
  footer?: ReactNode;
};

export function SectionPanel({ title, children, className = '', description, footer }: SectionPanelProps) {
  return (
    <article className={`panel ${className}`.trim()}>
      <div className="panel-heading">
        <div>
          <h2>{title}</h2>
          {description ? <p className="muted compact">{description}</p> : null}
        </div>
        {footer ? <div className="panel-actions">{footer}</div> : null}
      </div>
      {children}
    </article>
  );
}
