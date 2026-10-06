<script setup lang="ts">
const { t, localeProperties } = useI18n()

// The module does not set these itself; screen readers need the right language to pronounce it.
useHead({
  htmlAttrs: { lang: () => localeProperties.value.language },
  title: () => t('appName')
})
</script>

<template>
  <div class="app">
    <NuxtPwaManifest />
    <header class="app-header">
      <NuxtLink
        to="/"
        class="app-title"
      >
        {{ t('appName') }}
      </NuxtLink>
      <LanguageSwitcher />
    </header>
    <main class="app-main">
      <NuxtPage />
    </main>
  </div>
</template>
