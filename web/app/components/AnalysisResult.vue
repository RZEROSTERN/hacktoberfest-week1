<script setup lang="ts">
import type { DocumentResult } from '~~/shared/types'
import { formatDate, formatMoney, t } from '~/utils/strings'

const props = defineProps<{ result: DocumentResult, reminderUrl?: string }>()
const unreadable = computed(() => props.result.confidence === 'low')
</script>

<template>
  <article class="result">
    <section
      v-if="result.is_suspicious"
      class="card danger"
      role="alert"
    >
      <h2>⚠️ {{ t.result.fraudTitle }}</h2>
      <p v-if="result.fraud_reason">
        {{ result.fraud_reason }}
      </p>
      <p><strong>{{ t.result.fraudNever }}</strong></p>
    </section>

    <section
      v-if="unreadable"
      class="card warning"
    >
      <h2>{{ t.result.lowConfidenceTitle }}</h2>
      <p>{{ result.explanation }}</p>
    </section>

    <template v-else>
      <section class="card">
        <h2>{{ t.result.whatIs }}</h2>
        <p class="big">
          {{ result.document_type }}
        </p>
        <p v-if="result.issuer">
          {{ t.result.from }}: <strong>{{ result.issuer }}</strong>
        </p>
        <p>{{ result.explanation }}</p>
      </section>

      <section class="card">
        <h2>{{ t.result.whenAndHowMuch }}</h2>
        <p v-if="result.deadline">
          {{ t.result.deadline }}:<br><strong class="big">{{ formatDate(result.deadline) }}</strong>
        </p>
        <p v-else>
          {{ t.result.noDeadline }}
        </p>
        <p v-if="result.amount_due !== null">
          {{ t.result.amount }}:<br><strong class="big">{{ formatMoney(result.amount_due) }}</strong>
        </p>
        <p v-else>
          {{ t.result.noAmount }}
        </p>
        <a
          v-if="result.deadline && reminderUrl"
          :href="reminderUrl"
          class="big-button secondary"
          download
        >
          <span
            class="icon"
            aria-hidden="true"
          >📅</span>
          {{ t.result.addToCalendar }}
        </a>
      </section>

      <section class="card">
        <h2>{{ t.result.whatToDo }}</h2>
        <ol
          v-if="result.required_actions.length"
          class="steps"
        >
          <li
            v-for="step in result.required_actions"
            :key="step"
          >
            {{ step }}
          </li>
        </ol>
        <p v-else>
          {{ t.result.nothingToDo }}
        </p>
      </section>
    </template>

    <p class="disclaimer">
      {{ t.result.disclaimer }}
    </p>
  </article>
</template>
