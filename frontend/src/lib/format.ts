const dateFormat = new Intl.DateTimeFormat('es', { day: 'numeric', month: 'short', year: 'numeric' })
export const formatDate = (iso: string) => dateFormat.format(new Date(iso))
