import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faxudm.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS annonces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            type_bien TEXT NOT NULL,
            ville TEXT NOT NULL,
            quartier TEXT,
            chambres TEXT NOT NULL,
            prix INTEGER NOT NULL,
            contact TEXT NOT NULL,
            description TEXT,
            photos TEXT,
            proprietaire TEXT NOT NULL,
            statut TEXT NOT NULL DEFAULT 'en_attente',
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_validation TIMESTAMP,
            valide_par TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS interets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            annonce_id INTEGER NOT NULL,
            user_email TEXT NOT NULL,
            user_nom TEXT,
            user_prenom TEXT,
            telephone TEXT,
            date_demande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(annonce_id, user_email)
        )
    """)

    c.execute("SELECT * FROM users WHERE email = 'admin@faxudm.cm'")
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (nom, prenom, email, password, role) VALUES (?, ?, ?, ?, ?)",
            ("Admin", "FaxUdm", "admin@faxudm.cm", "admin123", "admin")
        )

    try:
        c.execute("ALTER TABLE annonces ADD COLUMN statut_occupation TEXT DEFAULT 'disponible'")
    except:
        pass
    try:
        c.execute("ALTER TABLE annonces ADD COLUMN valide_par TEXT")
    except:
        pass

    conn.commit()
    conn.close()

# ===== USERS =====

def create_user(nom, prenom, email, password, role="user"):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (nom, prenom, email, password, role) VALUES (?, ?, ?, ?, ?)",
            (nom, prenom, email, password, role)
        )
        conn.commit()
        return True, "Inscription réussie"
    except sqlite3.IntegrityError:
        return False, "Cet email est déjà utilisé"
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_conn()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user

def get_all_users():
    conn = get_conn()
    users = conn.execute("SELECT id, nom, prenom, email, role FROM users ORDER BY id").fetchall()
    conn.close()
    return users

def update_user_role(email, role):
    conn = get_conn()
    conn.execute("UPDATE users SET role = ? WHERE email = ?", (role, email))
    conn.commit()
    conn.close()

# ===== ANNONCES =====

def create_annonce(data):
    conn = get_conn()
    conn.execute("""
        INSERT INTO annonces
        (titre, type_bien, ville, quartier, chambres, prix, contact, description, photos, proprietaire)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["titre"], data["type_bien"], data["ville"], data.get("quartier", ""),
        data["chambres"], data["prix"], data["contact"],
        data.get("description", ""), data.get("photos", ""), data["proprietaire"]
    ))
    conn.commit()
    conn.close()

def get_annonces_validees(ville=None, type_bien=None, chambres=None, prix_max=None, quartier=None):
    conn = get_conn()
    query = "SELECT * FROM annonces WHERE statut = 'validée' AND (statut_occupation IS NULL OR statut_occupation = 'disponible')"
    params = []
    if ville:
        query += " AND LOWER(ville) LIKE ?"
        params.append(f"%{ville.lower()}%")
    if quartier:
        query += " AND LOWER(quartier) LIKE ?"
        params.append(f"%{quartier.lower()}%")
    if type_bien:
        query += " AND type_bien = ?"
        params.append(type_bien)
    if chambres:
        query += " AND chambres = ?"
        params.append(chambres)
    if prix_max:
        query += " AND prix <= ?"
        params.append(prix_max)
    query += " ORDER BY date_validation DESC"
    annonces = conn.execute(query, params).fetchall()
    conn.close()
    return annonces

def get_annonces_par_statut(statut):
    conn = get_conn()
    annonces = conn.execute(
        "SELECT * FROM annonces WHERE statut = ? ORDER BY date_creation DESC", (statut,)
    ).fetchall()
    conn.close()
    return annonces

def get_annonces_proprietaire(email):
    conn = get_conn()
    annonces = conn.execute(
        "SELECT * FROM annonces WHERE proprietaire = ? ORDER BY date_creation DESC", (email,)
    ).fetchall()
    conn.close()
    return annonces

def valider_annonce(annonce_id, admin_email):
    conn = get_conn()
    conn.execute("""
        UPDATE annonces SET statut = 'validée', valide_par = ?,
        date_validation = CURRENT_TIMESTAMP, statut_occupation = 'disponible'
        WHERE id = ?
    """, (admin_email, annonce_id))
    conn.commit()
    conn.close()

def rejeter_annonce(annonce_id, admin_email):
    conn = get_conn()
    conn.execute("""
        UPDATE annonces SET statut = 'rejetée', valide_par = ?
        WHERE id = ?
    """, (admin_email, annonce_id))
    conn.commit()
    conn.close()

def marquer_occupe(annonce_id):
    conn = get_conn()
    conn.execute("UPDATE annonces SET statut_occupation = 'occupé' WHERE id = ?", (annonce_id,))
    conn.commit()
    conn.close()

def marquer_disponible(annonce_id):
    conn = get_conn()
    conn.execute("UPDATE annonces SET statut_occupation = 'disponible' WHERE id = ?", (annonce_id,))
    conn.commit()
    conn.close()

def get_stats():
    conn = get_conn()
    stats = {
        "total":      conn.execute("SELECT COUNT(*) FROM annonces").fetchone()[0],
        "en_attente": conn.execute("SELECT COUNT(*) FROM annonces WHERE statut='en_attente'").fetchone()[0],
        "validées":   conn.execute("SELECT COUNT(*) FROM annonces WHERE statut='validée'").fetchone()[0],
        "rejetées":   conn.execute("SELECT COUNT(*) FROM annonces WHERE statut='rejetée'").fetchone()[0],
        "users":      conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "occupées":   conn.execute("SELECT COUNT(*) FROM annonces WHERE statut_occupation='occupé'").fetchone()[0],
    }
    conn.close()
    return stats

# ===== INTERETS =====

def add_interet(annonce_id, user_email, user_nom, user_prenom, telephone):
    conn = get_conn()
    try:
        conn.execute("""
            INSERT INTO interets (annonce_id, user_email, user_nom, user_prenom, telephone)
            VALUES (?, ?, ?, ?, ?)
        """, (annonce_id, user_email, user_nom, user_prenom, telephone))
        conn.commit()
        return True, "✅ Votre demande a été enregistrée ! Le service vous contactera."
    except:
        return False, "⚠️ Vous avez déjà manifesté votre intérêt pour cette annonce."
    finally:
        conn.close()

def get_interets_par_annonce(annonce_id):
    conn = get_conn()
    interets = conn.execute(
        "SELECT * FROM interets WHERE annonce_id = ? ORDER BY date_demande DESC",
        (annonce_id,)
    ).fetchall()
    conn.close()
    return interets

def get_all_interets():
    conn = get_conn()
    interets = conn.execute("""
        SELECT i.*, a.titre, a.ville, a.quartier, a.type_bien, a.chambres, a.prix
        FROM interets i
        JOIN annonces a ON i.annonce_id = a.id
        ORDER BY a.id, i.date_demande DESC
    """).fetchall()
    conn.close()
    return interets

def count_interets(annonce_id):
    conn = get_conn()
    count = conn.execute(
        "SELECT COUNT(*) FROM interets WHERE annonce_id = ?", (annonce_id,)
    ).fetchone()[0]
    conn.close()
    return count

init_db()