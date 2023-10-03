"""
LetMeet Application - (Terralogic Hackathon)
Team:-
Shaik Sameer
Shaik Ehtesham
Yenduluru Prasanth
Shaik Rakheeb Ahmed
"""
from flask import *
import json
import os
from flask_mail import Mail, Message
import pymongo
import certifi
from werkzeug.utils import secure_filename
from bson import json_util
import datetime
from pytz import timezone
import pandas as pd
import xlsxwriter
import random
import gridfs
from datetime import datetime
from uuid import uuid4
from bson import json_util, objectid
import io
#=======================

def Generate_Token():
    token=str(uuid4())
    return token
#=======================

ca = certifi.where()
client = pymongo.MongoClient(
    "mongodb+srv://sameer:x7SggQ1Jx1pk1K3D@mainproject.qjpme9r.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)
db = client [ 'terralogic_hackathon' ]
login_data = db [ 'logins' ]
events_data=db['events']
fs = gridfs.GridFS(db)
#=============================
"""Runtime Storage"""
temp_otp=[]
COOKIE_TIME_OUT=60 * 60 * 24 * 7
date_format='%Y-%m-%d'
now_utc = datetime.now(timezone('UTC'))
asia_time=now_utc.astimezone(timezone('Asia/Kolkata'))
#==============================

app=Flask(__name__)
app.config [ 'MAIL_SERVER' ] = 'smtp.gmail.com'
app.config [ 'MAIL_PORT' ] = 465
app.config [ 'MAIL_USERNAME' ] = 'inforium2023@gmail.com'
app.config [ 'MAIL_PASSWORD' ] = 'rgerentrgpnjpgdv'
app.config [ 'MAIL_USE_TLS' ] = False
app.config [ 'MAIL_USE_SSL' ] = True
mail = Mail(app)
app.extensions [ 'mail' ].debug = 0
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.secret_key='thisismysiteforletsmeet12121@#2143432543645732432@!@42mlkdnvkjdsnvdsdskjbgkjdsb'
#===============================
def Send_confirmation(eventid,user_id):
    email=login_data.find_one({'id':int(user_id)})['email']
    logo_id=events_data.find_one({"id":int(eventid)})['logo_id']
    print(logo_id)
    msg = Message('Successfully Registered - Let\'sMeet',sender='inforium2023@gmail.com',recipients=[ email ])
    msg.html = render_template('email.html', logo=logo_id)
    print('hee')
    mail.send(msg)
    return {'status': True}

#==============================
@app.route('/')
def index():
    todayevents=events_data.find({"date":asia_time.strftime(date_format)})
    todayevents=json.loads(json_util.dumps(todayevents))
    if 'token' in session:
        user = login_data.find_one({"token": session['token']})
        if user:
            resp=make_response(render_template('landingpage.html',login_status=True,events=todayevents))
            resp.set_cookie('token', user['token'], max_age=COOKIE_TIME_OUT)
            return resp
    elif 'token' in request.cookies:
        user=login_data.find_one({"token":request.cookies.get('token')})
        if user:
            session['user']=user['username']
            session['token']=user['token']
            return render_template('landingpage.html',login_status=True,events=todayevents)
    return render_template('landingpage.html',login_status=False,events=todayevents)
#==============================
@app.route('/<date>/')
def index_date(date):
    todayevents=events_data.find({"date":date})
    todayevents=json.loads(json_util.dumps(todayevents))
    if 'token' in session:
        user = login_data.find_one({"token": session['token']})
        if user:
            resp=make_response(render_template('landingpage.html',login_status=True,events=todayevents))
            resp.set_cookie('token', user['token'], max_age=COOKIE_TIME_OUT)
            return resp
    elif 'token' in request.cookies:
        user=login_data.find_one({"token":request.cookies.get('token')})
        if user:
            session['user']=user['username']
            session['token']=user['token']
            return render_template('landingpage.html',login_status=True,events=todayevents)
    return render_template('landingpage.html',login_status=False,events=todayevents)

@app.route('/login/',methods=["POST","GET"])
def login():
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        user=login_data.find_one({"username":username.lower()})
        if user and password==user['password']:
            token=Generate_Token()
            login_data.update_one({"username":username.lower()},{"$set":{"token":token}})
            session['user']=username
            session['token']=token
            return redirect('/')
        return render_template('login.html',msg="Invalid Login Details")
    return render_template('login.html')
@app.route('/signup/',methods=['GET','POST'])
def signup():
    if request.method=="POST":
        name=request.form['fullname']
        mobile=request.form['mobilenum']
        email=request.form['email']
        password=request.form['password']
        if login_data.find_one({"username":email})!=None:
            return render_template('signup.html',msg='Already Registered. Please Login')

        if login_data.find_one(sort=[ ("id", -1) ]) == None:
            id = 1
        else:
            id = login_data.find_one(sort=[ ("id", -1) ]) [ 'id' ]+1
        token = Generate_Token()
        login_data.insert_one({
            "id":id,
            "name":name,
            "mobile":mobile,
            "email":email,
            "username":email,
            "password":password,
            "events":[],
            "token":token
        })
        session [ 'user' ] = email
        session [ 'token' ] = token
        return redirect('/')
    return render_template('signup.html')
@app.route("/signout/")
def signout():
    session.pop('user')
    session.pop('token')
    return redirect('/login/')

@app.route('/CreateEvent/',methods=['POST','GET'])
def CreateEvent():
    if request.method=='POST':
        token=session['token']
        user_id=login_data.find_one({"token":token})
        title=request.form['title']
        desc=request.form['description']
        date=request.form['date']
        address=request.form['address']
        logo=request.files['files']
        eventtype=request.form['eventtype']
        conductedby=request.form['conductedby']
        file_id = fs.put(logo, content_type=logo.content_type, filename=logo.filename)
        if events_data.find_one(sort=[ ("id", -1) ]) == None:
            id = 1
        else:
            id = events_data.find_one(sort=[ ("id", -1) ]) [ 'id' ]+1
        events_data.insert_one({"id":id,"title":title,"desc":desc,"date":date,"address":address,"logo_id":str(file_id),"conductedby":conductedby,"registrations":[user_id['id']],"owner":user_id['id'],"eventtype":eventtype})
        login_data.update_one({"token":token},{"$push":{"events":id}})
        return redirect('/')
    return render_template('createeve.html',login_status=True)
@app.route('/ViewEvent/<eventid>')
def ViewEvent(eventid):
    if 'token' not in session:
        return redirect('/login/')
    token=session['token']
    user_id=login_data.find_one({"token":token})['id']
    event_det=events_data.find_one({'id':int(eventid)})
    if user_id in event_det['registrations']:
        applied=True
    else:
        applied=False
    return render_template('viewevent.html',event=event_det,login_status=True,applied=applied)
@app.route('/ViewImg/<img_id>/',methods=['GET'])
def ViewDocument(img_id,):
    file = fs.get(objectid.ObjectId(img_id))
    return send_file(io.BytesIO(file.read()),mimetype=file.content_type)
@app.route('/downloadExcel/<eventid>/')
def sendexcel(eventid):
    all_data=events_data.find_one({"id":int(eventid)},{"_id":0,"registrations":1})
    part_list=json.loads(json_util.dumps(all_data))
    print(part_list)
    part_details=[]
    for id in part_list['registrations']:
        det=login_data.find_one({"id":id},{"_id":0,"name":1,"email":1,"mobile":1})
        part_details.append(det)
    print(part_details)
    df=pd.DataFrame(part_details)
    print(df)
    df.to_excel('static/temp/alldata.xlsx',index=False)
    return send_from_directory('static','temp/alldata.xlsx')
@app.route('/ApplyEvent/<EventID>/')
def ApplyEvent(EventID):
    token=session['token']
    user_id=login_data.find_one({"token":token},{"_id":0,"id":1})['id']
    events_data.update_one({"id":int(EventID)},{"$push":{"registrations":user_id}})
    login_data.update_one({"token":token }, {"$push": {"events": EventID}})
    Send_confirmation(EventID,user_id)
    return render_template("sucess.html")
@app.route('/MyEvents/')
def MyEvents():
    if 'token' in session:
        token=session['token']
        myevents=login_data.find_one({"token":token})
        reg_events=[]
        for e in myevents['events']:
            reg_events.append(events_data.find_one({"id":int(e)}))
        return render_template('viewevents.html',reg_events=reg_events,user_id=myevents['id'],login_status=True)
    return redirect('/')
#========================================
"""APIs"""
@app.post('/otpapi/')
def send_otp():
    if request.method == 'POST':
        otp=random.randrange(1000, 9999)
        temp_otp.append(otp)
        jsond=request.json
        if jsond['type']=='new':
            msg=Message(
                'OTP For SignUp - Let\'sMeet',
                sender='inforium2023@gmail.com',
                recipients=[jsond ['email']]
            )
            msg.html=render_template('otpemail.html', name=jsond['name'],
                                     otp=otp)
            mail.send(msg)
            return {'status': True}
        else:
            if jsond['otp'] =='':
                return {"status": False, "msg": "Incorrect OTP"}
            if int(jsond['otp']) in temp_otp:
                return {"status":True,"msg":"OTP Verified"}
            return {"status":False,"msg":"Incorrect OTP"}
    return {"status":False,"msg":"Method not allowed"}


#========================================

if '__main__'==__name__:
    app.run()