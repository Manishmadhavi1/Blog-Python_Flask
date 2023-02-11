from flask import Flask, render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import  secure_filename
from flask_mail import Mail
import json
import os

with open('config.json','r') as c:
    params = json.load(c) ["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD =params['gmail-password']
)
mail = Mail(app)
if (local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']


db =SQLAlchemy(app)
class Contacts(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12),nullable =True)


class Posts(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    slug = db.Column(db.String(21), nullable=False)
    img = db.Column(db.String(21), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)



@app.route("/")
def home():
    posts=Posts.query.filter_by().all()
    return render_template('indexx.html',params=params,posts=posts)
# app.run(debug=True)

@app.route("/post/<string:post_slug>",methods = ['GET'])
def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params,post=post)



@app.route("/about")
def about():
    return render_template('about.html',params=params)

@app.route("/dashboard",methods =["GET","POST"])
def dashboard():
    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html',params =params,posts=posts)



    if request.method == 'POST':
        username =request.form.get('uname')
        userpass =request.form.get('pass')
        if (username == params['admin_user'] and userpass == params['admin_password']):
            #set the session variable
            posts = Posts.query.all()
            session['user']  = username
            return render_template('dashboard.html',params =params,posts=posts)


    return render_template('login.html',params=params)


@app.route("/edit/<string:srno>",methods = ['GET','POST'])
def edit(srno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            box_title =request.form.get('title')
            tline =request.form.get('tline')
            slug =request.form.get('slug')
            content =request.form.get('content')
            img =request.form.get('img')
            date =datetime.now()

            if srno=='0':
                post = Posts(title = box_title,slug =slug,content = content,img=img,tagline=tline,date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(srno=srno).first()
                post.title = box_title
                post.slug = slug
                post.content = content
                post.img = img
                post.tagline = tline
                post.date = date
                db.session.commit()
            return redirect('/edit/' + srno)

        post = Posts.query.filter_by(srno=srno).first()
        return render_template('edit.html',params=params,post =post)


@app.route("/uploader",methods = ['GET','POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
       if (request.method == 'POST'):
        f=request.files['file1']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename (f.filename)))
        return "uploaded successfully"


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delete/<string:srno>",methods = ['GET','POST'])
def delete(srno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Posts.query.filter_by(srno=srno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')



@app.route("/contact",methods = ['GET','POST'])


def contact():
    if (request.method == 'POST'):

        #add entries to the database
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contacts(name=name,email=email,phone=phone,message=message,date = datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from' + name,
                          sender=email,
                          recipients=[params['gmail-user']],
                          body=message + "\n" + phone)

    return render_template('contact.html',params=params)

# @app.route("/flask6")
# def flask6():
#     return render_template('flask6.html')


app.run(debug=True)