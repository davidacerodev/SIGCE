import { Button } from '@/components/ui/Button'
import { Dialog } from '@/components/ui/Dialog'
import type { Artifact } from '../types'

export function ArtifactViewer({ artifact, onClose }: { artifact: Artifact | null; onClose: () => void }) {
  return (
    <Dialog open={!!artifact} title={artifact?.title ?? ''} onClose={onClose}>
      {artifact?.status === 'failed' && <p role="alert" className="text-sm text-danger">{artifact.error_message}</p>}
      {artifact?.content?.demo && <p className="rounded-md bg-accent-soft p-2 text-sm">{artifact.content.notice}</p>}
      <ul className="max-h-80 space-y-3 overflow-y-auto text-sm">
        {artifact?.content?.excerpts?.map((e, i) => (
          <li key={i} className="border-l-2 border-note pl-3">
            <p className="whitespace-pre-wrap">{e.text}</p>
            <p className="mt-1 text-xs text-ink-muted">{e.source_name} · fragmento {e.position + 1}</p>
          </li>
        ))}
      </ul>
      <div className="flex justify-end"><Button onClick={onClose}>Cerrar</Button></div>
    </Dialog>
  )
}
