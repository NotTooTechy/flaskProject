import json
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import get_articles
from flaskext.mysql import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, BooleanField
from passlib.hash import sha256_crypt

app = Flask(__name__)
local_articles = get_articles()

# Initilize mysql
mysql = MySQL()
mysql.init_app(app)
with open('auth.json', 'r') as f:
	db_config = json.load(f)

app.config["MYSQL_DATABASE_HOST"] = db_config["host"]
app.config["MYSQL_DATABASE_USER"] = db_config["user"]
app.config["MYSQL_DATABASE_PASSWORD"] = db_config["password"]
app.config["MYSQL_DATABASE_DB"] = db_config["db"]



@app.route("/")
def index():
	return render_template("home.html")

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/articles")
def articles():
	return render_template("articles.html", articles=local_articles)

@app.route("/articles/<string:id>/")
def an_article(id):
	return render_template("archive_articles.html", id=id)

class RegistrationForm(Form):
	name = StringField('Name', [validators.Length(min=4, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=50)])
	email = StringField('Email Address', [validators.Length(min=6, max=150)])
	password = PasswordField('New Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords must match')
		])
	confirm = PasswordField('Repeat Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))
		#cursor = mysql.get_db().cursor()
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO users(name, email, username, password) VALUES("%s", "%s", "%s", "%s")'''%(name, email, username, password))
		conn.commit()
		cursor.close()
		flash("You are now registered and login", "success")
		return redirect(url_for('index'))
	return render_template('register.html', form=form)

if __name__ == "__main__":
	app.secret_key = "secret_123"
	app.run(debug=True)
