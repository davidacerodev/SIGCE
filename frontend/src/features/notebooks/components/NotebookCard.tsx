import { Pencil, Trash2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { formatDate } from '@/lib/format'
import type { Notebook } from '../types'

interface Props {
  notebook: Notebook
  onRename: () => void
  onDelete: () => void
}

export function NotebookCard({ notebook, onRename, onDelete }: Props) {
  const count = notebook.source_count
  return (
    <li className="group relative flex flex-col rounded-card border border-line bg-surface transition-shadow hover:shadow-md">
      <Link to={`/notebooks/${notebook.id}`} className="flex flex-1 flex-col gap-2 rounded-card p-4 pb-3">
        <h2 className="line-clamp-2 pr-14 text-lg leading-snug">{notebook.title}</h2>
        {notebook.description && <p className="line-clamp-2 text-sm text-ink-muted">{notebook.description}</p>}
        <p className="mt-auto pt-2 text-xs text-ink-muted">
          {formatDate(notebook.updated_at)} · {count} {count === 1 ? 'fuente' : 'fuentes'}
        </p>
      </Link>
      <div className="absolute right-2 top-2 flex gap-1">
        <button aria-label={`Editar ${notebook.title}`} onClick={onRename} className="rounded p-1.5 text-ink-muted hover:bg-accent-soft">
          <Pencil className="size-4" aria-hidden />
        </button>
        <button aria-label={`Eliminar ${notebook.title}`} onClick={onDelete} className="rounded p-1.5 text-ink-muted hover:bg-accent-soft hover:text-danger">
          <Trash2 className="size-4" aria-hidden />
        </button>
      </div>
    </li>
  )
}
