import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as api from '../services/auth'

const ME_KEY = ['me']

export const useMe = () => useQuery({ queryKey: ME_KEY, queryFn: api.getMe, retry: false, staleTime: Infinity })

export function useLogin() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (v: { email: string; password: string }) => api.login(v.email, v.password),
    onSuccess: (user) => qc.setQueryData(ME_KEY, user),
  })
}

export function useRegister() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (v: { email: string; password: string; display_name: string }) => {
      await api.register(v)
      return api.login(v.email, v.password)
    },
    onSuccess: (user) => qc.setQueryData(ME_KEY, user),
  })
}

export function useLogout() {
  const qc = useQueryClient()
  return useMutation({ mutationFn: api.logout, onSuccess: () => qc.clear() })
}
