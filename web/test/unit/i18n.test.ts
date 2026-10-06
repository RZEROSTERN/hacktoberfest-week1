import { describe, expect, it, vi } from 'vitest'
import { defineComponent, h } from 'vue'
import { getQuery } from 'h3'
import { useNuxtApp } from '#app'
import { mountSuspended, registerEndpoint } from '@nuxt/test-utils/runtime'
import App from '~/app.vue'
import AnalysisResult from '~/components/AnalysisResult.vue'
import LanguageSwitcher from '~/components/LanguageSwitcher.vue'
import Home from '~/pages/index.vue'
import es from '../../i18n/locales/es.json'
import en from '../../i18n/locales/en.json'
import type { DocumentResult } from '~~/shared/types'

function flatten(messages: object, prefix = ''): Record<string, string> {
  return Object.entries(messages).reduce<Record<string, string>>((all, [key, value]) => {
    if (typeof value === 'string') all[prefix + key] = value
    else Object.assign(all, flatten(value, `${prefix}${key}.`))
    return all
  }, {})
}

const placeholders = (text: string) => [...text.matchAll(/\{(\w+)\}/g)].map(m => m[1]).sort()

async function switchTo(code: 'es' | 'en') {
  await useNuxtApp().$i18n.setLocale(code)
}

describe('locale files', () => {
  const spanish = flatten(es)
  const english = flatten(en)

  it('define exactly the same keys in both languages', () => {
    expect(Object.keys(english).sort()).toEqual(Object.keys(spanish).sort())
  })

  it('have no empty strings and use the same {placeholders} in both languages', () => {
    for (const [key, text] of Object.entries(spanish)) {
      expect(text.trim(), key).not.toBe('')
      expect(english[key]!.trim(), key).not.toBe('')
      expect(placeholders(english[key]!), key).toEqual(placeholders(text))
    }
  })
})

describe('language switching', () => {
  it('starts in Spanish', async () => {
    const wrapper = await mountSuspended(Home)
    expect(wrapper.text()).toContain('Tomar foto')
  })

  it('renders the page in English after switching, and back', async () => {
    const wrapper = await mountSuspended(Home)

    await switchTo('en')
    await vi.waitFor(() => expect(wrapper.text()).toContain('Take photo'))
    expect(wrapper.text()).toContain('Ask with your voice')
    expect(wrapper.text()).not.toContain('Tomar foto')

    await switchTo('es')
    await vi.waitFor(() => expect(wrapper.text()).toContain('Tomar foto'))
  })

  it('formats amounts and dates for the active language', async () => {
    const result: DocumentResult = {
      id: 1, created_at: null, document_type: 'Recibo de luz', issuer: 'CFE', deadline: '2026-10-18',
      amount_due: 1482.5, required_actions: [], is_suspicious: false, fraud_reason: null,
      confidence: 'high', explanation: 'x'
    }
    const wrapper = await mountSuspended(AnalysisResult, { props: { result } })
    expect(wrapper.text()).toContain('$1,482.50')
    expect(wrapper.text()).toContain('18 de octubre de 2026')

    await switchTo('en')
    await vi.waitFor(() => expect(wrapper.text()).toContain('MX$1,482.50'))
    expect(wrapper.text()).toContain('Sunday, October 18, 2026')
    expect(wrapper.text()).toContain('Deadline')
  })
})

describe('LanguageSwitcher', () => {
  it('shows each language in its own name, with the current one marked', async () => {
    const wrapper = await mountSuspended(LanguageSwitcher)
    const buttons = wrapper.findAll('button')

    expect(buttons.map(b => b.text())).toEqual(['Español', 'English'])
    expect(buttons.map(b => b.attributes('lang'))).toEqual(['es', 'en'])
    expect(buttons.map(b => b.attributes('aria-pressed'))).toEqual(['true', 'false'])
  })

  it('changes the language and remembers it in the locale cookie', async () => {
    const wrapper = await mountSuspended(LanguageSwitcher)

    await wrapper.findAll('button')[1]!.trigger('click')

    await vi.waitFor(() => expect(wrapper.findAll('button')[1]!.attributes('aria-pressed')).toBe('true'))
    expect(useCookie('i18n_redirected').value).toBe('en')
  })

  it('keeps <html lang> and the page title in step with the language', async () => {
    await mountSuspended(App)
    await vi.waitFor(() => expect(document.documentElement.lang).toBe('es-MX'))
    expect(document.title).toBe('Traductor de Papeles')

    await switchTo('en')
    await vi.waitFor(() => expect(document.documentElement.lang).toBe('en-US'))
    expect(document.title).toBe('Paperwork Translator')
  })

  it('is part of the app header on every page', async () => {
    const wrapper = await mountSuspended(App)
    expect(wrapper.find('header .language-switcher').exists()).toBe(true)
  })
})

describe('language sent to the API', () => {
  const Probe = defineComponent({
    setup(_, { expose }) {
      const documents = useDocuments()
      const questions = useQuestions()
      expose({ documents, questions })
      return () => h('div')
    }
  })

  it('adds ?lang= to the calendar link so the .ics matches the screen', async () => {
    const wrapper = await mountSuspended(Probe)
    const { documents } = wrapper.vm as unknown as { documents: ReturnType<typeof useDocuments> }
    expect(documents.reminderUrl(3)).toBe('/api/documents/3/reminder.ics?lang=es')

    await switchTo('en')
    expect(documents.reminderUrl(3)).toBe('/api/documents/3/reminder.ics?lang=en')
  })

  it('sends the chosen language with a photo and with a voice question', async () => {
    const seen: Record<string, unknown>[] = []
    registerEndpoint('/api/documents/analyze', { method: 'POST', handler: (event) => { seen.push(getQuery(event)); return {} } })
    registerEndpoint('/api/questions/voice', { method: 'POST', handler: (event) => { seen.push(getQuery(event)); return {} } })
    const wrapper = await mountSuspended(Probe)
    const { documents, questions } = wrapper.vm as unknown as {
      documents: ReturnType<typeof useDocuments>
      questions: ReturnType<typeof useQuestions>
    }

    await documents.analyze(new Blob(['x'], { type: 'image/jpeg' }))
    await questions.ask(new Blob(['x'], { type: 'audio/webm' }))
    await switchTo('en')
    await documents.analyze(new Blob(['x'], { type: 'image/jpeg' }))
    await questions.ask(new Blob(['x'], { type: 'audio/webm' }))

    expect(seen.map(query => query.lang)).toEqual(['es', 'es', 'en', 'en'])
  })
})
