<script setup lang="ts">
import { t } from '~/utils/strings'
</script>

<template>
  <div class="app">
    <NuxtPwaManifest />
    <header class="app-header">
      <NuxtLink
        to="/"
        class="app-title"
      >
        {{ t.appName }}
      </NuxtLink>
    </header>
    <main class="app-main">
      <NuxtPage />
    </main>
  </div>
</template>
