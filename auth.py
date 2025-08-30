from flask import Blueprint,render_template,request,session,redirect,url_for
from db import create_user_table,insert_user,check_login

auth_bp = Blueprint('auth', __name__,url_prefix='/auth')
create_user_table()

@auth_bp.route('/login',methods=['GET', 'POST'])
def login():
    err = ''
    msg =''
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = check_login(username,password)

            if not user:
                err = "Invalid username or password!"
            else:
                session['user_id'] = user[0]  
                session['username'] = user[1] 
                session['name'] = user[2] 
                msg = "Login successful"
                if not user[0] == 1:
                    return redirect(url_for('dashboard'))
                else :
                    err = "Invalid username or password!"
            
    except Exception as e:
        err = "Erroe is:", e
        
    return render_template('auth_file/login.html', err=err)

@auth_bp.route('/register',methods=['GET', 'POST'])
def register():
    try:
        err = ''
        if request.method == 'POST':
            user = {
                "name": request.form.get('name'),
                "username": request.form.get('username'),
                "email": request.form.get('email'),
                "password": request.form.get('password'),
                "confirm_password": request.form.get('confirm_password')
            }

            if user.get("password") != user.get("confirm_password"):
                err = "Passwords do not match!"
            
            else :
                user_id = insert_user(user)
                session['user_id'] = user_id
                session["username"] = user['username']
                session['name'] = user["name"]
                msg = "Login successful"
                return redirect(url_for('dashboard'))
        
    except Exception as e:
        err = "Erroe is:", e

    return render_template('auth_file/register.html', err=err)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('dashboard'))