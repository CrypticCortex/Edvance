"use client"

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getSavedLanguage, saveLanguage, DEFAULT_LANGUAGE } from '@/lib/language';

interface LanguageContextType {
    currentLanguage: string;
    setLanguage: (language: string) => void;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

interface LanguageProviderProps {
    children: ReactNode;
}

export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children }) => {
    const [currentLanguage, setCurrentLanguage] = useState<string>(DEFAULT_LANGUAGE);

    useEffect(() => {
        // Load saved language preference on mount
        const saved = getSavedLanguage();
        setCurrentLanguage(saved);
    }, []);

    const setLanguage = (language: string) => {
        setCurrentLanguage(language);
        saveLanguage(language);
    };

    return (
        <LanguageContext.Provider value={{ currentLanguage, setLanguage }}>
            {children}
        </LanguageContext.Provider>
    );
};

export const useLanguage = (): LanguageContextType => {
    const context = useContext(LanguageContext);
    if (!context) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
};
