# FILE: app/core/language.py

from enum import Enum
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class SupportedLanguage(str, Enum):
    """Supported languages for AI generation."""
    ENGLISH = "english"
    TAMIL = "tamil"
    TELUGU = "telugu"

class LanguageConfig:
    """Language configuration and utilities."""
    
    LANGUAGE_NAMES = {
        SupportedLanguage.ENGLISH: "English",
        SupportedLanguage.TAMIL: "Tamil",
        SupportedLanguage.TELUGU: "Telugu"
    }
    
    LANGUAGE_CODES = {
        SupportedLanguage.ENGLISH: "en",
        SupportedLanguage.TAMIL: "ta", 
        SupportedLanguage.TELUGU: "te"
    }
    
    # Language-specific prompt instructions
    LANGUAGE_INSTRUCTIONS = {
        SupportedLanguage.ENGLISH: "Generate all content in English. Use clear, educational language appropriate for the specified grade level.",
        SupportedLanguage.TAMIL: "Generate all content in Tamil (தமிழ்). Use proper Tamil grammar and vocabulary. Ensure educational content is culturally appropriate and uses Tamil educational terminology.",
        SupportedLanguage.TELUGU: "Generate all content in Telugu (తెలుగు). Use proper Telugu grammar and vocabulary. Ensure educational content is culturally appropriate and uses Telugu educational terminology."
    }
    
    # Default language fallback
    DEFAULT_LANGUAGE = SupportedLanguage.ENGLISH

def validate_language(language: str) -> SupportedLanguage:
    """
    Validate and normalize language parameter.
    
    Args:
        language: Language string to validate
        
    Returns:
        SupportedLanguage enum value
        
    Raises:
        ValueError: If language is not supported
    """
    if not language:
        return LanguageConfig.DEFAULT_LANGUAGE
    
    language_lower = language.lower().strip()
    
    try:
        return SupportedLanguage(language_lower)
    except ValueError:
        logger.warning(f"Unsupported language '{language}', falling back to {LanguageConfig.DEFAULT_LANGUAGE}")
        return LanguageConfig.DEFAULT_LANGUAGE

def get_language_name(language: SupportedLanguage) -> str:
    """Get the display name for a language."""
    return LanguageConfig.LANGUAGE_NAMES.get(language, "English")

def get_language_code(language: SupportedLanguage) -> str:
    """Get the ISO language code for a language."""
    return LanguageConfig.LANGUAGE_CODES.get(language, "en")

def get_language_instruction(language: SupportedLanguage) -> str:
    """Get the prompt instruction for a language."""
    return LanguageConfig.LANGUAGE_INSTRUCTIONS.get(language, LanguageConfig.LANGUAGE_INSTRUCTIONS[SupportedLanguage.ENGLISH])

def create_language_prompt_prefix(language: SupportedLanguage, context: str = "") -> str:
    """
    Create a language-specific prompt prefix.
    
    Args:
        language: Target language
        context: Additional context about the content type
        
    Returns:
        Formatted prompt prefix with language instructions
    """
    language_name = get_language_name(language)
    instruction = get_language_instruction(language)
    
    prefix = f"""LANGUAGE REQUIREMENT: {instruction}

TARGET LANGUAGE: {language_name}
"""
    
    if context:
        prefix += f"CONTENT TYPE: {context}\n"
    
    prefix += "\nIMPORTANT: All generated content, including questions, answers, explanations, and instructions must be in {language_name}.\n\n"
    
    return prefix

def validate_generated_content_language(content: str, expected_language: SupportedLanguage) -> Dict[str, any]:
    """
    Basic validation of generated content language.
    
    Args:
        content: Generated content to validate
        expected_language: Expected language
        
    Returns:
        Dictionary with validation results
    """
    # This is a basic implementation - could be enhanced with proper language detection
    validation_result = {
        "is_valid": True,
        "confidence": 0.8,  # Default confidence
        "detected_language": expected_language,
        "issues": []
    }
    
    # Basic checks for non-English languages
    if expected_language == SupportedLanguage.TAMIL:
        # Check for Tamil script characters
        tamil_chars = any('\u0B80' <= char <= '\u0BFF' for char in content)
        if not tamil_chars and len(content) > 50:  # Only check for longer content
            validation_result["is_valid"] = False
            validation_result["confidence"] = 0.3
            validation_result["issues"].append("No Tamil script detected in content")
    
    elif expected_language == SupportedLanguage.TELUGU:
        # Check for Telugu script characters
        telugu_chars = any('\u0C00' <= char <= '\u0C7F' for char in content)
        if not telugu_chars and len(content) > 50:  # Only check for longer content
            validation_result["is_valid"] = False
            validation_result["confidence"] = 0.3
            validation_result["issues"].append("No Telugu script detected in content")
    
    return validation_result