import { timingSafeEqual } from 'node:crypto'

export const ACCESS_COOKIE = 'family_access'

export function isValidCode(given: string | undefined, expected: string): boolean {
  if (!expected || !given) return false
  const a = Buffer.from(given)
  const b = Buffer.from(expected)
  return a.length === b.length && timingSafeEqual(a, b)
}

// Reachable without the family cookie: the login page itself and the static files it needs.
// `/_i18n` serves the UI translations, so switching language works before anyone has logged in.
const PUBLIC_PREFIXES = ['/acceso', '/api/login', '/_nuxt', '/__nuxt', '/_i18n', '/favicon', '/icons', '/manifest', '/sw.js', '/workbox', '/robots.txt']

export function isPublicPath(path: string): boolean {
  return PUBLIC_PREFIXES.some(prefix => path.startsWith(prefix))
}
