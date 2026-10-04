import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import App from '~/app.vue'

describe('App', () => {
  it('renders the welcome page', async () => {
    const wrapper = await mountSuspended(App)
    expect(wrapper.html()).toContain('Nuxt')
  })
})
