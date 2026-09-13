"""Deterministic Intent Detection and Language Recognition for NeoBharat (Phase 7).

Provides rule-based, deterministic classification of conversational banking
queries across English, Hindi, and Hinglish. Uses normalized matching against
the financial conversation lexicon and respects safety-first intent priority.
"""

import re
import unicodedata
from typing import Any, Dict, List, Optional, Set, Tuple

from backend.data.conversation_lexicon import (
    HINGLISH_MARKERS,
    INTENT_LEXICON,
    INTENT_TO_TOPIC,
    LANGUAGES,
)

# Priority order for intent resolution (safety-critical first)
INTENT_PRIORITY: List[str] = [
    "WHAT_IF_I_DID_NOT_MAKE_TRANSACTION",
    "UNKNOWN_TRANSACTION",
    "IS_THIS_FRAUD",
    "WHY_TRANSACTION_FLAGGED",
    "VERIFY_TRANSACTION",
    "SHOULD_I_TAKE_LOAN",
    "WHY_NO_LOAN",
    "LOAN_AFFORDABILITY",
    "LOAN_REPAYMENT",
    "LOAN_COST_INQUIRY",
    "EMI_EXPLANATION",
    "PAYMENT_RISK",
    "UPCOMING_PAYMENTS",
    "WHY_IS_SPENDING_HIGH",
    "WHY_IS_SAVINGS_DECLINING",
    "HOW_CAN_I_SAVE_MORE",
    "WHY_RECOMMEND",
    "WHAT_IS_SIP",
    "HOW_MUCH_CAN_I_INVEST",
    "INVESTMENT_EXPLANATION",
    "WHY_THIS_DECISION",
    "WHAT_SHOULD_I_DO",
    "HOW_AM_I_DOING",
    "APPOINTMENT_HELP",
    "CANCEL_APPOINTMENT",
    "VIEW_APPOINTMENTS",
    "BOOK_APPOINTMENT",
    "GREETING",
    "THANKS",
    "HELP",
    "WHAT_CAN_YOU_DO",
]

# Mapping from intent to primary response strategy
STRATEGY_MAP: Dict[str, str] = {
    # Explanation strategies
    "WHY_NO_LOAN": "EXPLANATION",
    "LOAN_AFFORDABILITY": "EXPLANATION",
    "LOAN_REPAYMENT": "EXPLANATION",
    "LOAN_COST_INQUIRY": "EXPLANATION",
    "EMI_EXPLANATION": "EXPLANATION",
    "PAYMENT_RISK": "EXPLANATION",
    "WHY_IS_SPENDING_HIGH": "EXPLANATION",
    "WHY_IS_SAVINGS_DECLINING": "EXPLANATION",
    "INVESTMENT_EXPLANATION": "EXPLANATION",
    "WHAT_IS_SIP": "EXPLANATION",
    "WHY_THIS_DECISION": "EXPLANATION",
    "HOW_AM_I_DOING": "EXPLANATION",

    # Appointment strategies
    "BOOK_APPOINTMENT": "ACTION_PROMPT",
    "VIEW_APPOINTMENTS": "INQUIRY",
    "CANCEL_APPOINTMENT": "ACTION_PROMPT",
    "APPOINTMENT_HELP": "GUIDANCE",

    # Guidance strategies
    "SHOULD_I_TAKE_LOAN": "GUIDANCE",
    "WHAT_SHOULD_I_DO": "GUIDANCE",
    "HOW_CAN_I_SAVE_MORE": "GUIDANCE",
    "UPCOMING_PAYMENTS": "GUIDANCE",
    "HOW_MUCH_CAN_I_INVEST": "GUIDANCE",

    # Verification strategies
    "UNKNOWN_TRANSACTION": "VERIFICATION",
    "WHAT_IF_I_DID_NOT_MAKE_TRANSACTION": "VERIFICATION",
    "IS_THIS_FRAUD": "VERIFICATION",
    "WHY_TRANSACTION_FLAGGED": "VERIFICATION",
    "VERIFY_TRANSACTION": "VERIFICATION",

    # Recommendation strategies
    "WHY_RECOMMEND": "RECOMMENDATION",

    # General strategies
    "GREETING": "GREETING",
    "THANKS": "CLARIFICATION",
    "HELP": "CLARIFICATION",
    "WHAT_CAN_YOU_DO": "CLARIFICATION",
    "UNKNOWN": "CLARIFICATION",
    "UNSUPPORTED": "CLARIFICATION",
}

# Regex to detect Devanagari Unicode block (Hindi)
_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")

# Ambiguous short follow-up patterns
_WHY_FOLLOWUP = re.compile(r"^(\s*(why|kyu|kyun|kyon|क्यों|क्यों\s*रे|aisa\s*kyu)\s*[?\.!]*\s*)+$", re.IGNORECASE)
_WHAT_NOW_FOLLOWUP = re.compile(r"^(\s*(what\s+now|and\s+now|phir|ab\s+kya|phir\s+kya|आगे\s*क्या|अब\s*क्या)\s*[?\.!]*\s*)+$", re.IGNORECASE)
_MONTHLY_FOLLOWUP = re.compile(r"^(\s*(what\s+about\s+monthly|monthly|har\s+mahine|हर\s+महीने|monthly\s+kitna)\s*[?\.!]*\s*)+$", re.IGNORECASE)
_COST_FOLLOWUP = re.compile(
    r"^(\s*(exact\s+amount|exact\s+interest|exact\s+cost|exact\s+emi|exact\s+rate|what\s+would\s+i\s+pay|how\s+much\s+interest|what\s+is\s+the\s+interest|interest\s+rate|how\s+much\s+to\s+pay|how\s+much\s+will\s+it\s+cost|kitna\s+byaaj|byaaj\s+kitna|kitna\s+dena\s+hoga|kitna\s+bharna\s+padega|kitna\s+lagega|kitna\s+paisa\s+lagega|kitna\s+interest|interest\s+kitna|kitni\s+emi|सटीक\s*राशि|कितना\s*ब्याज|ब्याज\s*कितना|कितनी\s*ईएमआई)\s*[?\.!]*\s*)+$",
    re.IGNORECASE,
)


def normalize_message(text: str) -> str:
    """Normalize a message for intent and language detection.

    Steps:
    1. Unicode NFC normalization.
    2. Lowercase Latin characters while preserving Devanagari.
    3. Normalize punctuation to spaces, preserving word characters and Hindi script.
    4. Collapse multiple whitespace characters into single space.
    5. Strip leading/trailing whitespace.

    Args:
        text: Raw user message.

    Returns:
        str: Cleaned, normalized string.
    """
    if not text:
        return ""

    # 1. Normalize Unicode
    normalized = unicodedata.normalize("NFC", text)

    # 2. Lowercase Latin text
    normalized = normalized.lower()

    # 3. Replace punctuation with space, preserving alphanumeric and Devanagari
    # In regex, [^\w\s\u0900-\u097F] matches punctuation and symbols
    normalized = re.sub(r"[^\w\s\u0900-\u097F]", " ", normalized)

    # 4. Collapse whitespace
    normalized = re.sub(r"\s+", " ", normalized).strip()

    return normalized


def detect_language(text: str) -> str:
    """Detect whether a message is in English, Hindi, or Hinglish.

    Classification logic:
    - If message contains Devanagari characters -> HINDI.
    - If Latin script contains Hinglish lexical markers -> HINGLISH.
    - If Latin script without Hinglish markers -> ENGLISH.
    - If empty or unrecognized -> UNKNOWN.

    Args:
        text: Raw or normalized user message.

    Returns:
        str: 'ENGLISH', 'HINDI', 'HINGLISH', or 'UNKNOWN'.
    """
    if not text or not text.strip():
        return "UNKNOWN"

    # 1. Devanagari presence indicates Hindi
    if _DEVANAGARI_RE.search(text):
        return "HINDI"

    # 2. Tokenize Latin words
    normalized = normalize_message(text)
    words = set(normalized.split())
    if not words:
        return "UNKNOWN"

    # Check for Hinglish markers
    hinglish_matches = words.intersection(HINGLISH_MARKERS)
    if hinglish_matches:
        return "HINGLISH"

    # Also check multi-word Hinglish patterns from lexicon
    lower_raw = text.lower()
    for marker in ["kyu nahi", "kyun nahi", "lena chahiye", "kya karu", "maine nahi kiya"]:
        if marker in lower_raw:
            return "HINGLISH"

    return "ENGLISH"


def is_followup_message(normalized: str) -> Optional[str]:
    """Check if the message is an ambiguous short follow-up query.

    Returns:
        'WHY' if asking why, 'WHAT_NOW' if asking what now/next, 'MONTHLY' if asking about monthly,
        or None if not an ambiguous follow-up.
    """
    if _WHY_FOLLOWUP.match(normalized):
        return "WHY"
    if _WHAT_NOW_FOLLOWUP.match(normalized):
        return "WHAT_NOW"
    if _MONTHLY_FOLLOWUP.match(normalized):
        return "MONTHLY"
    if _COST_FOLLOWUP.match(normalized):
        return "LOAN_COST"
    return None


def detect_intent(
    message: str,
    conversation_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Detect user intent, language, and response strategy deterministically.

    Args:
        message: Raw conversational text from user.
        conversation_context: Optional previous conversation state for customer
                              (e.g., last_intent, last_topic, last_decision).

    Returns:
        Dict[str, Any] containing:
        - intent: str (e.g. 'WHY_NO_LOAN')
        - language: str ('ENGLISH', 'HINDI', 'HINGLISH', 'UNKNOWN')
        - confidence: float (0.0 to 1.0)
        - matched_terms: List[str]
        - topic: str (e.g. 'LOAN', 'FRAUD', 'PAYMENTS', etc.)
        - response_strategy: str ('EXPLANATION', 'GUIDANCE', etc.)
    """
    normalized = normalize_message(message)
    language = detect_language(message)

    # 1. Handle ambiguous follow-ups if context exists
    if conversation_context and is_followup_message(normalized):
        followup_type = is_followup_message(normalized)
        last_topic = conversation_context.get("last_topic")
        last_intent = conversation_context.get("last_intent")

        if followup_type == "WHY":
            if last_topic == "LOAN" or last_intent in {"SHOULD_I_TAKE_LOAN", "WHY_NO_LOAN"}:
                return {
                    "intent": "WHY_NO_LOAN",
                    "language": language,
                    "confidence": 0.90,
                    "matched_terms": [normalized, "context:" + str(last_intent)],
                    "topic": "LOAN",
                    "response_strategy": STRATEGY_MAP["WHY_NO_LOAN"],
                }
            if last_topic == "FRAUD" or last_intent in {"IS_THIS_FRAUD", "WHY_TRANSACTION_FLAGGED", "UNKNOWN_TRANSACTION"}:
                return {
                    "intent": "WHY_TRANSACTION_FLAGGED",
                    "language": language,
                    "confidence": 0.90,
                    "matched_terms": [normalized, "context:" + str(last_intent)],
                    "topic": "FRAUD",
                    "response_strategy": STRATEGY_MAP["WHY_TRANSACTION_FLAGGED"],
                }
            if last_topic == "INVESTMENTS" or last_intent in {"WHY_RECOMMEND", "WHAT_IS_SIP"}:
                return {
                    "intent": "WHY_RECOMMEND",
                    "language": language,
                    "confidence": 0.90,
                    "matched_terms": [normalized, "context:" + str(last_intent)],
                    "topic": "INVESTMENTS",
                    "response_strategy": STRATEGY_MAP["WHY_RECOMMEND"],
                }
            # Generic fallback why -> WHY_THIS_DECISION
            return {
                "intent": "WHY_THIS_DECISION",
                "language": language,
                "confidence": 0.85,
                "matched_terms": [normalized, "context:followup"],
                "topic": "FINANCIAL_HEALTH",
                "response_strategy": STRATEGY_MAP["WHY_THIS_DECISION"],
            }

        if followup_type == "WHAT_NOW":
            if last_topic == "FRAUD":
                return {
                    "intent": "VERIFY_TRANSACTION",
                    "language": language,
                    "confidence": 0.90,
                    "matched_terms": [normalized, "context:" + str(last_topic)],
                    "topic": "FRAUD",
                    "response_strategy": STRATEGY_MAP["VERIFY_TRANSACTION"],
                }
            return {
                "intent": "WHAT_SHOULD_I_DO",
                "language": language,
                "confidence": 0.90,
                "matched_terms": [normalized, "context:" + str(last_topic)],
                "topic": "FINANCIAL_HEALTH",
                "response_strategy": STRATEGY_MAP["WHAT_SHOULD_I_DO"],
            }

        if followup_type == "MONTHLY":
            if last_topic == "INVESTMENTS":
                return {
                    "intent": "HOW_MUCH_CAN_I_INVEST",
                    "language": language,
                    "confidence": 0.90,
                    "matched_terms": [normalized, "context:" + str(last_topic)],
                    "topic": "INVESTMENTS",
                    "response_strategy": STRATEGY_MAP["HOW_MUCH_CAN_I_INVEST"],
                }
            if last_topic == "PAYMENTS":
                return {
                    "intent": "EMI_EXPLANATION",
                    "language": language,
                    "confidence": 0.85,
                    "matched_terms": [normalized, "context:" + str(last_topic)],
                    "topic": "PAYMENTS",
                    "response_strategy": STRATEGY_MAP["EMI_EXPLANATION"],
                }

        if followup_type == "LOAN_COST":
            return {
                "intent": "LOAN_COST_INQUIRY",
                "language": language,
                "confidence": 0.95,
                "matched_terms": [normalized, "context:" + str(last_topic or last_intent or "LOAN")],
                "topic": "LOAN",
                "response_strategy": STRATEGY_MAP["LOAN_COST_INQUIRY"],
            }

    # 2. Score message against intent lexicon
    matched_intents: Dict[str, Tuple[float, List[str]]] = {}

    for intent, lang_dict in INTENT_LEXICON.items():
        best_intent_score = 0.0
        best_terms: List[str] = []

        for lang_key, phrases in lang_dict.items():
            for phrase in phrases:
                norm_phrase = normalize_message(phrase)
                if not norm_phrase:
                    continue

                # Exact full match
                if normalized == norm_phrase:
                    score = 1.0
                # Phrase substring match
                elif norm_phrase in normalized:
                    # Longer phrase match gives higher confidence
                    score = min(0.95, 0.70 + (len(norm_phrase) / max(len(normalized), 1)) * 0.25)
                # Word-level overlap
                else:
                    phrase_words = set(norm_phrase.split())
                    norm_words = set(normalized.split())
                    if phrase_words and phrase_words.issubset(norm_words):
                        score = 0.80
                    else:
                        continue

                if score > best_intent_score:
                    best_intent_score = score
                    best_terms = [phrase]

        if best_intent_score >= 0.70:
            matched_intents[intent] = (best_intent_score, best_terms)

    # 3. Resolve matched intents using priority order
    for priority_intent in INTENT_PRIORITY:
        if priority_intent in matched_intents:
            resolved_intent = priority_intent
            # Context-aware override for ambiguous actions (e.g. 'what should i do' in fraud context)
            if conversation_context and conversation_context.get("last_topic") == "FRAUD":
                if resolved_intent in ("WHAT_SHOULD_I_DO", "WHAT_CAN_YOU_DO", "HELP"):
                    resolved_intent = "VERIFY_TRANSACTION"

            score, terms = matched_intents[priority_intent]
            topic = INTENT_TO_TOPIC.get(resolved_intent, "GENERAL")
            strategy = STRATEGY_MAP.get(resolved_intent, "EXPLANATION")
            return {
                "intent": resolved_intent,
                "language": language,
                "confidence": round(score, 2),
                "matched_terms": terms,
                "topic": topic,
                "response_strategy": strategy,
            }

    # 4. Fallback if no specific intent matched
    # Check for general financial query keywords
    if any(w in normalized for w in ["finance", "status", "review", "khata", "paise", "rupaye"]):
        return {
            "intent": "HOW_AM_I_DOING",
            "language": language,
            "confidence": 0.60,
            "matched_terms": ["financial_keywords"],
            "topic": "FINANCIAL_HEALTH",
            "response_strategy": STRATEGY_MAP["HOW_AM_I_DOING"],
        }

    return {
        "intent": "UNKNOWN",
        "language": language,
        "confidence": 0.0,
        "matched_terms": [],
        "topic": "GENERAL",
        "response_strategy": "CLARIFICATION",
    }
