import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as api from '../services/chat'

export const useMessages = (nb: string) => useQuery({ queryKey: ['messages', nb], queryFn: () => api.listMessages(nb) })

export function useSendMessage(nb: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (v: { message: string; sourceIds: string[] }) => api.sendMessage(nb, v.message, v.sourceIds),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['messages', nb] }),
  })
}
