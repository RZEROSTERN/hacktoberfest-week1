import { timingSafeEqual } from 'node:crypto'

export const ACCESS_COOKIE = 'family_access'

export function isValidCode(given: string | undefined, expected: string): boolean {
  if (!expected || !given) return false
  const a = Buffer.from(given)
  const b = Buffer.from(expected)
  return a.length === b.length && timingSafeEqual(a, b)
}
