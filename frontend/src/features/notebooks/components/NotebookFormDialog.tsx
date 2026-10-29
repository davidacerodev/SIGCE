import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Dialog } from '@/components/ui/Dialog'

interface Props {
  open: boolean
  mode: 'create' | 'rename'
  initial?: { title: string; description: string }
  onSubmit: (values: { title: string; description: string }) => void
  onClose: () => void
}

export function NotebookFormDialog({ open, mode, initial, onSubmit, onClose }: Props) {
  const [title, setTitle] = useState(initial?.title ?? '')
  const [description, setDescription] = useState(initial?.description ?? '')
  const trimmed = title.trim()

  const submit = () => {
    if (!trimmed) return
    onSubmit({ title: trimmed, description: description.trim() })
    onClose()
  }

  return (
    <Dialog open={open} title={mode === 'create' ? 'Nuevo cuaderno' : 'Editar cuaderno'} onClose={onClose}>
      <label className="flex flex-col gap-1 text-sm">
        Título
        <input
          autoFocus
          value={title}
          maxLength={200}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submit()}
          className="rounded-md border border-line bg-white px-3 py-2"
        />
      </label>
      <label className="flex flex-col gap-1 text-sm">
        Descripción (opcional)
        <textarea
          value={description}
          maxLength={500}
          rows={3}
          onChange={(e) => setDescription(e.target.value)}
          className="rounded-md border border-line bg-white px-3 py-2"
        />
      </label>
      <div className="flex justify-end gap-2">
        <Button onClick={onClose}>Cancelar</Button>
        <Button variant="primary" disabled={!trimmed} onClick={submit}>
          {mode === 'create' ? 'Crear' : 'Guardar'}
        </Button>
      </div>
    </Dialog>
  )
}
