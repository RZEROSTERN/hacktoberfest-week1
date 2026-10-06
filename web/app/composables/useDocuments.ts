import type { DocumentResult } from '~~/shared/types'

export function useLastResult() {
  return useState<DocumentResult | null>('last-result', () => null)
}

/** Maps any API failure to a plain-language message; sends her to login on 401. */
export function errorMessage(error: unknown, t: (key: string) => string): string {
  const status = (error as { statusCode?: number, status?: number })?.statusCode
    ?? (error as { status?: number })?.status
  if (status === 401) {
    void navigateTo('/acceso')
    return t('access.wrong')
  }
  if (status === 413) return t('photo.errorTooBig')
  if (status === 415) return t('photo.errorType')
  if (status === undefined) return t('photo.errorNetwork')
  return t('photo.errorGeneric')
}

export function useDocuments() {
  const request = useRequestFetch() // forwards the access cookie during SSR
  const { locale } = useI18n() // the API writes its explanations in the chosen language

  return {
    analyze(photo: Blob): Promise<DocumentResult> {
      const form = new FormData()
      form.append('image', photo, 'foto.jpg')
      return $fetch<DocumentResult>('/api/documents/analyze', {
        method: 'POST',
        body: form,
        query: { lang: locale.value }
      })
    },
    list(): Promise<DocumentResult[]> {
      return request<DocumentResult[]>('/api/documents')
    },
    get(id: number | string): Promise<DocumentResult> {
      return request<DocumentResult>(`/api/documents/${id}`)
    },
    reminderUrl(id: number): string {
      return `/api/documents/${id}/reminder.ics?lang=${locale.value}`
    }
  }
}
