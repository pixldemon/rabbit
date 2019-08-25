from flask import Blueprint, render_template, session, request, url_for, redirect, flash
from passlib.hash import sha256_crypt

from forms import LoginForm, PostForm, RegistrationForm
from user_helpers import get_user, get_user_by_id, user_exists
from main import mysql
from posts import Post, get_post_by_id

from db_helpers import execute

routes = Blueprint("routes", __name__, template_folder="templates")

@routes.route("/")
def home():
	return render_template("home.html")

@routes.route("/login", methods=["GET", "POST"])
def login():

	form = LoginForm(request.form)

	if request.method == "POST" and form.validate():

		result = execute("SELECT password FROM users WHERE username = %s", (request.form["username"],))

		if result and sha256_crypt.verify(form.password.data, result["password"]):

			session["username"] = form.username.data
			flash("You are now logged in as %s" % (session["username"],), "success")
			return redirect(url_for("routes.home"))

		else:
			flash("Invalid password and/or username", "error")
			return redirect(url_for("routes.login"))

	return render_template("login.html", form=form)


@routes.route("/logout")
def logout():
	session.clear()
	return redirect(url_for("routes.home"))

@routes.route("/u/<string:username>")
def view_profile(username):

	user = get_user(username)
	posts = execute("SELECT * FROM posts WHERE author_id = %s;", (user._id,), True)
	posts = list(map(lambda p: Post(p), posts))

	return render_template("profile.html", user=user, posts=posts)


@routes.route("/register", methods=["GET", "POST"])
def register():

	form = RegistrationForm(request.form)

	if request.method == "POST" and form.validate():

		if user_exists(form.username.data):

			flash("This username is already taken", "error")
			return render_template("register.html", form=form)

		username = form.username.data
		email = form.email.data
		password = str(sha256_crypt.encrypt(form.password.data))

		execute("INSERT INTO users(email, username, password) VALUES(%s, %s, %s)", (email, username, password))
	

		flash("Thank you! You are now registered", "success")
		return redirect(url_for("routes.home"))

	return render_template("register.html", form=form)

@routes.route("/b/<string:board>/create_post", methods=["POST", "GET"])
def create_post(board):

	if not "username" in session:
		flash("You have to log in to be able to post", "error")
		return redirect(url_for("routes.login"))

	form = PostForm(request.form)
	author = get_user(session["username"])

	if request.method == "POST" and form.validate():
		
		execute("INSERT INTO posts(author_id, title, body, board) VALUES(%s, %s, %s, %s)", (author._id, form.title.data, form.body.data, board))
		_id = execute("SELECT LAST_INSERT_ID();")["LAST_INSERT_ID()"]
		
		print(id)
		return redirect(url_for("routes.view_post", board=board, _id=_id))
	else:
		return render_template("create_post.html", board=board, form=form)

@routes.route("/b/<string:board>/post/<int:_id>")
def view_post(board, _id):
	
	post = get_post_by_id(_id)
	
	if post.board == board:
		return render_template("single_post.html", post=post)
	
	flash("This post was not posted on this board", "error")
	return redirect(url_for("home"))

@routes.route("/b/<string:board>")
def view_board(board):
	
	posts = execute("SELECT * FROM posts WHERE board = %s;", (board,), True)
	print(posts)
	if posts:
		print("\n\n\n\n\n\n\n\n\n\n\n\n\n")
		posts = list(map(lambda p: Post(p), posts))
		print(posts)
		return render_template("board.html", board=board, posts=posts)
	else:
		flash("This board does not exist", "error")
		return redirect(url_for("routes.home")) 