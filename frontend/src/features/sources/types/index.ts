export type SourceStatus = 'pending' | 'processing' | 'ready' | 'failed'

export interface Source {
  id: string
  notebook_id: string
  type: 'file' | 'text' | 'url'
  name: string
  mime_type: string | null
  size_bytes: number | null
  status: SourceStatus
  error_message: string | null
  created_at: string
}
