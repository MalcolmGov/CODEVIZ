import React from 'react'
import clsx from 'clsx'

interface TableProps {
  columns: Array<{ key: string; label: string; render?: (row: any) => React.ReactNode }>
  data: Array<Record<string, any>>
  onRowClick?: (row: any) => void
}

export const Table: React.FC<TableProps> = ({ columns, data, onRowClick }) => (
  <div className="overflow-hidden border border-slate-border/40 rounded-xl bg-slate-surface/40 backdrop-blur-md">
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left border-collapse">
        <thead>
          <tr className="border-b border-slate-border/50 bg-slate-950/40">
            {columns.map((col) => (
              <th
                key={col.key}
                className="px-6 py-3.5 text-xs font-semibold uppercase tracking-wider text-slate-400 font-display"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-border/30">
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-6 py-10 text-center text-slate-500">
                No records found.
              </td>
            </tr>
          ) : (
            data.map((row, idx) => (
              <tr
                key={idx}
                onClick={() => onRowClick?.(row)}
                className={clsx(
                  'transition-colors duration-150',
                  onRowClick ? 'cursor-pointer hover:bg-slate-800/30' : 'hover:bg-slate-800/10'
                )}
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-6 py-4 text-slate-300 font-sans">
                    {col.render ? col.render(row) : String(row[col.key] ?? '-')}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  </div>
)

