<script setup lang="ts">
// Shows a result that was not saved (e.g. an unreadable photo).
const { t } = useI18n()
const lastResult = useLastResult()
if (!lastResult.value) await navigateTo('/')
</script>

<template>
  <div class="page">
    <AnalysisResult
      v-if="lastResult"
      :result="lastResult"
    />
    <div class="actions">
      <BigButton
        icon="📷"
        to="/"
      >
        {{ t('photo.tryAgain') }}
      </BigButton>
    </div>
  </div>
</template>
