type PaginationProps = {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
};

export function Pagination({ page, pageSize, total, onPageChange, onPageSizeChange }: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const start = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const end = Math.min(total, page * pageSize);

  return (
    <div className="pagination-bar">
      <span className="muted compact">Mostrando {start}-{end} de {total}</span>
      <div className="pagination-controls">
        {onPageSizeChange ? (
          <select value={pageSize} onChange={(event) => onPageSizeChange(Number(event.target.value))}>
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
        ) : null}
        <button className="secondary-button" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>Anterior</button>
        <strong>{page} / {totalPages}</strong>
        <button className="secondary-button" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>Siguiente</button>
      </div>
    </div>
  );
}
