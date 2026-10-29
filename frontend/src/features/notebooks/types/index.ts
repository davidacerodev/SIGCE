export interface Notebook {
  id: string
  title: string
  description: string | null
  created_at: string
  updated_at: string
  source_count: number
}

export interface NotebookInput {
  title: string
  description: string
}
