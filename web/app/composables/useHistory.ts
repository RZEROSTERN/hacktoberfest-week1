import type { DocumentResult } from '~~/shared/types'
import { daysUntil } from '~/utils/strings'

export type UpcomingDocument = DocumentResult & { deadline: string, daysLeft: number }

/** Splits the history into upcoming deadlines (soonest first) and everything (newest first). */
export function splitHistory(documents: DocumentResult[], today: Date = new Date()) {
  const upcoming: UpcomingDocument[] = documents
    .filter((d): d is DocumentResult & { deadline: string } => d.deadline !== null)
    .map(d => ({ ...d, daysLeft: daysUntil(d.deadline, today) }))
    .filter(d => d.daysLeft >= 0)
    .sort((a, b) => a.daysLeft - b.daysLeft)
  return { upcoming, all: documents }
}

export async function useHistory() {
  const { list } = useDocuments()
  const { data, status, error } = await useAsyncData('history', () => list())
  const split = computed(() => splitHistory(data.value ?? []))
  return { split, status, error }
}
