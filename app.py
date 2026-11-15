"""
LOYIHA: FIRIMARI AI — ULTIMATE IMPERIAL EDITION (v16.9)
MUALLIF: Farrux G'aybilloyev (Tiliton Tashkiloti)
"""

from datetime import datetime, timedelta
import json
import os
import urllib.error
import urllib.request
import firebase_admin
from firebase_admin import credentials, firestore
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
    .stChatMessage { background-color: #18181b !important; border: 1px solid #27272a; border-radius: 14px; padding: 1.2rem 1.5rem; margin-bottom: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    pre { background-color: #09090b !important; border: 1px solid #27272a; border-radius: 10px; padding: 16px; }
    code { color: #34d399 !important; font-family: 'Consolas', monospace; }
    [data-testid="stSidebar"] { background-color: #09090b; border-right: 1px solid #27272a; }
    .subject-banner { background: linear-gradient(135deg, #18181b 0%, #064e3b 100%); border-left: 5px solid #10b981; border: 1px solid #27272a; padding: 16px 20px; border-radius: 10px; margin-bottom: 16px; }
    .stButton>button { border-radius: 8px; font-weight: 600; transition: all 0.2s ease; }
    .stButton>button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(16,185,129,0.3); }
    .pricing-box { background: #18181b; border: 1px solid #27272a; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
    </style>
    """,
    unsafe_allow_html=True,
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(CURRENT_DIR, "serviceAccountKey.json")


@st.cache_resource
def init_firebase():
  try:
    if not firebase_admin._apps:
      if os.path.exists(KEY_PATH):
        cred = credentials.Certificate(KEY_PATH)
      elif os.path.exists(
          r"C:\Users\lenovva\Documents\serviceAccountKey.json"
      ):
        cred = credentials.Certificate(
            r"C:\Users\lenovva\Documents\serviceAccountKey.json"
        )
      else:
        return None
      firebase_admin.initialize_app(cred)
    return firestore.client()
  except Exception:
    return None


db = init_firebase()

VALID_SUBSCRIPTIONS = {
    "T-1M-39K": {"type": "1 oylik obuna", "price": "39,999 UZS", "days": 30},
    "T-3M-110K": {"type": "3 oylik obuna", "price": "109,999 UZS", "days": 90},
    "T-6M-200K": {"type": "6 oylik obuna", "price": "199,999 UZS", "days": 180},
    "Tiliton-Admin-Master": {
        "type": "Bosh Muhandis (Admin)",
        "price": "Bepul / Asoschisi",
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

if st.session_state.authenticated and st.session_state.expiry_date is not None:
  if datetime.now() > st.session_state.expiry_date:
    st.session_state.authenticated = False
    st.warning("Sizning obuna muddatingiz tugadi! Iltimos, yangi obuna oling.")

if not st.session_state.authenticated:
  st.title("🔒 Firimari AI — Obuna va Narxlar Tizimi")
  st.write("Platformadan foydalanish uchun obuna kalitini kiriting:")

  col_p1, col_p2, col_p3 = st.columns(3)
  with col_p1:
    st.markdown(
        "<div"
        " class='pricing-box'><h4>1</h4><p><b>39,999</b></p><p><small>T-1M-39K</small></p></div>",
        unsafe_allow_html=True,
    )
  with col_p2:
    st.markdown(
        "<div"
        " class='pricing-box'><h4>3</h4><p><b>109,999</b></p><p><small>T-3M-110K</small></p></div>",
        unsafe_allow_html=True,
    )
  with col_p3:
    st.markdown(
        "<div"
        " class='pricing-box'><h4>6</h4><p><b>199,999</b></p><p><small>T-6M-200K</small></p></div>",
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
if "saved_notes" not in st.session_state:
  st.session_state.saved_notes = []
if "library_books" not in st.session_state:
  st.session_state.library_books = [{
      "nomi": "Godrik Tili",
      "mazmuni": "Farruxning shaxsiy shifrlari.",
  }]
if "xp" not in st.session_state:
  st.session_state.xp = 270
if "tasks" not in st.session_state:
  st.session_state.tasks = [{"vazifa": "Fizika takrorlash", "holat": "Faol"}]
if "pending_prompt" not in st.session_state:
  st.session_state.pending_prompt = None
if "generated_test" not in st.session_state:
  st.session_state.generated_test = ""
if "f_idx" not in st.session_state:
  st.session_state.f_idx = 0


def call_gemini_engine(
    prompt_text,
    system_text,
    model_name,
    api_key,
    history_list=None,
    auto_fallback=True,
):
  contents = []
  if history_list:
    for msg in history_list[-10:]:
      role = "user" if msg["role"] == "user" else "model"
      contents.append({"role": role, "parts": [{"text": msg["content"]}]})
  contents.append({"role": "user", "parts": [{"text": prompt_text}]})

  payload = {
      "system_instruction": {"parts": [{"text": system_text}]},
      "contents": contents,
      "generationConfig": {"temperature": 0.5, "maxOutputTokens": 4096},
  }

  def send_request(target_model):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + target_model
        + ":generateContent?key="
        + api_key
    )
    headers = {"Content-Type": "application/json"}
    try:
      req = urllib.request.Request(
          url, data=json.dumps(payload).encode("utf-8"), headers=headers
      )
      with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return True, data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
      return False, str(e)

  success, result = send_request(model_name)
  if success:
    return result

  if auto_fallback:
    for backup_model in AVAILABLE_MODELS:
      if backup_model != model_name:
        s_b, r_b = send_request(backup_model)
        if s_b:
          return f"*(Zaxira: {backup_model})*\n\n{r_b}"

  return f"Xatolik: {result}"


MAKTAB_FANLARI_BAZASI = {
    "Barcha fanlar": {
        "icon": "🌐",
        "tavsif": "Universal rejim.",
        "yo_riqnoma": (
            "Sen Farrux G'aybilloyev yaratgan Firimari Aisan — ta'lim"
            " platformasisan."
        ),
        "asosiy_bolimlar": ["Aniq fanlar", "Tabiiy fanlar"],
