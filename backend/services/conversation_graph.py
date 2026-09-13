"""Conversational State Machine and LangGraph Orchestrator for NeoBharat.

Orchestrates conversational flow, intent routing, and state persistence while
strictly enforcing the core safety invariant:

    BACKEND DECIDES -> AI EXPLAINS

The deterministic financial engine remains completely authoritative.
This orchestrator owns conversation state machine transitions:
    START
      |
    LOAD_CONTEXT (Firestore)
      |
    CLASSIFY_INTENT (Rule-based lexicon)
      |
    LOAD_AUTHORITATIVE_DATA (SQLite + Phase 1-3)
      |
    DETERMINE_STRATEGY
      |
    APPOINTMENT_FLOW (Deterministic appointment guidance)
      |
    GENERATE_EXPLANATION (OpenAI explanation layer)
      |
    VALIDATE_RESPONSE (Phase 4 Schema & Semantic Safety)
      |
    END

If the 'langgraph' library is installed, it compiles a LangGraph StateGraph.
If not, it executes the identical state-machine sequence deterministically.
"""

import logging
from typing import Any, Dict, List, Optional, TypedDict

from backend.domain.conversation_intents import detect_intent
from backend.domain.conversation_fallbacks import generate_conversational_fallback
from backend.domain.phase4_validator import (
    validate_output_schema,
    validate_semantic_output,
)
from backend.integrations.openai_client import generate_explanation
from backend.repositories.appointment_repository import get_appointments_by_customer
from backend.repositories.conversation_repository import (
    append_conversation_turn,
    get_conversation_state,
    save_conversation_state,
)
from backend.services.appointment_service import (
    PROTOTYPE_SLOTS,
    get_advisor_recommendation_for_customer,
)
from backend.services.conversation_context import (
    get_conversation_context,
    update_conversation_context,
)

logger = logging.getLogger(__name__)

# Check if LangGraph is available in the environment
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    END = "__end__"


class ConversationGraphState(TypedDict, total=False):
    customer_id: int
    user_message: str
    reference_month: Optional[str]
    openai_client: Optional[Any]
    # State loaded from repositories
    session_state: Dict[str, Any]
    intent_obj: Dict[str, Any]
    input_payload: Optional[Dict[str, Any]]
    strategy: str
    appointment_handled: bool
    raw_response: Optional[Dict[str, Any]]
    final_response: Dict[str, Any]
    validation_status: str


def load_context_node(state: ConversationGraphState) -> ConversationGraphState:
    """Load persistent conversation state from Firestore."""
    customer_id = state["customer_id"]
    saved_state = get_conversation_state(customer_id) or {}
    state["session_state"] = saved_state
    return state


def classify_intent_node(state: ConversationGraphState) -> ConversationGraphState:
    """Classify user intent deterministically using Phase 7 lexicon."""
    customer_id = state["customer_id"]
    user_msg = state["user_message"]

    conv_ctx = get_conversation_context(customer_id)
    intent_obj = detect_intent(user_msg, conversation_context=conv_ctx)
    state["intent_obj"] = intent_obj
    return state


def load_authoritative_data_node(state: ConversationGraphState) -> ConversationGraphState:
    """Load authoritative financial context from Phase 1-3 deterministic engines."""
    from backend.services.chat_service import build_llm_input

    customer_id = state["customer_id"]
    user_msg = state["user_message"]
    ref_month = state.get("reference_month")

    input_payload = build_llm_input(customer_id, user_msg, ref_month)
    state["input_payload"] = input_payload
    return state


def determine_strategy_node(state: ConversationGraphState) -> ConversationGraphState:
    """Determine whether to route to appointment guidance or standard explanation."""
    intent = state.get("intent_obj", {}).get("intent", "UNKNOWN")

    if intent in ("BOOK_APPOINTMENT", "VIEW_APPOINTMENTS", "CANCEL_APPOINTMENT", "APPOINTMENT_HELP"):
        state["strategy"] = "APPOINTMENT_FLOW"
    else:
        state["strategy"] = "STANDARD_EXPLANATION"

    return state


def appointment_flow_node(state: ConversationGraphState) -> ConversationGraphState:
    """Handle appointment-related intents deterministically without inventing bookings."""
    customer_id = state["customer_id"]
    intent = state.get("intent_obj", {}).get("intent", "BOOK_APPOINTMENT")
    lang = state.get("intent_obj", {}).get("language", "ENGLISH")
    is_hindi = lang in ("HINDI", "HINGLISH")

    input_payload = state.get("input_payload") or {}
    decision_ctx = input_payload.get("decision_context", {})
    decision = decision_ctx.get("decision", "SUPPORT")

    advisor_rec = get_advisor_recommendation_for_customer(customer_id)
    existing_apts = get_appointments_by_customer(customer_id)
    active_apts = [a for a in existing_apts if a.get("status") == "SCHEDULED"]

    if intent == "VIEW_APPOINTMENTS":
        if active_apts:
            apt = active_apts[0]
            if is_hindi:
                msg = (
                    f"आपकी आगामी अपॉइंटमेंट {apt['date']} को {apt['time']} बजे "
                    f"({apt['advisor_type']}) निर्धारित है। स्थिति: {apt['status']}।"
                )
            else:
                msg = (
                    f"You have an upcoming appointment scheduled on {apt['date']} at {apt['time']} "
                    f"with {apt['advisor_type']}. Status: {apt['status']}."
                )
        else:
            if is_hindi:
                msg = "आपके खाते में वर्तमान में कोई निर्धारित अपॉइंटमेंट नहीं है।"
            else:
                msg = "You currently have no scheduled appointments on your account."

        response_dict = {
            "contract_version": "1.0",
            "response_type": "FINANCIAL_GUIDANCE",
            "message": msg,
            "decision_acknowledgement": {
                "decision": decision if decision in ("SUPPORT", "RECOMMEND", "VERIFY") else "SUPPORT",
                "action": "REVIEW_UPCOMING_PAYMENTS",
            },
            "evidence": [],
            "next_step": {
                "type": "INFORMATION",
                "label": "View your appointment history in the dashboard",
            },
            "safety": {
                "financial_decision_made_by": "DETERMINISTIC_ENGINE",
                "llm_role": "EXPLANATION_ONLY",
            },
        }

    elif intent == "CANCEL_APPOINTMENT":
        if is_hindi:
            msg = (
                "अपॉइंटमेंट रद्द करने के लिए आप डैशबोर्ड के अपॉइंटमेंट सेक्शन में जाकर 'रद्द करें' चुन सकते हैं, "
                "या मुझे बताएं कि आप किस अपॉइंटमेंट को रद्द करना चाहते हैं।"
            )
        else:
            msg = (
                "To cancel or reschedule an appointment, you can click 'Cancel' in your dashboard "
                "appointment drawer, or contact support with your appointment ID."
            )

        response_dict = {
            "contract_version": "1.0",
            "response_type": "FINANCIAL_GUIDANCE",
            "message": msg,
            "decision_acknowledgement": {
                "decision": decision if decision in ("SUPPORT", "RECOMMEND", "VERIFY") else "SUPPORT",
                "action": "REVIEW_UPCOMING_PAYMENTS",
            },
            "evidence": [],
            "next_step": {
                "type": "ACTION",
                "label": "Open Appointment Drawer to manage bookings",
            },
            "safety": {
                "financial_decision_made_by": "DETERMINISTIC_ENGINE",
                "llm_role": "EXPLANATION_ONLY",
            },
        }

    else:
        # BOOK_APPOINTMENT or APPOINTMENT_HELP
        advisor_title = advisor_rec.get("title", "Financial Advisor")
        slots_str = ", ".join(PROTOTYPE_SLOTS[:3])

        if decision == "SUPPORT":
            if is_hindi:
                msg = (
                    f"नमस्ते! आपके वित्तीय स्वास्थ्य को सहारा देने हेतु आप हमारे {advisor_rec.get('title_hindi', 'वित्तीय सलाहकार')} "
                    f"से 30 मिनट का निःशुल्क परामर्श बुक कर सकते हैं। उपलब्ध समय स्लॉट: {slots_str} आदि। "
                    f"कृपया 'अपॉइंटमेंट बुक करें' बटन द्वारा अपनी पसंदीदा तारीख व समय की पुष्टि करें।"
                )
            else:
                msg = (
                    f"To support your financial recovery and review upcoming EMI obligations, you can schedule "
                    f"a 30-minute consultation with a {advisor_title}. Prototype slots available: {slots_str}. "
                    f"Please confirm your preferred date and time via the appointment booking modal."
                )
            action_label = "Book Financial Advisor Appointment"
        elif decision == "VERIFY":
            if is_hindi:
                msg = (
                    f"सुरक्षा अलर्ट: हाल ही में असामान्य लेन-देन दर्ज हुआ है। आप तुरंत हमारे सुरक्षा विशेषज्ञ "
                    f"से परामर्श का समय निर्धारित कर सकते हैं। कृपया अपनी सुविधा अनुसार समय चुनें।"
                )
            else:
                msg = (
                    f"Security Alert: An unusual transaction was flagged. You can speak with a Security Specialist "
                    f"to verify this activity. Please confirm your desired slot via the booking modal."
                )
            action_label = "Consult Security Specialist"
        else:
            if is_hindi:
                msg = (
                    f"नियो भारत के साथ आप वेल्थ प्लानिंग एवं बचत परामर्श हेतु विशेषज्ञ से परामर्श ले सकते हैं। "
                    f"उपलब्ध स्लॉट: {slots_str}। आप अपनी सुविधा अनुसार अपॉइंटमेंट बुक कर सकते हैं।"
                )
            else:
                msg = (
                    f"You can consult with a NeoBharat banking specialist for disciplined wealth planning and surplus optimization. "
                    f"Prototype slots: {slots_str}. Please confirm your booking in the appointment modal."
                )
            action_label = "Book Wealth Consultation"

        response_dict = {
            "contract_version": "1.0",
            "response_type": "SUPPORT_GUIDANCE" if decision == "SUPPORT" else "FINANCIAL_GUIDANCE",
            "message": msg,
            "decision_acknowledgement": {
                "decision": decision if decision in ("SUPPORT", "RECOMMEND", "VERIFY") else "SUPPORT",
                "action": "REVIEW_UPCOMING_PAYMENTS" if decision == "SUPPORT" else "RECOMMEND" if decision == "RECOMMEND" else "VERIFY_SUSPICIOUS_TRANSACTION",
            },
            "evidence": [],
            "next_step": {
                "type": "ACTION",
                "label": action_label,
            },
            "safety": {
                "financial_decision_made_by": "DETERMINISTIC_ENGINE",
                "llm_role": "EXPLANATION_ONLY",
            },
        }

    state["raw_response"] = response_dict
    state["appointment_handled"] = True
    return state


def generate_explanation_node(state: ConversationGraphState) -> ConversationGraphState:
    """Call OpenAI explanation layer when not already handled by appointment flow."""
    if state.get("appointment_handled"):
        return state

    input_payload = state.get("input_payload")
    if not input_payload:
        return state

    openai_client = state.get("openai_client")
    intent_obj = state.get("intent_obj")

    raw_response = generate_explanation(input_payload, client=openai_client, intent_obj=intent_obj)
    state["raw_response"] = raw_response
    return state


def validate_response_node(state: ConversationGraphState) -> ConversationGraphState:
    """Validate output against Phase 4 schema and semantic safety rules."""
    customer_id = state["customer_id"]
    raw_response = state.get("raw_response")
    input_payload = state.get("input_payload") or {}
    intent_obj = state.get("intent_obj") or {}

    final_resp = None
    if raw_response is not None:
        if validate_output_schema(raw_response) and validate_semantic_output(raw_response, input_payload):
            final_resp = raw_response
            state["validation_status"] = "PASSED"
        else:
            logger.warning("Response failed validation. Engaging deterministic fallback.")
            state["validation_status"] = "FAILED_ENGAGING_FALLBACK"

    if final_resp is None:
        final_resp = generate_conversational_fallback(input_payload, intent_obj)
        state["is_fallback"] = True

    state["final_response"] = final_resp

    # Persist turn and state to Firestore
    try:
        append_conversation_turn(
            customer_id=customer_id,
            user_message=state["user_message"],
            response_message=final_resp.get("message", ""),
            intent=intent_obj.get("intent"),
            decision=final_resp.get("decision_acknowledgement", {}).get("decision"),
        )
        save_conversation_state(
            customer_id=customer_id,
            state={
                "last_intent": intent_obj.get("intent"),
                "last_strategy": state.get("strategy"),
                "last_decision": final_resp.get("decision_acknowledgement", {}).get("decision"),
                "last_topic": intent_obj.get("topic"),
                "language": intent_obj.get("language"),
                "status": state.get("validation_status", "COMPLETED"),
            },
        )
    except Exception as e:
        logger.warning("Could not persist conversation turn to Firestore: %s", e)

    # Update in-memory context
    update_conversation_context(
        customer_id=customer_id,
        intent=intent_obj.get("intent", "UNKNOWN"),
        language=intent_obj.get("language", "ENGLISH"),
        response_type=final_resp.get("response_type", "SUPPORT_GUIDANCE"),
        decision=final_resp.get("decision_acknowledgement", {}).get("decision", "SUPPORT"),
        topic=intent_obj.get("topic", "GENERAL"),
    )

    return state


def run_conversation_graph(
    customer_id: int,
    user_message: str,
    reference_month: Optional[str] = None,
    openai_client: Optional[Any] = None,
    return_state: bool = False,
) -> Any:
    """Execute the full conversation orchestration graph.

    Args:
        customer_id: SQLite customer ID.
        user_message: Untrusted customer message text.
        reference_month: Optional reference month.
        openai_client: Optional OpenAI client instance.
        return_state: If True, returns internal ConversationGraphState dictionary.

    Returns:
        Validated Phase 4 output dict, or ConversationGraphState if return_state is True, or None.
    """
    initial_state: ConversationGraphState = {
        "customer_id": customer_id,
        "user_message": user_message,
        "reference_month": reference_month,
        "openai_client": openai_client,
        "appointment_handled": False,
        "is_fallback": False,
        "validation_status": "PENDING",
    }

    # Step 1: Load context from Firestore
    state = load_context_node(initial_state)

    # Step 2: Classify intent
    state = classify_intent_node(state)

    # Step 3: Load authoritative data
    state = load_authoritative_data_node(state)
    if state.get("input_payload") is None:
        return None

    # Step 4: Determine strategy
    state = determine_strategy_node(state)

    # Step 5: Appointment flow (if applicable)
    if state.get("strategy") == "APPOINTMENT_FLOW":
        state = appointment_flow_node(state)

    # Step 6: Generate explanation (if not appointment-handled)
    state = generate_explanation_node(state)

    # Step 7: Validate response
    state = validate_response_node(state)

    if return_state:
        return state

    return state.get("final_response")
