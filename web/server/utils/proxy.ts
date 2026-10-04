import type { H3Event } from 'h3'

export function proxyToApi(event: H3Event) {
  const { apiBase, accessCode } = useRuntimeConfig(event)
  const url = getRequestURL(event)
  const target = `${apiBase}${url.pathname.replace(/^\/api/, '')}${url.search}`
  return proxyRequest(event, target, { headers: { 'X-Access-Code': accessCode } })
}
