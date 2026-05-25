import streamlit as st
import sys, os, json, base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from layout import layout
from database import get_annonces_validees, add_interet, count_interets
from PIL import Image
import io

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")
CONTACT_SERVICE = "+23560856572"

def img_to_base64(img_path):
    img = Image.open(img_path)
    img = img.convert("RGB")
    img = img.resize((200, 133))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()

def show():
    def content():
        st.title("🔍 Rechercher une maison en location")
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("form_recherche"):
            col1, col2 = st.columns(2)
            with col1:
                ville    = st.text_input("📍 Ville")
                quartier = st.text_input("🗺 Quartier")
            with col2:
                type_bien = st.selectbox("🏠 Type", ["Tous", "Appartement", "Villa", "Studio", "Duplex", "Chambre"])
                chambres  = st.selectbox("🛏 Chambres", ["Toutes", "1", "2", "3", "4", "5", "6+"])
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🔍 Rechercher", use_container_width=True)

        if submitted:
            annonces = get_annonces_validees(
                ville=ville if ville else None,
                quartier=quartier if quartier else None,
                type_bien=type_bien if type_bien != "Tous" else None,
                chambres=chambres if chambres != "Toutes" else None,
            )
            st.session_state["resultats_recherche"] = [dict(a) for a in annonces]

        annonces = st.session_state.get("resultats_recherche", None)

        if annonces is None:
            pass
        elif len(annonces) == 0:
            st.warning("Aucune annonce trouvée. Essayez d'autres critères.")
        else:
            st.success(f"✅ {len(annonces)} annonce(s) trouvée(s)")
            st.markdown("<br>", unsafe_allow_html=True)

            for a in annonces:
                try:
                    photos = json.loads(a['photos']) if a['photos'] else []
                except:
                    photos = []

                images_html = ""
                for nom_photo in photos:
                    chemin = os.path.normpath(os.path.join(UPLOAD_DIR, nom_photo))
                    if os.path.exists(chemin):
                        try:
                            b64 = img_to_base64(chemin)
                            images_html += (
                                '<img src="data:image/jpeg;base64,' + b64 + '" '
                                'style="width:200px;height:133px;object-fit:cover;'
                                'border-radius:8px;margin-right:8px;margin-bottom:8px;" />'
                            )
                        except:
                            pass

                quartier_txt = ' — ' + a['quartier'] if a['quartier'] else ''
                nb_interets  = count_interets(a['id'])

                st.markdown(
                    '<div style="background:white;border-radius:12px;padding:1.5rem;'
                    'margin-bottom:1rem;box-shadow:0 2px 8px rgba(0,0,0,0.08);'
                    'max-width:700px;margin-left:auto;margin-right:auto;">'
                    + ('<div style="text-align:center;margin-bottom:0.8rem;">' + images_html + '</div>' if images_html else '')
                    + '<h3 style="color:#1a1a2e;margin:0.5rem 0;text-align:center;">🏠 ' + a['titre'] + '</h3>'
                    '<p style="color:#666;margin:0.2rem 0;text-align:center;">'
                    '📍 ' + a['ville'] + quartier_txt +
                    ' &nbsp;|&nbsp; 🏠 ' + a['type_bien'] +
                    ' &nbsp;|&nbsp; 🛏 ' + a['chambres'] + ' chambre(s)</p>'
                    '<p style="color:#4A90E2;font-size:1.2rem;font-weight:700;margin:0.5rem 0;text-align:center;">'
                    '💰 ' + f"{int(a['prix']):,}" + ' FCFA / mois</p>'
                    '<p style="color:#444;margin:0.3rem 0;text-align:center;">' + (a['description'] or '') + '</p>'
                    '<p style="color:#1a1a2e;font-weight:600;text-align:center;">📞 Contacter le service : ' + CONTACT_SERVICE + '</p>'
                    '<p style="color:#e74c3c;font-size:0.9rem;text-align:center;font-weight:600;">❤️ ' + str(nb_interets) + ' personne(s) intéressée(s)</p>'
                    '</div>',
                    unsafe_allow_html=True
                )

                # ===== BOUTON INTÉRESSÉ =====
                col_l, col_c, col_r = st.columns([1, 2, 1])
                with col_c:
                    if st.button("❤️ Je suis intéressé(e)", key=f"int_{a['id']}", use_container_width=True):
                        st.session_state[f"show_form_{a['id']}"] = True

                # ===== FORMULAIRE INTÉRÊT =====
                if st.session_state.get(f"show_form_{a['id']}", False):
                    col_l, col_c, col_r = st.columns([1, 2, 1])
                    with col_c:
                        with st.form(f"form_interet_{a['id']}"):
                            st.markdown("**Laissez votre numéro de téléphone**")
                            telephone = st.text_input("📞 Votre numéro *")
                            send = st.form_submit_button("✅ Envoyer ma demande", use_container_width=True)
                            if send:
                                if not telephone:
                                    st.error("Veuillez entrer votre numéro")
                                else:
                                    ok, msg = add_interet(
                                        a['id'],
                                        st.session_state.get("user", ""),
                                        st.session_state.get("nom", ""),
                                        st.session_state.get("prenom", ""),
                                        telephone
                                    )
                                    if ok:
                                        st.success(msg)
                                        st.session_state[f"show_form_{a['id']}"] = False
                                        st.rerun()
                                    else:
                                        st.warning(msg)

                st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬅ Retour à l'accueil", use_container_width=True):
            st.session_state.pop("resultats_recherche", None)
            st.session_state.page = "home"
            st.rerun()

    layout(content)
