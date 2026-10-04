import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import AnalysisResult from '~/components/AnalysisResult.vue'
import type { DocumentResult } from '~~/shared/types'

const base: DocumentResult = {
  id: 3,
  created_at: '2026-10-04T10:00:00Z',
  document_type: 'Recibo de luz',
  issuer: 'CFE',
  deadline: '2026-10-18',
  amount_due: 1482.5,
  required_actions: ['Pagar en el OXXO.'],
  is_suspicious: false,
  fraud_reason: null,
  confidence: 'high',
  explanation: 'Es su recibo de luz.'
}

async function render(overrides: Partial<DocumentResult> = {}, reminderUrl?: string) {
  return mountSuspended(AnalysisResult, { props: { result: { ...base, ...overrides }, reminderUrl } })
}

describe('AnalysisResult', () => {
  it('shows type, issuer, formatted amount, steps and a calendar link', async () => {
    const wrapper = await render({}, '/api/documents/3/reminder.ics')
    const text = wrapper.text()
    expect(text).toContain('Recibo de luz')
    expect(text).toContain('CFE')
    expect(text).toContain('$1,482.50')
    expect(text).toContain('Pagar en el OXXO.')
    expect(wrapper.find('a[download]').attributes('href')).toBe('/api/documents/3/reminder.ics')
  })

  it('hides the calendar link when there is no deadline', async () => {
    const wrapper = await render({ deadline: null }, '/api/documents/3/reminder.ics')
    expect(wrapper.find('a[download]').exists()).toBe(false)
    expect(wrapper.text()).toContain('No encontré una fecha límite.')
  })

  it('shows a prominent fraud warning', async () => {
    const wrapper = await render({ is_suspicious: true, fraud_reason: 'Le piden su NIP.' })
    const alert = wrapper.find('[role="alert"]')
    expect(alert.text()).toContain('fraude')
    expect(alert.text()).toContain('Le piden su NIP.')
  })

  it('asks for another photo instead of showing fields when confidence is low', async () => {
    const wrapper = await render({ confidence: 'low', explanation: 'Tome otra foto.' })
    expect(wrapper.text()).toContain('No pude leer bien su papel')
    expect(wrapper.text()).not.toContain('¿Cuándo y cuánto?')
  })

  it('always shows the no-advice disclaimer', async () => {
    const wrapper = await render()
    expect(wrapper.text()).toContain('no es asesoría legal ni financiera')
  })
})
