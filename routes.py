from flask import Blueprint, render_template, session, request, url_for, redirect, flash
from passlib.hash import sha256_crypt
from functools import wraps

from forms import LoginForm, PostForm, RegistrationForm, CommentForm
from users import get_user, get_user_by_id, user_exists
from main import mysql
from posts import Comment, get_post_by_id

from db_helpers import execute



# Create a flask blueprint object in order to seperate routes from the main app
routes = Blueprint("routes", __name__, template_folder="templates")


# Decorator to require the user to be logged in to view a route
def login_required(f):

	# Copy function attributes of passed function onto the wrapper
	@wraps(f)
	def wrapper(*args, **kwargs):
		# If user key exists in session, user is logged in
		if not "user" in session:
			# Flash message and redirect to login page
			flash("You have to be logged in to view this page", "error")
			return redirect(url_for("routes.login"))
		else:
			# Otherwise, execute the passed function with all potential parameters
			return f(*args, **kwargs)

	# Finally, return the wrapped function
	return wrapper


# Basic route for main page
@routes.route("/")
def home():
	return render_template("home.html")


# Route to both render the login page aswell as handle the actual login POST requests
@routes.route("/login", methods=["GET", "POST"])
def login():

	# Gen WTForms form based on request data
	form = LoginForm(request.form)

	# In the case of a POST request, if form submission is valid...
	if request.method == "POST" and form.validate():
		
		# Get the password from DB
		result = execute("SELECT password FROM users WHERE username = %s", (request.form["username"],))

		# If user exists and password checks out...
		if result and sha256_crypt.verify(form.password.data, result["password"]):

			# Set session keys
			session["username"] = form.username.data
			session["user"] = get_user(form.username.data).__dict__

			# Flash a message, redirect to home
			flash("You are now logged in as %s" % (session["username"],), "success")
			return redirect(url_for("routes.home"))
		
		else:

			# Flash error message, redirect to login
			flash("Invalid password and/or username", "error")
			return redirect(url_for("routes.login"))

	# Render login page
	return render_template("login.html", form=form)


# Route to clear session and log out
@routes.route("/logout")
def logout():
	session.clear()
	return redirect(url_for("routes.home"))


# Route to render user profile
@routes.route("/u/<string:username>")
def view_profile(username):

	# Grab users information from DB
	user = get_user(username)
	# Grab users posts and comments from DB
	posts = execute("SELECT * FROM comments WHERE author_id = %s;", (user.id,), multiple=True)
	# Create Comment objects from query results in dictionary form
	posts = list(map(lambda p: Comment(p), posts))

	# Render the profile
	return render_template("profile.html", user=user, posts=posts)


# Route to both render registration page and handle registration POST requests
@routes.route("/register", methods=["GET", "POST"])
def register():

	# Gen WTForms form from request data
	form = RegistrationForm(request.form)

	# In case of a POST request and if data checks out...
	if request.method == "POST" and form.validate():

		# Check if username is taken
		if user_exists(form.username.data):

			flash("This username is already taken", "error")
			return render_template("register.html", form=form)

		# Create DB entry with submitted data
		username = form.username.data
		email = form.email.data
		password = str(sha256_crypt.encrypt(form.password.data))

		execute("INSERT INTO users(email, username, password) VALUES(%s, %s, %s)", (email, username, password))

		# Flash success message and redirect to home
		flash("Thank you! You are now registered", "success")
		return redirect(url_for("routes.home"))

	return render_template("register.html", form=form)


# Route to both render post submission page and handle POST posting requests
@routes.route("/b/<string:board>/create_post", methods=["POST", "GET"])
@login_required
def create_post(board):

	# Grab board data from DB
	board = execute("SELECT * FROM boards WHERE name = %s", (board,))
	# Create WTForms form from request data
	form = PostForm(request.form)
	# Store user in author variable
	author = session["user"]

	# In case of a POST request and if form checks out
	if request.method == "POST" and form.validate():

		# Create DB entry for post
		execute("INSERT INTO comments(author_id, title, body, board_id) VALUES(%s, %s, %s, %s)", (author["id"], form.title.data, form.body.data, board["id"]))
		# Get ID of the post just made and redirect to it
		id = execute("SELECT LAST_INSERT_ID();")["LAST_INSERT_ID()"]
		return redirect(url_for("routes.view_post", id=id))
	else:
		# Render post submission page
		return render_template("create_post.html", board=board["name"], form=form)


# Route to handle comment POST requests
@routes.route("/comment", methods=["POST"])
@login_required
def comment():
	
	# Create WTForms form from data
	form = CommentForm(request.form)
	# Store user in author
	author = session["user"]

	# Check if the form checks out
	if form.validate():
		# Create DB entry for comment
		execute("INSERT INTO comments(author_id, parent_id, body, board_id) VALUES(%s, %s, %s, %s)", (author["id"], request.form["post"], form.body.data, 1))

	# Render the commented post
	return redirect(url_for("routes.view_post", id=request.form["post"]))


# Route to view specific post
@routes.route("/post/<int:id>")
def view_post(id):

	# Get the post from DB
	post = get_post_by_id(id)
	# Check if the post 
	return render_template("single_post.html", post=post, commentform=CommentForm())


# Route to view a post and comment a comment
@routes.route("/reply/<int:comment_id>")
@login_required
def reply(comment_id):

	# Get target from DB
	target = get_post_by_id(comment_id)
	post = target

	while post.board_id == 1:
		post = get_post_by_id(post.parent_id)
	print(target.id)
	# Render the post
	return render_template("single_post.html", post=post, commentform=CommentForm(), comment_id=comment_id)


# Route to render board
@routes.route("/b/<string:board>")
def view_board(board):

	# Get ID from board name
	board_id = execute("SELECT id FROM boards WHERE name = %s", (board,))["id"]
	# Get all posts from DB
	posts = execute("SELECT * FROM comments WHERE board_id = %s", (board_id,), multiple=True)
	
	# If that query fetched posts...
	if board_id == 1 or not posts:
		# The board does not exist, flash message and redirect
		flash("This board does not exist", "error")
		return redirect(url_for("routes.home")) 
	else:
		# Render the posts
		posts = list(map(lambda p: Comment(p), posts))
		return render_template("board.html", board=board, posts=posts)