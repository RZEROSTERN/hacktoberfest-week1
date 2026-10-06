<script setup lang="ts">
const { t } = useI18n()

const code = ref('')
const error = ref('')
const sending = ref(false)
const ready = ref(false) // block native form submits before hydration
onMounted(() => { ready.value = true })

async function submit() {
  error.value = ''
  sending.value = true
  try {
    await $fetch('/api/login', { method: 'POST', body: { code: code.value } })
    await navigateTo('/', { external: true }) // full reload so SSR sees the new cookie
  }
  catch (err) {
    const status = (err as { statusCode?: number }).statusCode
    error.value = status === 401 ? t('access.wrong') : t('access.error')
  }
  finally {
    sending.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>{{ t('access.title') }}</h1>
    <p class="lead">
      {{ t('tagline') }}
    </p>
    <form
      class="access-form"
      @submit.prevent="submit"
    >
      <label for="code">{{ t('access.label') }}</label>
      <input
        id="code"
        v-model="code"
        type="password"
        autocomplete="current-password"
        required
      >
      <p
        v-if="error"
        class="form-error"
        role="alert"
      >
        {{ error }}
      </p>
      <button
        type="submit"
        class="big-button primary"
        :disabled="sending || !ready"
      >
        {{ sending ? t('common.loading') : t('access.submit') }}
      </button>
    </form>
  </div>
</template>
