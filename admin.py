from flask import session,redirect,url_for,render_template,request,Blueprint
from dotenv import load_dotenv
import sqlite3
import os

admin_bp = Blueprint('admin',__name__,url_prefix='/admin') 

load_dotenv()

def Admin():
    try:
        username = os.getenv("ADMIN_USERNAME")
        password = os.getenv("ADMIN_PASSWORD")

        db = sqlite3.connect("notesapp.db")
        c = db.cursor()
        c.execute('''insert into users (id,username,password,is_admin ) values (?, ?, ?, ?) 
        ON CONFLICT(id) DO UPDATE SET username = excluded.username,password = excluded.password''', 
        (1, username, password,True))
    except Exception as e:
        print(str(e))
    finally:
        db.commit()
        db.close()
Admin()

# ------------- Middleware ---------------
@admin_bp.before_request
def require_login():
    routes_to_avoid = ['admin.admin_login',"admin.admin_logout",'static']
    if request.endpoint not in routes_to_avoid and 'admin' not in session:
        return redirect(url_for('admin.admin_login'))

# ----------------------------admin-Login----------------------------------------------------------

@admin_bp.route('/admin_login',methods=['GET', 'POST'])
def admin_login():
    err =''
    try:
        if request.method == "POST":
            username = request.form.get('username')
            password = request.form.get('password')

            with sqlite3.connect("notesapp.db") as db:
                c = db.cursor()
                res = c.execute("select * from users where id = ? and username = ? and password =?",(1,username,password)).fetchone()

            if res:  
                session['admin'] = True 
                return redirect(url_for("admin.dashboard"))
            else:
                err = "Invalid username or password!"
    except Exception as e:
        err = str(e)
        print(str(e))
        
    return render_template('admin/admin_login.html',err = err)

@admin_bp.route('/dashboard')
def dashboard():
    return render_template("admin/admin_dashboard.html")

# ----------------------------Users----------------------------------------------------------

@admin_bp.route('/users',methods=['GET','POST'])
def users():
    err = ''
    total = 0
    db = sqlite3.connect("notesapp.db")
    c = db.cursor()
    try:
        users_data = c.execute("select * from users").fetchall()
        total = len(users_data)

        id = request.form.get("user_id")
        if id:
            id = int(id)
            if id != 1:
                c.execute("delete from users where id = ?",(id,))
                db.commit()
                err = "User deletd sussefully !"
                return redirect(url_for('admin.users'))
                
            else:
                err = "Admin user cannot be deleted."
    except Exception as e:
       err = f"Error: {e}"

    finally:
        db.close()

    return render_template("admin/user_data.html",data = users_data,err = err, total = total)
# ----------------------------files----------------------------------------------------------

@admin_bp.route('/files',methods=['GET','POST'])
def files():
    err = ''
    total = 0
    db = sqlite3.connect("notesapp.db")
    c = db.cursor()
    try:
        files_data = c.execute("select * from files_metadata").fetchall()
        total = len(files_data)

        id = request.form.get("user_id")
        if id :
            c.execute("delete from files_metadata where id = ?",(id,))
            db.commit()
            err = "file deletd sussefully !"
            return redirect(url_for('admin.files'))
    
    except Exception as e:
        err = f"Error: {e}"

    finally:
        db.close()
        
    return render_template("admin/all_files.html",data = files_data,err = err ,total = total)

# ----------------------------admin-logout----------------------------------------------------------

@admin_bp.route("/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin.admin_login"))
