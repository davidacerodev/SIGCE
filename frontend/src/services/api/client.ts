import { API_BASE_URL } from '@/lib/env'

export class ApiError extends Error {
  status: number
  code: string

  constructor(status: number, code: string, message: string) {
    super(message)
    this.status = status
    this.code = code
  }
}

type Body = FormData | Record<string, unknown>

export async function apiRequest<T>(path: string, options: { method?: string; body?: Body } = {}): Promise<T> {
  const { method = 'GET', body } = options
  const isForm = body instanceof FormData
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      credentials: 'include', // la sesión viaja en una cookie httpOnly
      headers: body && !isForm ? { 'Content-Type': 'application/json' } : undefined,
      body: body === undefined ? undefined : isForm ? body : JSON.stringify(body),
    })
  } catch {
    throw new ApiError(0, 'network_error', 'No se pudo conectar con el servidor.')
  }

  if (!response.ok) {
    const data = await response.json().catch(() => null)
    throw new ApiError(
      response.status,
      data?.error?.code ?? 'unknown_error',
      data?.error?.message ?? 'Ocurrió un error inesperado.',
    )
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}
