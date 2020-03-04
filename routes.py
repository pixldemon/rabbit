from flask import Blueprint, render_template, session, request, url_for, redirect, flash
from passlib.hash import sha256_crypt
from functools import wraps
from forms import LoginForm, PostForm, RegistrationForm, CommentForm
from database import insert, select, getbyid, User, Submission, Board
from main import db


# Create a flask blueprint object in order to seperate routes from the main app
routes = Blueprint("routes", __name__, template_folder="templates")


# Decorator to require the user to be logged in to access a route
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

		# Get the user from DB
		user = select(User, username=form.username.data)
		# If user exists and password checks out...
		if user and sha256_crypt.verify(form.password.data, user.password):

			# Set session keys
			session["username"] = form.username.data
			session["user"] = user.to_dict()

			# Flash a message, redirect to home
			flash("You are now logged in as %s" % session["username"], "success")
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
	user = select(User, username=username)

	# Render the profile
	return render_template("profile.html", user=user, submissions=user.submissions)


# Route to both render registration page and handle registration POST requests
@routes.route("/register", methods=["GET", "POST"])
def register():

	# Gen WTForms form from request data
	form = RegistrationForm(request.form)

	# In case of a POST request and if data checks out...
	if request.method == "POST" and form.validate():

		# Check if username is taken
		if not select(User, form.username.data):

			flash("This username is already taken", "error")
			return render_template("register.html", form=form)

		# Create DB entry with submitted data
		username = form.username.data
		email = form.email.data
		password = str(sha256_crypt.encrypt(form.password.data))

		insert(User, username=username, email=email, password=password)

		# Flash success message and redirect to home
		flash("Thank you! You are now registered", "success")
		return redirect(url_for("routes.home"))

	return render_template("register.html", form=form)


# Route to both render post submission page and handle POST posting requests
@routes.route("/b/<string:board>/create_post", methods=["POST", "GET"])
@login_required
def create_post(board):

	# Grab board data from DB
	board = select(Board, name=board)
	# Create WTForms form from request data
	form = PostForm(request.form)
	# Store user in author variable
	author = session["user"]

	# In case of a POST request and if form checks out
	if request.method == "POST" and form.validate():

		# Create DB entry for post
		entry = insert(Submission, author_id=author["id"], title=form.title.data, body=form.body.data, board_id=board.id)
		entry.original_post_id = entry.id
		db.session.commit()

		# Get ID of the post just made and redirect to it
		return redirect(url_for("routes.view_post", id=entry.id))
	else:
		# Render post submission page
		return render_template("create_post.html", board=board.name, form=form)

# Route to view specific post
@routes.route("/post/<int:id>")
def view_post(id):
	# Get the post from DB
	post = getbyid(Submission, id)

	# Render the post
	return render_template("single_post.html", post=post, comment_form=CommentForm(), comment_id=request.args.get("reply", default=post.id, type=int))


# Route to view a post and comment a comment
@routes.route("/reply/<int:comment_id>", methods=["GET", "POST"])
@login_required
def reply(comment_id):

	if request.method == "POST":
		
		# Create WTForms form from data
		form = CommentForm(request.form)
		# Store user in author 
		author = session["user"]

		# Check if the form checks out
		if form.validate():

			# Create DB entry for comment
			entry = insert(Submission, author_id=author["id"], parent_id=comment_id, body=form.body.data, board_id=0)
			entry.original_post_id = entry.parent.original_post_id

			db.session.commit()

	# BIG TODO: HIGHLY INEFFICIENT WAY OF FINDING ORIGINAL POST	
	# Get target from DB
	target = getbyid(Submission, comment_id)
	post = target.original_post
	
	# while post.board_id == 0:
	# 	post = post.parent

	# Render the post
	return redirect(url_for("routes.view_post", id=post.id, reply=target.id if request.method=="GET" else None))

# Route to render board
@routes.route("/b/<string:board>")
def view_board(board):

	# Get board from DB
	board = select(Board, name=board)

	# If the board doesn't exist
	if not board:
		# The board does not exist, flash message and redirect
		flash("This board does not exist", "error")
		return redirect(url_for("routes.home"))
	else:
		# Get posts form DB
		amount = request.args.get("amount", default=30)
		submissions = Submission.query.filter_by(board_id=board.id).order_by(Submission.creation_date).limit(amount)
		# Render the posts
		return render_template("board.html", board=board, submissions=submissions)
