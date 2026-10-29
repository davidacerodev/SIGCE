import { SendHorizonal } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/Button'
import { useMessages, useSendMessage } from '../hooks/useChat'
import type { Message } from '../types'

function Sources({ message }: { message: Message }) {
  const names = [...new Set((message.citations ?? []).map((c) => c.source_name))]
  if (names.length === 0) return null
  return <p className="mt-1 text-xs text-ink-muted">Fuentes: {names.join(', ')}</p>
}

interface Props {
  notebookId: string
  selectedIds: string[]
  hasSources: boolean
}

export function ChatPanel({ notebookId, selectedIds, hasSources }: Props) {
  const messages = useMessages(notebookId)
  const send = useSendMessage(notebookId)
  const [draft, setDraft] = useState('')
  const endRef = useRef<HTMLDivElement>(null)
  const canSend = draft.trim() !== '' && selectedIds.length > 0 && !send.isPending
  const list = messages.data ?? []

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: 'end' })
  }, [list.length, send.isPending])

  const submit = () => {
    if (!canSend) return
    const message = draft.trim()
    send.mutate({ message, sourceIds: selectedIds }, { onSuccess: () => setDraft('') })
  }

  return (
    <section aria-label="Chat" className="flex h-full flex-col bg-canvas">
      <header className="border-b border-line bg-surface p-3"><h2 className="text-lg">Chat</h2></header>
      <div className="flex-1 space-y-3 overflow-y-auto p-4" aria-live="polite">
        {messages.error && <p role="alert" className="text-sm text-danger">{messages.error.message}</p>}
        {!messages.isPending && list.length === 0 && (
          <p className="mt-8 text-center text-sm text-ink-muted">
            {hasSources ? 'Haz una pregunta sobre tus fuentes seleccionadas.' : 'Agrega y selecciona fuentes para poder preguntar.'}
          </p>
        )}
        {list.map((m) => (
          <div key={m.id} className={m.role === 'user' ? 'flex justify-end' : 'flex'}>
            <div className={`max-w-[85%] rounded-card px-3 py-2 text-sm ${m.role === 'user' ? 'bg-accent text-white' : 'border border-line bg-surface'}`}>
              <p className="whitespace-pre-wrap">{m.content}</p>
              <Sources message={m} />
            </div>
          </div>
        ))}
        {send.isPending && <p role="status" className="text-sm text-ink-muted">Consultando las fuentes…</p>}
        {send.error && <p role="alert" className="text-sm text-danger">{send.error.message}</p>}
        <div ref={endRef} />
      </div>
      <div className="border-t border-line bg-surface p-3">
        <div className="flex items-end gap-2">
          <textarea
            value={draft}
            rows={2}
            maxLength={4000}
            aria-label="Mensaje"
            placeholder={selectedIds.length ? 'Pregunta sobre tus fuentes…' : 'Selecciona al menos una fuente lista'}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submit() }
            }}
            className="flex-1 resize-none rounded-md border border-line bg-white px-3 py-2 text-sm"
          />
          <Button variant="primary" aria-label="Enviar" disabled={!canSend} onClick={submit}><SendHorizonal className="size-4" aria-hidden /></Button>
        </div>
        <p className="mt-1 text-xs text-ink-muted">
          {selectedIds.length} {selectedIds.length === 1 ? 'fuente seleccionada' : 'fuentes seleccionadas'} · Enter envía, Shift+Enter salto de línea
        </p>
      </div>
    </section>
  )
}
