import { Button } from './Button'
import { Dialog } from './Dialog'

interface Props {
  open: boolean
  title: string
  message: string
  confirmLabel: string
  onConfirm: () => void
  onClose: () => void
}

export function ConfirmDialog({ open, title, message, confirmLabel, onConfirm, onClose }: Props) {
  return (
    <Dialog open={open} title={title} onClose={onClose}>
      <p className="text-sm text-ink-muted">{message}</p>
      <div className="flex justify-end gap-2">
        <Button onClick={onClose}>Cancelar</Button>
        <Button variant="danger" onClick={() => { onConfirm(); onClose() }}>{confirmLabel}</Button>
      </div>
    </Dialog>
  )
}
