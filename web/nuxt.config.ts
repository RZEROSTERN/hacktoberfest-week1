// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  modules: ['@nuxt/eslint', '@nuxtjs/i18n', '@vite-pwa/nuxt'],
  typescript: { strict: true },
  css: ['~/assets/main.css'],
  app: {
    head: {
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'theme-color', content: '#0b4f9c' }
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/icons/icon.svg' },
        { rel: 'apple-touch-icon', href: '/icons/apple-touch-icon.png' }
      ]
    }
  },
  pwa: {
    registerType: 'autoUpdate',
    manifest: {
      name: 'Traductor de Papeles',
      short_name: 'Mis Papeles',
      description: 'Le explico sus papeles en palabras sencillas.',
      lang: 'es-MX',
      start_url: '/',
      display: 'standalone',
      orientation: 'portrait',
      background_color: '#ffffff',
      theme_color: '#0b4f9c',
      icons: [
        { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
        { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
        { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' }
      ]
    },
    workbox: {
      // Pages are server-rendered behind the access cookie: cache static assets only,
      // never documents or API responses.
      globPatterns: ['**/*.{js,css,png,svg,ico}'],
      navigateFallback: null
    }
  },
  // Spanish is the default; English is opt-in. `no_prefix` keeps every URL the same in both
  // languages (the access middleware and the PWA rely on them), so the choice lives in a cookie.
  i18n: {
    strategy: 'no_prefix',
    defaultLocale: 'es',
    locales: [
      { code: 'es', language: 'es-MX', name: 'Español', file: 'es.json' },
      { code: 'en', language: 'en-US', name: 'English', file: 'en.json' }
    ],
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'i18n_redirected',
      fallbackLocale: 'es'
    }
  },
  // Overridden at runtime by NUXT_* env vars. Server-only keys never reach the browser.
  runtimeConfig: {
    apiBase: 'http://localhost:8000',
    accessCode: ''
  }
})