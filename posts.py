from main import mysql
from user_helpers import get_user_by_id

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

class PostNotFoundError(Exception):
	pass