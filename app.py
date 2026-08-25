import streamlit as st
import requests

# 1. Page Config
st.set_page_config(
    page_title="Cambridge Stage 7 AI Math Coach",
    page_icon="📐",
    layout="centered"
)

st.title("📐 Cambridge Stage 7 AI Math Coach")
st.caption("Adaptive Learning Environment - Algebra: Expressions and Equations")

# Controls
with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🔄 Start New Problem / Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am your Cambridge Stage 7 Math Coach. What algebra problem are we working on today?"}
        ]
        st.rerun()

# 2. Get API Key
api_key = st.secrets.get("GEMINI_API_KEY", "").strip().replace('"', '').replace("'", "")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing in Streamlit Settings > Secrets!")
    st.stop()

# 3. System Prompt
SYSTEM_PROMPT = """
You are an expert Cambridge Stage 7 Mathematics Tutor specializing in Algebra (Expressions and Equations).

CORE BEHAVIOR RULES:
1. PHASE 1 (GUIDED INQUIRY):
   - When a student presents a problem or partial step, guide them with ONE clear, encouraging hint or Socratic question.
   - Prompt them to identify: inverse operations, balancing both sides, collecting like terms, or expanding brackets.
   - Use clean, standard text formatting for math (e.g., 2x + 5 = 15). Avoid awkward symbols.

2. PHASE 2 (SCAFFOLDED SOLUTION):
   - If the student explicitly asks for the answer ("give me the steps", "I don't know", "show solution") or gets stuck repeatedly:
     Provide a clear, complete, step-by-step algebraic explanation with the final answer stated plainly.
   - If the student solves correctly: Validate enthusiastically and confirm the final answer!

3. Keep explanations clear, supportive, and perfectly aligned with Cambridge Stage 7 standards.
"""

# 4. History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your Cambridge Stage 7 Math Coach. What algebra problem are we working on today?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 5. User Input
if prompt := st.chat_input("Type your algebra problem, step, or question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Use last 4 messages to optimize context
    recent_messages = st.session_state.messages[-4:]
    contents_payload = []
    for m in recent_messages:
        role = "model" if m["role"] == "assistant" else "user"
        contents_payload.append({
            "role": role,
            "parts": [{"text": str(m["content"])}]
        })

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⏳ *Thinking...*")
        
        # Using the exact recommended model: gemini-3.6-flash
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
        
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": contents_payload,
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 800
            }
        }

        try:
            res = requests.post(url, json=payload, timeout=25)
            data = res.json()
            
            if res.status_code == 200 and "candidates" in data:
                reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                message_placeholder.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                err_msg = data.get("error", {}).get("message", f"HTTP Error {res.status_code}")
                message_placeholder.error(f"⚠️ Google API Message: {err_msg}")
        except Exception as e:
            message_placeholder.error(f"⚠️ Connection Error: {e}")
