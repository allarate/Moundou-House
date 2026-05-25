from database import get_user_by_email, create_user

def login(email, password):
    user = get_user_by_email(email)
    if user and user["password"] == password:
        return True, user["role"], user["nom"], user["prenom"]
    return False, None, None, None

def register(nom, prenom, email, password):
    return create_user(nom, prenom, email, password, role="user")

def is_admin(email):
    user = get_user_by_email(email)
    return user and user["role"] == "admin"
