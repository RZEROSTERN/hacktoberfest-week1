<script setup lang="ts">
import { t } from '~/utils/strings'

// Shows a result that was not saved (e.g. an unreadable photo).
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
        {{ t.photo.tryAgain }}
      </BigButton>
    </div>
  </div>
</template>
