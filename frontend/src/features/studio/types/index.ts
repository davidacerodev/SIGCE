export type ArtifactType = 'summary' | 'faq' | 'study_guide' | 'flashcards' | 'quiz' | 'mind_map'

export interface Artifact {
  id: string
  type: ArtifactType
  title: string
  status: 'generating' | 'ready' | 'failed'
  content: { demo?: boolean; notice?: string; excerpts?: { source_name: string; position: number; text: string }[] } | null
  error_message: string | null
  created_at: string
}
