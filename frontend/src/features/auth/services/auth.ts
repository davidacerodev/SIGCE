import { apiRequest } from '@/services/api/client'

export interface User {
  id: string
  email: string
  display_name: string
}

export const getMe = () => apiRequest<User>('/auth/me')
export const login = (email: string, password: string) => apiRequest<User>('/auth/login', { method: 'POST', body: { email, password } })
export const register = (body: { email: string; password: string; display_name: string }) =>
  apiRequest<User>('/auth/register', { method: 'POST', body })
export const logout = () => apiRequest<void>('/auth/logout', { method: 'POST' })
