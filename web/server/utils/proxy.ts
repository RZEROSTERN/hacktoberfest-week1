import type { H3Event } from 'h3'

export function proxyToApi(event: H3Event) {
  const { apiBase, accessCode } = useRuntimeConfig(event)
  const url = getRequestURL(event)
  const target = `${withScheme(apiBase)}${url.pathname.replace(/^\/api/, '')}${url.search}`
  return proxyRequest(event, target, { headers: { 'X-Access-Code': accessCode } })
}

/** Render's private network gives `host:port` without a scheme. */
export function withScheme(base: string): string {
  return /^https?:\/\//.test(base) ? base.replace(/\/$/, '') : `http://${base}`
}
