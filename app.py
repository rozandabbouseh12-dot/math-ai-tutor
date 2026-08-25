import streamlit as st
from google import genai

st.set_page_config(page_title="AI Math Tutor - Stage 7", page_icon="📐", layout="centered")

st.title("📐 المرشد الذكي لوحدة الجبر")
st.caption("بيئة تعلم تكيفية - منهاج كامبردج Stage 7 (Expressions and Equations)")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ يرجى إضافة GEMINI_API_KEY في إعدادات المنصة (Secrets)!")
    st.stop()

client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """
You are an expert Cambridge Stage 7 Mathematics Socratic Tutor for Algebra (Expressions and Equations).

ABSOLUTE RESTRICTIONS (ZERO TOLERANCE):
1. NEVER output any algebraic calculation, intermediate step, or final solution.
2. NEVER write equations showing the solution (e.g., do NOT write "2x = 10 - 7" or "2x = 3").
3. DO NOT solve the problem under any circumstances, even if the student asks for the direct answer.

YOUR ONLY ROLE:
- Ask ONE guiding, Socratic question to prompt the student to think of the next move.
- Keep your response under 2 sentences.
- Guide step-by-step through: isolating the variable term, performing inverse operations, maintaining equation balance, and expanding brackets correctly.

Language: Match the student's language (English or Arabic).
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "مرحباً بك! أنا مرشدك الذكي لوحدة الجبر. اكتب مسألتك الجبرية، وسنعمل معاً خطوة بخطوة للوصول إلى الحل!"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("اكتب مسألتك الجبرية أو خطوة حلك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    conversation_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])

    with st.chat_message("assistant"):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{conversation_history}\nassistant:",
                config={"system_instruction": SYSTEM_PROMPT}
            )
            bot_reply = response.text.strip()
            st.write(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        except Exception as e:
            st.error(f"حدث خطأ أثناء الاتصال: {e}")
