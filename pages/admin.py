import streamlit as st
import sys, os, json, base64
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from layout import layout
from database import (get_annonces_par_statut, valider_annonce, rejeter_annonce,
                      get_stats, get_all_users, update_user_role,
                      get_interets_par_annonce, marquer_occupe, marquer_disponible)
from PIL import Image
import io

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uploads")

def img_to_base64(img_path):
    try:
        img = Image.open(img_path)
        img = img.convert("RGB")
        img = img.resize((250, 167))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        return base64.b64encode(buf.getvalue()).decode()
    except:
        return None

def get_images_html(photos_json):
    try:
        photos = json.loads(photos_json) if photos_json else []
    except:
        photos = []
    images_html = ""
    for nom_photo in photos:
        chemin = os.path.normpath(os.path.join(UPLOAD_DIR, nom_photo))
        if os.path.exists(chemin):
            b64 = img_to_base64(chemin)
            if b64:
                images_html += (
                    '<img src="data:image/jpeg;base64,' + b64 + '" '
                    'style="width:250px;height:167px;object-fit:cover;'
                    'border-radius:8px;margin-right:8px;margin-bottom:8px;" />'
                )
    return images_html

def show():
    def content():
        st.title("⚙️ Administration FaxUdm")
        admin = st.session_state.get("user")

        # ===== STATS =====
        stats = get_stats()
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("📋 Total",        stats["total"])
        c2.metric("🟡 En attente",   stats["en_attente"])
        c3.metric("🟢 Validées",     stats["validées"])
        c4.metric("🔴 Rejetées",     stats["rejetées"])
        c5.metric("🔒 Occupées",     stats["occupées"])
        c6.metric("👥 Utilisateurs", stats["users"])
        st.markdown("---")

        tab1, tab2, tab3 = st.tabs([
            "🟡 En attente",
            "❤️ Demandes d'intérêt",
            "👥 Utilisateurs"
        ])

        # ===== TAB 1 : En attente =====
        with tab1:
            annonces = get_annonces_par_statut("en_attente")
            if not annonces:
                st.success("✅ Aucune annonce en attente.")
            else:
                st.markdown(f"**{len(annonces)} annonce(s) à valider**")
                for a in annonces:
                    images_html = get_images_html(a['photos'])
                    st.markdown(
                        '<div style="background:white;border-radius:12px;padding:1.2rem;'
                        'margin-bottom:0.5rem;box-shadow:0 2px 8px rgba(0,0,0,0.08);'
                        'border-left:5px solid #f39c12;">'
                        + ('<div style="margin-bottom:0.8rem;text-align:center;">' + images_html + '</div>' if images_html else '')
                        + '<h3 style="color:#1a1a2e;margin:0;">🏠 ' + a['titre'] + '</h3>'
                        '<p style="color:#666;margin:0.3rem 0;">'
                        '📍 ' + a['ville'] + (' — ' + a['quartier'] if a['quartier'] else '') +
                        ' | 🏠 ' + a['type_bien'] + ' | 🛏 ' + a['chambres'] + ' ch.'
                        ' | 💰 <strong>' + f"{int(a['prix']):,}" + ' FCFA/mois</strong></p>'
                        '<p style="color:#444;">' + (a['description'] or '') + '</p>'
                        '<p style="color:#aaa;font-size:0.8rem;">Soumis par <strong>' + a['proprietaire'] + '</strong> le ' + a['date_creation'][:10] + '</p>'
                        '</div>',
                        unsafe_allow_html=True
                    )
                    col_v, col_r, col_sp = st.columns([2, 2, 4])
                    with col_v:
                        if st.button("✅ Valider", key=f"val_{a['id']}", use_container_width=True):
                            valider_annonce(a["id"], admin)
                            st.success(f"Annonce '{a['titre']}' validée !")
                            st.rerun()
                    with col_r:
                        if st.button("❌ Rejeter", key=f"rej_{a['id']}", use_container_width=True):
                            rejeter_annonce(a["id"], admin)
                            st.warning(f"Annonce '{a['titre']}' rejetée.")
                            st.rerun()
                    st.markdown("---")

        # ===== TAB 2 : Demandes d'intérêt avec image + boutons =====
        with tab2:
            annonces_val = get_annonces_par_statut("validée")
            has_interets = False

            for a in annonces_val:
                interets = get_interets_par_annonce(a['id'])
                if not interets:
                    continue
                has_interets = True

                occupe      = a['statut_occupation'] == 'occupé' if a['statut_occupation'] else False
                color       = "#e74c3c" if occupe else "#27ae60"
                label       = "🔒 OCCUPÉE" if occupe else "✅ DISPONIBLE"
                images_html = get_images_html(a['photos'])

                st.markdown(
                    '<div style="background:white;border-radius:12px;padding:1.2rem;'
                    'margin-bottom:0.5rem;box-shadow:0 2px 8px rgba(0,0,0,0.08);'
                    'border-left:5px solid ' + color + ';">'
                    '<div style="display:flex;justify-content:space-between;align-items:center;">'
                    '<h3 style="color:#1a1a2e;margin:0;">🏠 ' + a['titre'] +
                    ' — 📍 ' + a['ville'] + (' — ' + a['quartier'] if a['quartier'] else '') + '</h3>'
                    '<span style="background:' + color + '20;color:' + color + ';padding:4px 12px;'
                    'border-radius:20px;font-size:0.85rem;font-weight:600;">' + label + '</span>'
                    '</div>'
                    + ('<div style="margin:0.8rem 0;text-align:center;">' + images_html + '</div>' if images_html else '')
                    + '<p style="color:#666;margin:0.3rem 0;">'
                    '🏠 ' + a['type_bien'] + ' | 🛏 ' + a['chambres'] + ' ch.'
                    ' | 💰 <strong>' + f"{int(a['prix']):,}" + ' FCFA/mois</strong></p>'
                    '<p style="color:#e74c3c;font-weight:600;">❤️ ' + str(len(interets)) + ' demande(s)</p>'
                    '</div>',
                    unsafe_allow_html=True
                )

                # Boutons occupée / en location
                col1, col2, col3 = st.columns([2, 2, 4])
                with col1:
                    if not occupe:
                        if st.button("🔒 Occupée", key=f"occ_{a['id']}", use_container_width=True):
                            marquer_occupe(a['id'])
                            st.rerun()
                    else:
                        if st.button("🟢 En location", key=f"lib_{a['id']}", use_container_width=True):
                            marquer_disponible(a['id'])
                            st.rerun()

                # Liste des demandeurs
                st.markdown("<br>", unsafe_allow_html=True)
                for i in interets:
                    st.markdown(
                        '<div style="background:#f8f9fa;border-radius:8px;padding:0.8rem 1.2rem;'
                        'margin-bottom:0.4rem;border-left:4px solid #e74c3c;">'
                        '<p style="margin:0;color:#1a1a2e;">👤 <strong>' + str(i['user_prenom']) + ' ' + str(i['user_nom']) + '</strong>'
                        ' &nbsp;|&nbsp; 📧 ' + str(i['user_email']) +
                        ' &nbsp;|&nbsp; 📞 <strong style="color:#e74c3c;font-size:1.1rem;">' + str(i['telephone']) + '</strong></p>'
                        '<p style="margin:0;color:#aaa;font-size:0.8rem;">🕐 ' + str(i['date_demande'])[:16] + '</p>'
                        '</div>',
                        unsafe_allow_html=True
                    )
                st.markdown("<br>", unsafe_allow_html=True)

            if not has_interets:
                st.info("Aucune demande d'intérêt pour le moment.")

        # ===== TAB 3 : Utilisateurs =====
        with tab3:
            st.markdown("**Gestion des rôles utilisateurs**")
            users = get_all_users()
            for u in users:
                col_u, col_r2 = st.columns([3, 2])
                with col_u:
                    role_icon = "🔴 Admin" if u["role"] == "admin" else "👤 User"
                    st.markdown(f"**{u['prenom']} {u['nom']}** ({u['email']}) — {role_icon}")
                with col_r2:
                    if u["email"] != admin:
                        nouveau_role = "user" if u["role"] == "admin" else "admin"
                        label_btn = "👤 Rétrograder" if u["role"] == "admin" else "🔴 Promouvoir admin"
                        if st.button(label_btn, key=f"role_{u['id']}", use_container_width=True):
                            update_user_role(u["email"], nouveau_role)
                            st.rerun()
                    else:
                        st.markdown("*(vous-même)*")
                st.markdown("---")

        if st.button("⬅ Retour à l'accueil", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

    layout(content)