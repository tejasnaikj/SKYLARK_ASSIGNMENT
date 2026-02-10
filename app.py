import streamlit as st
from groq import Groq
import re

from tools import get_pilot_roster, check_conflicts, update_pilot_status

# -------------------------
# PAGE SETUP
# -------------------------
st.set_page_config(page_title="Skylark Ops AI", layout="wide")

# Header styling
st.markdown("""
<style>
.big-title {
    font-size:30px;
    font-weight:700;
    color:#0f172a;
}
.subtitle {
    color:#475569;
    margin-bottom:20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🚁 Skylark Operations Command</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-assisted pilot, drone & mission coordination</div>', unsafe_allow_html=True)

# -------------------------
# SIDEBAR PANEL
# -------------------------
with st.sidebar:
    st.header("📊 Operations Panel")
    st.metric("Active Pilots", "4")
    st.metric("Available Drones", "3")
    st.markdown("---")
    st.caption("Skylark Ops AI v1.0")

# -------------------------
# GROQ CLIENT
# -------------------------
if "GROQ_API_KEY" not in st.secrets:
    st.error("Add GROQ_API_KEY in Streamlit secrets")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "llama-3.1-8b-instant"

# -------------------------
# MEMORY
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------
# DISPLAY CHAT HISTORY
# -------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# -------------------------
# INTENT DETECTION
# -------------------------
def detect_intent(user_text):
    text = user_text.lower()

    if "thermal" in text or "skills" in text:
        return "roster"

    if "available" in text or "pilot" in text:
        return "roster"

    if "free" in text or "availability" in text:
        return "conflict"

    if "leave" in text or "mark" in text or "update" in text:
        return "update"

    return "general"

# -------------------------
# TOOL ROUTING
# -------------------------
def run_tool(intent, user_text):

    if intent == "roster":

        if "thermal" in user_text.lower():
            return get_pilot_roster("thermal", only_available=False)

        if "available" in user_text.lower():
            return get_pilot_roster(only_available=True)

        return get_pilot_roster()

    if intent == "conflict":
        pilot = re.findall(r'P\d+', user_text)
        date = re.findall(r'\d{4}-\d{2}-\d{2}', user_text)

        if pilot and date:
            return check_conflicts(pilot[0], date[0])

        return "Need pilot ID and date."

    if intent == "update":
        pilot = re.findall(r'P\d+', user_text)

        if pilot:
            if "leave" in user_text.lower():
                return update_pilot_status(pilot[0], "On Leave")

            if "available" in user_text.lower():
                return update_pilot_status(pilot[0], "Available")

        return "Need pilot ID."

    return None

# -------------------------
# CHAT LOOP (Q → A FORMAT)
# -------------------------
if user_input := st.chat_input("Ask about pilots, missions..."):

    # USER QUESTION
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role":"user","content":user_input})

    # ASSISTANT RESPONSE
    with st.chat_message("assistant"):
        with st.spinner("Coordinating operations..."):

            intent = detect_intent(user_input)
            tool_result = run_tool(intent, user_input)

            if intent != "general" and tool_result is None:
                st.warning("I need structured info like pilot ID and date.")

                st.session_state.messages.append({
                    "role":"assistant",
                    "content":"I need structured info like pilot ID and date."
                })

            elif tool_result is not None:

                if isinstance(tool_result, str):
                    st.success(tool_result)

                    st.session_state.messages.append({
                        "role":"assistant",
                        "content":tool_result
                    })

                else:
                    # show table
                    st.dataframe(tool_result, use_container_width=True)

                    # store table as markdown text so it appears again
                    st.session_state.messages.append({
                        "role":"assistant",
                        "content":tool_result.to_markdown(index=False)
                    })


            else:
                # fallback LLM
                resp = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role":"user","content":user_input}]
                )

                output = resp.choices[0].message.content
                st.markdown(output)

                st.session_state.messages.append({
                    "role":"assistant",
                    "content":output
                })
