import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Dialog } from '@/components/ui/Dialog'
import { useSourceMutations } from '../hooks/useSources'

type Tab = 'file' | 'text'

export function AddSourceDialog({ notebookId, open, onClose }: { notebookId: string; open: boolean; onClose: () => void }) {
  const { addText, upload } = useSourceMutations(notebookId)
  const [tab, setTab] = useState<Tab>('file')
  const [file, setFile] = useState<File | null>(null)
  const [name, setName] = useState('')
  const [content, setContent] = useState('')

  const mutation = tab === 'file' ? upload : addText
  const valid = tab === 'file' ? !!file : name.trim() !== '' && content.trim() !== ''

  const close = () => {
    upload.reset(); addText.reset(); setFile(null); setName(''); setContent('')
    onClose()
  }
  const submit = () => {
    if (!valid) return
    if (tab === 'file') upload.mutate(file!, { onSuccess: close })
    else addText.mutate({ name: name.trim(), content: content.trim() }, { onSuccess: close })
  }
  const tabClass = (t: Tab) => `flex-1 border-b-2 py-2 text-sm ${tab === t ? 'border-accent text-accent' : 'border-transparent text-ink-muted'}`

  return (
    <Dialog open={open} title="Agregar fuente" onClose={close}>
      <div role="tablist" className="flex border-b border-line">
        <button role="tab" aria-selected={tab === 'file'} className={tabClass('file')} onClick={() => setTab('file')}>Archivo</button>
        <button role="tab" aria-selected={tab === 'text'} className={tabClass('text')} onClick={() => setTab('text')}>Texto</button>
      </div>
      {tab === 'file' ? (
        <label className="flex flex-col gap-1 text-sm">
          Archivo PDF, TXT o Markdown
          <input type="file" accept=".pdf,.txt,.md" onChange={(e) => setFile(e.target.files?.[0] ?? null)} className="rounded-md border border-line bg-white px-3 py-2" />
        </label>
      ) : (
        <>
          <label className="flex flex-col gap-1 text-sm">Nombre
            <input value={name} maxLength={255} onChange={(e) => setName(e.target.value)} className="rounded-md border border-line bg-white px-3 py-2" />
          </label>
          <label className="flex flex-col gap-1 text-sm">Contenido
            <textarea value={content} rows={7} onChange={(e) => setContent(e.target.value)} className="rounded-md border border-line bg-white px-3 py-2" />
          </label>
        </>
      )}
      {mutation.error && <p role="alert" className="text-sm text-danger">{mutation.error.message}</p>}
      <div className="flex justify-end gap-2">
        <Button onClick={close}>Cancelar</Button>
        <Button variant="primary" disabled={!valid || mutation.isPending} onClick={submit}>{mutation.isPending ? 'Enviando…' : 'Agregar'}</Button>
      </div>
    </Dialog>
  )
}
