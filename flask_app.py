from flask import render_template, Flask, session, redirect, url_for, request, flash, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

# MySQL Configuration
app.config["MYSQL_HOST"] = "0.0.0.0"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "qwerty"
app.config["MYSQL_DB"] = "rabbit"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


@app.route("/")
def home():
	return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():

	form = LoginForm(request.form)

	if request.method == "POST" and form.validate():

		cur = mysql.connection.cursor()
		cur.execute("SELECT password FROM users WHERE username = %s", (request.form["username"],))

		result = cur.fetchone()
		cur.close()

		if result and sha256_crypt.verify(form.password.data, result["password"]):

			session["username"] = form.username.data
			flash("You are now logged in as %s" % (session["username"],), "success")
			return redirect(url_for("home"))

		else:
			flash("Invalid password and/or username", "error")
			return redirect(url_for("login"))

	return render_template("login.html", form=form)


@app.route("/logout")
def logout():
	session.clear()
	return redirect(url_for("home"))

@app.route("/u/<string:username>")
def profile(username):
	return render_template("profile.html", user=get_user(username))


@app.route("/register", methods=["GET", "POST"])
def register():

	form = RegistrationForm(request.form)

	if request.method == "POST" and form.validate():

		if user_exists(form.username.data):

			flash("This username is already taken", "error")
			return render_template("register.html", form=form)

		username = form.username.data
		email = form.email.data
		password = str(sha256_crypt.encrypt(form.password.data))

		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO users(email, username, password) VALUES(%s, %s, %s)", (email, username, password))

		mysql.connection.commit()
		cur.close()

		flash("Thank you! You are now registered", "success")
		return redirect(url_for("home"))

	return render_template("register.html", form=form)


def get_user_by_id(_id):

	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM users WHERE id = %s;", (_id,))
	result = cur.fetchone()
	cur.close()

	if result:
		return User(result)
	
	raise UserNotFoundError("This user does not exist")

def get_user(username):

	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM users WHERE username = %s", (username,))
	result = cur.fetchone()
	cur.close()

	if result:
		return User(result)
	
	raise UserNotFoundError("This user does not exist")

def user_exists(username):
	try:
		get_user(username)
	except UserNotFoundError:
		return False
	
	return True

class User:
	_id = 0
	username = ""
	email = ""
	password = ""
	admin = False
	registration_date = ""
	def __init__(self, props):
		self._id = props["id"]
		self.username = props["username"]
		self.email = props["email"]
		self.password = props["password"]
		self.admin = props["type"] == "admin"
		self.registration_date = props["registration_date"]

def get_post_by_id(_id):
	
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM posts WHERE id=%s", (_id,))
	result = cur.fetchone()

	if result:
		return Post(result)
	
	raise PostNotFoundError("This post does not exist")

class Post:
	_id = 0
	author = None
	title = ""
	body = ""
	score = 0
	creation_date = ""
	board = "all"

	def __init__(self, props):
		self._id = props["id"]
		self.title = props["title"]
		self.body = props["body"]
		self.score = props["score"]
		self.creation_date = props["creation_date"]
		self.board = props["board"]

		self.author = get_user_by_id(props["author_id"])


class UserNotFoundError(Exception):
	pass
class PostNotFoundError(Exception):
	pass


@app.route("/b/<string:board>/create_post", methods=["POST", "GET"])
def create_post(board):

	if not "username" in session:
		flash("You have to log in to be able to post", "error")
		return redirect(url_for("login"))

	form = PostForm(request.form)
	author = get_user(session["username"])

	if request.method == "POST" and form.validate():
		
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO posts(author_id, title, body, board) VALUES(%s, %s, %s, %s)", (author._id, form.title.data, form.body.data, board))
		
		cur.execute("SELECT LAST_INSERT_ID();")
		_id = cur.fetchone()["LAST_INSERT_ID()"]
		mysql.connection.commit()
		cur.close()

		print(id)
		return redirect(url_for("view_post", board=board, _id=_id))
	else:
		return render_template("create_post.html", board=board, form=form)

@app.route("/b/<string:board>/post/<int:_id>")
def view_post(board, _id):
	
	post = get_post_by_id(_id)
	
	if post.board == board:
		return render_template("single_post.html", post=post)
	
	flash("This post was not posted on this board", "error")
	return redirect(url_for("home"))

class RegistrationForm(Form):
	username = StringField("Username", [validators.DataRequired(), validators.Length(min=4, max=30)])
	email = StringField("Email", [validators.DataRequired(), validators.Length(min=6, max=100)])
	password = PasswordField("Password", [
		validators.DataRequired(),
		validators.EqualTo("confirm", message="Passwords do not match")
	])
	confirm = PasswordField("Confirm Password")

class LoginForm(Form):
	username = StringField("Username", [validators.Length(min=4, max=30), validators.DataRequired()])
	password = PasswordField("Password", [validators.DataRequired()])

class PostForm(Form):
	title = StringField("Title", [validators.Length(min=5, max=200), validators.DataRequired()])
	body = TextAreaField("Text", [validators.Length(min=0, max=500)])



@app.route("/test")
def test():
	return redirect(url_for("home"))

if __name__ == "__main__":
	app.secret_key = "qwerty"
	app.run("0.0.0.0", 8080, debug=True)