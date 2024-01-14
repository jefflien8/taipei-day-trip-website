from flask import *
from api import apiBlueprint

app=Flask(__name__,static_folder="public", static_url_path="/public")
app.register_blueprint(apiBlueprint)
app.config['SECRET_KEY']="123456"
app.config['SESSION_TYPE'] = 'filesystem'
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True


# Pages
@app.before_first_request
def make_session():
    session['name'] = None
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")


app.run(host='0.0.0.0',port=3000)