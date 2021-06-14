
from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import re
import os
from flask import  flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask import Flask
import ansible_runner

print("Inside market.py")

cdir=os.getcwd()
print ("The current working directory is %s" % cdir)
wdir="storage"


UPLOAD_FOLDER = os.path.join(cdir,wdir)
print ("The upload directory is %s" % UPLOAD_FOLDER)

# UPLOAD_FOLDER = '/Users/ar-gattem.mahesh/FlaskMarket/storage'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif '}

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your secret key'

db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  database="flaskmarket"
)

def allowed_file(filename):
    print("Inside allowed_file()")
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)

@app.route('/home', methods=['GET', 'POST'])
def upload_file():
    print("Inside /home->upload_file()")
    print ("The request is %s" % request)
    if not session and not 'username' in session:
        print ("The session is %s" % session)
        return redirect(url_for('login_page'))
      
    if request.method == 'POST':
        
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
          
        file = request.files['file']
        print ("The file is %s" % file.filename)
        
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print ("The filename is %s" % filename)
            
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            inventory_path = os.path.join(cdir, "copybot", "myInventory")
            print ("The inventory_path is %s" % inventory_path)
            
            playbook_path = os.path.join(cdir, "copybot", "copy.yml")
            print ("The playbook_path is %s" % playbook_path)

            # ansible-playbook -i myInventory copy.yml -Kk
            # -e src_base_path=/home/mahesh/copybot
            # -e file_name=myInventory -vvv
            extravars = {
                'src_base_path': UPLOAD_FOLDER,
                'file_name': filename
            }
            print ("The extravars is %s" % extravars)

            r = ansible_runner.run(
                inventory=inventory_path,
                extravars=extravars,
                playbook=playbook_path
            )
            print ("The r is %s" % r)
            print("file upload done")
            
            #return redirect(url_for('download_file', name=filename))
    return render_template('home.html')

@app.route('/')
def home():
    print("Inside /->home()")
    if session and 'username' in session:
        print ("The session is %s" % session)
        return redirect(url_for('home_page'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    print("Inside /login->login_page()")
    print ("The request is %s" % request)
    msg = ''
    if session and 'username' in session:
        print ("The session is %s" % session)
        return render_template('home.html')
      
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = db.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            msg = 'Logged in successfully !'
            print("login success")
            # return render_template('home.html', msg=msg)
            return redirect(url_for('home_page'))
        else:
            msg = 'Incorrect username / password !'
            print('Incorrect username / password !')
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout_page():
    print("Inside /logout->logout_page()")
    if not session and not 'username' in session:
      print ("The session is %s" % session)
      return redirect(url_for('login_page'))
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    print("logout success")
    return redirect(url_for('login_page'))

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    print("Inside register_page()")
    print ("The request is %s" % request)
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = db.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            db.commit()
            msg = 'You have successfully registered !'
            print("register success")
    elif request.method == 'POST':
        msg = 'Please fill out the form !'

        print("register failed- empty form")
    else:
        msg = 'Something went wrong !'
        print("register failed-error")
    return render_template('register.html', msg=msg)

@app.route('/home')
def home_page():
    print("Inside home_page()")
    if not session and not 'username' in session:
        print ("The session is %s" % session)
        return redirect(url_for('login_page'))
    return render_template('home.html')

@app.route('/upload' , methods = ['POST','GET'])
def upload():
    print("Inside upload()")
    file = request.files['fileToUpload']
    return file.filename

@app.route('/market')
def market_page():
    print("Inside market_page()")
    items = [
        {'id': 1, 'plan': 'silver', 'storage': '10', 'price': 10},
        {'id': 2, 'plan': 'Gold', 'storage': '100', 'price': 90},
        {'id': 3, 'plan': 'Diamond', 'storage': '1000', 'price': 500}
    ]
    return render_template('market.html', items=items)

@app.route('/forget')
def forgot_page():
    return render_template('forgot.html')
  
@app.route('/about')
def about_page():
    return render_template('about.html')

if __name__== '__main__':
    app.run(debug=True,host="0.0.0.0",port=3000)
