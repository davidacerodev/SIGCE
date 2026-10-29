import { ArrowLeft } from 'lucide-react'
import { useState } from 'react'
import { Group, Panel, Separator } from 'react-resizable-panels'
import { Link, useParams } from 'react-router-dom'
import { TopBar } from '@/components/layout/TopBar'
import { useMediaQuery } from '@/hooks/useMediaQuery'
import { ChatPanel } from '@/features/chat/components/ChatPanel'
import { SourcesPanel } from '@/features/sources/components/SourcesPanel'
import { useSourceSelection, useSources } from '@/features/sources/hooks/useSources'
import { StudioPanel } from '@/features/studio/components/StudioPanel'
import { useNotebook } from '../hooks/useNotebooks'

const TABS = ['Fuentes', 'Chat', 'Studio'] as const
type Tab = (typeof TABS)[number]
const SEPARATOR = 'w-px bg-line transition-colors hover:bg-accent data-[separator=active]:bg-accent'

export function WorkspacePage() {
  const { id = '' } = useParams()
  const notebook = useNotebook(id)
  const sources = useSources(id)
  const list = sources.data ?? []
  const { selectedIds, isSelected, toggle } = useSourceSelection(list)
  const isDesktop = useMediaQuery('(min-width: 1024px)')
  const [tab, setTab] = useState<Tab>('Chat')

  if (notebook.isPending) return <p role="status" className="p-8 text-center text-ink-muted">Cargando cuaderno…</p>
  if (!notebook.data) {
    return (
      <main className="flex h-full flex-col items-center justify-center gap-3 p-6 text-center">
        <h1 className="text-2xl">Cuaderno no encontrado</h1>
        <p className="text-sm text-ink-muted">{notebook.error?.message}</p>
        <Link to="/" className="text-accent underline">Volver a mis cuadernos</Link>
      </main>
    )
  }

  const sourcesPanel = (
    <SourcesPanel notebookId={id} sources={list} loading={sources.isPending} error={sources.error} isSelected={isSelected} onToggle={toggle} />
  )
  const chatPanel = <ChatPanel notebookId={id} selectedIds={selectedIds} hasSources={list.length > 0} />
  const studioPanel = <StudioPanel notebookId={id} selectedIds={selectedIds} />

  return (
    <div className="flex h-full flex-col">
      <TopBar>
        <Link to="/" aria-label="Volver a mis cuadernos" className="rounded p-1.5 hover:bg-accent-soft"><ArrowLeft className="size-4" aria-hidden /></Link>
        <h1 className="truncate text-lg">{notebook.data.title}</h1>
      </TopBar>
      {isDesktop ? (
        <Group orientation="horizontal" className="flex-1">
          <Panel defaultSize="24%" minSize="16%">{sourcesPanel}</Panel>
          <Separator className={SEPARATOR} />
          <Panel defaultSize="48%" minSize="30%">{chatPanel}</Panel>
          <Separator className={SEPARATOR} />
          <Panel defaultSize="28%" minSize="16%">{studioPanel}</Panel>
        </Group>
      ) : (
        <>
          <div role="tablist" aria-label="Paneles del cuaderno" className="flex border-b border-line bg-surface">
            {TABS.map((t) => (
              <button key={t} role="tab" aria-selected={tab === t} onClick={() => setTab(t)} className={`flex-1 border-b-2 py-2.5 text-sm font-medium ${tab === t ? 'border-accent text-accent' : 'border-transparent text-ink-muted'}`}>
                {t}
              </button>
            ))}
          </div>
          <div className="min-h-0 flex-1">
            {tab === 'Fuentes' && sourcesPanel}
            {tab === 'Chat' && chatPanel}
            {tab === 'Studio' && studioPanel}
          </div>
        </>
      )}
    </div>
  )
}
