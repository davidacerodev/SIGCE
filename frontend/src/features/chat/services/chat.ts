import { apiRequest } from '@/services/api/client'
import type { Message } from '../types'

export const listMessages = (nb: string) => apiRequest<Message[]>(`/notebooks/${nb}/messages`)
export const sendMessage = (nb: string, message: string, sourceIds: string[]) =>
  apiRequest<{ user_message: Message; assistant_message: Message }>(`/notebooks/${nb}/chat`, {
    method: 'POST',
    body: { message, source_ids: sourceIds },
  })
