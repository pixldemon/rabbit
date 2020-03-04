from main import db
from sqlalchemy import ForeignKey

class User(db.Model):
	__tablename__ = "user"

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(100), nullable=False)
	registration_date = db.Column(db.DateTime, server_default=db.func.now())

	def __repr__(self):
		return"<User %r>" % self.username

class Submission(db.Model):
	__tablename__ = "submission"

	id = db.Column(db.Integer, primary_key=True)
	author_id = db.Column(db.Integer, ForeignKey("user.id"), nullable=False)
	board_id = db.Column(db.Integer, ForeignKey("board.id"), nullable=False)
	parent_id = db.Column(db.Integer, ForeignKey("submission.id"))
	creation_date = db.Column(db.DateTime, server_default=db.func.now())
	title = db.Column(db.String(200))
	body = db.Column(db.Text)

	author = db.relationship("user", backref=db.backref("submissions", lazy=True))
	board = db.relationship("board", backref=db.backref("submissions", lazy=True))
	parent = db.relationship("submission", backref=db.backref("children", lazy=True))

	def __repr__(self):
		return "<Comment %r by %r>" % (self.id, self.author_id)

class Board(db.Model):
	__tablename__ = "board"

	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(80), nullable=False, unique=True)
	creator_id = db.Column(db.Integer, ForeignKey("user.id"), nullable=False)
	creation_date = db.Column(db.DateTime, server_default=db.func.now())

	creator = db.relationship("user", backref=db.backref("created_boards", lazy=True))

	def __repr__(self):
		return "<Board b/%r>" % self.name