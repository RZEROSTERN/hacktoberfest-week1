<script setup lang="ts">
import type { DocumentResult, VoiceAnswer } from '~~/shared/types'

const { t } = useI18n()
const route = useRoute()
const documentId = Number(route.query.documento) || undefined

const { get } = useDocuments()
const { ask } = useQuestions()
const { recording, seconds, start, stop } = useRecorder()

const { data: document } = await useAsyncData<DocumentResult | null>(
  `question-doc-${documentId ?? 'none'}`,
  () => (documentId ? get(documentId) : Promise.resolve(null))
)

const status = ref<'idle' | 'recording' | 'thinking' | 'answered' | 'error'>('idle')
const result = ref<VoiceAnswer | null>(null)
const error = ref('')

async function record() {
  error.value = ''
  status.value = 'recording'
  let audio: Blob
  try {
    audio = await start()
  }
  catch (err) {
    const kind = (err as Error).message
    error.value = kind === 'permission' ? t('voice.errorPermission') : t('voice.errorUnsupported')
    status.value = 'error'
    return
  }
  try {
    status.value = 'thinking'
    result.value = await ask(audio, documentId)
    status.value = 'answered'
  }
  catch (err) {
    const code = (err as { statusCode?: number }).statusCode
    error.value = code === 422 ? t('voice.errorAudio') : errorMessage(err, t)
    status.value = 'error'
  }
}
</script>

<template>
  <div class="page">
    <h1>{{ t('voice.title') }}</h1>
    <p
      v-if="document"
      class="card"
    >
      {{ t('voice.aboutDocument') }} <strong>{{ document.document_type }}</strong>
    </p>

    <template v-if="status === 'idle'">
      <p class="lead">
        {{ t('voice.hint') }}
      </p>
      <BigButton
        icon="🎤"
        @click="record"
      >
        {{ t('voice.start') }}
      </BigButton>
    </template>

    <template v-else-if="status === 'recording'">
      <div
        class="state"
        role="status"
        aria-live="polite"
      >
        <div
          class="recording-dot"
          aria-hidden="true"
        />
        <p class="state-title">
          {{ t('voice.recording') }}
        </p>
        <p class="state-hint">
          {{ t('voice.seconds', { seconds }) }}
        </p>
      </div>
      <BigButton
        icon="⏹️"
        :disabled="!recording"
        class="stop"
        @click="stop"
      >
        {{ t('voice.stop') }}
      </BigButton>
    </template>

    <LoadingState
      v-else-if="status === 'thinking'"
      :title="t('voice.listening')"
      :hint="t('voice.listeningHint')"
    />

    <template v-else-if="status === 'answered' && result">
      <section
        v-if="result.question"
        class="card"
      >
        <h2>{{ t('voice.youAsked') }}</h2>
        <p>“{{ result.question }}”</p>
      </section>
      <section
        class="card"
        :class="{ warning: result.confidence === 'low' }"
      >
        <h2>{{ t('voice.answer') }}</h2>
        <p class="big">
          {{ result.answer }}
        </p>
      </section>
      <p class="disclaimer">
        {{ t('result.disclaimer') }}
      </p>
      <BigButton
        icon="🎤"
        @click="record"
      >
        {{ t('voice.askAgain') }}
      </BigButton>
    </template>

    <ErrorState
      v-else-if="status === 'error'"
      :title="t('voice.errorTitle')"
      :message="error"
    >
      <BigButton
        icon="🎤"
        @click="record"
      >
        {{ t('voice.askAgain') }}
      </BigButton>
    </ErrorState>

    <BigButton
      variant="secondary"
      :to="documentId ? `/documentos/${documentId}` : '/'"
    >
      {{ t('common.back') }}
    </BigButton>
  </div>
</template>
