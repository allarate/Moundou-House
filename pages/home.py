import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from layout import layout
from database import get_stats

def show():
    def content():
        st.markdown("""
            <style>
            .stApp { background-color: #f0f2f6; }
            h1 { text-align: center; color: #1a1a2e; font-size: 2rem; }
            div[data-testid="stButton"] button {
                border-radius: 12px;
                font-size: 15px;
                font-weight: 600;
                width: 100%;
                height: 90px;
                background-color: #1a1a2e;
                color: white;
                border: none;
                transition: all 0.3s;
            }
            div[data-testid="stButton"] button:hover { background-color: #4A90E2; }
            .admin-btn button {
                background-color: #e67e22 !important;
                height: auto !important;
                padding: 12px !important;
            }
            .admin-btn button:hover { background-color: #d35400 !important; }
            </style>
        """, unsafe_allow_html=True)

        col_l, col_c, col_r = st.columns([1, 3, 1])
        with col_c:
            st.title("Accueil")
            nom    = st.session_state.get("nom", "")
            prenom = st.session_state.get("prenom", "")
            st.subheader(f"Bienvenue {prenom} {nom} ")

            role = st.session_state.get("role", "user")
            if role == "admin":
                st.markdown("🔴 **Compte Administrateur**")

            st.markdown("<br>", unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Rechercher\nune maison en location", use_container_width=True):
                    st.session_state.page = "recherche"
                    st.rerun()
            with col2:
                if st.button(" Mettre une maison\nen location", use_container_width=True):
                    st.session_state.page = "mise_en_location"
                    st.rerun()
            with col3:
                if st.button("IA Ready", use_container_width=True):
                    st.session_state.page = "ia"
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Les annonces", use_container_width=True):
                    st.session_state.page = "mes_annonces"
                    st.rerun()
            if role == "admin":
                with col_b:
                    stats = get_stats()
                    en_attente = stats["en_attente"]
                    label = "⚙️ Administration" + (f" 🔴 {en_attente}" if en_attente > 0 else "")
                    st.markdown('<div class="admin-btn">', unsafe_allow_html=True)
                    if st.button(label, use_container_width=True):
                        st.session_state.page = "admin"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    layout(content)
