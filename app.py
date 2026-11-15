"""
================================================================================
LOYIHA: FIRIMARI AI — ULTIMATE IMPERIAL EDITION (v18.2 Vision)
MUALLIF: Farrux G'aybilloyev (Tiliton Tashkiloti)
================================================================================
"""

from datetime import datetime, timedelta
import base64
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
    page_title="Firimari AI v18.2 Vision",
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

# Sessiya holatlari
if "messages" not in st.session_state:
  st.session_state.messages = []
if "saved_notes" not in st.session_state:
  st.session_state.saved_notes = [
      (
          "Yangi Daftar #1",
          "Godrik tili shifrlari va kelajakdagi ixtirolar rejasi.",
      )
  ]
if "library_books" not in st.session_state:
  st.session_state.library_books = [
      ("Godrik Tili va Shifrlar", "Farruxning shaxsiy shifrlari."),
      ("Fizika Formulalari", "Kinematika va dinamika asoslari."),
  ]
if "xp" not in st.session_state:
  st.session_state.xp = 350
if "pending_prompt" not in st.session_state:
  st.session_state.pending_prompt = None
if "generated_test" not in st.session_state:
  st.session_state.generated_test = ""

MAKTAB_FANLARI_BAZASI = {
    "Barcha fanlar (Universal rejim)": {
        "icon": "🌐",
        "tavsif": "1-11-sinf maktab dasturidagi barcha fanlar.",
        "yo_riqnoma": (
            "Sen Farrux G'aybilloyev yaratgan Firimari Aisan — ta'lim"
            " platformasisan."
        ),
        "asosiy_bolimlar": ["Aniq fanlar", "Tabiiy fanlar", "Ijtimoiy fanlar"],
        "tezkor_savollar": ["Nyutonning uchta qonunini hayotiy misol bilan ayt"],
    },
    "Fizika va Astronomiya": {
        "icon": "⚡",
        "tavsif": "Mexanika, termodinamika va elektr.",
        "yo_riqnoma": "Sen fizika va astronomiya mutaxassissan.",
        "asosiy_bolimlar": ["Kinematika", "Dinamika", "Om qonuni"],
        "tezkor_savollar": ["Om qonuni nima va qanday ishlatiladi?"],
    },
    "Matematika": {
        "icon": "📐",
        "tavsif": "Algebra va geometriya.",
        "yo_riqnoma": "Sen matematika mutaxassissan.",
        "asosiy_bolimlar": ["Kvadrat tenglamalar", "Pifagor teoremasi"],
        "tezkor_savollar": ["Diskriminant formulasi qanday?"],
    },
    "Tarix": {
        "icon": "🏛️",
        "tavsif": "O'zbekiston va jahon tarixi.",
        "yo_riqnoma": "Sen tarix fanidan mutaxassissan.",
        "asosiy_bolimlar": ["Temuriylar davri", "Buyuk Ipak yo'li"],
        "tezkor_savollar": ["Amir Temur davri boshqaruvi haqida ayt"],
    },
}

SINFLAR_ROYXATI = [
    "Barcha sinflar",
    "5-sinf",
    "6-sinf",
    "7-sinf",
    "8-sinf",
    "9-sinf",
    "10-sinf",
    "11-sinf",
]

with st.sidebar:
  st.markdown("## FIRIMARI AI v18.2")
  st.info(
      f"Obuna: **{st.session_state.sub_type}**\nNarxi:"
      f" **{st.session_state.sub_price}**"
  )
  if st.button("Chiqish"):
    st.session_state.authenticated = False
    st.rerun()

  st.markdown("---")
  st.write("Foydalanuvchi: Farrux G'aybilloyev")
  st.write("Unvon: Bosh Muhandis")
  st.metric(label="XP (Tajriba ochko)", value=int(st.session_state.xp))

  st.markdown("---")
  custom_key = st.text_input(
      "Google AI Studio API Key:", value=DEFAULT_API_KEY, type="password"
  )
  active_key = custom_key.strip() if custom_key.strip() else DEFAULT_API_KEY

  tanlangan_model = st.selectbox("AI Model:", AVAILABLE_MODELS)
  auto_fallback = st.checkbox("Avtomatik zaxira modelga o'tish", value=True)
  tanlangan_fan = st.selectbox(
      "Fan yo'nalishi:", list(MAKTAB_FANLARI_BAZASI.keys())
  )
  tanlangan_sinf = st.selectbox("Sinf:", SINFLAR_ROYXATI)

  if st.button("Yangi chat"):
    st.session_state.messages = []
    st.rerun()

fan_info = MAKTAB_FANLARI_BAZASI[tanlangan_fan]


def call_gemini_vision_engine(
    prompt_text,
    system_text,
    model_name,
    api_key,
    image_bytes=None,
    mime_type="image/jpeg",
):
  url = (
      "https://generativelanguage.googleapis.com/v1beta/models/"
      + model_name
      + ":generateContent?key="
      + api_key
  )

  parts = [{"text": prompt_text}]
  if image_bytes:
    encoded_img = base64.b64encode(image_bytes).decode("utf-8")
    parts.append({
        "inline_data": {"mime_type": mime_type, "data": encoded_img}
    })

  payload = {
      "system_instruction": {"parts": [{"text": system_text}]},
      "contents": [{"role": "user", "parts": parts}],
      "generationConfig": {"temperature": 0.5, "maxOutputTokens": 4096},
  }

  headers = {"Content-Type": "application/json"}
  try:
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )
    with urllib.request.urlopen(req, timeout=50) as resp:
      data = json.loads(resp.read().decode("utf-8"))
      return True, data["candidates"][0]["content"]["parts"][0]["text"]
  except Exception as e:
    return False, str(e)


st.title(f"{fan_info['icon']} Firimari AI — Imperial Ta'lim Tizimi")
st.markdown(
    f"<div class='subject-banner'><b>Fan:</b> {tanlangan_fan} | <b>Sinf:</b>"
    f" {tanlangan_sinf} | <b>Model:</b> {tanlangan_model}<br><small"
    f" style='color:#a1a1aa;'>{fan_info['tavsif']}</small></div>",
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "Jonli AI Chat & Rasm",
    "Mavzular",
    "Test va Sinov",
    "Yangi Daftar (Eslatmalar)",
    "Raqamli Kutubxona",
    "Kalkulyator",
    "Python Terminal",
])

with tabs[0]:
  for idx, m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"]):
      st.markdown(m["content"])
      if m.get("image"):
        st.image(m["image"], caption="Yuklangan rasm", width=300)

  uploaded_file = st.file_uploader(
      "Rasm yuklash (Ixtiyoriy - masalan masala yoki chizma):",
      type=["jpg", "jpeg", "png"],
  )
  user_input = st.chat_input("Savolingizni yozing yoki rasm bo'yicha so'rang...")

  if user_input or uploaded_file:
    prompt = (
        user_input if user_input else "Bu rasmda nima tasvirlangan? Tushuntirib ber."
    )
    img_bytes = uploaded_file.getvalue() if uploaded_file else None
    mime = uploaded_file.type if uploaded_file else "image/jpeg"

    msg_payload = {"role": "user", "content": prompt}
    if uploaded_file:
      msg_payload["image"] = img_bytes
    st.session_state.messages.append(msg_payload)
    st.session_state.xp += 5

    with st.chat_message("user"):
      st.markdown(prompt)
      if uploaded_file:
        st.image(uploaded_file, width=300)

    with st.chat_message("assistant"):
      with st.spinner(f"{tanlangan_model} tahlil qilmoqda..."):
        sys_prompt = (
            f"Sen Farrux G'aybilloyev yaratgan Firimari Aisan. Fan:"
            f" {tanlangan_fan}, Sinf: {tanlangan_sinf}."
            f" {fan_info['yo_riqnoma']}"
        )
        success, resp = call_gemini_vision_engine(
            prompt,
            sys_prompt,
            tanlangan_model,
            active_key,
            image_bytes=img_bytes,
            mime_type=mime,
        )
        st.markdown(resp)
      st.session_state.messages.append({"role": "assistant", "content": resp})
    st.rerun()

with tabs[1]:
  st.subheader(f"{tanlangan_fan} — Asosiy bo'limlar")
  for b in fan_info["asosiy_bolimlar"]:
    st.markdown(f"- {b}")
  st.markdown("---")
  st.markdown("### Tezkor savollar:")
  cols = st.columns(2)
  for idx, s in enumerate(fan_info["tezkor_savollar"]):
    with cols[idx % 2]:
      if st.button(s, key=f"q_{idx}", use_container_width=True):
        st.session_state.pending_prompt = s
        st.rerun()

with tabs[2]:
  st.subheader("Avtomatik Test Tizimi")
  t_mavzu = st.text_input("Test mavzusi (ixtiyoriy):")
  t_soni = st.selectbox("Savollar soni:", [5, 10], index=0)

  if st.button("Test tuzishni boshlash", type="primary"):
    t_prompt = (
        f"{tanlangan_fan} fanidan ({tanlangan_sinf}) "
        f"'{t_mavzu if t_mavzu else tanlangan_fan}' bo'yicha {t_soni} ta test"
        " tuz. Variantlari (A, B, C, D) va oxirida javoblarini ber."
    )
    with st.spinner("Test tuzilmoqda..."):
      success, test_res = call_gemini_vision_engine(
          t_prompt,
          "Sen qattiqqo'l fan o'qituvchisisan.",
          tanlangan_model,
          active_key,
      )
      st.session_state.generated_test = test_res
      st.session_state.xp += 20

  if st.session_state.generated_test:
    st.markdown("---")
    st.markdown(st.session_state.generated_test)

with tabs[3]:
  st.subheader("📝 Yangi Daftar (Shaxsiy Eslatmalar va G'oyalar)")
  st.write("O'zingizning shaxsiy eslatmalaringizni yozib saqlang:")

  note_title = st.text_input("Daftar mavzusi / sarlavhasi:")
  note_content = st.text_area("Yozuv va qaydlar mazmuni:")

  if st.button("Daftarga qo'shish"):
    if note_title:
      st.session_state.saved_notes.append((note_title, note_content))
      st.success("Yangi daftarga muvaffaqiyatli yozildi!")
      st.rerun()
    else:
      st.error("Iltimos, daftar mavzusini kiriting!")

  st.markdown("---")
  for title, content in st.session_state.saved_notes:
    with st.expander(f"📖 {title}"):
      st.write(content)

with tabs[4]:
  st.subheader("Raqamli Kutubxona")
  for title, content in st.session_state.library_books:
    with st.expander(title):
      st.write(content)

with tabs[5]:
  st.subheader("Ilmiy Kalkulyator")
  expr = st.text_input("Ifodani kiriting (masalan: 15 * 8 + 50):")
  if st.button("Hisoblash"):
    try:
      st.success(f"Natija: {eval(expr)}")
    except Exception as e:
      st.error(f"Xatolik: {e}")

with tabs[6]:
  st.subheader("Python Kod Muhiti")
  code = st.text_area("Python kodini yozing:", value="print('Salom, Tiliton!')")
  if st.button("Kodni bajarish"):
    try:
      import io
      import sys

      old = sys.stdout
      new = io.StringIO()
      sys.stdout = new
      exec(code)
      sys.stdout = old
      st.code(new.getvalue() if new.getvalue() else "Kod bajarildi.")
    except Exception as e:
      st.error(f"Xatolik: {e}")
        
