from main import mysql

def execute(query, params=(), multiple=False):
	
	cur = mysql.connection.cursor()
	cur.execute(query, params)
	
	if multiple:
		result = cur.fetchall()
	else:
		result = cur.fetchone()
	
	mysql.connection.commit()
	cur.close()

	return result