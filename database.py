from sqlalchemy import ForeignKey
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Wrapper to create entry in any table
def insert(table, **kwargs):
	entry = table(**kwargs)
	db.session.add(entry)
	db.session.commit()
	return entry

# Function for basic select queries
def select(table, multiple=False, **kwargs):
	data = table.query.filter_by(**kwargs)
	return data.first() if not multiple else data.all()

# Function for selecting by primary key
def getbyid(table, id):
	return table.query.get(id)

class User(db.Model):
	__tablename__ = "user"

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(100), nullable=False)
	type = db.Column(db.String(50), nullable=False, server_default="user")
	registration_date = db.Column(db.DateTime, server_default=db.func.now())

	def __repr__(self):
		return"<User %r>" % self.username
	
	def to_dict(self):
		return {
			"id": self.id,
			"username": self.username,
			"email": self.email,
			"registration_date": self.registration_date,
			"type": self.type
		}

class Submission(db.Model):
	__tablename__ = "submission"

	id = db.Column(db.Integer, primary_key=True)
	author_id = db.Column(db.Integer, ForeignKey("user.id"), nullable=False)
	board_id = db.Column(db.Integer, ForeignKey("board.id"), nullable=False)
	parent_id = db.Column(db.Integer, ForeignKey("submission.id"))
	original_post_id = db.Column(db.Integer, ForeignKey("submission.id"))

	creation_date = db.Column(db.DateTime, server_default=db.func.now())
	title = db.Column(db.String(200))
	body = db.Column(db.Text)

	author = db.relationship("User", backref=db.backref("submissions", lazy=True))
	board = db.relationship("Board", backref=db.backref("submissions", lazy=True))
	children = db.relationship("Submission", backref=db.backref("parent", remote_side=[id], foreign_keys=[parent_id], lazy=True), primaryjoin="Submission.id == Submission.parent_id")
	# original_post = db.relationship("Submission", backref=db.backref("replies", remote_side=[original_post_id], lazy=True), primaryjoin="Submission.id == Submission.original_post_id")
	replies = db.relationship("Submission", backref=db.backref("original_post", remote_side=[id], foreign_keys=[original_post_id], lazy=True), primaryjoin="Submission.original_post_id == Submission.id")
	
	def __repr__(self):
		return "<Comment %r by %r>" % (self.id, self.author_id)

class Board(db.Model):
	__tablename__ = "board"

	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(80), nullable=False, unique=True)
	creator_id = db.Column(db.Integer, ForeignKey("user.id"), nullable=False)
	creation_date = db.Column(db.DateTime, server_default=db.func.now())

	creator = db.relationship("User", backref=db.backref("created_boards", lazy=True))

	def __repr__(self):
		return "<Board b/%r>" % self.name