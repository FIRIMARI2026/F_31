"""
================================================================================
LOYIHA: FIRIMARI AI — ULTIMATE IMPERIAL EDITION (v16.9)
MUALLIF: Farrux G'aybilloyev (Tiliton Tashkiloti)
TEXNOLOGIYALAR: Python, Streamlit, Google Gemini, Firebase
================================================================================
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
  st.title("🔒 Firimari Aisan — Obuna va Narxlar Tizimi")
  st.write(
      "Platformadan foydalanish uchun o'zingizga mos obuna kalitini kiriting:"
  )

  col_p1, col_p2, col_p3 = st.columns(3)
  with col_p1:
    st.markdown(
        "<div class='pricing-box'><h4>1 Oylik</h4><p><b>39,999 UZS</b></p><p><small>Kalit:"
        " T-1M-39K</small></p></div>",
        unsafe_allow_html=True,
    )
  with col_p2:
    st.markdown(
        "<div class='pricing-box'><h4>3 Oylik</h4><p><b>109,999"
        " UZS</b></p><p><small>Kalit: T-3M-110K</small></p></div>",
        unsafe_allow_html=True,
    )
  with col_p3:
    st.markdown(
        "<div class='pricing-box'><h4>6 Oylik</h4><p><b>199,999"
        " UZS</b></p><p><small>Kalit: T-6M-200K</small></p></div>",
        unsafe_allow_html=True,
    )

  entered_code = st.text_input(
      "Obuna yoki kirish parolini kiriting:", type="password"
  )

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

      st.success(
          f"Xush kelibsiz, Farrux! Faollashgan obuna: {st.session_state.sub_type}"
          f" ({st.session_state.sub_price})"
      )
      st.rerun()
    else:
      st.error(
          "Xato parol yoki muddati tugagan obuna! Iltimos, to'g'ri kodni"
          " kiriting."
      )

  st.stop()

if "messages" not in st.session_state:
  st.session_state.messages = []
if "saved_notes" not in st.session_state:
  st.session_state.saved_notes = []
if "library_books" not in st.session_state:
  st.session_state.library_books = [
      {
          "nomi": "Godrik Tili Lug'ati va Shifrlar",
          "mazmuni": "Farruxning shaxsiy ijodiy loyihalari va maxsus kodlar bazasi.",
      },
      {
          "nomi": "Fizika va Matematika Asosiy Formulalar",
          "mazmuni": "Kinematika, dinamika, kvadrat tenglamalar va geometriya.",
      },
  ]
if "xp" not in st.session_state:
  st.session_state.xp = 270
if "tasks" not in st.session_state:
  st.session_state.tasks = [
      {"vazifa": "Fizika qonunlarini takrorlash", "holat": "Bajarilmoqda"},
      {"vazifa": "Godrik tili shifrlarini yozish", "holat": "Bajarildi"},
  ]
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
    except urllib.error.HTTPError as he:
      err_msg = he.read().decode("utf-8", errors="ignore")
      if he.code in (400, 401, 403):
        try:
          url_b = (
              "https://generativelanguage.googleapis.com/v1beta/models/"
              + target_model
              + ":generateContent"
          )
          headers_b = {
              "Content-Type": "application/json",
              "Authorization": "Bearer " + api_key,
          }
          req_b = urllib.request.Request(
              url_b, data=json.dumps(payload).encode("utf-8"), headers=headers_b
          )
          with urllib.request.urlopen(req_b, timeout=45) as resp_b:
            data_b = json.loads(resp_b.read().decode("utf-8"))
            return True, data_b["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
          pass
      return False, "HTTP " + str(he.code) + ": " + err_msg
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
          return (
              "*(Zaxira: "
              + model_name
              + " o'rniga **"
              + backup_model
              + "** orqali bajarildi)*\n\n"
              + r_b
          )

  return (
      "Xatolik: Barcha modellar javob bermadi. Tafsilot: "
      + str(result)
      + ". Iltimos, API kalitingizni tekshiring."
  )


MAKTAB_FANLARI_BAZASI = {
    "Barcha fanlar (Universal rejim)": {
        "icon": "🌐",
        "tavsif": "1-11-sinf maktab dasturidagi barcha fanlar bo'yicha yordam.",
        "yo_riqnoma": (
            "Sen Farrux G'aybilloyev yaratgan Firimari Aisan — O'zbekiston"
            " maktablari darsliklari asosida barcha fanlardan bilimga ega"
            " sun'iy intellektsan."
        ),
        "asosiy_bolimlar": [
            "Aniq fanlar (Matematika, Fizika, Informatika)",
            "Tabiiy fanlar (Kimyo, Biologiya, Geografiya)",
            "Ijtimoiy fanlar (Tarix, Ona tili, Adabiyot, Huquq)",
        ],
        "tezkor_savollar": [
            "Nyutonning uchta qonunini hayotiy misollar bilan tushuntir",
            "Kvadrat tenglamalarni diskriminant usulida yechishni ko'rsat",
            "Amir Temur davlati boshqaruv tizimi haqida ma'lumot ber",
        ],
    },
    "Fizika va Astronomiya": {
        "icon": "⚡",
        "tavsif": "Mexanika, termodinamika, elektr, optika va koinot fizikasi.",
        "yo_riqnoma": (
            "Sen fizika va astronomiya fanlari mutaxassissan (6-11-sinf"
            " darsliklari). Masalalarni bosqichma-bosqich tartibida yech."
        ),
        "asosiy_bolimlar": [
            "Kinematika va Dinamika",
            "Mexanik ish, energiya va quvvat",
            "Bosim va Arximed kuchi",
            "Elektr toki va Om qonuni",
        ],
        "tezkor_savollar": [
            "Om qonuni nima va zanjirda qanday qo'llaniladi?",
            "Arximed kuchi formulasini tushuntir va masala yechib ber",
        ],
    },
    "Matematika": {
        "icon": "📐",
        "tavsif": "Algebraik ifodalar, tenglamalar va geometriya.",
        "yo_riqnoma": (
            "Sen matematika bo'yicha mutaxassissan (1-11-sinf darsliklari). Har"
            " bir qadamni aniq va tushunarli yechib ko'rsat."
        ),
        "asosiy_bolimlar": [
            "Qisqa ko'paytirish formulalari",
            "Kvadrat tenglamalar",
            "Trigonometriya asoslari",
            "Pifagor teoremasi",
        ],
        "tezkor_savollar": [
            "Qisqa ko'paytirish formulalarining barchasini yozib ber",
            "Pifagor teoremasini misol bilan tushuntir",
        ],
    },
    "Tarix": {
        "icon": "🏛️",
        "tavsif": "O'zbekiston tarixi va Jahon tarixi.",
        "yo_riqnoma": (
            "Sen tarix fanidan mutaxassissan (5-11-sinf darsliklari). Sanalar va"
            " shaxslarni aniq yorit."
        ),
        "asosiy_bolimlar": [
            "Qadimgi davlatlar",
            "Buyuk Ipak yo'li",
            "Temuriylar renessansi",
            "Jadidchilik harakati",
        ],
        "tezkor_savollar": [
            "Qadimgi Xorazm va Baqtriya haqida nimalarni bilasan?",
            "Mirzo Ulug'bekning ilmiy merosi qanday?",
        ],
    },
}

SINFLAR_ROYXATI = [
    "Barcha sinflar (1–11-sinf)",
    "5-sinf",
    "6-sinf",
    "7-sinf",
    "8-sinf",
    "9-sinf",
    "10-sinf",
    "11-sinf",
]

FLASHCARDS_DATA = {
    "Fizika va Astronomiya": [
        (
            "Nyutonning 1-qonuni nima?",
            (
                "Jism tashqi kuch ta'sir qilmaguncha tinch holatini yoki to'g'ri"
                " chiziqli tekis harakatini saqlaydi."
            ),
        ),
        (
            "Om qonuni formulasi?",
            "I = U / R (Tok kuchi kuchlanishga to'g'ri, qarshilikka teskari"
            " proporsional).",
        ),
    ],
    "Matematika": [
        (
            "Diskriminant formulasi?",
            "D = b^2 - 4ac (D > 0 bo'lsa 2 ta ildizga ega).",
        ),
        ("Pifagor teoremasi?", "a^2 + b^2 = c^2"),
    ],
}

with st.sidebar:
  st.markdown("## FIRIMARI AI v16.9")
  st.caption("Ultimate Imperial Ta'lim Tizimi")
  st.markdown("---")

  st.markdown("### 💳 Obuna & Taymer Holati")
  st.info(
      f"Faol: **{st.session_state.sub_type}**\nNarxi:"
      f" **{st.session_state.sub_price}**"
  )
  if st.session_state.expiry_date:
    qolgan_vaqt = st.session_state.expiry_date - datetime.now()
    kunlar = qolgan_vaqt.days
    if kunlar >= 0:
      st.warning(f"⏳ Qolgan vaqt: **{kunlar} kun** qoldi")
    else:
      st.error("⚠️ Obuna muddati tugadi!")
  else:
    st.success("♾️ Abadiy Admin Kirishi")

  if st.button("Chiqish (Logout)", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.sub_type = ""
    st.session_state.sub_price = ""
    st.session_state.expiry_date = None
    st.rerun()

  st.markdown("---")
  st.markdown("### Tiliton Profili")
  st.write("Foydalanuvchi: Farrux G'aybilloyev")
  st.write("Unvon: Bosh Muhandis / Asoschisi")
  st.metric(label="XP (Tajriba ochko)", value=int(st.session_state.xp))

  st.markdown("---")
  st.markdown("### AI Ustoz Xarakteri")
  ai_persona = st.selectbox(
      "Ustoz uslubi:",
      [
          "Jonkuyar Repetitor (Sodda va qiziqarli)",
          "Qattiqqo'l Fan Olimpiadasi Murabbiyi",
          "Ilmiy Professor (Chuqur faktlar bilan)",
          "Multi-Persona (Barcha ustozlar birga)",
      ],
      index=0,
  )

  st.markdown("---")
  st.markdown("### Model va Kalit")
  tanlangan_model = st.selectbox("AI Model:", AVAILABLE_MODELS, index=0)
  auto_fallback = st.checkbox("Avtomatik zaxira modelga o'tish", value=True)

  with st.expander("API Kalit sozlamasi"):
    kiritilgan_kalit = st.text_input(
        "Google AI Studio API Key:", value=DEFAULT_API_KEY, type="password"
    )
  faol_kalit = (
      kiritilgan_kalit.strip() if kiritilgan_kalit.strip() else DEFAULT_API_KEY
  )

  st.markdown("---")
  st.markdown("### Darslik Sozlamalari")
  tanlangan_fan = st.selectbox(
      "Fan yo'nalishi:", list(MAKTAB_FANLARI_BAZASI.keys()), index=0
  )
  tanlangan_sinf = st.selectbox("Sinf darajasi:", SINFLAR_ROYXATI, index=0)

  st.markdown("---")
  c1, c2 = st.columns(2)
  with c1:
    if st.button("Yangi chat", use_container_width=True):
      st.session_state.messages = []
      st.session_state.pending_prompt = None
      st.rerun()
  with c2:
    if st.button("Tozalash", type="primary", use_container_width=True):
      st.session_state.messages = []
      st.session_state.pending_prompt = None
      st.rerun()

  st.markdown("---")
  st.metric(label="Suhbatdagi xabarlar", value=len(st.session_state.messages))
  st.caption("© 2026 Tiliton Tashkiloti | Farrux G'aybilloyev")

fan_info = MAKTAB_FANLARI_BAZASI[tanlangan_fan]


def build_system_prompt():
  if "Repetitor" in ai_persona:
    persona_desc = (
        "Sen jonkuyar repetitorsan. Murakkab mavzularni oddiy hayotiy misollar"
        " bilan tushuntirasan."
    )
  elif "Murabbiy" in ai_persona:
    persona_desc = (
        "Sen qattiqqo'l olimpiada murabbiyisan. O'quvchini chuqur o'ylashga"
        " majbur qiladigan savollar berasan."
    )
  elif "Professor" in ai_persona:
    persona_desc = (
        "Sen ilmiy professorsan. Aniq ilmiy atamalar va chuqur tahlillar bilan"
        " javob berasan."
    )
  else:
    persona_desc = (
        "Sen Multi-Personasan: repetitor, murabbiy va professor vazifalarini"
        " bajarib javob berasan."
    )

  xotira_matni = ""
  if st.session_state.saved_notes:
    for n in st.session_state.saved_notes:
      xotira_matni += "- " + n["matn"] + "\n"
  else:
    xotira_matni = "Hozircha maxsus xotiralar yo'q."

  kutubxona_matni = ""
  if st.session_state.library_books:
    for b in st.session_state.library_books:
      kutubxona_matni += "- " + b["nomi"] + ": " + b["mazmuni"] + "\n"

  return (
      "Sen Farrux G'aybilloyev yaratgan Firimari Aisan — onlayn va jonli"
      " ishlaydigan ta'lim platformasisan.\nXaraktering: "
      + persona_desc
      + "\n\nFan va sinf:\n- Fan: "
      + tanlangan_fan
      + "\n- Sinf: "
      + tanlangan_sinf
      + "\n"
      + fan_info["yo_riqnoma"]
      + "\n\nXotira daftari:\n"
      + xotira_matni
      + "\n\nKutubxona:\n"
      + kutubxona_matni
      + "\n\nQoidalar:\n1. Doimo sof va ravon O'zbek tilida javob ber.\n2."
      " Matematik va fizik formulalarni LaTeX formatida yoz.\n3. Xotira va"
      " kutubxonaga tayanib ish ko'r."
  )


st.title(fan_info["icon"] + " Firimari AI — Imperial Ta'lim Platformasi")
st.markdown(
    "<div class='subject-banner'><b>Fan:</b> "
    + tanlangan_fan
    + " | <b>Sinf:</b> "
    + tanlangan_sinf
    + " | <b>Model:</b> "
