import { cleanup, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { RouterProvider, createMemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import { Providers } from '@/app/providers'
import { routes } from '@/app/router'

// La librería de paneles depende de mediciones de layout que jsdom no ofrece; aquí se prueba nuestra lógica.
vi.mock('react-resizable-panels', () => ({
  Group: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Panel: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Separator: () => <hr />,
}))

/** API simulada en memoria: valida el contrato que usa el frontend (rutas, cookie de sesión, formas de respuesta). */
function fakeApi() {
  const now = new Date().toISOString()
  const state = { loggedIn: false, notebooks: [] as Record<string, unknown>[], sources: [] as Record<string, unknown>[], messages: [] as Record<string, unknown>[] }
  const json = (data: unknown, status = 200) => new Response(JSON.stringify(data), { status })
  const fn = vi.fn(async (url: string, init?: RequestInit) => {
    expect(init?.credentials).toBe('include')
    const path = url.replace('/api', '')
    const method = init?.method ?? 'GET'
    const body = typeof init?.body === 'string' ? JSON.parse(init.body) : undefined
    if (path === '/auth/me') return state.loggedIn ? json({ id: 'u1', email: 'a@b.co', display_name: 'Ana' }) : json({ error: { code: 'unauthorized', message: 'Sesión no válida.' } }, 401)
    if (path === '/auth/login') {
      if (body.password !== 'password123') return json({ error: { code: 'unauthorized', message: 'Correo o contraseña incorrectos.' } }, 401)
      state.loggedIn = true
      return json({ id: 'u1', email: body.email, display_name: 'Ana' })
    }
    if (path === '/auth/logout') { state.loggedIn = false; return new Response(null, { status: 204 }) }
    if (path.startsWith('/notebooks?')) return json(state.notebooks)
    if (path === '/notebooks' && method === 'POST') {
      const nb = { id: 'n1', title: body.title, description: body.description, created_at: now, updated_at: now, source_count: 0 }
      state.notebooks.push(nb)
      return json(nb, 201)
    }
    if (path === '/notebooks/n1') return json(state.notebooks[0])
    if (path === '/notebooks/n1/sources') return json(state.sources)
    if (path === '/notebooks/n1/sources/text') {
      const s = { id: 's1', notebook_id: 'n1', type: 'text', name: body.name, mime_type: 'text/plain', size_bytes: 10, status: 'ready', error_message: null, created_at: now }
      state.sources.push(s)
      return json(s, 201)
    }
    if (path === '/notebooks/n1/messages') return json(state.messages)
    if (path === '/notebooks/n1/chat') {
      expect(body.source_ids).toEqual(['s1'])
      const user = { id: 'm1', role: 'user', content: body.message, citations: null, created_at: now }
      const assistant = { id: 'm2', role: 'assistant', content: 'Demostración: fragmentos…', citations: [{ index: 1, source_id: 's1', source_name: 'Notas', position: 0 }], created_at: now }
      state.messages.push(user, assistant)
      return json({ user_message: user, assistant_message: assistant })
    }
    if (path === '/notebooks/n1/artifacts') return json([])
    return json({ error: { code: 'not_found', message: `Ruta no simulada: ${method} ${path}` } }, 404)
  })
  return { fn, state }
}

let api: ReturnType<typeof fakeApi>
beforeEach(() => {
  api = fakeApi()
  vi.stubGlobal('fetch', api.fn)
})
afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

const renderAt = (path: string) =>
  render(
    <Providers>
      <RouterProvider router={createMemoryRouter(routes, { initialEntries: [path] })} />
    </Providers>,
  )

test('sin sesión redirige al login y muestra el error de credenciales', async () => {
  const user = userEvent.setup()
  renderAt('/')
  expect(await screen.findByRole('heading', { name: 'Iniciar sesión' })).toBeTruthy()
  await user.type(screen.getByLabelText('Correo'), 'a@b.co')
  await user.type(screen.getByLabelText('Contraseña'), 'incorrecta1')
  await user.click(screen.getByRole('button', { name: 'Entrar' }))
  expect((await screen.findByRole('alert')).textContent).toContain('incorrectos')
})

test('flujo completo: login, cuaderno, fuente, chat con cita y cierre de sesión', async () => {
  const user = userEvent.setup()
  renderAt('/login')
  await user.type(await screen.findByLabelText('Correo'), 'a@b.co')
  await user.type(screen.getByLabelText('Contraseña'), 'password123')
  await user.click(screen.getByRole('button', { name: 'Entrar' }))

  expect(await screen.findByText('Aún no tienes cuadernos')).toBeTruthy()
  await user.click(screen.getByRole('button', { name: 'Crear mi primer cuaderno' }))
  await user.type(within(screen.getByRole('dialog')).getByLabelText('Título'), 'Biología')
  await user.click(within(screen.getByRole('dialog')).getByRole('button', { name: 'Crear' }))

  // Espacio de trabajo con los tres paneles
  expect(await screen.findByRole('heading', { name: 'Biología', level: 1 })).toBeTruthy()
  for (const name of ['Fuentes', 'Chat', 'Studio']) expect(screen.getByRole('region', { name })).toBeTruthy()
  expect(screen.getByRole('button', { name: 'Enviar' }).hasAttribute('disabled')).toBe(true)

  await user.click(screen.getByRole('button', { name: /Agregar/ }))
  const add = screen.getByRole('dialog')
  await user.click(within(add).getByRole('tab', { name: 'Texto' }))
  await user.type(within(add).getByLabelText('Nombre'), 'Notas')
  await user.type(within(add).getByLabelText('Contenido'), 'La célula es la unidad básica.')
  await user.click(within(add).getByRole('button', { name: 'Agregar' }))
  expect(await screen.findByText('Notas')).toBeTruthy()
  await waitFor(() => expect((screen.getByLabelText('Usar Notas en el chat') as HTMLInputElement).checked).toBe(true))

  await user.type(screen.getByLabelText('Mensaje'), '¿Qué es la célula?{Enter}')
  expect(await screen.findByText(/Demostración: fragmentos/)).toBeTruthy()
  expect(screen.getByText('Fuentes: Notas')).toBeTruthy()

  await user.click(screen.getByRole('button', { name: 'Cerrar sesión' }))
  expect(await screen.findByRole('heading', { name: 'Iniciar sesión' })).toBeTruthy()
  expect(api.state.loggedIn).toBe(false)
})
