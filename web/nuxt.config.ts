// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxt/eslint'],
  typescript: { strict: true },
  app: {
    head: {
      htmlAttrs: { lang: 'es-MX' },
      title: 'Traductor de Papeles',
      meta: [{ name: 'viewport', content: 'width=device-width, initial-scale=1' }]
    }
  },
  // Overridden at runtime by NUXT_* env vars. Server-only keys never reach the browser.
  runtimeConfig: {
    apiBase: 'http://localhost:8000',
    accessCode: ''
  }
})
