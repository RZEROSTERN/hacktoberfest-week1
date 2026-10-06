import { describe, expect, it } from 'vitest'
import { formatDate, formatMoney } from '~/utils/format'
import { isPublicPath, isValidCode } from '../../server/utils/access'
import { withScheme } from '../../server/utils/proxy'

describe('formatting', () => {
  it('formats MXN amounts', () => {
    expect(formatMoney(2798, 'es-MX')).toBe('$2,798.00')
  })

  it('marks pesos as MX$ for English readers so they are not read as US dollars', () => {
    expect(formatMoney(2798, 'en-US')).toBe('MX$2,798.00')
  })

  it('formats calendar dates without timezone shifts', () => {
    expect(formatDate('2026-10-18', 'es-MX')).toContain('18 de octubre de 2026')
    expect(formatDate('2026-10-18', 'en-US')).toBe('Sunday, October 18, 2026')
  })
})

describe('isValidCode', () => {
  it('accepts only the exact configured code', () => {
    expect(isValidCode('abc123', 'abc123')).toBe(true)
    expect(isValidCode('abc124', 'abc123')).toBe(false)
    expect(isValidCode('abc', 'abc123')).toBe(false)
    expect(isValidCode(undefined, 'abc123')).toBe(false)
  })

  it('rejects everything when no code is configured', () => {
    expect(isValidCode('', '')).toBe(false)
    expect(isValidCode('anything', '')).toBe(false)
  })
})

describe('withScheme', () => {
  it('adds http:// to a private host:port and keeps full URLs', () => {
    expect(withScheme('paperwork-api:8000')).toBe('http://paperwork-api:8000')
    expect(withScheme('http://localhost:8000/')).toBe('http://localhost:8000')
    expect(withScheme('https://api.example.com')).toBe('https://api.example.com')
  })
})

describe('isPublicPath', () => {
  it('lets the login page, its assets and the UI translations through without the cookie', () => {
    expect(isPublicPath('/acceso')).toBe(true)
    expect(isPublicPath('/api/login')).toBe(true)
    expect(isPublicPath('/_nuxt/entry.js')).toBe(true)
    // Switching language on the login page loads the other language from here.
    expect(isPublicPath('/_i18n/ab12cd/en/messages.json')).toBe(true)
  })

  it('keeps pages and the documents API behind the cookie', () => {
    expect(isPublicPath('/')).toBe(false)
    expect(isPublicPath('/documentos')).toBe(false)
    expect(isPublicPath('/api/documents/1')).toBe(false)
    expect(isPublicPath('/api/questions/voice')).toBe(false)
  })
})
