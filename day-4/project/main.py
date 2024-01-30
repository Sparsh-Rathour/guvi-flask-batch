from flask import Flask,redirect,render_template,request,url_for,flash,jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
from flask.globals import session
from flask import flash
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,login_manager,UserMixin,LoginManager,login_required,logout_user
from flask_login import current_user
from flask_mail import Mail
from werkzeug.utils import secure_filename
import os
from datetime import datetime 

local_server= True
app=Flask(__name__)
app.secret_key="^%$^$^^*&&FGGY9178"


login_manager=LoginManager(app)
login_manager.login_view='login'



with open('config.json','r') as c:
    params=json.load(c)["params"]

#
#  mail configuraton


app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)


# configuration for storing the images
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS']= ['png','jgp','jpeg','gif']
app.config['MAX_CONTENT_LENGTH']=16*1024*1024




# database configuration
# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databasename'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/capstoneproject'
db=SQLAlchemy(app)



@login_manager.user_loader
def load_user(user_id):
    return Signup.query.get(user_id)


# configuration of database tables
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(15))


class Signup(UserMixin,db.Model):
    user_id=db.Column(db.Integer,primary_key=True)
    first_name=db.Column(db.String(50))
    last_name=db.Column(db.String(50))
    email=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(1000))
    phone=db.Column(db.String(12),unique=True)
    
    def get_id(self):
        return self.user_id


class Blog(db.Model):
    bid=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50))
    description=db.Column(db.String(50))
    author=db.Column(db.String(100))
    date=db.Column(db.String(100))
    image=db.Column(db.String(1000))
    
    



@app.route("/test/")
def test():
    try:
        # query=Test.query.all()
        # print(query)
        sql_query="Select * from test"
        with db.engine.begin() as conn:
            response=conn.exec_driver_sql(sql_query).all()
            print(response)
        return f"Database is connected"

    except Exception as e:
        return f"Database is not connected {e} "


@app.route("/")
def home():
    try:
        return render_template("index.html")
    except Exception as e:
        return f"Database is not connected {e} "
    


@app.route("/signup",methods=['GET','POST'])
def signup():
    try:
        if request.method=="POST":
            firstName=request.form.get("fname")
            lastName=request.form.get("lname")
            email=request.form.get("email")
            phone=request.form.get("phone")
            pass1=request.form.get("pass1")
            pass2=request.form.get("pass2")

            if pass1!=pass2:
                flash("Password is not matching","warning")
                return redirect(url_for("signup"))
            
            fetchemail=Signup.query.filter_by(email=email).first()
            fetchphone=Signup.query.filter_by(phone=phone).first()

            if fetchemail or fetchphone:
                flash("User Already Exists","info")
                return redirect(url_for("signup"))

            if len(phone)!=10:
                flash("Please Enter 10 digit number","primary")
                return redirect(url_for("signup"))
            
            gen_pass=generate_password_hash(pass1)
            query=f"INSERT into `signup` (`first_name`,`last_name`,`email`,`password`,`phone`) VALUES ('{firstName}','{lastName}','{email}','{gen_pass}','{phone}')"

            with db.engine.begin() as conn:
                conn.exec_driver_sql(query)               
               # my mail starts from here if you not need to send mail comment the below line           
                # mail.send_message('Signup Success',sender=params["gmail-user"],recipients=[email],body="Welcome to my website" )
                flash("Signup is Successs Please Login","success")
                return redirect(url_for("login"))

        return render_template("signup.html")
    except Exception as e:
        return f"Database is not connected {e} "
    


@app.route("/login",methods=['GET','POST'])
def login():
    try:
        if request.method=="POST":
            email=request.form.get('email')
            password=request.form.get('pass1')
            user=Signup.query.filter_by(email=email).first()
            if user and check_password_hash(user.password,password):
                login_user(user)
                flash("Login Success","success")
                return redirect(url_for("home"))
            else:
                flash("Invalid Credentials","warning")
                return redirect(url_for("login"))


        return render_template("login.html")
    except Exception as e:
        return f"Database is not connected {e} "
    


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Success","primary")
    return redirect(url_for("login"))



def allowed_files(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in app.config['ALLOWED_EXTENSIONS']



@app.route("/posts",methods=['GET','POST'])
def posts():
    if not current_user.is_authenticated:
        flash("Please Login and try again","info")
        return redirect(url_for('login'))
    
    if request.method=="POST":
        title=request.form.get('title')
        des=request.form.get('desc')
        authname=request.form.get('authorname')
        image=request.files['image']
        date=datetime.now()
        getdate=date.date()
        gettime=date.time()
        if image and allowed_files(image.filename):
            filename=secure_filename(image.filename)
            print(filename)

            basedir = os.path.abspath(os.path.dirname(__file__))
            image.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

            query=Blog(title=title,description=des,author=authname,date=getdate,image=image.filename)
            db.session.add(query)
            db.session.commit()
            flash("Post is Uploaded","success")
            return redirect(url_for("home"))
        else:
            flash("Upload the images which has .jpg,.png, .jpeg or .gif file formats","danger")
            return render_template("blogpost.html")


    return render_template("blogpost.html")


app.run(debug=True)