"""
================================================================================
LOYIHA: FIRIMARI AI — ULTIMATE IMPERIAL EDITION (v16.6)
MUALLIF: Farrux G'aybilloyev (Tiliton Tashkiloti)
TEXNOLOGIYALAR: Python, Streamlit, Google Gemini, Firebase
================================================================================
"""

from datetime import datetime
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
    page_title="Firimari AI v16.6",
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

# --- OBUNA VA PAROL TIZIMI (SaaS) ---
VALID_SUBSCRIPTIONS = {
    "T-1M-39K": {"type": "1 oylik obuna", "price": "39,999 UZS"},
    "T-3M-110K": {"type": "3 oylik obuna", "price": "109,999 UZS"},
    "T-6M-200K": {"type": "6 oylik obuna", "price": "199,999 UZS"},
    "Tiliton-Admin-Master": {
        "type": "Bosh Muhandis (Admin)",
        "price": "Bepul / Asoschisi",
    },
}

if "authenticated" not in st.session_state:
  st.session_state.authenticated = False
if "sub_type" not in st.session_state:
  st.session_state.sub_type = ""
if "sub_price" not in st.session_state:
  st.session_state.sub_price = ""

# Agar foydalanuvchi tizimga kirmagan bo'lsa, obuna oynasini ko'rsatamiz
if not st.session_state.authenticated:
  st.title("🔒 Firimari Aisan — Obuna Tizimi")
  st.write(
      "Platformadan foydalanish uchun obuna parolingizni kiriting. (1 oylik"
      " obuna: 39,999 UZS)"
  )

  entered_code = st.text_input(
      "Obuna yoki kirish parolini kiriting:", type="password"
  )

  if st.button("Kirish"):
    if entered_code in VALID_SUBSCRIPTIONS:
      st.session_state.authenticated = True
      st.session_state.sub_type = VALID_SUBSCRIPTIONS[entered_code]["type"]
      st.session_state.sub_price = VALID_SUBSCRIPTIONS[entered_code]["price"]
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

# Session State initialization
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

# Sidebar controls
with st.sidebar:
  st.markdown("## FIRIMARI AI v16.6")
  st.caption("Ultimate Imperial Ta'lim Tizimi")
  st.markdown("---")

  # Obuna holatini sidebar'da ko'rsatish
  st.markdown("### 💳 Obuna Holati")
  st.info(
      f"Faol: **{st.session_state.sub_type}**\nNarxi:"
      f" **{st.session_state.sub_price}**"
  )
  if st.button("Chiqish (Logout)", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.sub_type = ""
    st.session_state.sub_price = ""
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
    + tanlangan_model
    + "<br><small style='color:#a1a1aa;'>"
    + fan_info["tavsif"]
    + "</small></div>",
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "Jonli AI Chat",
    "Mavzular",
    "Test",
    "Flashcards",
    "Godrik Shifr",
    "Xotira Daftari",
    "Kutubxona",
    "Taymer va Vazifa",
    "Kalkulyator",
    "Python Terminal",
])

tab_chat = tabs[0]
tab_mavzular = tabs[1]
tab_test = tabs[2]
tab_cards = tabs[3]
tab_shifr = tabs[4]
tab_memory = tabs[5]
tab_lib = tabs[6]
tab_timer = tabs[7]
tab_calc = tabs[8]
tab_term = tabs[9]

with tab_chat:
  for idx, m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
      st.markdown(m["content"])
      if m["role"] == "assistant" and "❌" not in m["content"]:
        if st.button("Xotiraga qo'shish", key="s_note_" + str(idx)):
          st.session_state.saved_notes.append({
              "fan": tanlangan_fan,
              "vaqt": datetime.now().strftime("%H:%M"),
              "matn": m["content"],
          })
          st.session_state.xp += 10
          st.toast("Xotiraga qo'shildi! (+10 XP)")

  user_input = st.chat_input(tanlangan_fan + " bo'yicha savolingizni yozing...")
  prompt = (
      st.session_state.pending_prompt
      if st.session_state.pending_prompt
      else user_input
  )
  if st.session_state.pending_prompt:
    st.session_state.pending_prompt = None

  if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.xp += 5
    with st.chat_message("user"):
      st.markdown(prompt)

    if db:
      try:
        db.collection("chat_history").add({
            "role": "user",
            "message": prompt,
            "subject": tanlangan_fan,
            "timestamp": datetime.utcnow(),
        })
      except Exception:
        pass

    with st.chat_message("assistant"):
      with st.spinner(tanlangan_model + " javob bermoqda..."):
        full_resp = call_gemini_engine(
            prompt_text=prompt,
            system_text=build_system_prompt(),
            model_name=tanlangan_model,
            api_key=faol_kalit,
            history_list=st.session_state.messages[:-1],
            auto_fallback=auto_fallback,
        )
        st.markdown(full_resp)

      if db and "❌" not in full_resp:
        try:
          db.collection("chat_history").add({
              "role": "assistant",
              "message": full_resp,
              "subject": tanlangan_fan,
              "timestamp": datetime.utcnow(),
          })
        except Exception:
          pass

      st.session_state.messages.append(
          {"role": "assistant", "content": full_resp}
      )
      st.rerun()

with tab_mavzular:
  st.subheader(tanlangan_fan + " — Asosiy darslik bo'limlari")
  for b in fan_info["asosiy_bolimlar"]:
    st.markdown("- " + b)
  st.markdown("---")
  st.subheader("Bir bosishda so'rash:")
  cols = st.columns(2)
  for idx, s in enumerate(fan_info["tezkor_savollar"]):
    with cols[idx % 2]:
      if st.button(s, key="q_" + str(idx), use_container_width=True):
        st.session_state.pending_prompt = s
        st.rerun()

with tab_test:
  st.subheader("Avtomatik Test va Bilim Sinovi")
  t_mavzu = st.text_input(
      "Test mavzusi (ixtiyoriy):", placeholder="Masalan: Nyuton qonunlari"
  )
  t_soni = st.selectbox("Savollar soni:", [5, 10], index=0)

  if st.button("Testni boshlash", type="primary", use_container_width=True):
    t_prompt = (
        tanlangan_fan
        + " fanidan ("
        + tanlangan_sinf
        + ") '"
        + (t_mavzu if t_mavzu else tanlangan_fan)
        + "' bo'yicha "
        + str(t_soni)
        + " ta test tuz. Variantlari (A, B, C, D) bo'lsin. Oxirida javoblarini"
        " ber."
    )
    with st.spinner("Test tuzilmoqda..."):
      st.session_state.generated_test = call_gemini_engine(
          t_prompt,
          build_system_prompt(),
          tanlangan_model,
          faol_kalit,
          auto_fallback=auto_fallback,
      )
      st.session_state.xp += 20

  if st.session_state.generated_test:
    st.markdown("---")
    st.markdown(st.session_state.generated_test)

with tab_cards:
  st.subheader("Interaktiv Takrorlash Kartochkalari")
  card_fan = st.selectbox(
      "Fan tanlang:", [f for f in FLASHCARDS_DATA.keys()], key="cfan"
  )
  cards_list = FLASHCARDS_DATA[card_fan]

  curr_card = cards_list[st.session_state.f_idx % len(cards_list)]
  st.markdown(
      "Savol "
      + str(st.session_state.f_idx % len(cards_list) + 1)
      + " / "
      + str(len(cards_list))
  )
  st.info(curr_card[0])

  if st.button("Javobni ko'rsatish"):
    st.success(curr_card[1])

  col_fc1, col_fc2 = st.columns(2)
  with col_fc1:
    if st.button("Oldingi"):
      st.session_state.f_idx -= 1
      st.rerun()
  with col_fc2:
    if st.button("Keyingi"):
      st.session_state.f_idx += 1
      st.rerun()

with tab_shifr:
  st.subheader("Godrik Tili va Shifr Generator")
  plain_text = st.text_area("Matnni kiriting:")
  shifr_turi = st.radio(
      "Shifrlash usuli:",
      ["Tersiga o'qish (Revers)", "Godrik Tili (Sirli kod)", "Aylanma shifr"],
  )

  if st.button("Shifrlash"):
    if shifr_turi == "Tersiga o'qish (Revers)":
      res = plain_text[::-1]
    elif shifr_turi == "Godrik Tili (Sirli kod)":
      res = "".join(
          [chr(ord(c) + 3) if c.isalpha() else c for c in plain_text]
      )
    else:
      res = " -.-. ".join([format(ord(c), "b") for c in plain_text])
    st.code(res)

with tab_memory:
  st.subheader("Shaxsiy Xotira Daftari")
  st.write("AI eslab qolishi kerak bo'lgan muhim qoidalar va eslatmalar.")
  if not st.session_state.saved_notes:
    st.info("Hozircha xotira daftari bo'sh.")
  else:
    for i, n in enumerate(st.session_state.saved_notes):
      with st.expander(
          "Xotira #" + str(i + 1) + ": " + n["fan"] + " (" + n["vaqt"] + ")"
      ):
        st.markdown(n["matn"])
    if st.button("Xotirani tozalash"):
      st.session_state.saved_notes = []
      st.rerun()

with tab_lib:
  st.subheader("Raqamli Kutubxona")
  st.write("Shaxsiy kitoblar va materiallar bazasi.")

  with st.form("add_book_form"):
    b_nomi = st.text_input("Kitob yoki material nomi:")
    b_mazmuni = st.text_area("Qisqacha mazmuni yoki matni:")
    submit_book = st.form_submit_button("Kutubxonaga qo'shish")
    if submit_book and b_nomi:
      st.session_state.library_books.append(
          {"nomi": b_nomi, "mazmuni": b_mazmuni}
      )
      st.success("'" + b_nomi + "' kutubxonaga qo'shildi!")
      st.rerun()

  st.markdown("---")
  st.markdown("### Kutubxonadagi materiallar:")
  for idx, book in enumerate(st.session_state.library_books):
    with st.expander(book["nomi"]):
      st.write(book["mazmuni"])

with tab_timer:
  st.subheader("Pomodoro Taymeri va Vazifalar")
  col_t1, col_t2 = st.columns(2)
  with col_t1:
    st.info("25 daqiqa dars / 5 daqiqa dam olish")
    if st.button("Seansni boshlash"):
      st.success("Diqqat rejimi yoqildi!")
  with col_t2:
    st.markdown("### Vazifalar:")
    for t in st.session_state.tasks:
      st.markdown("- " + t["vazifa"] + " (" + t["holat"] + ")")

with tab_calc:
  st.subheader("Ilmiy va Muhandislik Kalkulyatori")
  if_expr = st.text_input(
      "Ifodani kiriting (masalan: 5 * 8 + 10 / 2 yoki 2**10):"
  )
  if st.button("Hisoblash"):
    try:
      ans = eval(if_expr)
      st.success("Natija: " + str(ans))
    except Exception as e:
      st.error("Xatolik: " + str(e))

with tab_term:
  st.subheader("Mini Python Kod Muhiti")
  code_input = st.text_area(
      "Python kodini yozing:", value="print('Salom, Tiliton Tashkiloti!')"
  )
  if st.button("Kodni bajarish"):
    try:
      import io
      import sys

      old_stdout = sys.stdout
      new_stdout = io.StringIO()
      sys.stdout = new_stdout
      exec(code_input)
      sys.stdout = old_stdout
      output = new_stdout.getvalue()
      st.code(output if output else "Kod bajarildi (Natija yo'q)")
    except Exception as e:
      st.error("Xatolik: " + str(e))
