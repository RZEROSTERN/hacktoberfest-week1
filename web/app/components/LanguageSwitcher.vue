<script setup lang="ts">
// Two big buttons, each named in its own language, so nobody has to find a menu or read
// the current language to change it. setLocale also remembers the choice in a cookie.
const { t, locale, locales, setLocale } = useI18n()
</script>

<template>
  <div
    class="language-switcher"
    role="group"
    :aria-label="t('language.label')"
  >
    <button
      v-for="item in locales"
      :key="item.code"
      type="button"
      class="language-button"
      :class="{ active: item.code === locale }"
      :lang="item.code"
      :aria-pressed="item.code === locale"
      @click="setLocale(item.code)"
    >
      {{ item.name }}
    </button>
  </div>
</template>
