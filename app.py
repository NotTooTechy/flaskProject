import json
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import get_articles
from flaskext.mysql import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, BooleanField
from passlib.hash import sha256_crypt
from functools import wraps

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
#app.config["MYSQL_CURRSORCLASS"] = 'DictCursor'

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

# Registration form
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

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		# Get Form fields
		username = request.form['username']
		password_candidate = request.form['password']

		# Create cursor
		conn = mysql.connect()
		cursor = conn.cursor()
		result = cursor.execute('''SELECT * FROM users WHERE username="%s"'''%username)
		conn.close()
		if result > 0:
			# Get stored hash
			data = cursor.fetchone()
			app.logger.info(data[4])
			app.logger.info(data)
			password = data[4]
			# Compare Passwords
			if sha256_crypt.verify(password_candidate, password):
				 app.logger.info('Password Matched!!!')
				 session['logged_in'] = True
				 session['username'] = username
				 flash('You are now logged in', 'success')
				 return redirect(url_for('dashboard'))
			else:
				app.logger.info('...... ..... Password did not match!!!')
				error = "Invalid Password"
				return render_template('login.html', error=error)
		else:
			app.logger.info('NO user found')
			error = "Username not found"
			return render_template('login.html', error=error)
	return render_template('login.html')

# Check if the user il logged if __name__ == '__main__'
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please log in', 'danger')
			return redirect(url_for('login'))
	return wrap

# User logout
@app.route('/logout')
def logout():
	session.clear()
	flash("You are logged out", 'success')
	return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
	return render_template('dashboard.html')


if __name__ == "__main__":
	app.secret_key = "secret_123"
	app.run(debug=True)
