import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import * as api from '../services/sources'
import type { Source } from '../types'

const IN_PROGRESS = new Set(['pending', 'processing'])

export function useSources(notebookId: string) {
  return useQuery({
    queryKey: ['sources', notebookId],
    queryFn: () => api.listSources(notebookId),
    // Mientras haya fuentes procesándose se consulta su estado cada 1,5 s.
    refetchInterval: (q) => (q.state.data?.some((s) => IN_PROGRESS.has(s.status)) ? 1500 : false),
  })
}

export function useSourceMutations(notebookId: string) {
  const qc = useQueryClient()
  const refresh = () => {
    qc.invalidateQueries({ queryKey: ['sources', notebookId] })
    qc.invalidateQueries({ queryKey: ['notebooks'] })
  }
  return {
    addText: useMutation({ mutationFn: (v: { name: string; content: string }) => api.addTextSource(notebookId, v.name, v.content), onSuccess: refresh }),
    upload: useMutation({ mutationFn: (file: File) => api.uploadSource(notebookId, file), onSuccess: refresh }),
    remove: useMutation({ mutationFn: (id: string) => api.deleteSource(notebookId, id), onSuccess: refresh }),
  }
}

/** Las fuentes listas están seleccionadas por defecto; el usuario puede excluirlas. */
export function useSourceSelection(sources: Source[]) {
  const [excluded, setExcluded] = useState<Set<string>>(new Set())
  const isSelected = (s: Source) => s.status === 'ready' && !excluded.has(s.id)
  const toggle = (id: string) =>
    setExcluded((prev) => {
      const next = new Set(prev)
      if (!next.delete(id)) next.add(id)
      return next
    })
  return { selectedIds: sources.filter(isSelected).map((s) => s.id), isSelected, toggle }
}
