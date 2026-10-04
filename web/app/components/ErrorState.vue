<script setup lang="ts">
defineProps<{ title: string, message: string }>()
</script>

<template>
  <div
    class="state error"
    role="alert"
  >
    <p class="state-title">
      {{ title }}
    </p>
    <p class="state-hint">
      {{ message }}
    </p>
    <slot />
  </div>
</template>
