import sqlite3
import os
from flask import session,redirect,url_for
from flask import render_template,request,Blueprint
from dotenv import load_dotenv

admin_bp = Blueprint('admin',__name__,url_prefix='/admin') 

load_dotenv()

def Admin():
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")

    db = sqlite3.connect("notesapp.db")
    c = db.cursor()
    c.execute('''insert into users (id,username,password ) values (?, ?, ?) 
    ON CONFLICT(id) DO UPDATE SET username = excluded.username,password = excluded.password''', 
    (1, username, password))
    db.commit()
    db.close()
Admin()

# ------------- Middleware ---------------
@admin_bp.before_request
def require_login():
    routes_to_avoid = ['admin.admin_login',"admin.admin_logout",'static']
    if request.endpoint not in routes_to_avoid and 'admin' not in session:
        return redirect(url_for('admin.admin_login'))


@admin_bp.route('/admin_login',methods=['GET', 'POST'])
def admin_login():
    err =''
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
    
    return render_template('admin/admin_login.html',err = err)

@admin_bp.route('/dashboard')
def dashboard():
    return render_template("admin/admin_dashboard.html")

@admin_bp.route('/users',methods=['GET','POST'])
def users():
    err = ''
    db = sqlite3.connect("notesapp.db")
    c = db.cursor()
    try:
        users_data = c.execute("select * from users").fetchall()

        id = request.form.get("user_id")
        if id:
            id = int(id)
            if id != 1:
                c.execute("delete from users where id = ?",(id,))
                db.commit()
                err = "User deletd sussefully !"
                
            else:
                err = "Admin user cannot be deleted."
    except Exception as e:
       err = f"Error: {e}"

    finally:
        db.close()

    return render_template("admin/user_data.html",data = users_data,err = err)

@admin_bp.route('/files',methods=['GET','POST'])
def files():
    err = ''
    db = sqlite3.connect("notesapp.db")
    c = db.cursor()
    try:
        files_data = c.execute("select * from files_metadata").fetchall()

        id = request.form.get("user_id")
        if id :
            c.execute("delete from files_metadata where id = ?",(id,))
            db.commit()
            err = "file deletd sussefully !"
    
    except Exception as e:
        err = f"Error: {e}"

    finally:
        db.close()
        
    return render_template("admin/user_data.html",data = files_data,err = err)

@admin_bp.route("/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin.admin_login"))