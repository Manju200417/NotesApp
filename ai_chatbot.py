import os
import sqlite3
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

try:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
except Exception:
    client = None

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ai_chat', methods=['POST'])
def ai_chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"reply": "Please type a message! 😊"})
        
        reply = generate_ai_reply(user_message)
        return jsonify({"reply": reply})
    
    except Exception:
        return jsonify({"reply": "Sorry, something went wrong!"})


def load_project_knowledge():
    try:
        if os.path.exists("notesapp_ai_data.txt"):
            with open("notesapp_ai_data.txt", "r", encoding="utf-8") as f:
                return f.read()
        else:
            return ""
    except Exception:
        return ""

PROJECT_KNOWLEDGE = load_project_knowledge()

def search_notes(query):
    try:
        conn = sqlite3.connect("notesapp.db")
        cur = conn.cursor()
        
        search_term = f"%{query}%"
        cur.execute("""
            SELECT title, description, subject, filename 
            FROM files_metadata
            WHERE title LIKE ? 
               OR description LIKE ? 
               OR subject LIKE ?
               OR filename LIKE ?
            LIMIT 10
        """, (search_term, search_term, search_term, search_term))
        
        results = cur.fetchall()
        conn.close()
        return results

    except Exception:
        return []


def get_all_files():
    try:
        conn = sqlite3.connect("notesapp.db")
        cur = conn.cursor()
        cur.execute("""
            SELECT title, subject, filename 
            FROM files_metadata 
            ORDER BY id DESC 
            LIMIT 20
        """)
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return "📭 No files uploaded yet. Be the first to upload!"

        out = "📚 **All Uploaded Files:**\n\n"
        for i, (title, subject, filename) in enumerate(rows, 1):
            out += f"**{i}. {title}**\n   📖 Subject: {subject}\n   📁 `{filename}`\n\n"
        return out.strip()

    except Exception:
        return "❌ Unable to fetch files."


def get_all_subjects():
    try:
        conn = sqlite3.connect("notesapp.db")
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT subject FROM files_metadata")
        subjects = [row[0] for row in cur.fetchall()]
        conn.close()
        return subjects
    except:
        return []


def get_file_count():
    try:
        conn = sqlite3.connect("notesapp.db")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM files_metadata")
        count = cur.fetchone()[0]
        conn.close()
        return count
    except:
        return 0


def format_search_results(results):
    if not results:
        return None
    
    out = "📚 **Found these files:**\n\n"
    for i, (title, desc, subject, filename) in enumerate(results, 1):
        desc_short = desc[:80] + "..." if len(desc) > 80 else desc
        out += f"**{i}. {title}**\n"
        out += f"   📖 Subject: {subject}\n"
        out += f"   📝 {desc_short}\n"
        out += f"   📁 `{filename}`\n\n"
    
    return out.strip()


def is_project_question(msg):
    project_keywords = [
        "what is notesapp", "about notesapp", "about this app", "what is this",
        "how does this work", "how it works", "how this works",
        "features", "what can i do", "functionality", "capabilities",
        "who made", "who created", "who built", "developer", "built by",
        "technology", "tech stack", "made with", "built with",
        "how to use", "how do i use", "using this app", "guide",
        "what categories", "types of files", "file types", "what types",
        "how to login", "how to register", "signup", "sign up", "create account",
        "why notesapp", "purpose", "goal", "what for", "benefits"
    ]
    
    return any(keyword in msg for keyword in project_keywords)

def is_file_search(msg):
    search_keywords = [
        "find", "search", "get", "show", "have", "any",
        "is there", "do you have", "looking for", "need",
        "notes on", "notes for", "notes about",
        "book on", "book for", "book about",
        "paper on", "paper for", "question paper",
        "material", "pdf", "download"
    ]
    
    return any(keyword in msg for keyword in search_keywords)


def generate_ai_reply(user_msg):
    msg = user_msg.lower().strip()
        
    if msg in ["hi", "hello", "hey", "hii", "hola", "namaste"]:
        file_count = get_file_count()
        return f"Hello! 👋 Welcome to NotesApp!\n\n📊 We have **{file_count} files** uploaded.\n\nHow can I help you?\n- 🔍 Search for notes\n- 📚 Show all files\n- ❓ Ask about the app"

    if any(t in msg for t in ["thanks", "thank you", "thx", "ty"]):
        return "You're welcome! 😊 Happy studying!"

    if any(b in msg for b in ["bye", "goodbye", "see you", "exit"]):
        return "Goodbye! 👋 Come back anytime!"

    if msg in ["ok", "okay", "k", "fine", "alright"]:
        return "👍 Let me know if you need anything else!"
    
    file_keywords = ["show files", "list files", "all files", "show all", 
                     "uploaded files", "available files", "what files"]
    if any(k in msg for k in file_keywords):
        return get_all_files()
    
    count_keywords = ["how many files", "total files", "file count", "number of files"]
    if any(k in msg for k in count_keywords):
        count = get_file_count()
        return f"📊 There are **{count} files** currently uploaded in NotesApp!"
    
    subject_keywords = ["what subjects", "which subjects", "available subjects", "list subjects"]
    if any(k in msg for k in subject_keywords):
        subjects = get_all_subjects()
        if subjects:
            subject_list = "\n".join([f"   • {s}" for s in subjects])
            return f"📖 **Available Subjects:**\n\n{subject_list}"
        else:
            return "📭 No subjects found yet. Upload some files to get started!"
    
    if msg in ["help", "?", "commands"]:
        return """🤖 **NotesApp AI Assistant**

**I can help with:**

 **Search Files:** "Find physics notes"
 **Browse:** "Show all files"
 **Subjects:** "What subjects available?"
 **Stats:** "How many files?"
 **Upload:** "How to upload?"
 **About App:** "What is NotesApp?"
 **Just ask anything!** 😊"""
    
    upload_keywords = ["how to upload", "upload file", "upload steps", 
                       "how can i upload", "uploading", "add file"]
    if any(k in msg for k in upload_keywords):
        return """📤 **How to Upload Files:**

 Click **"Upload"** in the navigation bar
 Fill in the details:
  • Title of your file
  • Subject name
  • Description
 Select your file (PDF, DOC, etc.)
 Choose category (Notes/Textbook/Question Paper)
 Click **"Upload"** button

 Done! Your file will help other students! 🎉"""

    if is_project_question(msg):
        return ask_ai_with_project_knowledge(user_msg)

    remove_words = ["find", "search", "get", "show", "have", "any", "is", 
                    "there", "do", "you", "the", "a", "an", "for", "on",
                    "in", "this", "notesapp", "app", "please", "can", 
                    "i", "me", "looking", "need", "where", "are", "notes"]
    
    search_terms = msg
    for word in remove_words:
        search_terms = search_terms.replace(word, " ")
    search_terms = " ".join(search_terms.split()).strip()
    
    if search_terms:
        results = search_notes(search_terms)
        
        if results:
            formatted = format_search_results(results)
            return formatted + "\n\n💡 *Click on the file to view or download!*"
        elif is_file_search(msg):
            subjects = get_all_subjects()
            if subjects:
                subject_list = ", ".join(subjects[:5])
                return f"❌ **No files found for '{search_terms}'**\n\n📖 Available subjects: {subject_list}\n\n💡 Try searching for these, or upload your own!"
            else:
                return f"❌ **No files found for '{search_terms}'**\n\n📭 Database is empty. Be the first to upload!"
    
    results = search_notes(user_msg)
    if results:
        formatted = format_search_results(results)
        return formatted + "\n\n💡 *Click on the file to view or download!*"

    return ask_ai_with_full_context(user_msg)


def ask_ai_with_project_knowledge(user_msg):
    if client is None:
        return "🤖 I can help you learn about NotesApp!\n\n📤 Upload & share notes\n📚 Browse textbooks\n📄 Find question papers"

    try:
        system_prompt = f"""You are the AI assistant for NotesApp.

USE THIS PROJECT INFORMATION TO ANSWER:
---
{PROJECT_KNOWLEDGE}
---

RULES:
1. Answer based ONLY on the project information above
2. Be friendly and use emojis
3. Keep responses concise and helpful
4. If information is not in the project data, say "I don't have that information"
5. Focus on helping users understand and use the app

DO NOT make up features or information not in the project data."""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=400,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    except Exception:
        return "ℹ️ **About NotesApp:**\n\nNotesApp helps students share and access study materials like notes, textbooks, and question papers.\n\n📤 Upload your files\n📚 Browse materials\n🔍 Search by subject"


def ask_ai_with_full_context(user_msg):
    if client is None:
        return "🔍 Try:\n- 'Show all files'\n- 'Find [subject] notes'\n- 'What is NotesApp?'"

    try:
        file_count = get_file_count()
        subjects = get_all_subjects()
        subject_list = ", ".join(subjects) if subjects else "No subjects yet"
        
        system_prompt = f"""You are the AI assistant for NotesApp - a student study materials platform.

PROJECT INFORMATION:
---
{PROJECT_KNOWLEDGE}
---

CURRENT DATABASE STATUS:
- Total files uploaded: {file_count}
- Available subjects: {subject_list}

STRICT RULES:

1. FOR FILE/NOTES QUESTIONS:
   - Only mention subjects that are in the "Available subjects" list
   - If user asks about a subject NOT in the list, say "No [subject] files found"
   - NEVER invent or make up files

2. FOR APP/PROJECT QUESTIONS:
   - Use the PROJECT INFORMATION above
   - If not mentioned in project info, say "I don't have that information"

3. GENERAL:
   - Be friendly, use emojis
   - Keep responses short and helpful
   - Guide users to upload if their topic is not found

RESPONSE EXAMPLES:

User: "Do you have CMA notes?"
(If CMA not in subjects list)
Response: "❌ No CMA files found currently.\n\n📖 Available: {subject_list}\n\n💡 You can upload CMA notes to help others!"

User: "What is NotesApp?"
Response: [Answer from PROJECT INFORMATION]"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=300,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    except Exception:
        return "🔍 How can I help?\n\n- 'Show all files'\n- 'Find [subject] notes'\n- 'What is NotesApp?'"
