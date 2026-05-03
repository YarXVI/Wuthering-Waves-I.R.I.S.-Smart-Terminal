import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { locales, Locale, localeNames } from '../locales'

type LocaleStrings = typeof locales.en

interface LanguageContextValue {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: LocaleStrings
  localeNames: Record<Locale, string>
}

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined)

const LOCALE_STORAGE_KEY = 'nb-locale'

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [locale, setLocaleState] = useState<Locale>(() => {
    const stored = localStorage.getItem(LOCALE_STORAGE_KEY)
    if (stored === 'en' || stored === 'zh') {
      return stored
    }
    const browserLang = navigator.language.toLowerCase()
    if (browserLang.startsWith('zh')) {
      return 'zh'
    }
    return 'en'
  })

  useEffect(() => {
    localStorage.setItem(LOCALE_STORAGE_KEY, locale)
  }, [locale])

  const setLocale = useCallback((newLocale: Locale) => {
    setLocaleState(newLocale)
  }, [])

  const value: LanguageContextValue = {
    locale,
    setLocale,
    t: locales[locale],
    localeNames,
  }

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  )
}

export const useLanguage = (): LanguageContextValue => {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return context
}

export default LanguageProvider