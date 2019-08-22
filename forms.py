from wtforms import Form, StringField, PasswordField, TextAreaField, validators

class RegistrationForm(Form):
	username = StringField("Username", [validators.DataRequired(), validators.Length(min=4, max=30)])
	email = StringField("Email", [validators.DataRequired(), validators.Length(min=6, max=100)])
	password = PasswordField("Password", [
		validators.DataRequired(),
		validators.EqualTo("confirm", message="Passwords do not match")
	])
	confirm = PasswordField("Confirm Password")

class LoginForm(Form):
	username = StringField("Username", [validators.Length(min=4, max=30), validators.DataRequired()])
	password = PasswordField("Password", [validators.DataRequired()])

class PostForm(Form):
	title = StringField("Title", [validators.Length(min=5, max=200), validators.DataRequired()])
	body = TextAreaField("Text", [validators.Length(min=0, max=500)])

