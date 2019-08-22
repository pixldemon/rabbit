from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Configuration
app.config["MYSQL_HOST"] = "0.0.0.0"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "qwerty"
app.config["MYSQL_DB"] = "rabbit"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

if __name__ == "__main__":
	
	from routes import routes
	app.register_blueprint(routes)

	app.secret_key = "qwerty"
	app.run("0.0.0.0", 8080, debug=True)
