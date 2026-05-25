import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import register

def show():
    st.markdown("""
        <style>
        .stApp { background-color: #f0f2f6; }
        h1 { text-align: center; color: #1a1a2e; }
        .stButton button {
            background-color: #1a1a2e;
            color: white;
            border-radius: 8px;
            padding: 10px;
            font-size: 15px;
            font-weight: 600;
            width: 100%;
            border: none;
            transition: all 0.3s;
        }
        .stButton button:hover { background-color: #4A90E2; }
        </style>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.title("🏠 FaxUdm")
        st.subheader("Créer un compte")
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("form_inscription"):
            col1, col2 = st.columns(2)
            with col1:
                nom    = st.text_input("👤 Nom *")
            with col2:
                prenom = st.text_input("👤 Prénom *")

            email     = st.text_input("📧 Email *")
            password  = st.text_input("🔑 Mot de passe *", type="password")
            password2 = st.text_input("🔑 Confirmer le mot de passe *", type="password")

            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("S'inscrire", use_container_width=True)

        if submitted:
            if not nom or not prenom or not email or not password or not password2:
                st.error("Veuillez remplir tous les champs obligatoires (*)")
            elif "@" not in email:
                st.error("Veuillez entrer un email valide")
            elif password != password2:
                st.error("Les mots de passe ne correspondent pas")
            elif len(password) < 6:
                st.error("Le mot de passe doit contenir au moins 6 caractères")
            else:
                success, msg = register(nom, prenom, email, password)
                if success:
                    st.success("Compte créé avec succès ! Connectez-vous.")
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Déjà un compte ? Se connecter", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()