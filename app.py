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

# Gruppencode im Session-State speichern
if "group_code" not in st.session_state:
    st.session_state.group_code = generate_group_code()

# Titel und Gruppencode anzeigen
st.title("Pandemie-Interventionsplan")
st.subheader(f"🔖 Gruppencode: {st.session_state.group_code}")

# Alternative manuelle Eingabe
st.markdown("**... oder alternativ Gruppencode manuell eingeben:**")
manual_code = st.text_input("Gruppencode eingeben (z. B. A1)", value="", max_chars=2)
if manual_code:
    st.session_state.group_code = manual_code.upper()

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
        for url in images:
            st.image(url, width=500)
    else:
        st.info("Keine Bilder für diesen Gruppencode vorhanden.")

elif selected_tab == "Szenarien gemeinsam vergleichen":
    st.header("Szenarien gemeinsam vergleichen")
    if images:
        cols = st.columns(2)
        for i, url in enumerate(images):
            with cols[i % 2]:
                st.image(url, caption=f"Bild {i+1}", use_column_width=True)
    else:
        st.info("Keine Bilder für diesen Gruppencode vorhanden.")
