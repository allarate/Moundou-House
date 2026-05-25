import streamlit as st
import os
import base64

def layout(content_fn):
    if st.query_params.get("action") == "logout":
        for key in ["user", "role", "nom", "prenom"]:
            st.session_state[key] = None
        st.session_state.page = "login"
        st.query_params.clear()
        st.rerun()

    nom    = st.session_state.get("nom") or ""
    prenom = st.session_state.get("prenom") or ""
    display = (prenom + " " + nom).strip() or st.session_state.get("user") or ""

    logo_html = ""
    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages", "a4.png")
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        logo_html = '<img src="data:image/png;base64,' + b64 + '" style="height:40px;width:auto;object-fit:contain;" />'

    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .custom-header {
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 60px;
            background-color: #1a1a2e;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 2rem;
            z-index: 9999;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        .header-left { display: flex; align-items: center; }
        .header-right { display: flex; align-items: center; gap: 1rem; }
        .header-right .user { font-size: 0.9rem; color: #ccc; white-space: nowrap; }
        .header-right .btn-logout {
            background-color: transparent;
            color: #e74c3c;
            border: 1.5px solid #e74c3c;
            border-radius: 6px;
            padding: 5px 14px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            white-space: nowrap;
            transition: all 0.2s;
        }
        .header-right .btn-logout:hover { background-color: #e74c3c; color: white; }
        .custom-footer {
            position: fixed;
            bottom: 0; left: 0; right: 0;
            height: 50px;
            background-color: #1a1a2e;
            color: #aaa;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85rem;
            z-index: 9999;
        }
        </style>
    """, unsafe_allow_html=True)

    header_html = (
        '<div class="custom-header">'
        '<div class="header-left">' + logo_html + '</div>'
        '<div class="header-right">'
        '<span class="user">&#128100; ' + display + '</span>'
        '<a href="?action=logout" class="btn-logout" target="_self">&#128682; D&eacute;connexion</a>'
        '</div>'
        '</div>'
        '<div style="height:70px;"></div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

    content_fn()

    st.markdown("""
        <div class="custom-footer">
            &copy; 2025 FaxUdm &mdash; Tous droits r&eacute;serv&eacute;s
        </div>
    """, unsafe_allow_html=True)