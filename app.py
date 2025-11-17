from flask import Flask,render_template,session,request,redirect,url_for,Response,jsonify
from db import insert_file_metadata,create_files_table,insert_file_metadata,get_all_files_metadata,get_user_profile
from mysql_db import upload_file,get_file_from_db
from ai_chatbot import generate_ai_reply
from auth import auth_bp
from admin import admin_bp
import base64

# -----------------------------------------------------

app = Flask(__name__)
app.secret_key = "qw3ia76ew78ystdnicfnsemo89qw3u095r39827wo8y&^$&ruTIYWO7839YNE4987"

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

create_files_table()

# ------------- Middleware ---------------
@app.before_request
def require_login():
    if request.blueprint == 'admin':  
        return 
    # routes_to_avoid = ['dashboard','auth.login','auth.register',"auth.admin_login","admin.users","admin.files"]
    routes_to_avoid = ['dashboard','auth.login','auth.register','auth.logout','admin.admin_login','static']

    if request.endpoint not in routes_to_avoid and 'user_id' not in session:
        return redirect(url_for('auth.login'))

@app.route('/',methods=['GET', 'POST'])
def dashboard():
    return render_template("dashboard.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    err = ''
    msg = session.pop('msg', '')

    if request.method == "POST":
        uploaded_to_uploade = request.files.get("file")

        if uploaded_to_uploade:
            try:
                res = upload_file(uploaded_to_uploade)

                # Save metadata in Sqlite
                file_data = {
                    "title": request.form.get("title"),
                    "description": request.form.get("description",""),
                    "category": request.form.get("category"),
                    "year": request.form.get("year", 0),
                    "branch": request.form.get("branch"),
                    "sem": request.form.get("sem"),
                    "subject": request.form.get("subject"),
                    "uploaded_by": session.get("username"),
                    "filename": res.get('filename'),
                    "file_id": res.get('id')
                }

                insert_file_metadata(file_data)
                session['msg'] = f"File uploaded! {res.get('filename')}"
                return redirect(url_for("upload"))
            
            except Exception as e:
                err = f"Upload failed: {str(e)}"
        else:
            err = "No file selected!"

    return render_template("upload.html", msg=msg, err=err)


@app.route('/textbooks',methods=['GET', 'POST'])
def textbooks():
    err = ''
    try:
        all_notes = get_all_files_metadata("textbook") 
        if not all_notes:
            err = "No Textbook's Are Available"
    except Exception as e:
        err = str(e)
        print(str(e))
    return render_template("pages.html",notes=all_notes,err=err,title = "TextBook's")

@app.route('/notes',methods=['GET', 'POST'])
def notes():
    err = ''
    try:
        all_notes = get_all_files_metadata("notes") 
        if not all_notes:
            err = "No Note's Are Available"
            
    except Exception as e:
        err = str(e)
        print(str(e))

    return render_template("pages.html",notes=all_notes,err=err,title = "Note's")

@app.route('/qp',methods=['GET', 'POST'])
def qp():
    err = ''
    try:
        all_notes = get_all_files_metadata("previous_qp") 
        if not all_notes:
            err = "No Qustion Paper's Are Available"

    except Exception as e:
        err = str(e)
        print(str(e))

    return render_template("pages.html",notes=all_notes,err=err,title = "Qustions_Paper's")

@app.route("/preview/<int:file_id>")
def preview(file_id):
    try:
        row = get_file_from_db(file_id)

        if not row:
            return render_template("preview.html", error="File not found")
        
        filename = row[0].lower()
        filedata = row[1]

        # check file type
        if filename.endswith(".pdf"):
            is_supported = True
            filetype = "application/pdf"
        elif filename.endswith((".png", ".jpg", ".jpeg", ".gif")):
            is_supported = True
            filetype = "image/jpeg"
        elif filename.endswith(".txt"):
            is_supported = True
            filetype = "text/plain"
            filedata = filedata.decode("utf-8")
        else:
            is_supported = False
            filetype = None
            err = "Preview not supported for this file type."

        if is_supported and filetype != "text/plain":
            filedata = base64.b64encode(filedata).decode('utf-8')

        return render_template(
            "preview.html",
            filename=row[0],
            preview_supported=is_supported,
            filetype=filetype,
            filedata=filedata,
            error=err if not is_supported else None
        )
    except Exception:
        return render_template("preview.html", error="Can't connect to MySQL server")


@app.route("/download/<int:file_id>")
def download_file_route(file_id):
    try:
        row = get_file_from_db(file_id)
        filename, filedata = row
        return Response(
            filedata,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
            mimetype="application/octet-stream"
        )
    except Exception as e:
        print(str(e))

@app.route("/profile")
def profile():
    try:
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        
        user, notes_count = get_user_profile(session["user_id"])

        if not user:
            return "User not found"
    
    except Exception as e:
        print(str(e))

    return render_template("profile.html", user=user, notes_count=notes_count)

@app.route("/ai_chat", methods=["POST"])
def ai_chat():
    try:
        data = request.json
        user_msg = data.get("message", "")

        reply = generate_ai_reply(user_msg)

        return jsonify({"reply": reply})

    except Exception as e:
        print("AI ERROR:", e)
        return jsonify({"reply": "Something went wrong with AI."})


if __name__ == "__main__":
    try:
        app.run(port=5000,debug=True)
        # app.run(port=5000)
        
    except Exception as e:
        print(str(e))