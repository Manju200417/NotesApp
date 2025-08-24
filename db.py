import sqlite3

# For Users

def create_user_table():
    conn = sqlite3.connect("notesapp.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            username TEXT NOT NULL UNIQUE,
            email TEXT,
            password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def insert_user(user):
    conn = sqlite3.connect("notesapp.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (name, username, email, password) VALUES (?, ?, ?, ?)
    ''', (user['name'], user['username'], user['email'], user['password']))
    
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    return user_id


def check_login(username, password):
    conn = sqlite3.connect("notesapp.db")
    c = conn.cursor()
    c.execute('SELECT id, username, name FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()
    return user

# ---------------------------------------------------For File Meta-Data--------------------------------------------------------------------

# Table For Files Metadata

def create_files_table():
    conn = sqlite3.connect("notesapp.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS files_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            year INTEGER NOT NULL,
            branch TEXT NOT NULL,
            sem INTEGER NOT NULL,
            subject TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_id TEXT,
            uploaded_by TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# insert into files_metadata

def insert_file_metadata(file_data):
    conn = sqlite3.connect("notesapp.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO files_metadata 
        (title, description, category, year, branch, sem, subject, filename, file_id, uploaded_by) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        file_data["title"],
        file_data.get("description", ""),
        file_data["category"],
        file_data["year"],
        file_data["branch"],
        file_data["sem"],
        file_data["subject"],
        file_data["filename"], 
        file_data["file_id"], 
        file_data["uploaded_by"]
    ))
    conn.commit()
    conn.close()



def get_all_files_metadata(category):
    conn = sqlite3.connect("notesapp.db")
    c = conn.cursor()
    c.execute("""
        SELECT title, subject, uploaded_by, description, file_id 
        FROM files_metadata
        WHERE category = ?
        ORDER BY uploaded_at DESC
    """,(category,))
    rows = c.fetchall()
    conn.close()
    return rows
# ------------------------------------------user_profile--------------------------------------------------------------------------------------------------

def get_user_profile(user_id):
    conn = sqlite3.connect("notesapp.db")
    c = conn.cursor()
    
    c.execute("SELECT id, name,username, email, created_at FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()

    username = user[2]

    c.execute("SELECT COUNT(*) from files_metadata where uploaded_by = ?", (username,))
    notes_count = c.fetchone()[0]

    conn.close()

    return user, notes_count