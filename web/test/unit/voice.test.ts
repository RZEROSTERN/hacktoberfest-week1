import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import Ask from '~/pages/preguntar.vue'

describe('Voice question page', () => {
  it('starts idle with one big button to start speaking', async () => {
    const wrapper = await mountSuspended(Ask)
    expect(wrapper.text()).toContain('Pregúnteme con su voz')
    const buttons = wrapper.findAll('button.big-button')
    expect(buttons).toHaveLength(1)
    expect(buttons[0]!.text()).toContain('Empezar a hablar')
  })
})
