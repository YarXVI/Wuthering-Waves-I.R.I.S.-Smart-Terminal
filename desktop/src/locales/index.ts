import { en } from './en'
import { zh } from './zh'

export type Locale = 'en' | 'zh'

export const locales = {
  en,
  zh,
} as const

export type LocaleKey = Locale

export const localeNames: Record<Locale, string> = {
  en: 'English',
  zh: '中文',
}

export { en, zh }