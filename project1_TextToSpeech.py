# Import the required module for text to speech conversion
# This module is imported so that we can play the converted audio

from flask import Flask, render_template, request, redirect, jsonify, make_response, flash
from gtts import gTTS
from pygame import mixer
from flask_sqlalchemy import SQLAlchemy
import os
import pyttsx3
import json
from datetime import datetime

converter = pyttsx3.init()
converter.setProperty('rate', 150)

local_server=True
with open("config.json", "r")as c:
    params=json.load(c)["params"]

app = Flask(__name__ , template_folder='template')

if local_server:
        app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["production_uri"]
db = SQLAlchemy(app)

#database name:contact
#database column:id,name,email,phone,message,date
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(120), nullable=True)

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    subtitle = db.Column(db.String(120), nullable=False)

word="No Text-to-speek"
@app.route("/")
def root():
    return render_template('index.html')

count=0
def increment():
    global count
    count +=1
    return count

def get_filename():
    global c
    c=increment()
    filename = 'sample' + str(c) + '.mp3'
    return filename

def del_file():
    global c
    if c>1:
        file_no_del=c-1
        file_name_to_del= 'sample' + str(file_no_del) + '.mp3'
        os.remove(file_name_to_del)

mixer.init()

@app.route("/upload_data", methods=['GET','POST'])
def upload_data():
    if request.method==('POST'):
        heading=request.form.get("title")
        subheading=request.form.get("subtitle")
        if heading and subheading:
            entry=Content(title=heading, subtitle =subheading)
            db.session.add(entry)
            db.session.commit()

    return render_template('index.html')


@app.route("/get_word", methods=['GET','POST'])
def get_word():
    word = request.form.get("word")
    if word!='':  
        s=word.split(" ")
        dict1={}
        i=0
        for item in s:
            dict1[i]=item
            i+=1     
        audio = gTTS(text=word, lang='en-uk', slow=False)
        file=get_filename() 
        audio.save(file)
        mixer.music.load(file)
        mixer.music.play()
        del_file()
        return render_template('showSpan.html',dictnory=dict1)  
    return render_template('showSpan.html',dictnory=dict1)  
    #     return jsonify({'success':'True'},{'string':word})        
    # return jsonify({'error':'missing data'})  

pause = False
@app.route("/pause", methods=['GET', 'POST'])
def pause():
    global pause
    pause=True
    mixer.music.pause()
    return jsonify({'success':'paused'})

@app.route("/unpause", methods=['GET', 'POST'])
def unpause():
    if pause:
        mixer.music.unpause() 
        return jsonify({'success':'unpaused'})

reset =False
@app.route("/reset", methods=['GET', 'POST'])
def reset():
    global reset
    reset=True
    mixer.music.stop()
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

#database column:id,name,email,phone,message,date#database
@app.route("/contact",methods=['GET', 'POST'])
def contact():
    if request.method==('POST'):
        uname = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        if uname and email and phone and message:
            entry = Contact(name=uname, email=email, phone=phone, message=message, date=datetime.now())
            db.session.add(entry)
            db.session.commit()  
        return render_template('contact.html',params=params)  
    return render_template('contact.html',params=params)        
   
@app.route("/get_title",methods=['GET','POST'])
def get_title():
    if request.method==('POST'):
        data = Content.query.all()
        return render_template('get_title.html',data=data)

@app.route("/get_content<string:id>",methods=['GET','POST'])
def content(id):
    content=Content.query.filter_by(id=id).first()
    if (request.method == 'POST'):
        global word
        word = request.form.get("word") 
        s=word.split(" ")
        dict1={}
        i=0
        for item in s:
            dict1[i]=item
            i+=1   
        audio = gTTS(text=word, lang='en-uk', slow=False)
        file=get_filename() 
        audio.save(file)
        mixer.music.load(file)
        mixer.music.play() 
        del_file()
        return render_template('showSpan.html',dictnory=dict1)
    return render_template('get_content.html',content=content,id='id')
app.run(use_reloader = True,debug=True)