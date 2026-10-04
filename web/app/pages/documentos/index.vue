<script setup lang="ts">
import { t } from '~/utils/strings'

const { split, status, error } = await useHistory()

function dueLabel(daysLeft: number): string {
  if (daysLeft === 0) return t.history.today
  if (daysLeft === 1) return t.history.tomorrow
  return t.history.inDays(daysLeft)
}
</script>

<template>
  <div class="page">
    <h1>{{ t.history.title }}</h1>

    <LoadingState
      v-if="status === 'pending'"
      :title="t.common.loading"
    />
    <ErrorState
      v-else-if="error"
      :title="t.photo.errorTitle"
      :message="t.photo.errorNetwork"
    />
    <p
      v-else-if="!split.all.length"
      class="lead"
    >
      {{ t.history.empty }}
    </p>

    <template v-else>
      <section class="history-section">
        <h2>{{ t.history.upcoming }}</h2>
        <p v-if="!split.upcoming.length">
          {{ t.history.noUpcoming }}
        </p>
        <DocumentCard
          v-for="doc in split.upcoming"
          :key="`up-${doc.id}`"
          :document="doc"
          :due-label="dueLabel(doc.daysLeft)"
        />
      </section>

      <section class="history-section">
        <h2>{{ t.history.all }}</h2>
        <DocumentCard
          v-for="doc in split.all"
          :key="doc.id ?? doc.document_type"
          :document="doc"
        />
      </section>
    </template>

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
