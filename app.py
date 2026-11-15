"""
LOYIHA: FIRIMARI AI — ULTIMATE IMPERIAL EDITION (v16.9)
MUALLIF: Farrux G'aybilloyev (Tiliton Tashkiloti)
"""

from datetime import datetime, timedelta
import json
import os
import urllib.request
import streamlit as st

DEFAULT_API_KEY = "AQ.Ab8RN6ItyupOcuvYGPpoP-VDGTawKPOx7SSc_hBQnnHDHh2ogw"

AVAILABLE_MODELS = [
    "gemini-2.5-flash",
    "gemini-3-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.6-flash",
    "gemini-2.5-pro",
]

st.set_page_config(
    page_title="Firimari AI v16.9",
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
    "T-1M-39K": {"type": "1 oylik obuna", "price": "39,999 UZS", "days": 30},
    "T-3M-110K": {"type": "3 oylik obuna", "price": "109,999 UZS", "days": 90},
    "T-6M-200K": {"type": "6 oylik obuna", "price": "199,999 UZS", "days": 180},
    "Tiliton-Admin-Master": {
        "type": "Bosh Muhandis (Admin)",
        "price": "Bepul",
        "days": None,
    },
}

if "authenticated" not in st.session_state:
  st.session_state.authenticated = False
if "sub_type" not in st.session_state:
  st.session_state.sub_type = ""
if "sub_price" not in st.session_state:
  st.session_state.sub_price = ""
if "expiry_date" not in st.session_state:
  st.session_state.expiry_date = None

if not st.session_state.authenticated:
  st.title("🔒 Firimari AI — Obuna Tizimi")
  st.write("Platformadan foydalanish uchun obuna kalitini kiriting:")

  col1, col2, col3 = st.columns(3)
  with col1:
    st.markdown(
        "<div"
        " class='pricing-box'><h4>1 Oylik</h4><p><b>39,999</b></p><p><small>T-1M-39K</small></p></div>",
        unsafe_allow_html=True,
    )
  with col2:
    st.markdown(
        "<div"
        " class='pricing-box'><h4>3 Oylik</h4><p><b>109,999</b></p><p><small>T-3M-110K</small></p></div>",
        unsafe_allow_html=True,
    )
  with col3:
    st.markdown(
        "<div"
        " class='pricing-box'><h4>6 Oylik</h4><p><b>199,999</b></p><p><small>T-6M-200K</small></p></div>",
        unsafe_allow_html=True,
    )

  entered_code = st.text_input("Obuna parolini kiriting:", type="password")

  if st.button("Kirish"):
    if entered_code in VALID_SUBSCRIPTIONS:
      sub_info = VALID_SUBSCRIPTIONS[entered_code]
      st.session_state.authenticated = True
      st.session_state.sub_type = sub_info["type"]
      st.session_state.sub_price = sub_info["price"]
      if sub_info["days"] is not None:
        st.session_state.expiry_date = datetime.now() + timedelta(
            days=sub_info["days"]
        )
      else:
        st.session_state.expiry_date = None
      st.success(f"Xush kelibsiz, Farrux! Faol: {st.session_state.sub_type}")
      st.rerun()
    else:
      st.error("Xato parol yoki obuna muddati tugagan!")
  st.stop()

if "messages" not in st.session_state:
  st.session_state.messages = []


def call_gemini_engine(prompt_text, model_name, api_key):
  url = (
      "https://generativelanguage.googleapis.com/v1beta/models/"
      + model_name
      + ":generateContent?key="
      + api_key
  )
  payload = {
      "contents": [{"role": "user", "parts": [{"text": prompt_text}]}],
      "generationConfig": {"temperature": 0.5},
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
    return f"Xatolik: {e}"


with st.sidebar:
  st.markdown("## FIRIMARI AI")
  st.info(f"Faol: {st.session_state.sub_type}")
  if st.button("Chiqish"):
    st.session_state.authenticated = False
    st.rerun()

  tanlangan_model = st.selectbox("Model:", AVAILABLE_MODELS)
  tanlangan_fan = st.selectbox(
      "Fan:", ["Barcha fanlar", "Fizika", "Matematika", "Tarix"]
  )

st.title(f"⚡ Firimari AI — {tanlangan_fan}")

for m in st.session_state.messages:
  with st.chat_message(m["role"]):
    st.markdown(m["content"])

prompt = st.chat_input("Savolingizni yozing...")
if prompt:
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  with st.chat_message("assistant"):
    resp = call_gemini_engine(prompt, tanlangan_model, DEFAULT_API_KEY)
    st.markdown(resp)
    st.session_state.messages.append({"role": "assistant", "content": resp})
  st.rerun()
