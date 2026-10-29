import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as api from '../services/notebooks'
import type { NotebookInput } from '../types'

export const useNotebooks = () => useQuery({ queryKey: ['notebooks'], queryFn: api.listNotebooks })
export const useNotebook = (id: string) => useQuery({ queryKey: ['notebooks', id], queryFn: () => api.getNotebook(id), retry: false })

export function useNotebookMutations() {
  const qc = useQueryClient()
  const refresh = () => qc.invalidateQueries({ queryKey: ['notebooks'] })
  return {
    create: useMutation({ mutationFn: (b: NotebookInput) => api.createNotebook(b), onSuccess: refresh }),
    update: useMutation({ mutationFn: (v: { id: string; body: NotebookInput }) => api.updateNotebook(v.id, v.body), onSuccess: refresh }),
    remove: useMutation({ mutationFn: (id: string) => api.deleteNotebook(id), onSuccess: refresh }),
  }
}
