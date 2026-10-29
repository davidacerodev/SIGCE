import { afterEach, expect, test, vi } from 'vitest'
import { ApiError, apiRequest } from '@/services/api/client'

afterEach(() => vi.unstubAllGlobals())

test('envía cookies, serializa JSON y devuelve la respuesta', async () => {
  const fetchMock = vi.fn(async () => new Response(JSON.stringify({ ok: 1 }), { status: 200 }))
  vi.stubGlobal('fetch', fetchMock)
  expect(await apiRequest('/x', { method: 'POST', body: { a: 1 } })).toEqual({ ok: 1 })
  const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit]
  expect(url).toBe('/api/x')
  expect(init.credentials).toBe('include')
  expect(init.body).toBe('{"a":1}')
})

test('FormData no fija Content-Type (lo añade el navegador con el boundary)', async () => {
  const fetchMock = vi.fn(async () => new Response('{}', { status: 201 }))
  vi.stubGlobal('fetch', fetchMock)
  const form = new FormData()
  form.append('file', new File(['a'], 'a.txt'))
  await apiRequest('/up', { method: 'POST', body: form })
  const init = (fetchMock.mock.calls[0] as unknown as [string, RequestInit])[1]
  expect(init.headers).toBeUndefined()
  expect(init.body).toBe(form)
})

test('204 devuelve undefined y los errores se traducen a ApiError', async () => {
  vi.stubGlobal('fetch', vi.fn(async () => new Response(null, { status: 204 })))
  expect(await apiRequest('/x', { method: 'DELETE' })).toBeUndefined()

  vi.stubGlobal('fetch', vi.fn(async () => new Response(JSON.stringify({ error: { code: 'conflict', message: 'Duplicada' } }), { status: 409 })))
  await expect(apiRequest('/x')).rejects.toMatchObject({ status: 409, code: 'conflict', message: 'Duplicada' })

  vi.stubGlobal('fetch', vi.fn(async () => { throw new TypeError('offline') }))
  await expect(apiRequest('/x')).rejects.toBeInstanceOf(ApiError)
})
