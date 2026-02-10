import streamlit as st
from groq import Groq
import json

# import your tools
from tools import get_pilot_roster, check_conflicts, update_pilot_status



# -------------------------
# BEAUTIFUL & CREATIVE UI STYLING
# -------------------------
st.markdown("""
<style>
/* 1. Main Background Gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%) !important;
}

/* 2. Fix the Ghost Text (Force all text to dark slate) */
html, body, [data-testid="stWidgetLabel"], .stMarkdown p {
    color: #1e293b !important;
}

/* 3. Sidebar Styling - Clean White with Border */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #bae6fd !important;
}

/* 4. Metric Styling - Better Visibility */
[data-testid="stMetricValue"] {
    color: #0369a1 !important;
    font-weight: 800 !important;
}

[data-testid="stMetricLabel"] {
    color: #475569 !important;
}

/* 5. Header Styling */
.big-title {
    font-size: 42px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -1px;
    margin-bottom: 0px;
}

.subtitle {
    color: #334155;
    font-size: 18px;
    margin-bottom: 30px;
    opacity: 0.8;
}

/* 6. Chat & Tool Cards */
.card {
    background: rgba(255, 255, 255, 0.9);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #ffffff;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    margin-bottom: 12px;
    color: #1e293b !important;
}

.success-box {
    background: #dcfce7;
    color: #166534;
    padding: 14px;
    border-radius: 12px;
    font-weight: 600;
    border: 1px solid #bbf7d0;
}

.warning-box {
    background: #fee2e2;
    color: #991b1b;
    padding: 14px;
    border-radius: 12px;
    font-weight: 600;
    border: 1px solid #fecaca;
}

.info-box {
    background: #e0f2fe;
    color: #075985;
    padding: 14px;
    border-radius: 12px;
    border: 1px solid #bae6fd;
}

/* 7. Hide the default Streamlit Header for a cleaner look */
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER
# -------------------------
st.markdown('<div class="big-title">🚁 Skylark Operations Command</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered pilot, drone & mission coordination</div>', unsafe_allow_html=True)

# -------------------------
# GROQ CLIENT
# -------------------------
if "GROQ_API_KEY" not in st.secrets:
    st.error("Add GROQ_API_KEY in Streamlit secrets")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "llama-3.3-70b-versatile"

# -------------------------
# SYSTEM PROMPT
# -------------------------
SYSTEM_PROMPT = """
You are Skylark Drone Operations AI.

You must decide if a tool is needed.

If tool needed → respond ONLY in JSON format:

{
 "tool": "tool_name",
 "arguments": { }
}

Available tools:

1. get_pilot_roster
   args: skill (string optional), only_available (boolean optional)

2. check_conflicts
   args: pilot_id (string), date (string optional)

3. update_pilot_status
   args: pilot_id (string), status (string)

If no tool needed → reply normally in text.
"""

# -------------------------
# MEMORY
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# -------------------------
# OUTPUT FORMATTER
# -------------------------
def format_tool_output(tool_name, result):

    if isinstance(result, str):
        return result

    if tool_name == "get_pilot_roster":
        if not result:
            return "No pilots found."

        formatted = "### 👨‍✈️ Pilot Roster\n\n"
        for p in result:
            status_icon = {
                "Available": "🟢",
                "On Leave": "🔴",
                "Busy": "🟡"
            }.get(p.get("status"), "⚪")

            formatted += f"""
**{p['name']} ({p['pilot_id']})**
- Skills: {p['skills']}
- Location: {p['location']}
- Status: {status_icon} {p['status']}

---
"""
        return formatted

    if tool_name == "check_conflicts":
        return f"### ⚠️ Conflict Result\n\n{result}"

    if tool_name == "update_pilot_status":
        return f"### ✅ Status Updated\n\n{result}"

    return str(result)

# -------------------------
# TOOL EXECUTION
# -------------------------
def run_tool(tool_name, args, user_query=None):

    # -----------------------------
    # FORCE INTENT FROM USER QUERY
    # -----------------------------
    if user_query:
        q = user_query.lower()

        if tool_name == "get_pilot_roster":

            # detect availability intent
            if "available" in q:
                args["only_available"] = True

            # detect skill intent
            skills = ["thermal","mapping","inspection","survey"]
            for s in skills:
                if s in q:
                    args["skill"] = s

    # -----------------------------
    # SAFE BOOLEAN PARSING
    # -----------------------------
    if "only_available" in args:
        val = args["only_available"]
        if isinstance(val, bool):
            pass
        elif isinstance(val, str):
            args["only_available"] = val.lower() == "true"
        else:
            args["only_available"] = False

    # -----------------------------
    # CALL TOOL
    # -----------------------------
    try:
        if tool_name == "get_pilot_roster":
            return get_pilot_roster(
                skill=args.get("skill"),
                only_available=args.get("only_available", False)
            )

        elif tool_name == "check_conflicts":
            return check_conflicts(
                args.get("pilot_id"),
                args.get("date")
            )

        elif tool_name == "update_pilot_status":
            return update_pilot_status(
                args.get("pilot_id"),
                args.get("status")
            )

    except Exception as e:
        return f"Tool error: {str(e)}"


# -------------------------
# SHOW CHAT HISTORY
# -------------------------
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# -------------------------
# CHAT INPUT
# -------------------------
if user_input := st.chat_input("Ask operations..."):

    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # LLM CALL
    response = client.chat.completions.create(
        model=MODEL,
        messages=st.session_state.messages
    )

    output = response.choices[0].message.content

    # -------------------------
    # TRY TOOL PARSE
    # -------------------------
    try:
        data = json.loads(output)

        if "tool" in data:

            tool_result = run_tool(
                data["tool"],
                data.get("arguments", {})
            )

            # add conversation memory
            st.session_state.messages.append({
                "role": "assistant",
                "content": output
            })

            st.session_state.messages.append({
                "role": "user",
                "content": format_tool_output(data["tool"], tool_result)
            })

            # FINAL LLM RESPONSE
            final = client.chat.completions.create(
                model=MODEL,
                messages=st.session_state.messages
            )

            final_output = final.choices[0].message.content

            st.chat_message("assistant").markdown(final_output)
            st.session_state.messages.append({
                "role": "assistant",
                "content": final_output
            })

        else:
            raise Exception()

    except:
        # NORMAL AI RESPONSE
        st.chat_message("assistant").markdown(output)
        st.session_state.messages.append({
            "role": "assistant",
            "content": output
        })
