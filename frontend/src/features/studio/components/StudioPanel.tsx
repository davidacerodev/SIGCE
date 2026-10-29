import { BrainCircuit, FileQuestion, GraduationCap, Layers, ListChecks, ScrollText, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { formatDate } from '@/lib/format'
import { useArtifacts, useStudioMutations } from '../hooks/useStudio'
import type { Artifact, ArtifactType } from '../types'
import { ArtifactViewer } from './ArtifactViewer'

const TOOLS = [
  { type: 'summary', label: 'Resumen', icon: ScrollText },
  { type: 'faq', label: 'Preguntas frecuentes', icon: FileQuestion },
  { type: 'study_guide', label: 'Guía de estudio', icon: GraduationCap },
  { type: 'flashcards', label: 'Tarjetas de memoria', icon: Layers },
  { type: 'quiz', label: 'Cuestionario', icon: ListChecks },
  { type: 'mind_map', label: 'Mapa mental', icon: BrainCircuit },
] as const satisfies readonly { type: ArtifactType; label: string; icon: unknown }[]

export function StudioPanel({ notebookId, selectedIds }: { notebookId: string; selectedIds: string[] }) {
  const artifacts = useArtifacts(notebookId)
  const { create, remove } = useStudioMutations(notebookId)
  const [open, setOpen] = useState<Artifact | null>(null)
  const disabled = selectedIds.length === 0 || create.isPending

  return (
    <section aria-label="Studio" className="flex h-full flex-col bg-surface">
      <header className="border-b border-line p-3"><h2 className="text-lg">Studio</h2></header>
      <div className="flex-1 overflow-y-auto p-3">
        <p className="mb-3 text-sm text-ink-muted">
          {selectedIds.length === 0 ? 'Selecciona al menos una fuente lista para generar recursos.' : 'Sin IA conectada, los recursos son extractos de tus fuentes (demostración).'}
        </p>
        <ul className="grid grid-cols-2 gap-2">
          {TOOLS.map(({ type, label, icon: Icon }) => (
            <li key={type}>
              <button
                disabled={disabled}
                onClick={() => create.mutate({ type, sourceIds: selectedIds }, { onSuccess: setOpen })}
                className="flex h-full w-full flex-col items-start gap-2 rounded-card border border-line p-3 text-left text-sm hover:bg-accent-soft disabled:cursor-not-allowed disabled:opacity-60"
              >
                <Icon className="size-5 text-note" aria-hidden />
                {label}
              </button>
            </li>
          ))}
        </ul>
        {create.isPending && <p role="status" className="mt-3 text-sm text-ink-muted">Generando…</p>}
        {create.error && <p role="alert" className="mt-3 text-sm text-danger">{create.error.message}</p>}

        {artifacts.error && <p role="alert" className="mt-4 text-sm text-danger">{artifacts.error.message}</p>}
        {!!artifacts.data?.length && (
          <>
            <h3 className="mb-2 mt-5 text-base">Generados</h3>
            <ul className="space-y-1">
              {artifacts.data.map((a) => (
                <li key={a.id} className="flex items-center gap-2 rounded-md hover:bg-accent-soft">
                  <button onClick={() => setOpen(a)} className="flex min-w-0 flex-1 flex-col p-2 text-left text-sm">
                    <span className="truncate">{a.title}</span>
                    <span className="text-xs text-ink-muted">{formatDate(a.created_at)}{a.status === 'failed' ? ' · Error' : ''}</span>
                  </button>
                  <button aria-label={`Eliminar ${a.title}`} onClick={() => remove.mutate(a.id)} className="rounded p-1.5 text-ink-muted hover:text-danger">
                    <Trash2 className="size-4" aria-hidden />
                  </button>
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
      <ArtifactViewer artifact={open} onClose={() => setOpen(null)} />
    </section>
  )
}
