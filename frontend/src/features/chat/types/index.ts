export interface Citation {
  index: number
  source_id: string
  source_name: string
  position: number
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations: Citation[] | null
  created_at: string
}
