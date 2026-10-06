import { formatDate, formatMoney, formatShortDate } from '~/utils/format'

/** Money and date formatters bound to the active language; they follow it when it changes. */
export function useFormatters() {
  const { localeProperties } = useI18n()
  const tag = () => localeProperties.value.language ?? 'es-MX'

  return {
    formatMoney: (amount: number) => formatMoney(amount, tag()),
    formatDate: (isoDate: string) => formatDate(isoDate, tag()),
    formatShortDate: (isoDate: string) => formatShortDate(isoDate, tag())
  }
}
