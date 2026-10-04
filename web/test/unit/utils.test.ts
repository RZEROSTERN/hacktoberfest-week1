import { describe, expect, it } from 'vitest'
import { formatDate, formatMoney } from '~/utils/strings'
import { isValidCode } from '../../server/utils/access'

describe('formatting', () => {
  it('formats MXN amounts', () => {
    expect(formatMoney(2798)).toBe('$2,798.00')
  })

  it('formats calendar dates without timezone shifts', () => {
    expect(formatDate('2026-10-18')).toContain('18 de octubre de 2026')
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
