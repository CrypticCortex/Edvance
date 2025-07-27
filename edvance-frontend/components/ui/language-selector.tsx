"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"
import { Languages, Check } from "lucide-react"
import { useLanguage } from "@/contexts/LanguageContext"
import { SUPPORTED_LANGUAGES, getLanguageNativeName } from "@/lib/language"

interface LanguageSelectorProps {
    className?: string
    variant?: "button" | "badge" | "compact"
    showIcon?: boolean
}

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({
    className = "",
    variant = "button",
    showIcon = true
}) => {
    const { currentLanguage, setLanguage } = useLanguage()
    const [isOpen, setIsOpen] = useState(false)

    const handleLanguageSelect = (languageCode: string) => {
        setLanguage(languageCode)
        setIsOpen(false)
    }

    const currentLanguageNative = getLanguageNativeName(currentLanguage)

    if (variant === "badge") {
        return (
            <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
                <DropdownMenuTrigger asChild>
                    <Badge
                        variant="outline"
                        className={`cursor-pointer hover:bg-gray-100 ${className}`}
                    >
                        {showIcon && <Languages className="w-3 h-3 mr-1" />}
                        {currentLanguageNative}
                    </Badge>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                    {SUPPORTED_LANGUAGES.map((language) => (
                        <DropdownMenuItem
                            key={language.code}
                            onClick={() => handleLanguageSelect(language.code)}
                            className="flex items-center justify-between cursor-pointer"
                        >
                            <span className="flex items-center">
                                <span className="mr-2">{language.nativeName}</span>
                                <span className="text-sm text-gray-500">({language.name})</span>
                            </span>
                            {currentLanguage === language.code && (
                                <Check className="w-4 h-4 text-green-600" />
                            )}
                        </DropdownMenuItem>
                    ))}
                </DropdownMenuContent>
            </DropdownMenu>
        )
    }

    if (variant === "compact") {
        return (
            <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
                <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className={`p-2 ${className}`}>
                        {showIcon && <Languages className="w-4 h-4" />}
                        {!showIcon && currentLanguageNative}
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                    {SUPPORTED_LANGUAGES.map((language) => (
                        <DropdownMenuItem
                            key={language.code}
                            onClick={() => handleLanguageSelect(language.code)}
                            className="flex items-center justify-between cursor-pointer"
                        >
                            <span className="flex items-center">
                                <span className="mr-2">{language.nativeName}</span>
                                <span className="text-sm text-gray-500">({language.name})</span>
                            </span>
                            {currentLanguage === language.code && (
                                <Check className="w-4 h-4 text-green-600" />
                            )}
                        </DropdownMenuItem>
                    ))}
                </DropdownMenuContent>
            </DropdownMenu>
        )
    }

    // Default button variant
    return (
        <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
            <DropdownMenuTrigger asChild>
                <Button variant="outline" className={className}>
                    {showIcon && <Languages className="w-4 h-4 mr-2" />}
                    {currentLanguageNative}
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
                {SUPPORTED_LANGUAGES.map((language) => (
                    <DropdownMenuItem
                        key={language.code}
                        onClick={() => handleLanguageSelect(language.code)}
                        className="flex items-center justify-between cursor-pointer"
                    >
                        <span className="flex items-center">
                            <span className="mr-2">{language.nativeName}</span>
                            <span className="text-sm text-gray-500">({language.name})</span>
                        </span>
                        {currentLanguage === language.code && (
                            <Check className="w-4 h-4 text-green-600" />
                        )}
                    </DropdownMenuItem>
                ))}
            </DropdownMenuContent>
        </DropdownMenu>
    )
}
