import os
import sqlite3
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ------------------ RAG Search (SQLite) ------------------
def search_notes(query):
    try:
        conn = sqlite3.connect("notesapp.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT title, description, subject, filename 
            FROM files_metadata
            WHERE title LIKE ? 
               OR description LIKE ? 
               OR subject LIKE ?
               OR filename LIKE ?
            LIMIT 5
        """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))

        results = cur.fetchall()
        conn.close()

        if not results:
            return "No matching study materials found."

        out = ""
        for title, desc, subject, filename in results:
            out += (
                f"\nTitle: {title}\n"
                f"Subject: {subject}\n"
                f"Description: {desc}\n"
                f"File: {filename}\n"
                "--------------------------------------\n"
            )

        return out.strip()

    except Exception as e:
        return f"RAG Error: {str(e)}"


# ------------------ List All Files ------------------
def get_all_files():
    try:
        conn = sqlite3.connect("notesapp.db")
        cur = conn.cursor()

        cur.execute("""
            SELECT title, subject, filename 
            FROM files_metadata
            ORDER BY id DESC
        """)

        rows = cur.fetchall()
        conn.close()

        if not rows:
            return "No files uploaded yet."

        out = "Uploaded Files:\n"
        for title, subject, filename in rows:
            out += f"\n{title}\nSubject: {subject}\nFile: {filename}\n"

        return out.strip()

    except Exception as e:
        return f"DB Error: {e}"


# ------------------ Load Master Knowledge File ------------------
def load_ai_text():
    """
    Loads notesapp_ai_data.txt (merged README + wiki + app instructions).
    """
    try:
        if os.path.exists("notesapp_ai_data.txt"):
            with open("notesapp_ai_data.txt", "r", encoding="utf-8") as f:
                return f.read()
        else:
            return "notesapp_ai_data.txt not found."
    except Exception as e:
        return f"AI Knowledge Load Error: {e}"


# ------------------ Main AI Function ------------------
def generate_ai_reply(user_msg):

    msg = user_msg.lower()

    # 1. Ask about full file list
    if any(k in msg for k in [
        "list all files", "list files", "show files",
        "show all files", "uploaded files", "uploads", "my files"
    ]):
        return get_all_files()

    # 2. Database RAG (search metadata)
    db_rag = search_notes(msg)

    # 3. Load main text knowledge file
    main_rag = load_ai_text()

    # 4. Merge RAG
    combined_rag = f"{db_rag}\n\n{main_rag}"

    # 5. System rules
    system_prompt = """
    You are the AI assistant inside NotesApp.
    Use ONLY the provided RAG data and knowledge file.
    Allowed topics:
      - NotesApp usage
      - Uploading files
      - Notes, textbooks, QPs
      - Year/branch/semester
      - Metadata
      - Simple conversation (hi, hello, ok)
    Not allowed:
      - Politics, celebrities, news, sports, movies, hacking.
    Be short, helpful, and accurate.
    """

    # 6. Groq model call
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": f"RAG:\n{combined_rag}"},
            {"role": "user", "content": user_msg},
        ]
    )

    return response.choices[0].message.content
