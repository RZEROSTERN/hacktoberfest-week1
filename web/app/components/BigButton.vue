<script setup lang="ts">
withDefaults(defineProps<{ icon?: string, variant?: 'primary' | 'secondary', to?: string, disabled?: boolean }>(), {
  icon: undefined,
  variant: 'primary',
  to: undefined,
  disabled: false
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
    :disabled="disabled"
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
