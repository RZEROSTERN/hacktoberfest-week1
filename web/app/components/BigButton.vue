<script setup lang="ts">
withDefaults(defineProps<{ icon?: string, variant?: 'primary' | 'secondary', to?: string }>(), {
  icon: undefined,
  variant: 'primary',
  to: undefined
})
defineEmits<{ click: [] }>()
</script>

<template>
  <NuxtLink
    v-if="to"
    :to="to"
    class="big-button"
    :class="variant"
  >
    <span
      v-if="icon"
      class="icon"
      aria-hidden="true"
    >{{ icon }}</span>
    <slot />
  </NuxtLink>
  <button
    v-else
    type="button"
    class="big-button"
    :class="variant"
    @click="$emit('click')"
  >
    <span
      v-if="icon"
      class="icon"
      aria-hidden="true"
    >{{ icon }}</span>
    <slot />
  </button>
</template>
