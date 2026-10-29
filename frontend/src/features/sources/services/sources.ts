import { apiRequest } from '@/services/api/client'
import type { Source } from '../types'

const base = (nb: string) => `/notebooks/${nb}/sources`

export const listSources = (nb: string) => apiRequest<Source[]>(base(nb))
export const addTextSource = (nb: string, name: string, content: string) =>
  apiRequest<Source>(`${base(nb)}/text`, { method: 'POST', body: { name, content } })
export const uploadSource = (nb: string, file: File) => {
  const form = new FormData()
  form.append('file', file)
  return apiRequest<Source>(`${base(nb)}/upload`, { method: 'POST', body: form })
}
export const deleteSource = (nb: string, id: string) => apiRequest<void>(`${base(nb)}/${id}`, { method: 'DELETE' })
