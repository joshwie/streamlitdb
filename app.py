import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import random
import string

# Firebase initialization
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": st.secrets["type"],
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"].replace('\\n', '\n'),
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"]
    })
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Generate random group code (1 letter + 1 digit)
def generate_group_code():
    letter = random.choice(string.ascii_uppercase)
    digit = random.choice(string.digits)
    return f"{letter}{digit}"

# Store group code in session state
if "group_code" not in st.session_state:
    st.session_state.group_code = generate_group_code()

# Title and group code display
st.title("Pandemic Intervention Plan")
st.subheader(f"🧬 Group Code: {st.session_state.group_code}")

# Sidebar navigation
selected_tab = st.sidebar.radio("Navigation", ["Analyze Scenarios", "Compare Scenarios"])

# Fetch data from Firestore
code = st.session_state.group_code
doc_ref = db.collection("szenarien").document(code)
doc = doc_ref.get()
images = doc.to_dict().get("images", []) if doc.exists else []

# Display logic based on tab selection
if selected_tab == "Analyze Scenarios":
    st.header("Analyze Scenarios")
    if images:
        for url in images:
            st.image(url, width=500)
    else:
        st.info("No images available for this group code.")

elif selected_tab == "Compare Scenarios":
    st.header("Compare Scenarios")
    if images:
        cols = st.columns(2)
        for i, url in enumerate(images):
            with cols[i % 2]:
                st.image(url, caption=f"Image {i+1}", use_column_width=True)
    else:
        st.info("No comparison data available.")
