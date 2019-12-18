import json
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, BooleanField
from passlib.hash import sha256_crypt
from functools import wraps
from using_sqlite import create_user, create_an_article, get_all_articles, get_all_users, get_user, delete_an_article, \
						get_an_article, update_an_article

app = Flask(__name__)
#local_articles = get_articles()

USE_SQLite = True

# Check if the user is logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please log in', 'danger')
			return redirect(url_for('login'))
	return wrap

@app.route("/", methods=['GET', 'POST'])
def index():
	return render_template("home.html")

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/articles")
@is_logged_in
def articles():
	articles = get_all_articles()
	app.logger.info(articles)
	if articles:
		return render_template('articles.html', articles=articles)
	else:
		msg = '''No articles found'''
		return render_template('articles.html', msg=msg)

@app.route("/articles/<string:id>/")
def an_article(id):
	article = get_an_article(id)
	return render_template("archive_articles.html", article=article)

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
		create_user(name, email, username, password)
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
		data = get_user(username)
		if data is not None:
			# Get stored hash
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



# User logout
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash("You are logged out", 'success')
	return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
	# Pull article list from db
	# create curosor
	articles = get_all_articles()
	app.logger.info(articles)
	if  articles:
		return render_template('dashboard.html', articles=articles)
	else:
		msg = '''No articles found'''
		return render_template('dashboard.html', msg=msg)

# Article form class
class ArticleForm(Form):
	title = StringField('Title', [validators.Length(min=4, max=200)])
	body = TextAreaField('Body', [validators.Length(min=30)])

# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
	form = ArticleForm(request.form)
	if request.method == "POST" and form.validate():
		title = form.title.data
		body = form.body.data
		create_an_article(title, body, session['username'])

		flash('Article Created', 'success')
		return redirect(url_for('dashboard'))
	return render_template('add_article.html', form=form)

# Add Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
	article = get_an_article(id)
	# Get article form
	form = ArticleForm(request.form)

	# Pupulete article form fileds
	form.title.data = article[1]
	form.body.data = article[3]

	if request.method == "POST" and form.validate():
		title = request.form['title']
		body = request.form['body']
		update_an_article(title, body, id)
		flash('Article Updated', 'success')
		return redirect(url_for('dashboard'))
	return render_template('edit_article.html', form=form)

# Delete Articles
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
	delete_an_article(id)
	flash('Article deleted', 'success')
	return redirect(url_for('dashboard'))


if __name__ == "__main__":
	import os
	from using_sqlite import main as main_prepare_db
	main_prepare_db()
	app.secret_key = "secret_123"
	port = int(os.environ.get('PORT', 5000))
	#app.run(debug=True)
	app.run(host='0.0.0.0', port=port, debug=True)
