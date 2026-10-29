import { FileText, Plus, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { useSourceMutations } from '../hooks/useSources'
import type { Source, SourceStatus } from '../types'
import { AddSourceDialog } from './AddSourceDialog'

const STATUS_LABEL: Record<SourceStatus, string> = { pending: 'En cola', processing: 'Procesando…', ready: 'Lista', failed: 'Error' }
const FORMAT: Record<string, string> = { 'application/pdf': 'PDF', 'text/markdown': 'Markdown', 'text/plain': 'Texto' }

interface Props {
  notebookId: string
  sources: Source[]
  loading: boolean
  error: Error | null
  isSelected: (s: Source) => boolean
  onToggle: (id: string) => void
}

export function SourcesPanel({ notebookId, sources, loading, error, isSelected, onToggle }: Props) {
  const { remove } = useSourceMutations(notebookId)
  const [adding, setAdding] = useState(false)
  const [removing, setRemoving] = useState<Source | null>(null)

  return (
    <section aria-label="Fuentes" className="flex h-full flex-col bg-surface">
      <header className="flex items-center justify-between border-b border-line p-3">
        <h2 className="text-lg">Fuentes</h2>
        <Button onClick={() => setAdding(true)}><Plus className="size-4" aria-hidden /> Agregar</Button>
      </header>
      {loading ? (
        <p role="status" className="p-4 text-sm text-ink-muted">Cargando fuentes…</p>
      ) : error ? (
        <p role="alert" className="p-4 text-sm text-danger">{error.message}</p>
      ) : sources.length === 0 ? (
        <p className="p-4 text-sm text-ink-muted">Agrega una fuente para empezar a conversar con tu contenido.</p>
      ) : (
        <ul className="flex-1 overflow-y-auto p-2">
          {sources.map((s) => (
            <li key={s.id} className="flex items-center gap-2 rounded-md p-2 hover:bg-accent-soft">
              <FileText className="size-4 shrink-0 text-note" aria-hidden />
              <div className="flex min-w-0 flex-1 flex-col text-sm">
                <span className="truncate">{s.name}</span>
                <span className={`text-xs ${s.status === 'failed' ? 'text-danger' : 'text-ink-muted'}`} title={s.error_message ?? undefined}>
                  {FORMAT[s.mime_type ?? ''] ?? 'Archivo'} · {STATUS_LABEL[s.status]}
                  {s.status === 'failed' && s.error_message ? ` — ${s.error_message}` : ''}
                </span>
              </div>
              <input type="checkbox" checked={isSelected(s)} disabled={s.status !== 'ready'} onChange={() => onToggle(s.id)} aria-label={`Usar ${s.name} en el chat`} className="size-4 accent-accent" />
              <button aria-label={`Eliminar ${s.name}`} onClick={() => setRemoving(s)} className="rounded p-1 text-ink-muted hover:text-danger">
                <Trash2 className="size-4" aria-hidden />
              </button>
            </li>
          ))}
        </ul>
      )}
      <AddSourceDialog notebookId={notebookId} open={adding} onClose={() => setAdding(false)} />
      <ConfirmDialog
        open={!!removing}
        title="Eliminar fuente"
        message={`Se eliminará «${removing?.name}» de este cuaderno.`}
        confirmLabel="Eliminar"
        onConfirm={() => removing && remove.mutate(removing.id)}
        onClose={() => setRemoving(null)}
      />
    </section>
  )
}
