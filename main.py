"""
TODO: Use HTML data attributes to style usernames depending on their roles/ranks, perhaps more in appropiate usecases 
TODO: Sort posts by creation date
TODO: List boards on homepage
TODO: Board description
TODO: Figure out how to rank posts
"""

from flask import Flask
from database import db


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///rabbit.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

if __name__ == "__main__":
	
	from routes import routes
	app.register_blueprint(routes)

	app.secret_key = "qwerty"
	app.run("0.0.0.0", 8080, debug=True)