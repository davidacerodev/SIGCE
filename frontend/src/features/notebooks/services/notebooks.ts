import { apiRequest } from '@/services/api/client'
import type { Notebook, NotebookInput } from '../types'

export const listNotebooks = () => apiRequest<Notebook[]>('/notebooks?limit=100')
export const getNotebook = (id: string) => apiRequest<Notebook>(`/notebooks/${id}`)
export const createNotebook = (body: NotebookInput) => apiRequest<Notebook>('/notebooks', { method: 'POST', body: { ...body } })
export const updateNotebook = (id: string, body: NotebookInput) => apiRequest<Notebook>(`/notebooks/${id}`, { method: 'PATCH', body: { ...body } })
export const deleteNotebook = (id: string) => apiRequest<void>(`/notebooks/${id}`, { method: 'DELETE' })
