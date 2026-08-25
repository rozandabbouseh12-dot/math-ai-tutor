import streamlit as st
import requests

# 1. Page Configuration
st.set_page_config(page_title="Cambridge Stage 7 AI Math Coach", page_icon="📐", layout="centered")

st.title("📐 Cambridge Stage 7 AI Math Coach")
st.caption("Adaptive Learning Environment - Algebra: Expressions and Equations")

# 2. Retrieve and sanitize API Key
api_key = st.secrets.get("GEMINI_API_KEY", "").strip().replace('"', '').replace("'", "")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing in Streamlit Settings > Secrets!")
    st.stop()

# 3. System Prompt (Option 2: Hint first -> Full solution on demand)
SYSTEM_PROMPT = """
You are an expert Cambridge Stage 7 Mathematics Tutor specializing in Algebra (Expressions and Equations).

CORE BEHAVIOR RULES:
1. PHASE 1 (GUIDANCE FIRST): When a student gives an algebra problem or step, guide them first with ONE clear hint or Socratic question to prompt their thinking. Keep responses short (under 2 sentences).
2. PHASE 2 (SCAFFOLDING & REVEALING):
   - If the student explicitly asks for the answer or says "I don't know" / "give me the solution" / "show me the steps":
     Provide the clear, step-by-step algebraic solution with the final answer clearly stated, explained at the Cambridge Stage 7 level.
   - If the student makes repeated mistakes: provide a bigger hint, and if they still struggle, show them the next step directly to unblock them.
   - If the student solves it correctly: Validate enthusiastically and confirm the final answer!
3. Always respond in clear, simple English.
"""

# 4. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your Cambridge Stage 7 Math Coach. What algebra problem are we working on today?"}
    ]

# 5. Display existing conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 6. User Input & API Request Handling
if prompt := st.chat_input("Type your algebra problem or question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Format history payload for Gemini REST endpoint
    contents_payload = []
    for m in st.session_state.messages:
        role = "model" if m["role"] == "assistant" else "user"
        contents_payload.append({
            "role": role,
            "parts": [{"text": str(m["content"])}]
        })

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⏳ *Thinking...*")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": contents_payload,
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 300}
        }

        try:
            res = requests.post(url, json=payload, timeout=15)
            data = res.json()
            
            if res.status_code == 200 and "candidates" in data:
                reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                message_placeholder.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            else:
                err = data.get("error", {}).get("message", "API request failed.")
                message_placeholder.error(f"Error: {err}")
        except Exception as ex:
            message_placeholder.error(f"Request timeout or network issue: {ex}")
