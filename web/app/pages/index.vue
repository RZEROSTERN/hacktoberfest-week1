<script setup lang="ts">
import { prepareImage } from '~/utils/image'
import { t } from '~/utils/strings'

const { analyze } = useDocuments()
const lastResult = useLastResult()

const fileInput = ref<HTMLInputElement | null>(null)
const status = ref<'idle' | 'preparing' | 'reading' | 'error'>('idle')
const error = ref('')

function takePhoto() {
  fileInput.value?.click()
}

async function onPhoto(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = '' // allow taking the same photo again
  if (!file) return

  try {
    status.value = 'preparing'
    const photo = await prepareImage(file)
    status.value = 'reading'
    const result = await analyze(photo)
    lastResult.value = result
    await navigateTo(result.id ? `/documentos/${result.id}` : '/resultado')
  }
  catch (err) {
    error.value = errorMessage(err)
    status.value = 'error'
  }
}
</script>

<template>
  <div class="page">
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      capture="environment"
      class="visually-hidden"
      tabindex="-1"
      aria-hidden="true"
      @change="onPhoto"
    >

    <LoadingState
      v-if="status === 'preparing'"
      :title="t.photo.preparing"
    />
    <LoadingState
      v-else-if="status === 'reading'"
      :title="t.photo.reading"
      :hint="t.photo.readingHint"
    />
    <ErrorState
      v-else-if="status === 'error'"
      :title="t.photo.errorTitle"
      :message="error"
    >
      <BigButton
        icon="📷"
        @click="takePhoto"
      >
        {{ t.photo.tryAgain }}
      </BigButton>
    </ErrorState>

    <template v-else>
      <p class="lead">
        {{ t.home.hint }}
      </p>
      <div class="actions">
        <BigButton
          icon="📷"
          @click="takePhoto"
        >
          {{ t.home.takePhoto }}
        </BigButton>
        <BigButton
          icon="🎤"
          to="/preguntar"
        >
          {{ t.home.askVoice }}
        </BigButton>
      </div>
    </template>
  </div>
</template>
