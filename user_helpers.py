
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

class UserNotFoundError(Exception):
	pass
