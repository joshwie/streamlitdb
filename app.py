import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import random
import string

# ⬅️ Volle Breite aktivieren
st.set_page_config(layout="wide")

# Firebase-Initialisierung
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": st.secrets["type"],
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"].replace('\n', '\n'),
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"]
    })
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Gruppencode erzeugen
def generate_group_code():
    letter = random.choice(string.ascii_uppercase)
    digit = random.choice(string.digits)
    return f"{letter}{digit}"

if "group_code" not in st.session_state:
    st.session_state.group_code = generate_group_code()

# Titel & Gruppencode-Eingabe
st.title("Pandemieausbrüche unter der Lupe – gemeinsame Analyse")
st.subheader(f"🔖 Gruppen-Code: {st.session_state.group_code}")
manual_code = st.text_input("... oder alternativ Gruppen-Code manuell eingeben (z. B. A1)", value=st.session_state.group_code, max_chars=2, key="manual_code_input")

if manual_code.upper() != st.session_state.group_code:
    st.session_state.group_code = manual_code.upper()
    st.rerun()

# Tabs oben
selected_tab = st.radio("Navigation", ["Szenarien einzeln analysieren", "Szenarien gemeinsam vergleichen"], horizontal=True, label_visibility="collapsed")

# Daten laden
code = st.session_state.group_code
doc_ref = db.collection("szenarien").document(code)
doc = doc_ref.get()
data = doc.to_dict() if doc.exists else {}
szenarien = data.get("szenarien", [])

# EINZELN ANALYSIEREN
if selected_tab == "Szenarien einzeln analysieren":
    st.header("🔍 Szenarien einzeln analysieren")
    if szenarien:
        tab_labels = [s.get("gruppenname", f"Szenario {i+1}") for i, s in enumerate(szenarien)]
        tabs = st.tabs(tab_labels)

        for i, (tab, sz) in enumerate(zip(tabs, szenarien)):
            with tab:
                image_group = sz.get("images", [])
                for j in range(0, min(4, len(image_group)), 2):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(image_group[j], use_container_width=True)
                    if j + 1 < len(image_group):
                        with col2:
                            st.image(image_group[j + 1], use_container_width=True)
                if len(image_group) >= 5:
                    st.image(image_group[4], use_container_width=True)

                # 🗑️ Szenario löschen
                if st.button(f"🗑️ Szenario löschen", key=f"delete_{i}"):
                    new_szenarien = szenarien[:i] + szenarien[i+1:]
                    db.collection("szenarien").document(code).update({"szenarien": new_szenarien})
                    st.rerun()
    else:
        st.info(f"Keine Bilder für Gruppencode '{code}' vorhanden.")

# GEMEINSAM VERGLEICHEN
elif selected_tab == "Szenarien gemeinsam vergleichen":
    st.header("🤔 Szenarien gemeinsam vergleichen")
    if szenarien:
        all_images = [sz.get("images", []) for sz in szenarien]
        grouped = list(zip(*all_images)) if all_images else []

        category_labels = [
            "Infektionsverlauf (SIR)",
            "Infektions-Stati im Zeitverlauf",
            "Infektionen nach Ort",
            "Infektionen nach Alter",
            "Neue Diagnosen nach Alter"
        ]

        for k, category_images in enumerate(grouped):
            label = category_labels[k] if k < len(category_labels) else f"Kategorie {k+1}"
            with st.expander(label):
                cols = st.columns(len(category_images))
                for s, image in enumerate(category_images):
                    with cols[s]:
                        st.image(image, use_container_width=True)
    else:
        st.info(f"Keine Bilder für Gruppencode '{code}' vorhanden.")
