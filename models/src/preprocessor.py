"""Text Preprocessing and Language Detection Module for Raksha.

Conforms strictly to:
- ai-ml-system.md: Character/script heuristics, Kannada script vs Latin script handling,
  contextual transliteration preserving English tokens, fallback on low confidence.
- feature-specification.md (FEAT-01, FEAT-02, FEAT-03).
- api-specification.md (Language values: "kannada", "english", "code-mixed", "unknown").
- testing-and-evaluation.md (Handles native Kannada, transliterated Kanglish, code-mixed, English, URLs).
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


# Kannada Unicode Block: U+0C80 to U+0CFF
KANNADA_UNICODE_REGEX = re.compile(r"[\u0C80-\u0CFF]")
LATIN_UNICODE_REGEX = re.compile(r"[a-zA-Z]")
URL_PATTERN_REGEX = re.compile(
    r"(?:https?://|www\.)[^\s/$.?#].[^\s]*|"
    r"(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?",
    re.IGNORECASE,
)

# Non-printable and zero-width artifacts (except intentional zero-width joiners in valid scripts)
NON_PRINTABLE_REGEX = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]")


# High-confidence Transliterated Kannada (Kanglish) Lexicon
# Common root words, suffixes, verbal forms, pronouns, and regional phrasing
KANGLISH_VOCABULARY: Set[str] = {
    # Pronouns & Address
    "nimma", "namma", "nanna", "ninna", "neevu", "naanu", "avaru", "ivaru", "avara", "ivara",
    "grahakare", "sir", "madam", "yarigu", "yarigoo", "nange", "namge", "nimge", "avanige", "avalige",
    # Verbs & Conjugations
    "madi", "maadi", "madbedi", "madbeda", "madiddini", "madidare", "madoke", "madbeka",
    "agide", "aagide", "agatte", "aagatte", "agutte", "aagutte", "aytu", "aaythu", "agalla",
    "bidi", "heli", "nodiri", "nodi", "kattiri", "kalsidini", "kalsi", "kalisi", "padayiri",
    "geddidiri", "tholisi", "thilisi", "banniri", "banni", "bartheera", "barta", "hogiri",
    "iruvudarinda", "iruvude", "ide", "illa", "iddare", "beku", "beda", "bekagide", "bekaagide",
    # Temporal & Quantity
    "ivattu", "ivatte", "ivattina", "nale", "naale", "ninne", "eega", "eegale", "koodale",
    "thakshana", "thurthu", "ghanteyalli", "dina", "dinakke", "tingala", "varsha", "sanje", "belagge",
    # Connectives & Postpositions
    "matthu", "haagu", "athava", "andre", "adare", "yake", "hege", "alli", "illi", "inda",
    "ge", "kke", "annu", "ige", "inda",
    # Common Scam / Transactional Vocabulary
    "khathe", "khate", "hana", "danda", "raddati", "raddagutte", "thapisalu", "shubhashayagalu",
    "abhinandanegalu", "habba", "habbada", "nemakati", "kelasa", "maneyindale", "galisi",
    "vilasa", "namaskara", "shubhoday", "hegidira",
}

# English Common Stopwords and Vocabulary
COMMON_ENGLISH_WORDS: Set[str] = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on",
    "with", "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we",
    "say", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their",
    "what", "so", "up", "out", "if", "about", "who", "get", "which", "go", "me", "when", "make",
    "can", "like", "time", "no", "just", "him", "know", "take", "people", "into", "year", "your",
    "good", "some", "could", "them", "see", "other", "than", "then", "now", "look", "only", "come",
    "its", "over", "think", "also", "back", "after", "use", "two", "how", "our", "work", "first",
    "well", "way", "even", "new", "want", "because", "any", "these", "give", "day", "most", "us",
    "dear", "customer", "account", "bank", "credit", "card", "debit", "blocked", "suspended",
    "urgent", "immediately", "verify", "update", "click", "link", "password", "otp", "code",
    "payment", "bill", "due", "unpaid", "recharge", "balance", "congratulations", "prize", "won",
    "reward", "offer", "discount", "free", "order", "delivery", "delivered", "package", "parcel",
    "failed", "meeting", "morning", "afternoon", "team", "project", "review", "feedback", "email",
}

# Contextual high-confidence Latin -> Kannada dictionary mapping for standardization
# Standardizes common Kanglish roots while safely preserving English terminology
KANGLISH_TO_KANNADA_MAP: Dict[str, str] = {
    "nimma": "ನಿಮ್ಮ",
    "namma": "ನಮ್ಮ",
    "nanna": "ನನ್ನ",
    "neevu": "ನೀವು",
    "naanu": "ನಾನು",
    "grahakare": "ಗ್ರಾಹಕರೇ",
    "koodale": "ಕೂಡಲೇ",
    "thakshana": "ತಕ್ಷಣ",
    "thurthu": "ತುರ್ತು",
    "ivattu": "ಇವತ್ತು",
    "ivatte": "ಇವತ್ತೇ",
    "nale": "ನಾಳೆ",
    "naale": "ನಾಳೆ",
    "eega": "ಈಗ",
    "eegale": "ಈಗಲೇ",
    "madi": "ಮಾಡಿ",
    "maadi": "ಮಾಡಿ",
    "madbedi": "ಮಾಡಬೇಡಿ",
    "agide": "ಆಗಿದೆ",
    "aagide": "ಆಗಿದೆ",
    "agatte": "ಆಗತ್ತೆ",
    "aagatte": "ಆಗತ್ತೆ",
    "agutte": "ಆಗುತ್ತದೆ",
    "aagutte": "ಆಗುತ್ತದೆ",
    "aytu": "ಆಯಿತು",
    "aaythu": "ಆಯಿತು",
    "ide": "ಇದೆ",
    "illa": "ಇಲ್ಲ",
    "khate": "ಖಾತೆ",
    "khathe": "ಖಾತೆ",
    "hana": "ಹಣ",
    "namaskara": "ನಮಸ್ಕಾರ",
    "shubhashayagalu": "ಶುಭಾಶಯಗಳು",
    "abhinandanegalu": "ಅಭಿನಂದನೆಗಳು",
    "kelasa": "ಕೆಲಸ",
    "vilasa": "ವಿಳಾಸ",
    "danda": "ದಂಡ",
    "thapisalu": "ತಪ್ಪಿಸಲು",
}


@dataclass
class PreprocessedText:
    """Structured container for preprocessed text and linguistic metadata."""
    raw_text: str
    cleaned_text: str
    language: str  # 'kannada', 'english', 'code-mixed', 'unknown'
    script: str    # 'kannada', 'latin', 'mixed', 'unknown'
    kannada_char_ratio: float
    latin_char_ratio: float
    tokens: List[str]
    normalized_tokens: List[str]
    extracted_urls: List[str]
    is_empty: bool = False


class TextPreprocessor:
    """Deterministic regional-language text preprocessor and language detector."""

    def __init__(self):
        self.kannada_vocab = KANGLISH_VOCABULARY
        self.english_vocab = COMMON_ENGLISH_WORDS
        self.transliteration_map = KANGLISH_TO_KANNADA_MAP

    def sanitize_text(self, text: Optional[str]) -> str:
        """Sanitizes raw text, removes non-printable characters and normalizes Unicode."""
        if not text:
            return ""

        # Normalize Unicode to NFC (canonical decomposition followed by canonical composition)
        normalized = unicodedata.normalize("NFC", str(text))

        # Remove non-printable control characters
        sanitized = NON_PRINTABLE_REGEX.sub("", normalized)

        # Normalize excess whitespace
        sanitized = re.sub(r"\s+", " ", sanitized).strip()

        return sanitized

    def extract_urls(self, text: str) -> List[str]:
        """Extracts all URL patterns from input string."""
        if not text:
            return []
        return URL_PATTERN_REGEX.findall(text)

    def analyze_script(self, text: str) -> Tuple[str, float, float]:
        """Analyzes character script distribution.
        
        Returns:
            (script_type, kannada_ratio, latin_ratio)
            script_type is one of: 'kannada', 'latin', 'mixed', 'unknown'
        """
        if not text or not text.strip():
            return "unknown", 0.0, 0.0

        # Strip URLs and digits when assessing underlying linguistic script
        text_without_urls = URL_PATTERN_REGEX.sub("", text)
        alpha_chars = [c for c in text_without_urls if c.isalpha() or KANNADA_UNICODE_REGEX.match(c)]

        if not alpha_chars:
            return "unknown", 0.0, 0.0

        total_alpha = len(alpha_chars)
        kannada_count = sum(1 for c in alpha_chars if KANNADA_UNICODE_REGEX.match(c))
        latin_count = sum(1 for c in alpha_chars if LATIN_UNICODE_REGEX.match(c))

        kannada_ratio = kannada_count / total_alpha
        latin_ratio = latin_count / total_alpha

        if kannada_ratio >= 0.70:
            script_type = "kannada"
        elif latin_ratio >= 0.70:
            script_type = "latin"
        elif kannada_count > 0 and latin_count > 0:
            script_type = "mixed"
        elif kannada_ratio > latin_ratio:
            script_type = "kannada"
        elif latin_ratio > 0:
            script_type = "latin"
        else:
            script_type = "unknown"

        return script_type, round(kannada_ratio, 4), round(latin_ratio, 4)

    def detect_language(self, text: str) -> str:
        """Detects language conforming to api-specification.md enum.
        
        Returns exactly one of: 'kannada', 'english', 'code-mixed', 'unknown'.
        """
        if not text or not text.strip():
            return "unknown"

        script_type, kannada_ratio, latin_ratio = self.analyze_script(text)

        if script_type == "unknown":
            return "unknown"

        # Case 1: Dominant native Kannada script
        if script_type == "kannada" or kannada_ratio >= 0.60:
            # Check if there are significant English words interspersed
            words = re.findall(r"[a-zA-Z]+", text)
            english_word_count = sum(1 for w in words if w.lower() in self.english_vocab and len(w) > 2)
            if english_word_count >= 3:
                return "code-mixed"
            return "kannada"

        # Case 2: Mixed Kannada script and Latin script
        if script_type == "mixed":
            return "code-mixed"

        # Case 3: Latin script input (English, Transliterated Kannada, or Code-mixed)
        # Tokenize Latin words
        text_no_url = URL_PATTERN_REGEX.sub("", text)
        words = [w.lower() for w in re.findall(r"\b[a-zA-Z']+\b", text_no_url) if len(w) > 1]

        if not words:
            return "unknown"

        kannada_matches = 0
        english_matches = 0

        for w in words:
            is_kannada = w in self.kannada_vocab
            is_english = w in self.english_vocab

            if is_kannada and not is_english:
                kannada_matches += 1.5
            elif is_kannada and is_english:
                # Ambiguous words like 'is', 'me', 'in', 'to'
                kannada_matches += 0.5
                english_matches += 0.5
            elif is_english:
                english_matches += 1.0
            else:
                # Check for Kannada morphological suffixes: -alli, -inda, -annu, -ige, -ge, -beku, -agide
                if (w.endswith("alli") or w.endswith("inda") or w.endswith("annu") or 
                    w.endswith("galu") or w.endswith("agide") or w.endswith("agatte") or 
                    w.endswith("madi") or w.endswith("beku")):
                    kannada_matches += 1.2
                else:
                    # Unrecognized word, could be English noun/slang or transliterated
                    pass

        total_matches = kannada_matches + english_matches

        if total_matches == 0:
            return "unknown"

        kannada_score = kannada_matches / max(1, len(words))
        english_score = english_matches / max(1, len(words))

        # Decision rules
        if kannada_matches > 0 and english_matches > 0:
            if kannada_score >= 0.15 and english_score >= 0.20:
                return "code-mixed"
            elif kannada_matches >= 2.0 and english_matches >= 2.0:
                return "code-mixed"

        if kannada_matches > english_matches and kannada_score >= 0.20:
            return "kannada"

        if english_matches > 0:
            return "english"

        if kannada_matches > 0:
            return "kannada"

        return "unknown"

    def tokenize(self, text: str) -> List[str]:
        """Tokenizes text preserving Kannada words, Latin words, numbers, and URLs."""
        if not text:
            return []

        # Regex extracts URLs, Kannada character sequences, and Latin character sequences
        token_pattern = re.compile(
            r"https?://[^\s/$.?#].[^\s]*|"          # URLs
            r"[\u0C80-\u0CFF]+|"                   # Kannada script tokens
            r"[a-zA-Z0-9_']+|"                     # Latin alphanumeric tokens
            r"[^\s\w]"                             # Punctuation
        )
        tokens = token_pattern.findall(text)
        return [t.strip() for t in tokens if t.strip()]

    def normalize_tokens(self, tokens: List[str], language: str) -> List[str]:
        """Contextually normalizes tokens while preserving English keywords.
        
        Per ai-ml-system.md:
        - Do not blindly convert all Latin tokens to Kannada.
        - Preserve English tokens.
        - High-confidence contextual transliteration for known Kanglish words.
        """
        normalized = []
        for token in tokens:
            lower_token = token.lower()

            # Preserve URLs as-is
            if URL_PATTERN_REGEX.match(token):
                normalized.append(token)
                continue

            # If token is known English word, keep in Latin script
            if lower_token in self.english_vocab:
                normalized.append(lower_token)
                continue

            # If token is high-confidence transliterated Kannada, apply contextual mapping
            if language in ("kannada", "code-mixed") and lower_token in self.transliteration_map:
                normalized.append(self.transliteration_map[lower_token])
            else:
                # Preserve original token (low-confidence fallback)
                normalized.append(lower_token)

        return normalized

    def preprocess(self, text: Optional[str]) -> PreprocessedText:
        """Full deterministic preprocessing pipeline."""
        if not text or not str(text).strip():
            return PreprocessedText(
                raw_text="" if text is None else str(text),
                cleaned_text="",
                language="unknown",
                script="unknown",
                kannada_char_ratio=0.0,
                latin_char_ratio=0.0,
                tokens=[],
                normalized_tokens=[],
                extracted_urls=[],
                is_empty=True,
            )

        sanitized = self.sanitize_text(text)
        urls = self.extract_urls(sanitized)
        script_type, kannada_ratio, latin_ratio = self.analyze_script(sanitized)
        language = self.detect_language(sanitized)
        tokens = self.tokenize(sanitized)
        normalized_tokens = self.normalize_tokens(tokens, language)

        return PreprocessedText(
            raw_text=str(text),
            cleaned_text=sanitized,
            language=language,
            script=script_type,
            kannada_char_ratio=kannada_ratio,
            latin_char_ratio=latin_ratio,
            tokens=tokens,
            normalized_tokens=normalized_tokens,
            extracted_urls=urls,
            is_empty=False,
        )


# Global singleton instance for clean consumption across ML and backend
preprocessor = TextPreprocessor()
