<script setup lang="ts">
import type { DocumentResult } from '~~/shared/types'
import { formatMoney, formatShortDate, t } from '~/utils/strings'

defineProps<{ document: DocumentResult, dueLabel?: string }>()
</script>

<template>
  <NuxtLink
    :to="`/documentos/${document.id}`"
    class="doc-card"
    :class="{ danger: document.is_suspicious }"
  >
    <span
      v-if="dueLabel"
      class="doc-due"
    >{{ dueLabel }}</span>
    <strong class="doc-type">{{ document.document_type }}</strong>
    <span v-if="document.issuer">{{ document.issuer }}</span>
    <span v-if="document.amount_due !== null">{{ formatMoney(document.amount_due) }}</span>
    <span v-if="document.deadline">{{ t.history.due }}: {{ formatShortDate(document.deadline) }}</span>
    <span
      v-if="document.is_suspicious"
      class="doc-flag"
    >⚠️ {{ t.history.suspicious }}</span>
    <span
      v-if="!dueLabel && document.created_at"
      class="doc-meta"
    >{{ t.history.scanned }} {{ formatShortDate(document.created_at) }}</span>
  </NuxtLink>
</template>
