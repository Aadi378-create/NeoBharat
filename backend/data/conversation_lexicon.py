"""Financial Conversation Lexicon for NeoBharat (Phase 7).

Provides focused keyword, phrase, and pattern dictionaries across English,
Hindi (Devanagari), and Hinglish (Romanized Hindi) for deterministic intent
detection and language recognition.
"""

from typing import Dict, List, Set

# Languages supported
LANGUAGES = {"ENGLISH", "HINDI", "HINGLISH", "UNKNOWN"}

# Topic categories mapped to intents
TOPICS = {
    "LOAN": {
        "SHOULD_I_TAKE_LOAN",
        "WHY_NO_LOAN",
        "LOAN_AFFORDABILITY",
        "LOAN_REPAYMENT",
    },
    "PAYMENTS": {
        "UPCOMING_PAYMENTS",
        "EMI_EXPLANATION",
        "PAYMENT_RISK",
    },
    "INVESTMENTS": {
        "WHY_RECOMMEND",
        "WHAT_IS_SIP",
        "HOW_MUCH_CAN_I_INVEST",
        "INVESTMENT_EXPLANATION",
    },
    "FRAUD": {
        "WHY_TRANSACTION_FLAGGED",
        "IS_THIS_FRAUD",
        "VERIFY_TRANSACTION",
        "UNKNOWN_TRANSACTION",
        "WHAT_IF_I_DID_NOT_MAKE_TRANSACTION",
    },
    "FINANCIAL_HEALTH": {
        "WHY_THIS_DECISION",
        "HOW_AM_I_DOING",
        "WHAT_SHOULD_I_DO",
        "WHY_IS_SPENDING_HIGH",
        "WHY_IS_SAVINGS_DECLINING",
        "HOW_CAN_I_SAVE_MORE",
    },
    "APPOINTMENT": {
        "BOOK_APPOINTMENT",
        "VIEW_APPOINTMENTS",
        "CANCEL_APPOINTMENT",
        "APPOINTMENT_HELP",
    },
    "GENERAL": {
        "GREETING",
        "THANKS",
        "HELP",
        "WHAT_CAN_YOU_DO",
    },
}

# Reverse mapping: intent -> topic
INTENT_TO_TOPIC: Dict[str, str] = {}
for topic, intents in TOPICS.items():
    for intent in intents:
        INTENT_TO_TOPIC[intent] = topic

# Common Hinglish lexical markers indicating romanized vernacular usage
HINGLISH_MARKERS: Set[str] = {
    "namaste", "namaskar", "pranam", "dhanyawad", "shukriya",
    "kyu", "kyun", "kyon", "nahi", "nahin", "chahiye", "chaahiye",
    "kya", "kese", "kaise", "mera", "meri", "mere", "mujhe",
    "mujhko", "humko", "aap", "aapne", "aapka", "aapki", "karna",
    "kare", "karu", "karoon", "karo", "hoga", "hogi", "hai",
    "hain", "hoon", "tha", "thi", "the", "batao", "bataiye",
    "samjhao", "dikhao", "paisa", "paise", "bachat", "kharcha",
    "kharch", "kitna", "kitni", "lena", "dena", "liye", "diya",
    "phir", "ab", "aage", "kuch", "sab", "wala", "wali",
    "milega", "milegi", "sakta", "sakti", "raha", "rahi",
    "maine", "usne", "yeh", "ye", "woh", "wo",
}

# Lexicon organized by intent
INTENT_LEXICON: Dict[str, Dict[str, List[str]]] = {
    # -------------------------------------------------------------
    # FRAUD & ANOMALY (Safety Critical)
    # -------------------------------------------------------------
    "UNKNOWN_TRANSACTION": {
        "english": [
            "i did not make this transaction",
            "i didn't make this transaction",
            "i did not do this transaction",
            "i didn't do this transaction",
            "did not make this payment",
            "didn't make this payment",
            "not my transaction",
            "unauthorized transaction",
            "i haven't made this",
            "i did not authorize",
        ],
        "hindi": [
            "मैंने यह लेनदेन नहीं किया",
            "मैंने यह ट्रांजैक्शन नहीं किया",
            "यह मेरा लेनदेन नहीं है",
            "यह भुगतान मैंने नहीं किया",
            "मैंने नहीं किया",
        ],
        "hinglish": [
            "maine nahi kiya",
            "maine ye transaction nahi kiya",
            "ye transaction maine nahi kiya",
            "ye payment maine nahi kiya",
            "ye maine nahi kiya",
            "mera transaction nahi hai",
            "maine nahi kiya hai",
        ],
    },
    "WHAT_IF_I_DID_NOT_MAKE_TRANSACTION": {
        "english": [
            "what if i did not make",
            "what if i didn't make",
            "what if i didn't do this",
            "if this wasn't me",
            "what if this transaction is not mine",
        ],
        "hindi": [
            "अगर मैंने यह नहीं किया तो क्या",
            "अगर यह लेनदेन मेरा नहीं है तो",
            "अगर मैंने भुगतान नहीं किया तो",
        ],
        "hinglish": [
            "agar maine nahi kiya toh",
            "agar maine transaction nahi kiya",
            "agar ye maine nahi kiya",
            "agar mera payment nahi hai toh",
        ],
    },
    "IS_THIS_FRAUD": {
        "english": [
            "is this fraud",
            "is this definitely fraud",
            "is this transaction fraudulent",
            "am i hacked",
            "was i hacked",
            "is my money stolen",
            "was my account compromised",
            "is this a scam",
            "has my account been hacked",
        ],
        "hindi": [
            "क्या यह धोखाधड़ी है",
            "क्या यह फ्रॉड है",
            "क्या मेरा खाता हैक हो गया",
            "क्या यह धोखा है",
            "क्या मेरे पैसे चोरी हो गए",
        ],
        "hinglish": [
            "kya ye fraud hai",
            "ye fraud hai kya",
            "kya ye scam hai",
            "kya account hack hua",
            "paisa chori ho gaya kya",
            "definitely fraud hai kya",
            "kya mera account hacked hai",
        ],
    },
    "WHY_TRANSACTION_FLAGGED": {
        "english": [
            "why was this transaction flagged",
            "why is transaction flagged",
            "why is this flagged",
            "why is this transaction suspicious",
            "is this transaction suspicious",
            "why suspicious transaction",
            "suspicious transaction reason",
            "why alert on transaction",
        ],
        "hindi": [
            "यह लेनदेन क्यों फ्लैग किया गया",
            "यह ट्रांजैक्शन संदिग्ध क्यों है",
            "क्या यह लेनदेन संदिग्ध है",
            "यह असामान्य क्यों है",
            "इस लेनदेन पर चेतावनी क्यों है",
        ],
        "hinglish": [
            "transaction flagged kyu hua",
            "ye transaction suspicious kyu hai",
            "flag kyu kiya",
            "unusual kyu hai",
            "suspicious kyu bola",
            "unusual transaction kyu",
        ],
    },
    "VERIFY_TRANSACTION": {
        "english": [
            "verify transaction",
            "how to verify transaction",
            "how do i verify this",
            "verify payment",
            "confirm transaction",
            "where do i confirm transaction",
        ],
        "hindi": [
            "लेनदेन सत्यापित करें",
            "ट्रांजैक्शन कैसे वेरीफाई करें",
            "पुष्टि कैसे करें",
            "लेनदेन की पुष्टि",
        ],
        "hinglish": [
            "transaction verify kaise kare",
            "kaise verify kare",
            "verify kaise karu",
            "confirm kaise kare",
            "transaction confirm kaise karu",
        ],
    },

    # -------------------------------------------------------------
    # LOANS & CREDIT (Safety Sensitive)
    # -------------------------------------------------------------
    "SHOULD_I_TAKE_LOAN": {
        "english": [
            "should i take a loan",
            "should i get a loan",
            "can i get a loan",
            "can i take a loan",
            "can i borrow more",
            "can i apply for loan",
            "should i borrow",
            "is it good to take a loan",
            "give me a loan",
            "approve my loan",
            "i want a loan",
            "can you give me loan",
        ],
        "hindi": [
            "क्या मुझे ऋण लेना चाहिए",
            "क्या मुझे लोन लेना चाहिए",
            "क्या मुझे लोन मिल सकता है",
            "क्या मैं लोन ले सकता हूँ",
            "मुझे लोन चाहिए",
            "क्या मुझे कर्ज लेना चाहिए",
        ],
        "hinglish": [
            "mujhe loan lena chahiye kya",
            "loan lena chahiye",
            "kya mujhe loan lena chahiye",
            "loan lena chahiye kya",
            "loan milega kya",
            "loan milega",
            "kya loan mil sakta hai",
            "loan apply kar sakta hu",
            "borrow karu kya",
            "mujhe loan chahiye",
            "loan le lu kya",
        ],
    },
    "WHY_NO_LOAN": {
        "english": [
            "why didn't you recommend a loan",
            "why did you not recommend a loan",
            "why no loan",
            "why not recommend loan",
            "why loan not recommended",
            "why did you refuse loan",
            "why reject loan",
            "why is credit blocked",
            "why cannot i get a loan",
            "why don't you offer loan",
        ],
        "hindi": [
            "आपने मुझे लोन क्यों नहीं सुझाया",
            "लोन क्यों नहीं दिया",
            "ऋण क्यों नहीं सुझाया",
            "लोन ब्लॉक क्यों है",
            "लोन क्यों नहीं मिल रहा",
            "मुझे लोन क्यों नहीं मिला",
            "लोन क्यों नहीं मिला",
        ],
        "hinglish": [
            "loan recommend kyu nahi kiya",
            "loan kyu nahi diya",
            "loan kyu nahi mila",
            "credit kyu block hai",
            "loan kyu mana kiya",
            "mujhe loan kyu nahi diya",
            "loan offer kyu nahi hai",
            "loan kyu nahi de rahe",
        ],
    },
    "LOAN_AFFORDABILITY": {
        "english": [
            "how much loan can i afford",
            "loan affordability",
            "what is my loan capacity",
            "my borrowing limit",
            "how much can i borrow",
            "what is my borrowing capacity",
        ],
        "hindi": [
            "मैं कितना ऋण ले सकता हूँ",
            "मेरी ऋण क्षमता क्या है",
            "मैं कितना कर्ज चुका सकता हूँ",
        ],
        "hinglish": [
            "kitna loan afford kar sakta hu",
            "meri loan capacity kitni hai",
            "kitna borrow kar sakta hu",
            "kitna udhar le sakta hu",
        ],
    },
    "LOAN_REPAYMENT": {
        "english": [
            "how to repay loan",
            "loan repayment options",
            "how can i pay off my debt",
            "clear my debt",
            "repay faster",
            "debt clearance",
        ],
        "hindi": [
            "ऋण का पुनर्भुगतान कैसे करें",
            "कर्ज कैसे चुकाएं",
            "लोन कैसे बंद करें",
        ],
        "hinglish": [
            "loan repay kaise kare",
            "karz kaise chukaye",
            "debt clear kaise kare",
            "loan jaldi kaise bhare",
        ],
    },

    # -------------------------------------------------------------
    # PAYMENTS & EMI
    # -------------------------------------------------------------
    "UPCOMING_PAYMENTS": {
        "english": [
            "upcoming payments",
            "what are my upcoming payments",
            "when is my next payment",
            "next emi due date",
            "upcoming dues",
            "upcoming bills",
            "next due payments",
        ],
        "hindi": [
            "आगामी भुगतान क्या हैं",
            "अगली ईएमआई कब है",
            "आने वाले भुगतान",
            "बकाया राशि क्या है",
        ],
        "hinglish": [
            "upcoming payments kya hai",
            "next emi kab hai",
            "aage ka payment",
            "aane wale payment",
            "upcoming emi kitni hai",
            "agli emi kab aayegi",
        ],
    },
    "EMI_EXPLANATION": {
        "english": [
            "how is emi calculated",
            "explain my emi",
            "what is my emi burden",
            "emi ratio explanation",
            "why is emi high",
            "emi breakdown",
        ],
        "hindi": [
            "ईएमआई की गणना कैसे की जाती है",
            "मेरी ईएमआई क्या है",
            "ईएमआई अनुपात क्या है",
            "ईएमआई इतनी ज्यादा क्यों है",
        ],
        "hinglish": [
            "emi kaise calculate hoti hai",
            "mera emi ratio kya hai",
            "emi itni high kyu hai",
            "emi ka matlab kya hai",
            "emi breakdown batao",
        ],
    },
    "PAYMENT_RISK": {
        "english": [
            "what is payment risk",
            "why is payment risk score high",
            "payment risk explanation",
            "payment risk score",
            "why high payment risk",
        ],
        "hindi": [
            "भुगतान जोखिम क्या है",
            "भुगतान जोखिम स्कोर क्यों बढ़ा है",
            "पेमेंट रिस्क क्या होता है",
        ],
        "hinglish": [
            "payment risk score kya hai",
            "payment risk high kyu hai",
            "payment risk ka matlab",
            "payment risk kyu aa raha hai",
        ],
    },

    # -------------------------------------------------------------
    # INVESTMENTS & WEALTH
    # -------------------------------------------------------------
    "WHY_RECOMMEND": {
        "english": [
            "why are you recommending this",
            "why did you recommend this",
            "why this product",
            "why recommend sip",
            "why recommend investment",
            "why recommend wealth builder",
            "why suggest sip",
        ],
        "hindi": [
            "आप यह क्यों सुझा रहे हैं",
            "यह सिफारिश क्यों की गई",
            "एसआईपी का सुझाव क्यों दिया",
            "यह प्रोडक्ट क्यों रेकमेंड किया",
        ],
        "hinglish": [
            "ye recommend kyu kiya",
            "recommend kyu kiya",
            "ye product kyu suggest kiya",
            "sip kyu recommend kiya",
            "why recommend this",
            "ye recommend kyu ho raha hai",
        ],
    },
    "WHAT_IS_SIP": {
        "english": [
            "what is sip",
            "explain sip",
            "what is systematic investment plan",
            "how does sip work",
            "tell me about sip",
            "what is wealth builder sip",
        ],
        "hindi": [
            "एसआईपी क्या है",
            "सिस्टमैटिक इन्वेस्टमेंट प्लान क्या होता है",
            "एसआईपी कैसे काम करता है",
            "एसआईपी के बारे में बताएं",
        ],
        "hinglish": [
            "sip kya hai",
            "sip kya hota hai",
            "sip kaise kaam karta hai",
            "sip ke baare me batao",
            "sip kya cheez hai",
        ],
    },
    "HOW_MUCH_CAN_I_INVEST": {
        "english": [
            "how much can i invest",
            "how much should i invest",
            "what amount should i invest",
            "how much to invest monthly",
            "what about monthly",
            "safe investment amount",
        ],
        "hindi": [
            "मैं कितना निवेश कर सकता हूँ",
            "मुझे कितना निवेश करना चाहिए",
            "हर महीने कितना निवेश करूं",
            "कितना पैसा लगाऊं",
        ],
        "hinglish": [
            "main kitna invest kar sakta hoon",
            "kitna invest karu",
            "kitna invest karna chahiye",
            "monthly kitna invest karu",
            "kitna daal sakta hu",
            "mujhe kitna invest karna chahiye",
        ],
    },
    "INVESTMENT_EXPLANATION": {
        "english": [
            "explain investment",
            "investment risks",
            "is investment safe",
            "tell me about this investment",
            "mutual fund risk",
        ],
        "hindi": [
            "निवेश के बारे में बताएं",
            "क्या निवेश सुरक्षित है",
            "निवेश जोखिम क्या हैं",
        ],
        "hinglish": [
            "investment ke baare me batao",
            "kya investment safe hai",
            "risk kya hai",
            "investment safe hai kya",
        ],
    },

    # -------------------------------------------------------------
    # FINANCIAL HEALTH & BUDGETING
    # -------------------------------------------------------------
    "WHY_THIS_DECISION": {
        "english": [
            "why am i seeing this",
            "why this decision",
            "explain this decision",
            "why did bank decide this",
            "why support decision",
            "what is this decision",
            "why this status",
        ],
        "hindi": [
            "मैं यह क्यों देख रहा हूँ",
            "यह निर्णय क्यों लिया गया",
            "इस फैसले का क्या मतलब है",
            "यह स्थिति क्यों दिखाई दे रही है",
        ],
        "hinglish": [
            "why am i seeing this",
            "ye decision kyu liya",
            "ye kyu dikha raha hai",
            "decision ka matlab kya hai",
            "ye decision kyu aaya",
            "ye status kyu hai",
        ],
    },
    "HOW_AM_I_DOING": {
        "english": [
            "how am i doing",
            "how are my finances",
            "what is my financial status",
            "how is my financial health",
            "check my finances",
            "how is my financial condition",
        ],
        "hindi": [
            "मेरी वित्तीय स्थिति कैसी है",
            "मेरा वित्तीय स्वास्थ्य कैसा है",
            "मेरे खाते की हालत कैसी है",
        ],
        "hinglish": [
            "meri financial health kaisi hai",
            "mera financial status kaisa hai",
            "sab theek chal raha hai kya",
            "mera status batao",
            "meri financial condition kaisi hai",
        ],
    },
    "WHAT_SHOULD_I_DO": {
        "english": [
            "what should i do next",
            "what should i do",
            "what is my next step",
            "next step for me",
            "how should i proceed",
            "and now",
            "what now",
        ],
        "hindi": [
            "मुझे आगे क्या करना चाहिए",
            "मेरा अगला कदम क्या होना चाहिए",
            "अब क्या करें",
            "आगे क्या करना है",
        ],
        "hinglish": [
            "what should i do next",
            "mujhe aage kya karna chahiye",
            "ab kya karu",
            "kya karna chahiye",
            "phir kya kare",
            "next step kya hai",
            "ab aage kya",
        ],
    },
    "WHY_IS_SPENDING_HIGH": {
        "english": [
            "why is my spending high",
            "why is spending high",
            "why expenses increased",
            "why spending spiked",
            "spending spike explanation",
            "why discretionary spending high",
        ],
        "hindi": [
            "मेरा खर्च इतना अधिक क्यों है",
            "खर्च क्यों बढ़ गया",
            "इतना खर्चा क्यों हुआ",
        ],
        "hinglish": [
            "mera spending itna high kyu hai",
            "spending high kyu hai",
            "kharcha itna kyu badha",
            "kharch kyu zyada hai",
            "kharcha kyu badh gaya",
        ],
    },
    "WHY_IS_SAVINGS_DECLINING": {
        "english": [
            "why are my savings declining",
            "why is savings decreasing",
            "why are savings dropping",
            "savings decline explanation",
            "why is savings down",
            "why savings dropping",
        ],
        "hindi": [
            "मेरी बचत क्यों कम हो रही है",
            "बचत क्यों घट रही है",
            "बचत में गिरावट क्यों आई",
        ],
        "hinglish": [
            "meri savings kyun kam ho rahi hai",
            "savings kam kyu ho rahi hai",
            "bachat kyu ghat rahi hai",
            "savings decline kyu hua",
            "meri bachat kam kyu hui",
        ],
    },
    "HOW_CAN_I_SAVE_MORE": {
        "english": [
            "how can i save more",
            "how to save money",
            "tips to save money",
            "improve my savings",
            "budgeting advice",
            "how to increase savings",
        ],
        "hindi": [
            "मैं अधिक बचत कैसे कर सकता हूँ",
            "पैसे कैसे बचाएं",
            "बचत कैसे बढ़ाएं",
            "बचत करने के तरीके",
        ],
        "hinglish": [
            "jyada bachat kaise kare",
            "paise kaise bachaye",
            "savings kaise badhaye",
            "save kaise karu",
            "paisa bachane ke tips",
        ],
    },

    # -------------------------------------------------------------
    # APPOINTMENT INTENTS
    # -------------------------------------------------------------
    "BOOK_APPOINTMENT": {
        "english": [
            "book appointment",
            "schedule appointment",
            "book an appointment",
            "talk to an advisor",
            "talk to advisor",
            "speak to an advisor",
            "speak with advisor",
            "meet an advisor",
            "book advisor",
            "talk to someone",
            "speak to someone",
            "schedule meeting",
            "book meeting",
            "consult advisor",
            "book consultation",
            "schedule consultation",
            "consultation",
            "financial advisor appointment",
            "security specialist appointment",
            "book a session",
        ],
        "hindi": [
            "अपॉइंटमेंट बुक करो",
            "अपॉइंटमेंट बुक करें",
            "सलाहकार से बात करनी है",
            "सलाहकार से मिलना है",
            "बैंकिंग सलाहकार से बात करें",
            "मीटिंग तय करो",
            "अपॉइंटमेंट लेना है",
            "किसी से बात करनी है",
            "सलाहकार से परामर्श",
        ],
        "hinglish": [
            "appointment book kardo",
            "appointment book karo",
            "appointment book karna hai",
            "advisor se baat karni hai",
            "advisor se baat karna hai",
            "advisor se milna hai",
            "meeting schedule kardo",
            "meeting book karo",
            "talk to someone",
            "appointment lena hai",
            "advisor appointment",
            "consultation book karo",
        ],
    },
    "VIEW_APPOINTMENTS": {
        "english": [
            "show my appointments",
            "view appointments",
            "check my appointments",
            "my booked appointments",
            "scheduled appointments",
            "show appointments",
            "when is my appointment",
            "view my meetings",
        ],
        "hindi": [
            "मेरी अपॉइंटमेंट दिखाओ",
            "अपॉइंटमेंट चेक करो",
            "मेरी मीटिंग कब है",
            "मेरी अपॉइंटमेंट",
            "बुकिंग दिखाओ",
        ],
        "hinglish": [
            "meri appointment dikhao",
            "appointment check karo",
            "booked appointment",
            "show appointments",
            "meeting kab hai",
            "check appointment",
        ],
    },
    "CANCEL_APPOINTMENT": {
        "english": [
            "cancel appointment",
            "cancel my appointment",
            "reschedule appointment",
            "delete appointment",
            "drop appointment",
        ],
        "hindi": [
            "अपॉइंटमेंट रद्द करो",
            "अपॉइंटमेंट कैंसिल करो",
            "मीटिंग रद्द करो",
            "अपॉइंटमेंट हटाओ",
        ],
        "hinglish": [
            "appointment cancel kardo",
            "appointment cancel karo",
            "appointment radd karo",
            "cancel appointment",
            "meeting cancel kardo",
        ],
    },
    "APPOINTMENT_HELP": {
        "english": [
            "how to book appointment",
            "how to book an appointment",
            "how to schedule appointment",
            "how do appointments work",
            "advisor assistance",
            "need advisor help",
            "appointment process",
            "appointment help",
        ],
        "hindi": [
            "अपॉइंटमेंट कैसे बुक करें",
            "सलाहकार से कैसे बात करें",
            "सलाहकार सहायता",
            "अपॉइंटमेंट प्रक्रिया",
        ],
        "hinglish": [
            "appointment kaise book kare",
            "advisor se kaise baat kare",
            "advisor help chahiye",
            "appointment process kya hai",
        ],
    },

    # -------------------------------------------------------------
    # GENERAL INTENTS
    # -------------------------------------------------------------
    "GREETING": {
        "english": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
        "hindi": ["नमस्ते", "प्रणाम", "नमस्कार"],
        "hinglish": ["namaste", "pranam", "namaskar", "kaise ho", "kese ho", "kya haal hai"],
    },
    "THANKS": {
        "english": ["thank you", "thanks", "thanks a lot", "thank you so much", "appreciate it"],
        "hindi": ["धन्यवाद", "शुक्रिया", "बहुत बहुत धन्यवाद"],
        "hinglish": ["dhanyawad", "shukriya", "thank u", "thx", "shukriya bahut"],
    },
    "HELP": {
        "english": ["help", "can you help me", "i need help", "support", "assist me"],
        "hindi": ["मदद", "सहायता", "मुझे मदद चाहिए", "सहायता करें"],
        "hinglish": ["help chahiye", "madad chahiye", "help karo", "kuch help karo"],
    },
    "WHAT_CAN_YOU_DO": {
        "english": ["what can you do", "what are your features", "how do you work", "who are you"],
        "hindi": ["आप क्या कर सकते हैं", "आप कौन हैं", "आप कैसे काम करते हैं"],
        "hinglish": ["kya kar sakte ho", "aap kya karte ho", "tum kaun ho", "kya kya kar sakte ho"],
    },
}
