import { describe, expect, it } from 'vitest'
import { splitHistory } from '~/composables/useHistory'
import { daysUntil } from '~/utils/format'
import type { DocumentResult } from '~~/shared/types'

function doc(id: number, deadline: string | null): DocumentResult {
  return {
    id, created_at: '2026-10-01T10:00:00Z', document_type: `Doc ${id}`, issuer: null,
    deadline, amount_due: null, required_actions: [], is_suspicious: false,
    fraud_reason: null, confidence: 'high', explanation: ''
  }
}

const today = new Date(2026, 9, 4) // Oct 4, 2026 local

describe('daysUntil', () => {
  it('counts whole calendar days', () => {
    expect(daysUntil('2026-10-04', today)).toBe(0)
    expect(daysUntil('2026-10-05', today)).toBe(1)
    expect(daysUntil('2026-10-01', today)).toBe(-3)
  })
})

describe('splitHistory', () => {
  it('lists only future or today deadlines, soonest first, and keeps all documents', () => {
    const documents = [doc(1, '2026-10-20'), doc(2, null), doc(3, '2026-10-01'), doc(4, '2026-10-04')]
    const { upcoming, all } = splitHistory(documents, today)
    expect(upcoming.map(d => [d.id, d.daysLeft])).toEqual([[4, 0], [1, 16]])
    expect(all).toHaveLength(4)
  })
})
