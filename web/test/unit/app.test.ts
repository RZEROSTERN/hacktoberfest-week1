import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import App from '~/app.vue'

describe('App', () => {
  it('renders the app name in the header', async () => {
    const wrapper = await mountSuspended(App)
    expect(wrapper.text()).toContain('Traductor de Papeles')
  })
})
