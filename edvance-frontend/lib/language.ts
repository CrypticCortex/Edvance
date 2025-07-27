// Language configuration and utilities for Edvance frontend

export interface LanguageOption {
    code: string;
    name: string;
    nativeName: string;
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
    { code: 'english', name: 'English', nativeName: 'English' },
    { code: 'tamil', name: 'Tamil', nativeName: 'தமிழ்' },
    { code: 'telugu', name: 'Telugu', nativeName: 'తెలుగు' }
];

export const DEFAULT_LANGUAGE = 'english';

export const getLanguageName = (code: string): string => {
    const language = SUPPORTED_LANGUAGES.find(lang => lang.code === code);
    return language ? language.name : 'English';
};

export const getLanguageNativeName = (code: string): string => {
    const language = SUPPORTED_LANGUAGES.find(lang => lang.code === code);
    return language ? language.nativeName : 'English';
};

// Storage keys for language preferences
export const LANGUAGE_STORAGE_KEY = 'edvance_selected_language';

// Get saved language preference or default
export const getSavedLanguage = (): string => {
    if (typeof window !== 'undefined') {
        const saved = localStorage.getItem(LANGUAGE_STORAGE_KEY);
        if (saved && SUPPORTED_LANGUAGES.some(lang => lang.code === saved)) {
            return saved;
        }
    }
    return DEFAULT_LANGUAGE;
};

// Save language preference
export const saveLanguage = (languageCode: string): void => {
    if (typeof window !== 'undefined') {
        localStorage.setItem(LANGUAGE_STORAGE_KEY, languageCode);
    }
};
