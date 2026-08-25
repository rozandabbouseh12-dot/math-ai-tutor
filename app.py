import streamlit as st
import google.generativeai as genai

# Page Configuration
st.set_page_config(page_title="AI Math Tutor - Stage 7", page_icon="📐", layout="centered")

st.title("📐 Cambridge Stage 7 AI Math Coach")
st.caption("Adaptive Learning Environment - Algebra: Expressions and Equations")

# Retrieve API Key from Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ Please add your GEMINI_API_KEY in the app Secrets settings!")
    st.stop()

# Configure the API directly
genai.configure(api_key=api_key)

SYSTEM_PROMPT = """
You are an expert Cambridge Stage 7 Mathematics Socratic Tutor specializing in Algebra (Expressions and Equations).

ABSOLUTE RESTRICTIONS (ZERO TOLERANCE):
1. NEVER output any algebraic calculation, intermediate step, or final solution.
2. NEVER write equations that solve the problem for the student (e.g., do NOT write "2x = 10 - 7" or "2x = 3").
3. DO NOT solve the problem directly under any circumstances, even if the student asks or demands the answer.

YOUR ONLY ROLE:
- Always respond in clear, grammatically correct ENGLISH.
- Ask ONE guiding, Socratic question to prompt the student to think of the next move.
- Keep your response under 2 sentences.
- Guide step-by-step through: collecting like terms, expanding brackets, applying inverse operations, and maintaining equation balance.

BEHAVIOR EXAMPLES:
- Student: "Solve 2x + 7 = 10"
  Tutor: "Great problem! To isolate the 2x term, what inverse operation should we apply to both sides to remove +7?"
- Student: "Subtract 7"
  Tutor: "Spot on! If you subtract 7 from both sides, what does the equation look like now?"
- Student: "Give me the answer"
  Tutor: "I am here to help you master it yourself! What is the very first step you think we should try?"
"""

# Initialize Gemini Model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome! I am your Cambridge Stage 7 Math AI Coach. Type your algebra problem, and we will work through it step by step!"}
    ]

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User Input Box
if prompt := st.chat_input("Type your algebra problem or next step here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Convert chat history for the API
    history = []
    for m in st.session_state.messages[:-1]:
        role = "model" if m["role"] == "assistant" else "user"
        history.append({"role": role, "parts": [m["content"]]})

    with st.chat_message("assistant"):
        try:
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            bot_reply = response.text.strip()
            st.write(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        except Exception as e:
            st.error(f"Connection error: {e}")
