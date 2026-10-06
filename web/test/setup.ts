import { beforeEach } from 'vitest'
import { useNuxtApp } from '#app'

// happy-dom reports navigator.language as "en-US", so browser-language detection would start
// every test in English. Start each one in the default language (Spanish) instead.
beforeEach(async () => {
  await useNuxtApp().$i18n.setLocale('es')
})
