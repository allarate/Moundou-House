import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from layout import layout

def show():
    def content():
        st.title(" Assistant IA FaxUdm")
        st.markdown("Posez vos questions sur la location immobilière au Cameroun.")
        st.markdown("<br>", unsafe_allow_html=True)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if prompt := st.chat_input("Ex: Quel est le prix moyen d'un appartement à Douala ?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            p = prompt.lower()
            if "prix" in p or "loyer" in p:
                rep = " Les loyers à Douala varient entre 50 000 et 500 000 FCFA selon le quartier et le type de bien."
            elif "quartier" in p:
                rep = "📍 Quartiers populaires : Bonamoussadi, Akwa, Bonapriso, Makepe, Logbaba."
            elif "chambre" in p or "studio" in p:
                rep = "🛏 Studio : 50 000–100 000 FCFA/mois. Appartement 2 chambres : 100 000–250 000 FCFA/mois."
            else:
                rep = f"Merci pour votre question. Notre IA immobilière est en cours de développement. Consultez nos annonces pour trouver votre logement !"

            st.session_state.messages.append({"role": "assistant", "content": rep})
            with st.chat_message("assistant"):
                st.write(rep)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑 Effacer la conversation", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("⬅ Retour à l'accueil", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()

    layout(content)
