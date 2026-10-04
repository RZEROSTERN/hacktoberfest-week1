import type { VoiceAnswer } from '~~/shared/types'

export function useQuestions() {
  return {
    ask(audio: Blob, documentId?: number): Promise<VoiceAnswer> {
      const form = new FormData()
      const extension = audio.type.includes('mp4') ? 'm4a' : audio.type.includes('ogg') ? 'ogg' : 'webm'
      form.append('audio', audio, `pregunta.${extension}`)
      if (documentId) form.append('document_id', String(documentId))
      return $fetch<VoiceAnswer>('/api/questions/voice', { method: 'POST', body: form })
    }
  }
}
