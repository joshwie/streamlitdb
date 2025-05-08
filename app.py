import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import random
import string

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

# Zufälligen Gruppencode erzeugen (1 Buchstabe + 1 Ziffer)
def generate_group_code():
    letter = random.choice(string.ascii_uppercase)
    digit = random.choice(string.digits)
    return f"{letter}{digit}"

# Gruppencode initialisieren
if "group_code" not in st.session_state:
    st.session_state.group_code = generate_group_code()

# Titel anzeigen
st.title("Pandemieausbrüche unter der Lupe")

# Alternative manuelle Eingabe
st.subheader(f"🔖 Gruppencode: {st.session_state.group_code}")

manual_code = st.text_input("... oder alternativ Gruppencode manuell eingeben (z. B. A1)", value=st.session_state.group_code, max_chars=2, key="manual_code_input")

# Gruppencode übernehmen, wenn geändert
if manual_code.upper() != st.session_state.group_code:
    st.session_state.group_code = manual_code.upper()
    st.rerun()

# Navigation horizontal oben
selected_tab = st.radio("", ["Szenarien einzeln analysieren", "Szenarien gemeinsam vergleichen"], horizontal=True)

# Daten aus Firestore abrufen
code = st.session_state.group_code
doc_ref = db.collection("szenarien").document(code)
doc = doc_ref.get()
images = doc.to_dict().get("images", []) if doc.exists else []

# Anzeige der Szenarien
if selected_tab == "Szenarien einzeln analysieren":
    st.header("Szenarien einzeln analysieren")
    if images:
        cols = st.columns(2)
        for i, url in enumerate(images):
            if i == len(images) - 1:
                st.image(url, use_container_width=True)
            else:
                with cols[i % 2]:
                    st.image(url, use_container_width=True)
    else:
        st.info(f"Keine Bilder für Gruppencode '{code}' vorhanden.")

elif selected_tab == "Szenarien gemeinsam vergleichen":
    st.header("Szenarien gemeinsam vergleichen")
    if images:
        # Gruppiere Bilder in 5er-Blöcke für Kategorien
        grouped_images = [images[i:i+5] for i in range(0, len(images), 5)]
        for i, group in enumerate(grouped_images):
            with st.expander(f"Kategorie {i+1}"):
                cols = st.columns(5)
                for j, url in enumerate(group):
                    with cols[j % 5]:
                        st.image(url, use_container_width=True)
    else:
        st.info(f"Keine Bilder für Gruppencode '{code}' vorhanden.")
