// Locale-aware formatting. `locale` is a BCP 47 tag such as "es-MX" or "en-US"; amounts are
// always Mexican pesos, so English readers see "MX$" and never mistake them for US dollars.
export function formatMoney(amount: number, locale: string): string {
  return new Intl.NumberFormat(locale, { style: 'currency', currency: 'MXN' }).format(amount)
}

export function formatDate(isoDate: string, locale: string): string {
  // Dates are calendar days (YYYY-MM-DD); parse as local noon to avoid timezone shifts.
  return new Intl.DateTimeFormat(locale, { dateStyle: 'full' }).format(new Date(`${isoDate}T12:00:00`))
}

/** Whole days from today (local) until an ISO calendar date. */
export function daysUntil(isoDate: string, today: Date = new Date()): number {
  const start = new Date(today.getFullYear(), today.getMonth(), today.getDate())
  const [y, m, d] = isoDate.split('-').map(Number) as [number, number, number]
  return Math.round((new Date(y, m - 1, d).getTime() - start.getTime()) / 86_400_000)
}

export function formatShortDate(isoDate: string, locale: string): string {
  return new Intl.DateTimeFormat(locale, { day: 'numeric', month: 'long', year: 'numeric' })
    .format(new Date(isoDate.length === 10 ? `${isoDate}T12:00:00` : isoDate))
}
