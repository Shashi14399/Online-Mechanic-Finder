from flask import Flask,request,render_template
import pickle
from flask import Flask, render_template
from flask import * 
from flask import request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy import exc
from datetime import datetime
import requests
import os
from math import radians, cos, sin, asin, sqrt

mech_uname = ""

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///web.db'
 
db = SQLAlchemy(app)

class Customers(UserMixin, db.Model):
	__tablename__ = 'Customers'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	email = db.Column(db.String(50))
	username = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(50))
	age = db.Column(db.String(50))
	phone = db.Column(db.String(50))

class Mechanics(UserMixin, db.Model):
	__tablename__ = 'Mechanics'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	email = db.Column(db.String(50))
	username = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(50))
	age = db.Column(db.String(50))
	phone = db.Column(db.String(50))
	location = db.Column(db.String(50))
	specification = db.Column(db.String(50))
	image = db.Column(db.String(50))
	latitude = db.Column(db.String(50))
	longitude = db.Column(db.String(50))
	total_rating = db.Column(db.String(50))
	avg_rating = db.Column(db.String(50))
	req_count = db.Column(db.String(50))

class CarRequests(db.Model):
    __tablename__ = 'CarRequests'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50),db.ForeignKey('Customers.username'))
    problem = db.Column(db.String(50))
    suggestions = db.Column(db.String(50))
    latitude = db.Column(db.String(100))
    longitude = db.Column(db.String(100))
class ScooterRequests(db.Model):
    __tablename__ = 'ScooterRequests'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50),db.ForeignKey('Customers.username'))
    problem = db.Column(db.String(50))
    suggestions = db.Column(db.String(50))
    latitude = db.Column(db.String(100))
    longitude = db.Column(db.String(100))
class BicycleRequests(db.Model):
    __tablename__ = 'BicycleRequests'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50),db.ForeignKey('Customers.username'))
    problem = db.Column(db.String(50))
    suggestions = db.Column(db.String(50))
    latitude = db.Column(db.String(100))
    longitude = db.Column(db.String(100))

class Feedback(db.Model):
    __tablename__ = 'Feedback'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50),db.ForeignKey('Mechanics.username'))
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    review = db.Column(db.String(100))
    overall = db.Column(db.String(50))
    timely = db.Column(db.String(50))
    support = db.Column(db.String(50))
    satisfaction = db.Column(db.String(50))
    rating = db.Column(db.String(50))
    suggestions = db.Column(db.String(100))

db.create_all()

def distance(lat1, lat2, lon1, lon2): 
      
	lon1 = radians(lon1) 
	lon2 = radians(lon2) 
	lat1 = radians(lat1) 
	lat2 = radians(lat2) 
	     
	dlon = lon2 - lon1  
	dlat = lat2 - lat1 
	a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2

	c = 2 * asin(sqrt(a))  
	 
	r = 6371
	   
	return(c * r) 

@login_manager.user_loader
def load_user(user_id):
	return Customers.query.get(int(user_id))

@app.route('/req_car_mech',methods=["GET","POST"])
@login_required
def request_page1():
	return render_template("car_request.html")

@app.route('/req_scooter_mech',methods=["GET","POST"])
@login_required
def request_page2():
	return render_template("scooter_request.html")

@app.route('/req_bicycle_mech',methods=["GET","POST"])
@login_required
def request_page3():
	return render_template("bicycle_request.html")

@app.route('/requests_car',methods=["GET","POST"])
@login_required
def request_data1():
	global mech_uname
	uname = request.form['username']
	problem = request.form['problem']
	suggestions = request.form['sugg']
	latitude = request.form['lat']
	longitude = request.form['long']
	query = "SELECT COUNT(*) from Customers where username = '"+uname+"'"
	mydata = {"query":query}
	r = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=mydata)
	res = json.loads(r.text)
	count = res[0]["COUNT(*)"]
	if count==0:
		return render_template("signup_cust.html",info="Invalid username Please signup")
	else:
		try:
			name = "Car"
			query2 = "SELECT * from Mechanics where specification = '"+name+"'"
			mydata2 = {"query":query2}
			r = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=mydata2)
			res = json.loads(r.text)
			mech_dist = {}
			for mech in res:
				n = mech['username']
				la1 = float(mech['latitude'])
				lo1 = float(mech['longitude'])
				la2 = float(latitude)
				lo2 = float(longitude)
				dis = distance(la1,la2,lo1,lo2)
				mech_dist[n] = dis
			a = sorted(mech_dist.items(), key=lambda x: x[1])
			##### intellingent part added #######
			l=[]
			rating_dict = {}
			k = 3 #selects three nearest mechanics, can be changed
			for i in range(k):
				l.append((a[i][0],round(a[i][1],2)))
			for value in l:
				mname = value[0]
				d = value[1]
				query4 = "SELECT avg_rating from Mechanics where username = '"+mname+"'"
				mydata4 = {"query":query4}
				r4 = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=mydata4)
				res4 = json.loads(r4.text)
				#return jsonify(res4[0]['rating'])
				rating_dict[mname] = (d,res4[0]['avg_rating'])
			
			rat = sorted(rating_dict.items(), key=lambda x: x[1][1],reverse=True)
			mech_uname = rat[0][0]
			d = rat[0][1][0]
			##### ends here #########
			query3 = "SELECT * from Mechanics where username = '"+mech_uname+"'"
			mydata3 = {"query":query3}
			r3 = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=mydata3)
			res3 = json.loads(r3.text)
			for data in res3:
				mech_name = data['name']
				mech_email = data['email']
				mech_age = data['age']
				mech_phone = data['phone']
			mydata = {"table":"CarRequests","insert":[uname,problem,suggestions,latitude,longitude]}
			r = requests.post("http://127.0.0.1:5000/api/v1/db/write",json=mydata)
			res = r.text
			entry = Mechanics.query.filter_by(username=mech_uname).first()
			if(res=='201'):
				if(entry.req_count == None):
					return render_template("req_succ.html", name=mech_name, uname=entry.username, dis = d, email = mech_email, spec=entry.specification, age = mech_age, phone = mech_phone, rcount=0, mech_rating=0, image=entry.image)
				else:
					return render_template("req_succ.html", name=mech_name, uname=entry.username, dis = d, email = mech_email, spec=entry.specification, age = mech_age, phone = mech_phone, rcount=entry.req_count, mech_rating=entry.avg_rating, image=entry.image)
		except:
			return render_template("no_mech.html")

			
@app.route('/requests_scooter',methods=["GET","POST"])
@login_required
def request_data2():
	global mech_uname
	uname = request.form['username']
	problem = request.form['problem']
	suggestions = request.form['sugg']
	latitude = request.form['lat']
	longitude = request.form['long']
	query = "SELECT COUNT(*) from Customers where username = '"+uname+"'"
	mydata = {"query":query}
	r = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=mydata)
	res = json.loads(r.text)
	count = res[0]["COUNT(*)"]
	if count==0:
		return render_template("signup_cust.html",info="Invalid username Please signup")
	else:
		try:
			name = "Scooter"
			query2 = "SELECT * from Mechanics where specification = '"+name+"'"
			mydata2 = {"query":query2}
			r = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=mydata2)
			res = json.loads(r.text)
			mech_dist = {}
			for mech in res:
				n = mech['username']
				la1 = float(mech['latitude'])
				lo1 = float(mech['longitude'])
				la2 = float(latitude)
				lo2 = float(longitude)
				dis = distance(la1,la2,lo1,lo2)
				mech_dist[n] = dis
			a = sorted(mech_dist.items(), key=lambda x: x[1])
			#mech_uname = a[0][0]
			#d = round(a[0][1],2)
			##### intellingent part added #######
			l=[]
			rating_dict = {}
			k = 3 ## selects three nearest mechanics, can be changed
			for i in range(k):
				l.append((a[i][0],round(a[i][1],2)))
			for value in l:
				mname = value[0]
				d = value[1]
				query4 = "SELECT avg_rating from Mechanics where username = '"+mname+"'"
				mydata4 = {"query":query4}
				r4 = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=mydata4)
				res4 = json.loads(r4.text)
				#return jsonify(res4[0]['rating'])
				rating_dict[mname] = (d,res4[0]['avg_rating'])
			
			rat = sorted(rating_dict.items(), key=lambda x: x[1][1],reverse=True)
			mech_uname = rat[0][0]
			d = rat[0][1][0]
			##### ends here #########
			query3 = "SELECT * from Mechanics where username = '"+mech_uname+"'"
			mydata3 = {"query":query3}
			r3 = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=mydata3)
			res3 = json.loads(r3.text)
			for data in res3:
				mech_name = data['name']
				mech_email = data['email']
				mech_age = data['age']
				mech_phone = data['phone']
			mydata = {"table":"ScooterRequests","insert":[uname,problem,suggestions,latitude,longitude]}
			r = requests.post("http://127.0.0.1:5000/api/v1/db/write",json=mydata)
			res = r.text
			entry = Mechanics.query.filter_by(username=mech_uname).first()
			if(res=='201'):
				if(entry.req_count == None):
					return render_template("req_succ.html", name=mech_name, uname=entry.username, spec=entry.specification, dis = d, email = mech_email, age = mech_age, phone = mech_phone, rcount=0, mech_rating=0, image=entry.image)
				else:
					return render_template("req_succ.html", name=mech_name, uname=entry.username, spec=entry.specification, dis = d, email = mech_email, age = mech_age, phone = mech_phone, rcount=entry.req_count, mech_rating=entry.avg_rating, image=entry.image)
		except:
			return render_template("no_mech.html")

@app.route('/requests_bicycle',methods=["GET","POST"])
@login_required
def request_data3():
	global mech_uname
	uname = request.form['username']
	problem = request.form['problem']
	suggestions = request.form['sugg']
	latitude = request.form['lat']
	longitude = request.form['long']
	query = "SELECT COUNT(*) from Customers where username = '"+uname+"'"
	mydata = {"query":query}
	r = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=mydata)
	res = json.loads(r.text)
	count = res[0]["COUNT(*)"]
	if count==0:
		return render_template("signup_cust.html",info="Invalid username Please signup")
	else:
		try:
			name = "Bicycle"
			query2 = "SELECT * from Mechanics where specification = '"+name+"'"
			mydata2 = {"query":query2}
			r = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=mydata2)
			res = json.loads(r.text)
			mech_dist = {}
			for mech in res:
				n = mech['username']
				la1 = float(mech['latitude'])
				lo1 = float(mech['longitude'])
				la2 = float(latitude)
				lo2 = float(longitude)
				dis = distance(la1,la2,lo1,lo2)
				mech_dist[n] = dis
			a = sorted(mech_dist.items(), key=lambda x: x[1])
			##mech_uname = a[0][0]
			##d = round(a[0][1],2)
			##### intellingent part added #######
			l=[]
			rating_dict = {}
			k = 3 # selects three nearest mechanics, can be changed
			for i in range(k):
				l.append((a[i][0],round(a[i][1],2)))
			for value in l:
				mname = value[0]
				d = value[1]
				query4 = "SELECT avg_rating from Mechanics where username = '"+mname+"'"
				mydata4 = {"query":query4}
				r4 = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=mydata4)
				res4 = json.loads(r4.text)
				#return jsonify(res4[0]['rating'])
				rating_dict[mname] = (d,res4[0]['avg_rating'])
			
			rat = sorted(rating_dict.items(), key=lambda x: x[1][1],reverse=True)
			mech_uname = rat[0][0]
			d = rat[0][1][0]
			##### ends here #########
			query3 = "SELECT * from Mechanics where username = '"+mech_uname+"'"
			mydata3 = {"query":query3}
			r3 = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=mydata3)
			res3 = json.loads(r3.text)
			for data in res3:
				mech_name = data['name']
				mech_email = data['email']
				mech_age = data['age']
				mech_phone = data['phone']
			mydata = {"table":"BicycleRequests","insert":[uname,problem,suggestions,latitude,longitude]}
			r = requests.post("http://127.0.0.1:5000/api/v1/db/write",json=mydata)
			res = r.text
			entry = Mechanics.query.filter_by(username=mech_uname).first()
			if(res=='201'):
				if(entry.req_count == None):
					return render_template("req_succ.html", name=mech_name, uname=entry.username, spec=entry.specification, dis = d, email = mech_email, age = mech_age, phone = mech_phone, rcount=0, mech_rating=0, image=entry.image)
				else:
					return render_template("req_succ.html", name=mech_name, uname=entry.username, spec=entry.specification, dis = d, email = mech_email, age = mech_age, phone = mech_phone, rcount=entry.req_count, mech_rating=entry.avg_rating, image=entry.image)
		except:
			return render_template("no_mech.html")


@app.route('/index')
def homepage():
	return render_template("index.html")

@app.route('/cust_request_types')
@login_required
def cust_request_types():
	return render_template("cust_request_types.html", name=current_user.name)

'''@app.route('/mech_prof')
def mech_prof():
	return render_template("mech_profile.html", name=current_user.name, spec=current_user.specification, age=current_user.age, phone=current_user.phone, email=current_user.email, loc=current_user.location, image=current_user.image)
'''

@app.route('/pricing')
def pricing():
	return render_template("pricing.html")

@app.route('/about')
def about():
	return render_template("about.html")

@app.route('/sign_cust_page')
def sign_up_form1():
	return render_template("signup_cust.html")

@app.route('/sign_mech_page')
def sign_up_form2():
	return render_template("signup_mech.html")
	

@app.route('/log_cust_page')
def login_form1():
	return render_template("login_cust.html")

@app.route('/feedback_form')
@login_required
def feedbackform():
	return render_template("feedback.html")

@app.route('/test')
def test():
	return render_template("test.html")

'''@app.route('/log_mech_page')
def login_form2():
	return render_template("login_mech.html")'''

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return render_template("index.html")

@login_manager.unauthorized_handler
def unauthorized_callback():
	   return render_template("not_loggedin.html")



@app.route('/feedback',methods=['POST','GET'])
def feedback():
	global mech_uname
	name=request.form['name']
	email=request.form['email']
	review=request.form['review']
	overall=request.form['radio']
	timely=request.form['radio1']
	support=request.form['radio2']
	satisfaction=request.form['radio3']
	rating=request.form['rating']
	suggestions=request.form['suggestions']

	mydata = {"table":"Feedback","insert":[mech_uname,name,email,review,overall,timely,support,satisfaction,rating,suggestions]}
	r = requests.post("http://127.0.0.1:5000/api/v1/db/write",json=mydata)
	res = r.text
	if res=='201':
		print(mech_uname)
		entry = Mechanics.query.filter_by(username=mech_uname).first()
		print(entry)
		entry.req_count = Feedback.query.filter_by(username=mech_uname).count()
		print(entry.total_rating)
		try:
			entry.total_rating = int(entry.total_rating) + int(rating)
			entry.avg_rating = int(entry.total_rating)/int(entry.req_count)
		except:
			entry.total_rating = int(rating)
			entry.avg_rating = int(rating)
		db.session.commit()
		return render_template('index.html',info='Added')
	else:
		return render_template('notadded.html',info='Unsuccessful')


@app.route('/sign_cust',methods=['POST','GET'])
def sign_up_cust():
	name=request.form['name']
	email=request.form['email']
	uname=request.form['uname']
	pwd=request.form['pass1']
	cpwd=request.form['pass2']
	age=request.form['age']
	phone=request.form['phno']

	mydata = {"table":"Customers","insert":[name,email,uname,pwd,age,phone]}
	r = requests.post("http://127.0.0.1:5000/api/v1/db/write",json=mydata)
	res = r.text
	if res=='201':
		return render_template('index.html',info='Added')
	else:
		return render_template('notadded.html',info='Unsuccessful')

@app.route('/sign_mech',methods=['POST','GET'])
def sign_up_mech():
	name=request.form['name']
	email=request.form['email']
	uname=request.form['uname']
	pwd=request.form['pass1']
	cpwd=request.form['pass2']
	age=request.form['age']
	phone=request.form['phno']
	loc=request.form['location']
	spec=request.form['spec']
	img=request.form['img']

	if(loc=="Jayanagar"):
		latitude = "12.925007"
		longitude = "77.593803"
	elif(loc=="Rajajinagar"):
		latitude = "12.987950"
		longitude = "77.560669"
	elif(loc=="Indiranagar"):
		latitude = "12.971891"
		longitude = "77.641151"
	elif(loc=="Yelahanka"):
		latitude = "13.080820"
		longitude = "77.592918"
	elif(loc=="Banashankari"):
		latitude = "12.922260"
		longitude = "77.557671"
	elif(loc=="Kormangala"):
		latitude = "13.058500"
		longitude = "77.294693"
	elif(loc=="Whitefield"):
		latitude = "12.969807"
		longitude = "77.749962"
	elif(loc=="Bannerghatta"):
		latitude = "12.826670"
		longitude = "77.554932"
	elif(loc=="Malleshwaram"):
		latitude = "12.995460"
		longitude = "77.573837"
	elif(loc=="Hebbal"):
		latitude = "13.043640"
		longitude = "77.590698"
	

	mydata = {"table":"Mechanics","insert":[name,email,uname,pwd,age,phone,loc,spec,img,latitude,longitude]}
	r = requests.post("http://127.0.0.1:5000/api/v1/db/write",json=mydata)
	res = r.text
	if res=='201':
		return render_template('index.html',info='Added')
	else:
		return render_template('notadded.html',info='Unsuccessful')


@app.route('/log_cust',methods=['POST','GET'])
def login_cust():
	uname=request.form['username']
	pwd=request.form['password']
	query = "SELECT COUNT(*) from Customers where username = '"+uname+"'"
	mydata = {"query":query}
	r = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=mydata)
	res = json.loads(r.text)

	
	#count = 0
	count = res[0]["COUNT(*)"]
	if count==0:
		return render_template('ivalid.html',info='Invalid User')
	else:
		query1 = "SELECT password from Customers where username = '"+uname+"'"
		mydata1 = {"query":query1}
		user = Customers.query.filter_by(username=uname).first()
		r1 = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=mydata1)
		res1 = json.loads(r1.text)
		pas = res1[0]["password"]
		if(pwd==pas):
			login_user(user)
			return render_template('cust_request_types.html', name=current_user.name)
		else:
			return render_template('ivalid.html',info='InValid User')

'''@app.route('/log_mech',methods=['POST','GET'])
def login_mech():
	uname=request.form['username']
	pwd=request.form['password']
	query = "SELECT COUNT(*) from Mechanics where username = '"+uname+"'"
	mydata = {"query":query}
	user = Mechanics.query.filter_by(username=uname).first()
	r = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=mydata)
	res = json.loads(r.text)

	
	#count = 0
	count = res[0]["COUNT(*)"]
	if count==0:
		return render_template('ivalid.html',info='Invalid User')
	else:
		query1 = "SELECT password from Mechanics where username = '"+uname+"'"
		mydata1 = {"query":query1}
		r1 = requests.post("http://127.0.0.1:5000/api/v1/db/read",json=mydata1)
		res1 = json.loads(r1.text)
		pas = res1[0]["password"]
		if(pwd==pas):
			login_user(user)
			return render_template('mech_profile.html', name=current_user.name, spec=current_user.specification, age=current_user.age, phone=current_user.phone, email=current_user.email, loc=current_user.location, image=current_user.image)
		else:
			return render_template('ivalid.html',info='InValid User')'''

	
@app.route("/api/v1/db/read",methods=["POST"])
def read_db():
	query = request.get_json()["query"]
	res = {}
	engine = create_engine('sqlite:///web.db')
	connection = engine.connect()
	if "DELETE" in query:
		connection.execute(query)
		return "200"
	else:
		result = connection.execute(query)
		res = [dict(x) for x in result]
		return jsonify(res)

@app.route("/api/v1/db/write",methods=["POST"])
def write_db():
	tbl = request.get_json()["table"]
	print(tbl)
	data = request.get_json()["insert"]
	if (tbl == "Customers"):
		try:
			user = Customers(name=data[0], email=data[1], username=data[2], password=data[3], age=data[4], phone=data[5])
			db.session.add(user)
			db.session.commit()
			return '201'
		except exc.IntegrityError as e:
			db.session().rollback()
			return '400'
		except:
			return '500'

	elif (tbl == "Mechanics"):
		try:
			user = Mechanics(name=data[0], email=data[1], username=data[2], password=data[3], age=data[4], phone=data[5], location=data[6], specification=data[7], image=data[8], latitude=data[9], longitude=data[10])
			db.session.add(user)
			db.session.commit()
			return '201'
		except exc.IntegrityError as e:
			db.session().rollback()
			return '400'
		except:
			return '500'
	elif(tbl == 'CarRequests'):
		try:
			user = CarRequests(username=data[0], problem=data[1], suggestions=data[2], latitude=data[3], longitude=data[4])
			db.session.add(user)
			db.session.commit()
			return '201'
		except exc.IntegrityError as e:
			db.session().rollback()
			return '400'
		except:
			return '500'
	elif(tbl == 'ScooterRequests'):
		try:
			user = ScooterRequests(username=data[0], problem=data[1], suggestions=data[2], latitude=data[3], longitude=data[4])
			db.session.add(user)
			db.session.commit()
			return '201'
		except exc.IntegrityError as e:
			db.session().rollback()
			return '400'
		except:
			return '500'
	elif(tbl == 'BicycleRequests'):
		try:
			user = BicycleRequests(username=data[0], problem=data[1], suggestions=data[2], latitude=data[3], longitude=data[4])
			db.session.add(user)
			db.session.commit()
			return '201'
		except exc.IntegrityError as e:
			db.session().rollback()
			return '400'
		except:
			return '500'

	elif (tbl == "Feedback"):
		try:
			user = Feedback(username=data[0], name=data[1], email=data[2], review=data[3], overall=data[4], timely=data[5], support=data[6], satisfaction=data[7], rating=data[8], suggestions=data[9])
			db.session.add(user)
			db.session.commit()
			return '201'
		except exc.IntegrityError as e:
			db.session().rollback()
			return '400'
		except:
			return '500'




if __name__ == '__main__':
	app.run()
