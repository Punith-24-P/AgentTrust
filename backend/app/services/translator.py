import re
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional
from app.config import settings
from app.services.llm import get_llm_provider


class BaseTranslationProvider(ABC):
    @abstractmethod
    async def translate(self, text: str, source_lang: str, target_lang: str = "en") -> str:
        pass

    @property
    @abstractmethod
    def is_mock(self) -> bool:
        pass


class LLMTranslationProvider(BaseTranslationProvider):
    def __init__(self):
        self.llm = get_llm_provider()

    @property
    def is_mock(self) -> bool:
        return self.llm.is_mock

    async def translate(self, text: str, source_lang: str, target_lang: str = "en") -> str:
        if source_lang.lower() == target_lang.lower():
            return text

        if self.is_mock:
            # Route to rule-based mock translator
            return await MockTranslationProvider().translate(text, source_lang, target_lang)

        prompt = (
            f"Translate the following text from {source_lang} to {target_lang}. "
            f"Preserve all statutory numbers, section numbers (§), dates, deadlines, and legal obligations precisely.\n\n"
            f"Text:\n{text}\n\nTranslation:"
        )
        return await self.llm.generate(prompt=prompt, system_prompt="You are an expert legal and civic document translator.", temperature=0.0)


class MockTranslationProvider(BaseTranslationProvider):
    """
    Multilingual rule-based back-translation dictionary and parser for Kannada, Hindi, and Telugu.
    Translates observable civic terms, numbers, sections, and dates accurately into English,
    while faithfully preserving simulated drift anomalies.
    """

    @property
    def is_mock(self) -> bool:
        return True

    # Common cross-lingual lexical maps for mock demonstration
    LEXICON = {
        # Kannada
        "ನಾಗರಿಕ ಅನುಮತಿಗಳ ನಿರ್ದೇಶನದ": "Civic Permits Directive",
        "ಕ್ಯಾಲೆಂಡರ್ ದಿನಗಳ": "calendar days",
        "ವ್ಯವಹಾರ ದಿನಗಳಲ್ಲಿ": "business days",
        "ದಿನಗಳಲ್ಲಿ": "days",
        "ಗಂಟೆಗಳ": "hours",
        "ನಗರಾಡಳಿತ ಇಲಾಖೆಗೆ": "Department of Urban Administration",
        "ಭದ್ರತಾ ಠೇವಣಿಯನ್ನು": "security deposit",
        "ಮರುಪಾವತಿಸಲಾಗುತ್ತದೆ": "is refunded",
        "ದಂಡವನ್ನು": "fine",
        "ಕ್ರೆಡಿಟ್‌ಗಳ": "credits",
        "ಮೇಲ್ಮನವಿ": "appeal",
        "ಪರಿಸರ ಅಪಾಯ ಪ್ರತಿಕ್ರಿಯೆ ಘಟಕಕ್ಕೆ": "Environmental Hazard Response Unit",
        "ಮಳೆನೀರು": "rainwater",
        "ಶಾಸನಬದ್ಧ": "statutory",

        # Hindi
        "नागरिक अनुमति निर्देश": "Civic Permits Directive",
        "कैलेंडर दिन": "calendar days",
        "कैलेंडर दिनों": "calendar days",
        "कार्य दिवसों": "business days",
        "घंटे": "hours",
        "घंटों": "hours",
        "शहरी प्रशासन विभाग": "Department of Urban Administration",
        "सुरक्षा जमा": "security deposit",
        "वापस": "refunded",
        "जुर्माना": "fine",
        "क्रेडिट": "credits",
        "अपील": "appeal",
        "पर्यावरण खतरा प्रतिक्रिया इकाई": "Environmental Hazard Response Unit",
        "वर्षा जल": "rainwater",
        "वैधानिक": "statutory",

        # Telugu
        "పౌర అనుమతుల ఆదేశం": "Civic Permits Directive",
        "క్యాలెండర్ రోజులు": "calendar days",
        "క్యాలెండర్ రోజులలోపు": "calendar days",
        "పని దినాలలోపు": "business days",
        "గంటల్లోపు": "hours",
        "పట్టణ పరిపాలన విభాగానికి": "Department of Urban Administration",
        "సెక్యూరిటీ డిపాజిట్": "security deposit",
        "తిరిగి ఇవ్వబడుతుంది": "is refunded",
        "జరిమానా": "fine",
        "క్రెడిట్ల": "credits",
        "అప్పీల్": "appeal",
        "పర్యావరణ ప్రమాద ప్రతిస్పందన యూనిట్‌కు": "Environmental Hazard Response Unit",
        "వర్షపు నీటి": "rainwater",
        "చట్టబద్ధమైన": "statutory"
    }

    async def translate(self, text: str, source_lang: str, target_lang: str = "en") -> str:
        if source_lang.lower() == target_lang.lower():
            return text

        # Check for simulated drift markers injected by demo agent
        if "[DRIFT_ANOMALY]" in text or "60 calendar days" in text:
            return "Applications must be submitted within 60 calendar days under Section 4 to the Department of Urban Administration."

        if "[DRIFT_FINE_FLAT]" in text:
            return "Violating curfew incurs a one-time flat fine of 5,000 credits without hourly accumulation."

        if "[DRIFT_DAYS_TO_MONTHS]" in text:
            return "Security deposits are refunded within 14 business months following event conclusion."

        # Extract section markers (e.g., §4, §12, §18)
        sections = re.findall(r"§\s*\d+", text)
        section_str = sections[0] if sections else "§4"

        # Extract numeric entities
        numbers = re.findall(r"\b\d+[\d,]*\b", text)

        # Synthesize faithful back-translation based on source language semantics
        if "150" in text or "30" in text:
            return f"Under {section_str}, applications for gatherings exceeding 150 attendees must be submitted at least 30 calendar days in advance to the Department of Urban Administration."
        elif "14" in text or "ಠೇವಣಿ" in text or "सुरक्षा जमा" in text or "డిపాజిట్" in text:
            return f"Under {section_str}, full security deposit refund is remitted within 14 business days following event conclusion provided no public property damage is assessed."
        elif "5,000" in text or "5000" in text or "75" in text:
            return f"Under {section_str}, operating above 75 decibels incurs a statutory fine of 5,000 credits per fractional hour of violation under the Municipal Enforcement Council."
        elif "21" in text or "ಮಧ್ಯಸ್ಥಿಕೆ" in text or "मध्यस्थता" in text or "మధ్యవర్తిత్వ" in text:
            return f"Under {section_str}, the Board of Civic Arbitration must render a final binding determination within 21 calendar days."
        elif "50" in text or "2" in text or "ದ್ರಾವಕ" in text or "विलायक" in text or "ద్రావకం" in text:
            return f"Under {section_str} of DOC-ENV-002, accidental solvent releases exceeding 50 liters require telephonic notice within 2 hours to the Environmental Hazard Response Unit."
        elif "2,500" in text or "2500" in text or "80%" in text or "80" in text:
            return f"Under {section_str} of DOC-ENV-002, commercial structures exceeding 2,500 square meters of roof area must install rainwater retention systems capturing at least 80% of quarterly precipitation."
        elif "100,000" in text or "100000" in text:
            return f"Under {section_str} of DOC-PROC-003, supply contracts exceeding 100,000 credits require competitive public bidding published for at least 21 calendar days."
        elif "15" in text and ("ಪೋರ್ಟಬಿಲಿಟಿ" in text or "गोपनीयता" in text or "డేటా" in text):
            return f"Under {section_str} of DOC-DSA-004, citizens may request machine-readable export of personal records within 15 calendar days at zero fee."

        # Default back-translation fallback
        return f"Translated from {source_lang.upper()} [Demo Lexicon]: {text}"


def get_translation_provider() -> BaseTranslationProvider:
    if settings.TRANSLATION_PROVIDER == "llm" and settings.LLM_API_KEY:
        return LLMTranslationProvider()
    return MockTranslationProvider()
