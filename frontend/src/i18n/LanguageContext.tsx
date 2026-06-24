import React, { createContext, useContext, useState } from 'react';
import { translations } from './translations';
import type { Language, TranslationKey } from './translations';
import { ConfigProvider } from 'antd';
import enUS from 'antd/locale/en_US';
import viVN from 'antd/locale/vi_VN';
import jaJP from 'antd/locale/ja_JP';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: TranslationKey) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    const saved = localStorage.getItem('app_lang');
    return (saved as Language) || 'en';
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('app_lang', lang);
  };

  const t = (key: TranslationKey): string => {
    const translation = translations[language];
    // Cast key to keyof typeof translations.en to get type safety
    return (translation as any)[key] || (translations['en'] as any)[key] || String(key);
  };

  const getAntdLocale = () => {
    switch (language) {
      case 'vi':
        return viVN;
      case 'ja':
        return jaJP;
      default:
        return enUS;
    }
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      <ConfigProvider locale={getAntdLocale()}>
        {children}
      </ConfigProvider>
    </LanguageContext.Provider>
  );
};

export const useTranslation = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useTranslation must be used within a LanguageProvider');
  }
  return context;
};
