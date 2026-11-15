"""
================================================================================
LOYIHA: FIRIMARI AI — ULTIMATE IMPERIAL EDITION (v20.1 Argon)
MUALLIF: Farrux G'aybilloyev (Tiliton Tashkiloti)
================================================================================
"""

from datetime import datetime, timedelta
import json
import os
import urllib.request
import streamlit as st

DEFAULT_API_KEY = "AQ.Ab8RN6KyFWCec0HohRJRSzGzoHwD3AXwL61hPRWhWMSBXpWmgg"

AVAILABLE_MODELS = {
    "Argon-1 Ultra Flash": "gemini-1.5-flash",
    "Argon-2 Pro Engine": "gemini-1.5-pro",
    "Argon-3 Master Vision": "gemini-1.5-flash",
    "Argon-4 Ultimate Prime": "gemini-1.5-pro",
}

st.set_page_config(
    page_title="Firimari AI v20.1 Argon Edition",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background-color: #0f0f13; color: #f4f4f5; }
    .stChatMessage { background-color: #18181b !important; border: 1px solid #27272a; border-radius: 14px; padding: 1.2rem 1.5rem; margin-bottom: 14px; }
    pre { background-color: #09090b !important; border: 1px solid #27272a; border-radius: 10px; padding: 16px; }
    code { color: #34d399 !important; font-family: 'Consolas', monospace; }
    [data-testid="stSidebar"] { background-color: #09090b; border-right: 1px solid #27272a; }
    .pricing-box { background: #18181b; border: 1px solid #27272a; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
    </style>
    """,
    unsafe_allow_html=True,
)

VALID_SUBSCRIPTIONS = {
    "T-1M-39K": {"type": "1 oylik obuna", "price": "39,999 UZS"},
    "T-3M-110K": {"type": "3 oylik obuna", "price": "109,999 UZS"},
    "T-6M-200K": {"type": "6 oylik obuna", "price": "199,999 UZS"},
    "Tiliton-Admin-Master": {
        "type": "Bosh Muhandis (Admin)",
        "price": "Bepul",
    },
}

if "authenticated" not in st.session_state:
  st.session_state.authenticated = False
if "sub_type" not in st.session_state:
  st.session_state.sub_type = ""

if not st.session_state.authenticated:
  st.title("🔒 Firimari AI — Obuna Tizimi")
  st.write("Platformadan foydalanish uchun obuna kalitini kiriting:")

  col1, col2, col3 = st.columns(3)
  with col1:
    st.markdown(
        "<div"
        " class='pricing-box'><h4>1 Oylik</h4><p><b>39,999 UZS</b></p><p><small>Kalit:"
        " T-1M-39K</small></p></div>",
        unsafe_allow_html=True,
    )
  with col2:
    st.markdown(
        "<div"
        " class='pricing-box'><h4>3 Oylik</h4><p><b>109,999"
        " UZS</b></p><p><small>Kalit: T-3M-110K</small></p></div>",
        unsafe_allow_html=True,
    )
  with col3:
    st.markdown(
        "<div"
        " class='pricing-box'><h4>6 Oylik</h4><p><b>199,999"
        " UZS</b></p><p><small>Kalit: T-6M-200K</small></p></div>",
        unsafe_allow_html=True,
    )

  entered_code = st.text_input("Obuna parolini kiriting:", type="password")

  if st.button("Kirish"):
    if entered_code in VALID_SUBSCRIPTIONS:
      sub_info = VALID_SUBSCRIPTIONS[entered_code]
      st.session_state.authenticated = True
      st.session_state.sub_type = sub_info["type"]
      st.success(f"Xush kelibsiz, Farrux! Faol: {st.session_state.sub_type}")
      st.rerun()
    else:
      st.error("Xato parol!")
  st.stop()

if "messages" not in st.session_state:
  st.session_state.messages = []
if "saved_notes" not in st.session_state:
  st.session_state.saved_notes = [
      ("Reja #1", "Godrik tili va fizika formulalarini takrorlash.")
  ]
if "xp" not in st.session_state:
  st.session_state.xp = 450

with st.sidebar:
  st.markdown("## FIRIMARI AI v20.1")
  st.info(f"Obuna: **{st.session_state.sub_type}**")
  if st.button("Chiqish"):
    st.session_state.authenticated = False
    st.rerun()
  st.markdown("---")
  st.write("Foydalanuvchi: Farrux G'aybilloyev")
  st.metric(label="XP (Tajriba ochko)", value=int(st.session_state.xp))
  st.markdown("---")
  custom_key = st.text_input(
      "API Key:", value=DEFAULT_API_KEY, type="password"
  )
  active_key = custom_key.strip() if custom_key.strip() else DEFAULT_API_KEY

  selected_argon_name = st.selectbox(
      "Argon Modelini Tanlang:", list(AVAILABLE_MODELS.keys())
  )
  target_gemini_model = AVAILABLE_MODELS[selected_argon_name]

  if st.button("Yangi chat"):
    st.session_state.messages = []
    st.rerun()


def call_argon_ai(prompt, model_name, api_key):
  url = (
      "https://generativelanguage.googleapis.com/v1/models/"
      + model_name
      + ":generateContent?key="
      + api_key
  )
  payload = {
      "contents": [{"role": "user", "parts": [{"text": prompt}]}],
      "generationConfig": {"temperature": 0.7},
  }
  headers = {"Content-Type": "application/json"}
  try:
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
      data = json.loads(resp.read().decode("utf-8"))
      return data["candidates"][0]["content"]["parts"][0]["text"]
  except Exception as e:
    return f"Xatolik yuz berdi: {e}"


st.title(f"⚡ Firimari AI — {selected_argon_name}")

tabs = st.tabs([
    "Jonli AI Chat",
    "Fanlar & Mavzular",
    "Test Sinovi",
    "Shaxsiy Daftar",
    "Vaqtni Boshqarish",
    "Kalkulyator & Python",
])

with tabs[0]:
  for m in st.session_state.messages:
    with st.chat_message(m["role"]):
      st.markdown(m["content"])

  prompt = st.chat_input(f"{selected_argon_name}ga savolingizni yozing...")
  if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.xp += 5
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      with st.spinner(f"{selected_argon_name} javob bermoqda..."):
        resp = call_argon_ai(prompt, target_gemini_model, active_key)
        st.markdown(resp)
      st.session_state.messages.append({"role": "assistant", "content": resp})
    st.rerun()

with tabs[1]:
  st.subheader("Asosiy Ta'lim Yo'nalishlari")
  col1, col2 = st.columns(2)
  with col1:
    st.markdown("### ⚡ Aniq va Tabiiy fanlar")
    st.write("Fizika, Matematika va Astronomiya.")
  with col2:
    st.markdown("### 💻 Dasturlash va Texnologiya")
    st.write("Python, Telegram botlar va Algoritmlar.")

with tabs[2]:
  st.subheader("Avtomatik Test Tizimi")
  t_mavzu = st.text_input("Test mavzusini kiriting:")
  if st.button("Test Tuzish") and t_mavzu:
    test_prompt = f"{t_mavzu} bo'yicha 5 ta test savolini variantlari (A, B, C, D) va javoblari bilan tuzib ber."
    with st.spinner("Testlar tayyorlanmoqda..."):
      st.markdown(call_argon_ai(test_prompt, target_gemini_model, active_key))

with tabs[3]:
  st.subheader("📝 Shaxsiy Daftar va Eslatmalar")
  n_title = st.text_input("Sarlavha:")
  n_text = st.text_area("Qayd matni:")
  if st.button("Daftarga saqlash") and n_title:
    st.session_state.saved_notes.append((n_title, n_text))
    st.success("Muvaffaqiyatli saqlandi!")
    st.rerun()

  st.markdown("---")
  for title, content in st.session_state.saved_notes:
    with st.expander(f"📖 {title}"):
      st.write(content)

with tabs[4]:
  st.subheader("⏱️ Pomodoro Dars va Vaqt Rejimi")
  st.write("25 daqiqa dars, 5 daqiqa dam olish qoidasi.")
  if st.button("Darsni boshlash (25 min)"):
    st.info("Diqqat! Vaqt ketdi. Darsga diqqatingizni qarating.")

with tabs[5]:
  st.subheader("🧮 Kalkulyator va Python Muhiti")
  col_a, col_b = st.columns(2)
  with col_a:
    st.markdown("#### Kalkulyator")
    expr = st.text_input("Ifodani yozing:")
    if st.button("Hisoblash"):
      try:
        st.success(f"Natija: {eval(expr)}")
      except Exception as e:
        st.error(f"Xato: {e}")
  with col_b:
    st.markdown("#### Python Terminal")
    code = st.text_area("Python kod:", value="print('Salom Farrux!')")
    if st.button("Kodni bajarish"):
      try:
        import io
        import sys

        old = sys.stdout
        new = io.StringIO()
        sys.stdout = new
        exec(code)
        sys.stdout = old
        st.code(new.getvalue())
      except Exception as e:
        st.error(f"Xato: {e}")
