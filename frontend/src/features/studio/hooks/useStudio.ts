import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as api from '../services/studio'
import type { ArtifactType } from '../types'

export const useArtifacts = (nb: string) => useQuery({ queryKey: ['artifacts', nb], queryFn: () => api.listArtifacts(nb) })

export function useStudioMutations(nb: string) {
  const qc = useQueryClient()
  const refresh = () => qc.invalidateQueries({ queryKey: ['artifacts', nb] })
  return {
    create: useMutation({ mutationFn: (v: { type: ArtifactType; sourceIds: string[] }) => api.createArtifact(nb, v.type, v.sourceIds), onSuccess: refresh }),
    remove: useMutation({ mutationFn: (id: string) => api.deleteArtifact(nb, id), onSuccess: refresh }),
  }
}
