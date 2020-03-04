from main import db
from users import get_user_by_id
from db_helpers import execute

def get_post_by_id(id):
	
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM comments WHERE id=%s", (id,))
	result = cur.fetchone()

	if result:
		return Comment(result)
	
	raise PostNotFoundError("This post does not exist")

class Comment:
	id = 0
	author = None
	title = ""
	body = ""
	creation_date = ""
	board_id = None
	board_name = None
	parent_id = None
	children = []

	def __init__(self, props):
		self.id = props["id"]
		self.title = props["title"]
		self.body = props["body"]
		self.creation_date = props["creation_date"]
		self.board_id = props["board_id"]
		self.board_name = execute("SELECT name FROM boards WHERE id = %s", (self.board_id,))["name"]
		self.author = get_user_by_id(props["author_id"])
		self.parent_id = props["parent_id"]
		
		self.children = execute("SELECT * FROM comments WHERE parent_id = %s", (self.id,), True)
		self.children = list(map(lambda c: Comment(c), self.children))
		
class PostNotFoundError(Exception):
	pass