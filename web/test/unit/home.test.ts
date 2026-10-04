import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import Home from '~/pages/index.vue'

describe('Home page', () => {
  it('shows the two big primary buttons and a camera input', async () => {
    const wrapper = await mountSuspended(Home)
    expect(wrapper.text()).toContain('Tomar foto')
    expect(wrapper.text()).toContain('Preguntar con voz')
    const input = wrapper.find('input[type="file"]')
    expect(input.attributes('accept')).toBe('image/*')
    expect(input.attributes('capture')).toBe('environment')
  })
})
