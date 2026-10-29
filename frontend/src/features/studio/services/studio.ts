import { apiRequest } from '@/services/api/client'
import type { Artifact, ArtifactType } from '../types'

const base = (nb: string) => `/notebooks/${nb}/artifacts`

export const listArtifacts = (nb: string) => apiRequest<Artifact[]>(base(nb))
export const createArtifact = (nb: string, type: ArtifactType, sourceIds: string[]) =>
  apiRequest<Artifact>(base(nb), { method: 'POST', body: { type, source_ids: sourceIds } })
export const deleteArtifact = (nb: string, id: string) => apiRequest<void>(`${base(nb)}/${id}`, { method: 'DELETE' })
