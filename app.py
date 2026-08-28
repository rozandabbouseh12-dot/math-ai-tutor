import streamlit as st
import requests

# 1. إعداد الصفحة
st.set_page_config(
    page_title="Cambridge Stage 8 AI Math Coach",
    page_icon="📐",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. تصميم CSS عصري وفاخر مع بطاقات التلعيب
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(145deg, #f4f7fc 0%, #e9eef7 100%);
    }
    .hero-container {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: white;
        padding: 22px;
        border-radius: 18px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.12);
        margin-bottom: 20px;
        text-align: center;
    }
    .hero-title {
        font-size: 24px;
        font-weight: 800;
        color: #ffffff !important;
        margin-bottom: 4px;
    }
    .hero-sub {
        font-size: 13px;
        color: #a0c4ff;
        margin-bottom: 10px;
    }
    .badge-pill {
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.25);
        color: #e2eafc;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 11px;
        font-weight: 600;
        display: inline-block;
        margin: 2px 4px;
    }
    .score-card {
        background: white;
        padding: 14px;
        border-radius: 12px;
        border-left: 5px solid #ffb703;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# 3. الهيدر الترحيبي
st.markdown("""
<div class="hero-container">
    <div class="hero-title">📐 Cambridge Stage 8 • AI Math Coach</div>
    <div class="hero-sub">Socratic Adaptive Tutoring • Algebra & Linear Equations</div>
    <div>
        <span class="badge-pill">⚖️ Balancing</span>
        <span class="badge-pill">🔄 Inverse Operations</span>
        <span class="badge-pill">📦 Expanding Brackets</span>
        <span class="badge-pill">🏆 Gamified Learning</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. تهيئة متغيرات التلعيب (Gamification State)
if "score" not in st.session_state:
    st.session_state.score = 0
if "problems_solved" not in st.session_state:
    st.session_state.problems_solved = 0
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 **Hello! I am your Cambridge Stage 8 Math Coach.**\n\nWhat algebraic equation or expression are we exploring today?"}
    ]

# 5. الشريط الجانبي: لوحة المتصدرين والأوسمة
with st.sidebar:
    st.image("https://img.icons8.com/isometric/200/trophy.png", width=80)
    st.header("🏆 Student Progress")
    
    # بطاقة النقاط ومستوى التقدم
    st.markdown(f"""
    <div class="score-card">
        <h4 style="margin:0; color:#023047;">⭐ Total Score: <b>{st.session_state.score} pts</b></h4>
        <p style="margin:4px 0 0 0; font-size:13px; color:#555;">✅ Solved: <b>{st.session_state.problems_solved} equations</b></p>
    </div>
    """, unsafe_allow_html=True)

    # شريط التقدم
    progress_val = min(st.session_state.score / 60.0, 1.0)
    st.progress(progress_val)
    
    st.markdown("### 🎖️ Badges Earned:")
    if st.session_state.problems_solved >= 1:
        st.success("🥉 **Algebra Apprentice** (Solved 1st problem)")
    else:
        st.caption("🔒 *Algebra Apprentice (Solve 1 problem)*")

    if st.session_state.score >= 30:
        st.success("🥈 **Equation Solver** (Earned 30+ pts)")
    else:
        st.caption("🔒 *Equation Solver (Earn 30 pts)*")

    if st.session_state.score >= 60:
        st.success("🥇 **Master of Stage 8** (Earned 60+ pts)")
    else:
        st.caption("🔒 *Master of Stage 8 (Earn 60 pts)*")

    st.markdown("---")
    
    # إعادة تعيين الجلسة
    if st.button("🔄 Reset / Start New Problem", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 **Ready for a new challenge!** Type your next algebra problem below."}
        ]
        st.rerun()

    # زر تصدير السجل للأطروحة
    if len(st.session_state.messages) > 1:
        transcript = f"STUDENT SCORE: {st.session_state.score} pts | SOLVED: {st.session_state.problems_solved}\n\n"
        transcript += "\n\n".join([f"[{m['role'].upper()}]: {m['content']}" for m in st.session_state.messages])
        st.download_button(
            label="📥 Export Chat Log (Research Data)",
            data=transcript,
            file_name="student_math_session.txt",
            mime="text/plain",
            use_container_width=True
        )

# 6. قراءة مفتاح الـ API
api_key = st.secrets.get("GEMINI_API_KEY", "").strip().replace('"', '').replace("'", "")
if not api_key:
    st.error("⚠️ GEMINI_API_KEY is missing in Streamlit Settings > Secrets!")
    st.stop()

# 7. موجه التدريس السقراطي المباشر
SYSTEM_PROMPT = """
You are an expert Cambridge Stage 8 / Grade 7 Mathematics Coach for Algebra.

CORE RULES:
1. Be extremely concise. Output ONLY ONE direct, encouraging Socratic question guiding the student to the next step.
2. If the student answers or solves correctly, start your response with the exact tag: [CORRECT] followed by an encouraging confirmation.
   Example: "[CORRECT] Spot on! That is correct. Ready for the next problem?"
3. If the student makes an error, gently guide them with one question about the inverse operation or balancing.
4. If the student asks for steps, give only a 3-line calculation breakdown.
"""

# 8. شريط المسائل السريعة
st.write("**⚡ Quick Practice (Click to test):**")
c1, c2, c3 = st.columns(3)
preset_clicked = None
if c1.button("📌 2x + 7 = 19", use_container_width=True):
    preset_clicked = "2x + 7 = 19"
if c2.button("📌 3(x - 4) = 15", use_container_width=True):
    preset_clicked = "3(x - 4) = 15"
if c3.button("📌 5x - 8 = 2x + 7", use_container_width=True):
    preset_clicked = "5x - 8 = 2x + 7"

# 9. عرض المحادثة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 10. معالجة الإدخال والتوليد
typed_prompt = st.chat_input("Type your algebra problem or step here...")
user_input = typed_prompt if typed_prompt else preset_clicked

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

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
        message_placeholder.markdown("⏳ *Analyzing equation...*")
        
        # النماذج الحديثة المعتمدة والنشطة حالياً
        models_to_try = [
            "gemini-3.6-flash-lite",
            "gemini-3.6-flash",
            "gemini-3.1-pro-preview"
        ]
        
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": contents_payload,
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 200}
        }

        success = False
        last_error = ""

        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            try:
                res = requests.post(url, json=payload, timeout=20)
                data = res.json()
                
                if res.status_code == 200 and "candidates" in data:
                    reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    
                    if "[CORRECT]" in reply:
                        st.session_state.score += 10
                        st.session_state.problems_solved += 1
                        st.balloons()
                        reply = reply.replace("[CORRECT]", "🎉 ").strip()
                    
                    message_placeholder.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    success = True
                    break
                else:
                    last_error = data.get("error", {}).get("message", f"HTTP {res.status_code}")
            except Exception as e:
                last_error = str(e)
                continue

        if not success:
            message_placeholder.error(f"⚠️ Service busy: {last_error}. Please send again.")
