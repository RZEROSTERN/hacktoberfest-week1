import type { DocumentResult } from '~~/shared/types'
import { t } from '~/utils/strings'

export function useLastResult() {
  return useState<DocumentResult | null>('last-result', () => null)
}

/** Maps any API failure to a plain-Spanish message; sends her to login on 401. */
export function errorMessage(error: unknown): string {
  const status = (error as { statusCode?: number, status?: number })?.statusCode
    ?? (error as { status?: number })?.status
  if (status === 401) {
    void navigateTo('/acceso')
    return t.access.wrong
  }
  if (status === 413) return t.photo.errorTooBig
  if (status === 415) return t.photo.errorType
  if (status === undefined) return t.photo.errorNetwork
  return t.photo.errorGeneric
}

export function useDocuments() {
  const request = useRequestFetch() // forwards the access cookie during SSR

  return {
    analyze(photo: Blob): Promise<DocumentResult> {
      const form = new FormData()
      form.append('image', photo, 'foto.jpg')
      return $fetch<DocumentResult>('/api/documents/analyze', { method: 'POST', body: form })
    },
    list(): Promise<DocumentResult[]> {
      return request<DocumentResult[]>('/api/documents')
    },
    get(id: number | string): Promise<DocumentResult> {
      return request<DocumentResult>(`/api/documents/${id}`)
    },
    reminderUrl(id: number): string {
      return `/api/documents/${id}/reminder.ics`
    }
  }
}
