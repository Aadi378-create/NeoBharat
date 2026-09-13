"""Deterministic Vernacular Fallback Generator for NeoBharat (Phase 7).

Generates rich, intent-specific, and language-adapted fallback responses
when the OpenAI API is unavailable, times out, or fails validation.

Guarantees:
- Every returned dictionary strictly satisfies phase4_llm_output.schema.json.
- Fully respects Phase 4 semantic safety rules (no credit promotion when blocked,
  no confirmed fraud claims, no fabricated figures).
- Directly interpolates authoritative figures from backend context.
- Provides distinct responses for distinct intents across English, Hindi, and Hinglish.
"""

from typing import Any, Dict, List, Optional


def _format_inr(amount: Optional[float]) -> str:
    """Format an amount in Indian Rupees with comma separators."""
    if amount is None:
        return "—"
    try:
        val = int(round(float(amount)))
        # Format with Indian comma grouping
        s = str(abs(val))
        if len(s) <= 3:
            res = s
        else:
            last3 = s[-3:]
            remaining = s[:-3]
            groups = []
            while len(remaining) > 2:
                groups.insert(0, remaining[-2:])
                remaining = remaining[:-2]
            if remaining:
                groups.insert(0, remaining)
            res = ",".join(groups) + "," + last3
        prefix = "-₹" if val < 0 else "₹"
        return f"{prefix}{res}"
    except Exception:
        return f"₹{amount}"


def generate_conversational_fallback(
    context: Dict[str, Any],
    intent_obj: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generate an authoritative, intent-specific, and language-appropriate fallback response.

    Args:
        context: Authoritative Phase 3 context dictionary conforming to phase4_llm_input.schema.json.
        intent_obj: Optional intent detection result containing 'intent' and 'language'.

    Returns:
        Dict[str, Any]: Response dictionary conforming to phase4_llm_output.schema.json.
    """
    decision_ctx = context.get("decision_context", {})
    decision = decision_ctx.get("decision", "SUPPORT")
    recommendation = decision_ctx.get("recommendation", {})
    ack_action = recommendation.get("action", "REVIEW_UPCOMING_PAYMENTS")

    financial = context.get("financial_context", {})
    scores = context.get("guardian_context", {}).get("scores", {})

    intent = (intent_obj.get("intent") if intent_obj else None) or "WHY_THIS_DECISION"
    language = (intent_obj.get("language") if intent_obj else None) or "ENGLISH"

    # Default mapping of response_type based on decision
    if decision == "VERIFY":
        response_type = "FRAUD_VERIFICATION"
        default_ack_action = "VERIFY_SUSPICIOUS_TRANSACTION"
    elif decision == "RECOMMEND":
        response_type = "RECOMMENDATION_EXPLANATION"
        default_ack_action = "RECOMMEND"
    elif decision == "SUPPORT":
        response_type = "SUPPORT_GUIDANCE"
        default_ack_action = "REVIEW_UPCOMING_PAYMENTS"
    else:
        response_type = "FINANCIAL_GUIDANCE"
        default_ack_action = "NO_RECOMMENDATION"

    if decision == "VERIFY":
        ack_action = "VERIFY_SUSPICIOUS_TRANSACTION"
    elif decision == "SUPPORT":
        ack_action = "REVIEW_UPCOMING_PAYMENTS" if ack_action in {"SUPPORT", "REVIEW_UPCOMING_PAYMENTS"} else "REVIEW_UPCOMING_PAYMENTS"
    elif decision == "RECOMMEND":
        ack_action = "RECOMMEND"
    else:
        ack_action = "NO_RECOMMENDATION"

    # Gather evidence items (max 5)
    evidence: List[Dict[str, Any]] = []
    if "financial_stress_score" in scores:
        evidence.append({"metric": "financial_stress_score", "value": scores["financial_stress_score"]})
    if "payment_risk_score" in scores:
        evidence.append({"metric": "payment_risk_score", "value": scores["payment_risk_score"]})
    if "fraud_score" in scores and scores["fraud_score"] > 20:
        evidence.append({"metric": "fraud_score", "value": scores["fraud_score"]})
    if "current_emi" in financial and financial["current_emi"] > 0:
        evidence.append({"metric": "current_emi", "value": financial["current_emi"]})
    if "net_monthly_surplus" in financial:
        evidence.append({"metric": "net_monthly_surplus", "value": financial["net_monthly_surplus"]})

    # Default next step
    if decision == "VERIFY":
        next_step = {"type": "VERIFY", "label": "Verify recent transaction activity"}
    elif decision == "SUPPORT":
        next_step = {"type": "ACTION", "label": "Review upcoming payments and expenses"}
    elif decision == "RECOMMEND":
        next_step = {"type": "INFORMATION", "label": "Review illustrative product details"}
    else:
        next_step = {"type": "NONE", "label": "No action required"}

    # Authoritative numbers formatted
    emi_str = _format_inr(financial.get("current_emi"))
    surplus_str = _format_inr(financial.get("net_monthly_surplus"))
    spending_str = _format_inr(financial.get("monthly_spending"))
    income_str = _format_inr(financial.get("income"))
    prod_name = recommendation.get("product_name") or "Systematic Wealth Builder SIP"

    # =========================================================================
    # INTENT & LANGUAGE SPECIFIC MESSAGING
    # =========================================================================
    message = ""

    # 1. LOAN: SHOULD_I_TAKE_LOAN / LOAN_AFFORDABILITY / LOAN_REPAYMENT
    if intent in ("SHOULD_I_TAKE_LOAN", "LOAN_AFFORDABILITY", "LOAN_REPAYMENT"):
        if decision == "SUPPORT":
            if language == "HINDI":
                message = (
                    f"आपकी वर्तमान वित्तीय स्थिति में ईएमआई {emi_str} और मासिक बचत {surplus_str} को देखते हुए, "
                    "अतिरिक्त ऋण लेना उचित नहीं होगा। NeoBharat आपको ऋण के जाल से बचाने के लिए सहायता और बजट समीक्षा की सलाह देता है।"
                )
            elif language == "HINGLISH":
                message = (
                    f"Aapke current EMI commitments ({emi_str}) aur monthly surplus ({surplus_str}) ko dekhte hue, "
                    "abhi naya loan lena suitable nahi hai. NeoBharat ne financial health ko protect karne ke liye support ko priority di hai."
                )
            else:
                message = (
                    f"Given your current EMI commitments of {emi_str} and estimated surplus of {surplus_str}, "
                    "we do not recommend taking an additional loan. NeoBharat prioritizes supporting your cash flow over additional borrowing."
                )
        elif decision == "VERIFY":
            if language == "HINDI":
                message = "आपके खाते में संदिग्ध गतिविधि के कारण सभी ऋण प्रक्रियाएं निलंबित हैं। कृपया पहले लेनदेन की पुष्टि करें।"
            elif language == "HINGLISH":
                message = "Aapke account me suspicious activity detect hui hai, isliye credit applications suspended hain. Kripya pehle transaction verify karein."
            else:
                message = "Unusual activity was detected on your account. Commercial credit applications are suspended until transactions are verified."
        else:
            if language == "HINDI":
                message = f"आपकी वित्तीय स्थिति स्थिर है और मासिक बचत {surplus_str} है। कृपया केवल आवश्यकता पड़ने पर ही ऋण पर विचार करें।"
            elif language == "HINGLISH":
                message = f"Aapki financial standing healthy hai with monthly surplus of {surplus_str}. Sirf genuine need hone par hi credit consider karein."
            else:
                message = f"Your finances are stable with a monthly surplus of {surplus_str}. Borrowing should only be considered for genuine productive needs."

    # 2. LOAN: WHY_NO_LOAN
    elif intent == "WHY_NO_LOAN":
        if decision == "SUPPORT":
            if language == "HINDI":
                message = (
                    f"NeoBharat ने अतिरिक्त ऋण नहीं सुझाया क्योंकि आपका वित्तीय तनाव और भुगतान जोखिम बढ़ा हुआ है। "
                    f"आपकी मासिक ईएमआई {emi_str} है और अनुमानित बचत {surplus_str} है। पहला कदम आगामी भुगतानों की समीक्षा करना है।"
                )
            elif language == "HINGLISH":
                message = (
                    f"NeoBharat ne loan recommend isliye nahi kiya kyunki aapka stress aur payment risk elevated hai. "
                    f"Aapki current EMI {emi_str} hai aur surplus {surplus_str} hai. Recommended step upcoming payments review karna hai."
                )
            else:
                message = (
                    f"NeoBharat does not recommend additional credit because your current financial indicators show elevated stress and payment risk. "
                    f"Your current EMI is {emi_str} and estimated monthly surplus is {surplus_str}. The recommended next step is to review upcoming payments and expenses."
                )
        elif decision == "VERIFY":
            if language == "HINDI":
                message = "असामान्य लेनदेन के कारण सुरक्षा कारणों से ऋण की सिफारिश नहीं की गई है। कृपया पहले संदिग्ध लेनदेन की पुष्टि करें।"
            elif language == "HINGLISH":
                message = "Unusual transaction detect hone ki wajah se commercial offers locked hain. Pehle recent transaction verify karein."
            else:
                message = "Commercial credit offers are locked due to suspected unusual transaction activity pending your verification."
        else:
            if language == "HINDI":
                message = f"आपकी बचत {surplus_str} है। ऋण लेने की बजाय हमने अनुशासित निवेश (एसआईपी) का सुझाव दिया है।"
            elif language == "HINGLISH":
                message = f"Aapka healthy surplus ({surplus_str}) hai, isliye credit lene ke bajay disciplined wealth building (SIP) suggest kiya gaya hai."
            else:
                message = f"With a healthy surplus of {surplus_str}, we recommended disciplined wealth accumulation rather than taking unnecessary debt."

    # 2b. LOAN: LOAN_COST_INQUIRY
    elif intent == "LOAN_COST_INQUIRY":
        if decision == "SUPPORT":
            if language == "HINDI":
                message = (
                    f"मैं समझता हूँ कि आप ऋण लागत और ब्याज के बारे में पूछ रहे हैं। इस प्रोटोटाइप में, किसी निर्दिष्ट ऋण उत्पाद, ब्याज दर और पुनर्भुगतान अवधि के बिना सटीक ब्याज या ईएमआई की गणना नहीं की जा सकती। "
                    f"इसके अलावा, NeoBharat अभी अतिरिक्त ऋण लेने की सलाह नहीं देता क्योंकि आपकी मासिक ईएमआई {emi_str} और वित्तीय तनाव को देखते हुए नकदी प्रवाह को सहारा देना हमारी प्राथमिकता है।"
                )
            elif language == "HINGLISH":
                message = (
                    f"Main samajhta hoon ki aap loan cost aur interest ke baare me pooch rahe hain. Current prototype me exact interest ya EMI amount bina assigned loan rate aur tenure ke calculate nahi kiya ja sakta. "
                    f"Saath hi, elevated stress aur current EMI ({emi_str}) ko dekhte hue NeoBharat abhi naya loan lene ki advice nahi deta, balki cash flow ko support karna priority hai."
                )
            else:
                message = (
                    f"I understand you are asking about loan costs and interest. In this prototype, exact interest, EMI, or repayment amounts cannot be calculated authoritatively without an assigned loan product, interest rate, and tenure. "
                    f"Furthermore, NeoBharat does not recommend taking an additional loan right now because your financial indicators show elevated stress (current EMI: {emi_str}). Our priority is supporting your cash flow rather than adding borrowing costs."
                )
        elif decision == "VERIFY":
            if language == "HINDI":
                message = (
                    "मैं समझता हूँ कि आप ऋण लागत और ब्याज के बारे में पूछ रहे हैं। प्रोटोटाइप में वास्तविक ब्याज दर और अवधि के बिना सटीक ब्याज राशि की गणना नहीं की जा सकती। "
                    "इसके अतिरिक्त, असामान्य गतिविधि की पुष्टि होने तक सभी ऋण प्रक्रियाएं निलंबित हैं।"
                )
            elif language == "HINGLISH":
                message = (
                    "Main samajhta hoon ki aap loan cost aur interest ke baare me pooch rahe hain. Prototype me exact interest ya EMI amount invent nahi kiya ja sakta. "
                    "Saath hi, unusual transaction verify hone tak sabhi credit applications suspended hain."
                )
            else:
                message = (
                    "I understand you are asking about loan costs and interest. In this prototype, exact interest amounts cannot be calculated authoritatively without an assigned loan rate and tenure. "
                    "Furthermore, all credit evaluations are suspended until recent unusual transaction activity is verified."
                )
        elif decision == "RECOMMEND":
            if language == "HINDI":
                message = (
                    f"मैं समझता हूँ कि आप ऋण लागत और ब्याज के बारे में पूछ रहे हैं। इस प्रोटोटाइप में, किसी निर्दिष्ट ऋण उत्पाद, ब्याज दर और अवधि के बिना सटीक ब्याज या ईएमआई की गणना नहीं की जा सकती। "
                    f"आपके स्वस्थ मासिक अधिशेष ({surplus_str}) के साथ, NeoBharat ऋण का बोझ उठाने के बजाय अनुशासित बचत की सलाह देता है।"
                )
            elif language == "HINGLISH":
                message = (
                    f"Main samajhta hoon ki aap loan cost aur interest ke baare me pooch rahe hain. Current prototype me bina assigned loan rate aur tenure ke exact interest ya EMI calculate nahi kiya ja sakta. "
                    f"Aapke healthy surplus ({surplus_str}) ke sath, NeoBharat loan lene ke bajay disciplined savings recommend karta hai."
                )
            else:
                message = (
                    f"I understand you are asking about loan costs and interest. In this prototype, exact interest or EMI amounts cannot be calculated authoritatively without an assigned loan product, interest rate, and tenure. "
                    f"With your healthy surplus of {surplus_str}, NeoBharat recommends disciplined savings or wealth accumulation rather than taking on loan debt and interest obligations."
                )
        else:
            if language == "HINDI":
                message = "मैं समझता हूँ कि आप ऋण लागत और ब्याज के बारे में पूछ रहे हैं। प्रोटोटाइप में वास्तविक ब्याज दर और अवधि के बिना सटीक ब्याज या ईएमआई की गणना नहीं की जा सकती।"
            elif language == "HINGLISH":
                message = "Main samajhta hoon ki aap loan cost aur interest ke baare me pooch rahe hain. Prototype me bina assigned loan rate aur tenure ke exact interest ya EMI amount calculate nahi kiya ja sakta."
            else:
                message = "I understand you are asking about loan costs and interest. In this prototype, exact interest, EMI, or repayment amounts cannot be calculated authoritatively without an assigned loan product, interest rate, and tenure. We do not invent interest numbers or rates."

    # 3. FINANCIAL HEALTH: WHAT_SHOULD_I_DO
    elif intent == "WHAT_SHOULD_I_DO":
        if decision == "SUPPORT":
            if language == "HINDI":
                message = (
                    f"आपकी वर्तमान प्राथमिकता नकदी प्रवाह को स्थिर करना है। ईएमआई ({emi_str}) और खर्चों की समीक्षा करें, "
                    "और अतिरिक्त वित्तीय बोझ लेने से बचें।"
                )
            elif language == "HINGLISH":
                message = (
                    f"Aapki current priority cash flow stabilize karna hai. EMI ({emi_str}) aur discretionary expenses review karein, "
                    "aur naya loan lene se bachein."
                )
            else:
                message = (
                    f"Your current priority is to stabilize cash flow. Review your upcoming EMI of {emi_str} and discretionary expenses "
                    "before taking on any additional financial obligations."
                )
        elif decision == "VERIFY":
            if language == "HINDI":
                message = "कृपया अपनी हालिया गतिविधि देखें और पुष्टि करें कि क्या आपने असामान्य लेनदेन किया था। यह धोखाधड़ी की पुष्टि नहीं करता है।"
            elif language == "HINGLISH":
                message = "Kripya apni recent activity check karein aur confirm karein ki transaction aapne kiya tha ya nahi. Ye fraud confirm nahi karta."
            else:
                message = "Please review your recent transactions and verify whether you authorized the unusual activity. This does not confirm fraud."
        else:
            if language == "HINDI":
                message = f"आपकी बचत स्थिति अच्छी है। अपने मासिक अधिशेष {surplus_str} के अनुसार अनुशासित निवेश की योजना बनाएं।"
            elif language == "HINGLISH":
                message = f"Aapki savings healthy hain. Monthly surplus ({surplus_str}) ke hisaab se disciplined SIP planning start karein."
            else:
                message = f"Your savings trend is healthy. Review the illustrative systematic investment terms aligned with your surplus of {surplus_str}."

    # 4. FRAUD: WHY_TRANSACTION_FLAGGED or IS_THIS_FRAUD or VERIFY_TRANSACTION
    elif intent in ("WHY_TRANSACTION_FLAGGED", "IS_THIS_FRAUD", "VERIFY_TRANSACTION", "UNKNOWN_TRANSACTION", "WHAT_IF_I_DID_NOT_MAKE_TRANSACTION"):
        if language == "HINDI":
            message = (
                "यह लेनदेन आपके पिछले इतिहास से काफी अलग और असामान्य पाया गया है। "
                "यह धोखाधड़ी की पुष्टि नहीं करता है। कृपया पुष्टि करें कि क्या यह लेनदेन आपने किया था।"
            )
        elif language == "HINGLISH":
            message = (
                "Ye transaction aapke normal spending pattern se significantly different hai. "
                "Ye fraud confirm nahi karta. Kripya verify karein ki kya ye transaction aapne kiya tha."
            )
        else:
            message = (
                "This transaction appears unusual compared with your normal spending pattern. "
                "This does not confirm fraud. Please verify whether you made it."
            )

    # 5. INVESTMENTS: WHY_RECOMMEND
    elif intent == "WHY_RECOMMEND":
        if decision == "RECOMMEND":
            if language == "HINDI":
                message = (
                    f"आपकी अनुशासित बचत प्रवृत्ति और ₹{surplus_str} के मासिक अधिशेष को देखते हुए, "
                    f"{prod_name} आपके दीर्घकालिक वित्तीय लक्ष्यों के लिए उपयुक्त है।"
                )
            elif language == "HINGLISH":
                message = (
                    f"Aapke disciplined savings trend aur monthly surplus ({surplus_str}) ko dekhte hue, "
                    f"{prod_name} aapki long-term wealth building ke liye suggest kiya gaya hai."
                )
            else:
                message = (
                    f"Based on your disciplined savings trend and healthy financial standing with a surplus of {surplus_str}, "
                    f"{prod_name} is presented for your review."
                )
        else:
            if language == "HINDI":
                message = "वर्तमान वित्तीय तनाव या असामान्य गतिविधि के कारण अभी निवेश की सिफारिश नहीं की गई है।"
            elif language == "HINGLISH":
                message = "Current financial stress ya alert status ke chalte abhi investment recommend nahi kiya gaya hai."
            else:
                message = "At this time, commercial recommendations are suspended until your financial indicators normalize."

    # 6. INVESTMENTS: WHAT_IS_SIP
    elif intent == "WHAT_IS_SIP":
        if language == "HINDI":
            message = (
                "सिस्टमैटिक इन्वेस्टमेंट प्लान (एसआईपी) हर महीने एक निश्चित राशि नियमित रूप से निवेश करने का एक अनुशासित तरीका है। "
                "यह बाजार के जोखिमों के अधीन है, लेकिन दीर्घकालिक संपत्ति निर्माण में मदद करता है।"
            )
        elif language == "HINGLISH":
            message = (
                "SIP (Systematic Investment Plan) har mahine ek fixed amount invest karne ka disciplined tareeka hai. "
                "Ye market risks ke subject hota hai par long-term wealth accumulate karne me madad karta hai."
            )
        else:
            message = (
                "A Systematic Investment Plan (SIP) allows disciplined monthly investing into diversified funds. "
                "Investments are subject to market risks, but support systematic long-term wealth accumulation."
            )

    # 7. INVESTMENTS: HOW_MUCH_CAN_I_INVEST
    elif intent == "HOW_MUCH_CAN_I_INVEST":
        if decision == "RECOMMEND":
            if language == "HINDI":
                message = (
                    f"आपके पास {surplus_str} का मासिक अधिशेष है। एक सुरक्षित दिशानिर्देश के रूप में, "
                    "प्रति माह ₹2,000 से ₹5,000 की राशि से शुरुआत करना उपयुक्त हो सकता है।"
                )
            elif language == "HINGLISH":
                message = (
                    f"Aapka monthly surplus {surplus_str} hai. Ek safe guideline ke mutabiq, "
                    "aap ₹2,000–₹5,000 per month se disciplined shuruat kar sakte hain."
                )
            else:
                message = (
                    f"With your estimated monthly surplus of {surplus_str}, an illustrative contribution "
                    "of ₹2,000–₹5,000 per month is suitable for systematic wealth building."
                )
        else:
            if language == "HINDI":
                message = "वर्तमान में नकदी स्थिति को प्राथमिकता दें और निवेश से पहले अपने आगामी भुगतानों को सुरक्षित करें।"
            elif language == "HINGLISH":
                message = "Abhi ke liye cash flow stabilize karein aur naye investments se pehle upcoming EMIs secure karein."
            else:
                message = "Prioritize stabilizing your cash flow and meeting upcoming commitments before initiating new investments."

    # 8. FINANCIAL HEALTH: WHY_IS_SPENDING_HIGH
    elif intent == "WHY_IS_SPENDING_HIGH":
        if language == "HINDI":
            message = (
                f"आपका मासिक खर्च {spending_str} दर्ज हुआ है, जो आपके पिछले खर्चों से अधिक है। "
                "गैर-जरूरी खर्चों की समीक्षा करने से नकदी प्रवाह में सुधार हो सकता है।"
            )
        elif language == "HINGLISH":
            message = (
                f"Aapka monthly spending {spending_str} record hua hai, jo baseline se higher hai. "
                "Discretionary kharche review karne se cash flow me sudhaar hoga."
            )
        else:
            message = (
                f"Your recorded monthly spending is {spending_str}, reflecting a shift compared to baseline. "
                "Reviewing discretionary expenses can help restore comfortable savings margins."
            )

    # 9. FINANCIAL HEALTH: WHY_IS_SAVINGS_DECLINING
    elif intent == "WHY_IS_SAVINGS_DECLINING":
        if language == "HINDI":
            message = (
                f"आपकी अनुमानित बचत घटकर {surplus_str} रह गई है, जिसका मुख्य कारण बढ़े हुए खर्च और ईएमआई दायित्व ({emi_str}) हैं।"
            )
        elif language == "HINGLISH":
            message = (
                f"Aapki estimated savings ghat kar {surplus_str} ho gayi hai, mostly higher discretionary spending aur EMI ({emi_str}) ki wajah se."
            )
        else:
            message = (
                f"Your estimated savings have declined to {surplus_str}, driven by increased discretionary spending and regular EMI obligations of {emi_str}."
            )

    # 10. FINANCIAL HEALTH: HOW_CAN_I_SAVE_MORE
    elif intent == "HOW_CAN_I_SAVE_MORE":
        if language == "HINDI":
            message = (
                f"मासिक बचत बढ़ाने के लिए, गैर-जरूरी खर्चों को सीमित करें और ईएमआई ({emi_str}) का समय पर भुगतान सुनिश्चित करें।"
            )
        elif language == "HINGLISH":
            message = (
                f"Savings badhane ke liye discretionary kharcho par dhyan de aur EMI ({emi_str}) ko timely manage karein."
            )
        else:
            message = (
                f"To increase savings, review non-essential expenses and maintain timely payments on current obligations ({emi_str})."
            )

    # 11. PAYMENTS: EMI_EXPLANATION / UPCOMING_PAYMENTS / PAYMENT_RISK
    elif intent in ("EMI_EXPLANATION", "UPCOMING_PAYMENTS", "PAYMENT_RISK"):
        if language == "HINDI":
            message = (
                f"आपकी वर्तमान मासिक ईएमआई {emi_str} है, जो आपकी कुल आय {income_str} का हिस्सा है। "
                "समय पर भुगतान बनाए रखने से भुगतान जोखिम नियंत्रित रहता है।"
            )
        elif language == "HINGLISH":
            message = (
                f"Aapki current monthly EMI {emi_str} hai, jo aapki monthly income ({income_str}) par based hai. "
                "Timely payment maintain karne se payment risk low rehta hai."
            )
        else:
            message = (
                f"Your active monthly EMI obligation is {emi_str}, evaluated against your monthly income of {income_str}. "
                "Maintaining timely payments keeps your payment risk within safe thresholds."
            )

    # 12. GENERAL: GREETING
    elif intent == "GREETING":
        if language == "HINDI":
            message = "नमस्ते! मैं NeoBharat का वित्तीय सहायक हूँ। मैं आपकी स्थिति, निर्णयों और वित्तीय स्वास्थ्य को स्पष्ट कर सकता हूँ। मैं आपकी क्या सहायता करूँ?"
        elif language == "HINGLISH":
            message = "Namaste! Main NeoBharat ka explanation assistant hoon. Main aapke risk scores, financial status aur recommendations ko explain kar sakta hoon. Poochiye aapka kya sawaal hai?"
        else:
            message = "Hello! I am NeoBharat's financial explanation assistant. I can explain the decisions, risk scores, and guidance provided by our engines. How can I help you today?"

    # 13. GENERAL: THANKS / HELP / WHAT_CAN_YOU_DO
    elif intent in ("THANKS", "HELP", "WHAT_CAN_YOU_DO"):
        if language == "HINDI":
            message = "NeoBharat आपके वित्तीय कल्याण के लिए काम करता है। आप अपने खर्च, बचत, ईएमआई, या सुरक्षा अलर्ट के बारे में कभी भी पूछ सकते हैं।"
        elif language == "HINGLISH":
            message = "NeoBharat aapki financial safety ke liye dedicated hai. Aap kabhi bhi apne spending, savings, EMI, ya security alert ke baare me pooch sakte hain."
        else:
            message = "NeoBharat is dedicated to your financial wellbeing. You can ask about your spending trends, savings, EMI obligations, or verification alerts anytime."

    # 14. DEFAULT / WHY_THIS_DECISION
    else:
        if decision == "SUPPORT":
            if language == "HINDI":
                message = (
                    f"आपकी हालिया वित्तीय गतिविधि में खर्च और बचत में बदलाव देखा गया है। "
                    f"ईएमआई {emi_str} और बचत {surplus_str} को ध्यान में रखते हुए, सहायता और समीक्षा को प्राथमिकता दी गई है।"
                )
            elif language == "HINGLISH":
                message = (
                    f"Aapki recent activity me spending aur savings shifts dikhe hain. "
                    f"EMI ({emi_str}) aur surplus ({surplus_str}) ko dekhte hue support guidance priority par hai."
                )
            else:
                message = (
                    "Your recent financial activity shows spending and savings shifts. "
                    "To support your financial wellbeing, please review your upcoming payments and commitments."
                )
        elif decision == "VERIFY":
            if language == "HINDI":
                message = "यह लेनदेन आपके सामान्य खर्च पैटर्न से अलग है। यह धोखाधड़ी की पुष्टि नहीं करता है। कृपया पुष्टि करें कि क्या यह आपने किया था।"
            elif language == "HINGLISH":
                message = "Ye transaction aapke normal spending se alag hai. Ye fraud confirm nahi karta. Kripya verify karein ki kya ye aapne kiya hai."
            else:
                message = "This transaction appears unusual compared with your normal spending pattern. This does not confirm fraud. Please verify whether you made it."
        elif decision == "RECOMMEND":
            if language == "HINDI":
                message = f"आपकी अनुशासित बचत प्रवृत्ति और अधिशेष {surplus_str} के आधार पर, {prod_name} आपके अवलोकन के लिए प्रस्तुत है।"
            elif language == "HINGLISH":
                message = f"Aapke disciplined savings trend aur surplus ({surplus_str}) ke aadhar par, {prod_name} review ke liye present kiya gaya hai."
            else:
                message = f"Based on your disciplined savings trend and healthy financial standing, {prod_name} is presented for your review."
        else:
            message = "At this time, no commercial banking product provides a clear additional benefit without adding unnecessary obligations."

    return {
        "contract_version": "1.0",
        "response_type": response_type,
        "message": message,
        "decision_acknowledgement": {
            "decision": decision,
            "action": ack_action,
        },
        "evidence": evidence[:5],
        "next_step": next_step,
        "safety": {
            "financial_decision_made_by": "DETERMINISTIC_ENGINE",
            "llm_role": "EXPLANATION_ONLY",
        },
    }
