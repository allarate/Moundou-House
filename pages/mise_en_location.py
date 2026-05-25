import streamlit as st
import sys, os, json, base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from layout import layout
from database import create_annonce
from PIL import Image
import io

def img_to_base64(img_path):
    img = Image.open(img_path)
    img = img.convert("RGB")
    img = img.resize((200, 133))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()

def show():
    def content():
        st.title("Mettre une maison en location")
        st.info("Votre annonce sera visible après validation par un administrateur.")
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            titre    = st.text_input("Titre de l'annonce *")
            ville    = st.text_input("Ville *")
            quartier = st.text_input("Quartier")
            prix     = st.number_input("Prix mensuel (FCFA) *", min_value=0, step=5000)
        with col2:
            chambres  = st.selectbox("🛏 Nombre de chambres *", ["1", "2", "3", "4", "5", "6+"])
            type_bien = st.selectbox("Type de bien *", ["Appartement", "Villa", "Studio", "Duplex", "Chambre"])
            contact   = st.text_input("Contact *")

        description = st.text_area("Description de la maison", height=120,
                                   placeholder="Décrivez votre bien : superficie, équipements, proximité des commodités...")

        photos = st.file_uploader("📸 Photos de la maison", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        photo_names = []
        if photos:
            images_html = ""
            for photo in photos:
                chemin = os.path.join(upload_dir, photo.name)
                with open(chemin, "wb") as f:
                    f.write(photo.getbuffer())
                photo_names.append(photo.name)
                try:
                    b64 = img_to_base64(chemin)
                    images_html += (
                        '<img src="data:image/jpeg;base64,' + b64 + '" '
                        'style="width:200px;height:133px;object-fit:cover;'
                        'border-radius:8px;margin-right:8px;margin-bottom:8px;" />'
                    )
                except:
                    pass

            if images_html:
                st.markdown(
                    '<div style="text-align:center;margin-top:0.5rem;">' + images_html + '</div>',
                    unsafe_allow_html=True
                )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("📤 Soumettre l'annonce", use_container_width=True):
            if not titre or not ville or not contact or prix == 0:
                st.error("Veuillez remplir tous les champs obligatoires (*)")
            else:
                create_annonce({
                    "titre":        titre,
                    "type_bien":    type_bien,
                    "ville":        ville,
                    "quartier":     quartier,
                    "chambres":     chambres,
                    "prix":         prix,
                    "contact":      contact,
                    "description":  description,
                    "photos":       json.dumps(photo_names),
                    "proprietaire": st.session_state.get("user")
                })
                st.success("Annonce soumise ! Elle sera visible après validation par un administrateur.")
                st.balloons()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬅ Retour à l'accueil", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

    layout(content)