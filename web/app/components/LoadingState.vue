<script setup lang="ts">
defineProps<{ title: string, hint?: string }>()
</script>

<template>
  <div
    class="state"
    role="status"
    aria-live="polite"
  >
    <div
      class="spinner"
      aria-hidden="true"
    />
    <p class="state-title">
      {{ title }}
    </p>
    <p
      v-if="hint"
      class="state-hint"
    >
      {{ hint }}
    </p>
  </div>
</template>
