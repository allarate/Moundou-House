# FaxUdm — Application de location immobilière

## Structure du projet

```
FaxUdm/
├── app.py                  # Point d'entrée Streamlit
├── main.py                 # Routeur de pages
├── auth.py                 # Authentification (login/register)
├── layout.py               # Header + Footer commun avec logo
├── users.json              # Base utilisateurs (créé automatiquement)
└── pages/
    ├── __init__.py
    ├── a4.png              # ← Ton logo (déjà présent)
    ├── home.py             # Page d'accueil
    ├── login.py            # Page de connexion
    ├── register.py         # Page d'inscription
    ├── recherche.py        # Recherche de maison
    ├── mise_en_location.py # Publier une annonce
    └── ia.py               # Assistant IA
```

## Installation

```bash
pip install streamlit
```

## Lancement

```bash
streamlit run app.py
```

## Compte par défaut

- **Utilisateur** : admin@faxudm.cm
- **Mot de passe** : admin123
