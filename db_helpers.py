from main import db, User, Submission, Board

# Simple wrapper to create entry in any table
def insert(table, **kwargs):
	entry = table(**kwargs)
	db.session.add(entry)
	db.session.commit()

# Even simpler function for basic select queries
def select(table, **kwargs, multiple=False):
	data = table.query.filter_by(**kwargs)
	return data.first if not multiple else data.all