import { BookOpen, Plus, Search } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { TopBar } from '@/components/layout/TopBar'
import { Button } from '@/components/ui/Button'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { NotebookCard } from '../components/NotebookCard'
import { NotebookFormDialog } from '../components/NotebookFormDialog'
import { useNotebookMutations, useNotebooks } from '../hooks/useNotebooks'
import type { Notebook } from '../types'

type Editing = { mode: 'create' } | { mode: 'rename'; notebook: Notebook } | null

export function HomePage() {
  const navigate = useNavigate()
  const { data: notebooks, error, isPending, refetch } = useNotebooks()
  const { create, update, remove } = useNotebookMutations()
  const [query, setQuery] = useState('')
  const [editing, setEditing] = useState<Editing>(null)
  const [deleting, setDeleting] = useState<Notebook | null>(null)

  const visible = (notebooks ?? []).filter((n) => n.title.toLowerCase().includes(query.trim().toLowerCase()))
  const mutationError = create.error ?? update.error ?? remove.error

  return (
    <div className="flex h-full flex-col">
      <TopBar>
        <label className="relative ml-auto w-full max-w-sm">
          <span className="sr-only">Buscar cuadernos</span>
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-ink-muted" aria-hidden />
          <input type="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Buscar cuadernos" className="w-full rounded-full border border-line bg-canvas py-1.5 pl-9 pr-3 text-sm" />
        </label>
      </TopBar>
      <main className="mx-auto w-full max-w-6xl flex-1 overflow-y-auto p-6">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-3xl">Mis cuadernos</h1>
          <Button variant="primary" onClick={() => setEditing({ mode: 'create' })}>
            <Plus className="size-4" aria-hidden /> Nuevo cuaderno
          </Button>
        </div>
        {mutationError && <p role="alert" className="mb-4 text-sm text-danger">{mutationError.message}</p>}

        {isPending ? (
          <p role="status" className="py-12 text-center text-ink-muted">Cargando cuadernos…</p>
        ) : error ? (
          <div role="alert" className="flex flex-col items-center gap-3 py-12 text-center">
            <p className="text-danger">{error.message}</p>
            <Button onClick={() => refetch()}>Reintentar</Button>
          </div>
        ) : notebooks.length === 0 ? (
          <div className="flex flex-col items-center gap-3 rounded-card border border-dashed border-line py-20 text-center">
            <BookOpen className="size-10 text-accent" aria-hidden />
            <p className="font-serif text-xl">Aún no tienes cuadernos</p>
            <p className="max-w-sm text-sm text-ink-muted">Crea uno, agrega tus fuentes y conversa con ellas.</p>
            <Button variant="primary" onClick={() => setEditing({ mode: 'create' })}>Crear mi primer cuaderno</Button>
          </div>
        ) : visible.length === 0 ? (
          <p className="py-12 text-center text-ink-muted">Ningún cuaderno coincide con «{query}».</p>
        ) : (
          <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {visible.map((n) => (
              <NotebookCard key={n.id} notebook={n} onRename={() => setEditing({ mode: 'rename', notebook: n })} onDelete={() => setDeleting(n)} />
            ))}
          </ul>
        )}
      </main>

      {editing && (
        <NotebookFormDialog
          key={editing.mode === 'rename' ? editing.notebook.id : 'new'}
          open
          mode={editing.mode}
          initial={editing.mode === 'rename' ? { title: editing.notebook.title, description: editing.notebook.description ?? '' } : undefined}
          onClose={() => setEditing(null)}
          onSubmit={(v) => {
            if (editing.mode === 'create') create.mutate(v, { onSuccess: (nb) => navigate(`/notebooks/${nb.id}`) })
            else update.mutate({ id: editing.notebook.id, body: v })
          }}
        />
      )}
      <ConfirmDialog
        open={!!deleting}
        title="Eliminar cuaderno"
        message={`Se eliminará «${deleting?.title}» con todas sus fuentes y conversaciones. Esta acción no se puede deshacer.`}
        confirmLabel="Eliminar"
        onConfirm={() => deleting && remove.mutate(deleting.id)}
        onClose={() => setDeleting(null)}
      />
    </div>
  )
}
