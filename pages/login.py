import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import login

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
        st.title("Moundou House")
        st.subheader("Connexion")
        st.markdown("<br>", unsafe_allow_html=True)

        email    = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Se connecter", use_container_width=True):
            success, role, nom, prenom = login(email, password)
            if success:
                st.session_state.user   = email
                st.session_state.role   = role
                st.session_state.nom    = nom
                st.session_state.prenom = prenom
                st.session_state.page   = "home"
                st.rerun()
            else:
                st.error("Email ou mot de passe incorrect")

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Pas de compte ? S'inscrire", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()
