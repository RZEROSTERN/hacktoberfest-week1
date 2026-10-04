<script setup lang="ts">
import { t } from '~/utils/strings'

const route = useRoute()
const id = String(route.params.id)
const { get, reminderUrl } = useDocuments()

const { data: result, status, error } = await useAsyncData(`document-${id}`, () => get(id))
</script>

<template>
  <div class="page">
    <LoadingState
      v-if="status === 'pending'"
      :title="t.common.loading"
    />
    <ErrorState
      v-else-if="error || !result"
      :title="t.photo.errorTitle"
      :message="t.result.notFound"
    />
    <AnalysisResult
      v-else
      :result="result"
      :reminder-url="result.id ? reminderUrl(result.id) : undefined"
    />
    <div class="actions">
      <BigButton
        variant="secondary"
        to="/"
      >
        {{ t.result.home }}
      </BigButton>
    </div>
  </div>
</template>
