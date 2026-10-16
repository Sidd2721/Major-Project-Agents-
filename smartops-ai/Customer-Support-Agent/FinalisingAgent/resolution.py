from langchain_core.prompts import ChatPromptTemplate
from Agent.llm import get_llm
from Agent.utils.json_guard import extract_json
from .schema import ResolutionDecision

llm = get_llm()

prompt = ChatPromptTemplate.from_template("""
You are a complaint resolution decision agent.

Complaint:
{complaint}

Final Priority: {priority}
Escalation Required: {escalated}

Decision rules:
- Low priority → auto_resolve = true
- Medium priority feedback → auto_resolve = true
- High priority → auto_resolve = false
- Legal, fraud, chargeback → auto_resolve = false

Return valid JSON with EXACTLY:
- auto_resolve (true/false)
- reason

Example:
{{"auto_resolve": true, "reason": "Low priority feedback complaint"}}
""")

def decide_resolution(complaint, priority, escalated) -> ResolutionDecision:
    try:
        mode = os.getenv("LLM_MODE", "mock").lower()
        groq_key = os.getenv("GROQ_API_KEY", "").strip()
        if mode == "mock" or not groq_key or "placeholder" in groq_key:
            raise ValueError("Offline/Mock mode active")
        response = llm.invoke(
            prompt.format_messages(
                complaint=complaint,
                priority=priority,
                escalated=escalated
            )
        )
        clean_json = extract_json(response.content)
        return ResolutionDecision.model_validate_json(clean_json)
    except Exception:
        is_p1_p2 = priority in ["P1", "P2", "Critical", "High"] or bool(escalated)
        return ResolutionDecision(
            auto_resolve=not is_p1_p2,
            reason="Critical priority requires human supervisor escalation" if is_p1_p2 else "Standard operational ticket auto-resolved"
        )
