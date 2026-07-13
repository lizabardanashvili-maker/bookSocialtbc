from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, Length, NumberRange


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(),
        Length(min=3, max=20)
    ])

    email = StringField("Email", validators=[
        DataRequired(),
        Email()
    ])

    password = PasswordField("Password", validators=[
        DataRequired(),
        Length(min=6)
    ])

    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(),
        Email()
    ])

    password = PasswordField("Password", validators=[
        DataRequired()
    ])

    submit = SubmitField("Login")


class BookForm(FlaskForm):
    title = StringField("Book Title", validators=[
        DataRequired()
    ])

    author = StringField("Author", validators=[
        DataRequired()
    ])

    review = TextAreaField("Review", validators=[
        DataRequired(),
        Length(min=10)
    ])

    rating = IntegerField("Rating (1-5)", validators=[
        DataRequired(),
        NumberRange(min=1, max=5)
    ])

    image = FileField("Book Cover", validators=[
        FileAllowed(["jpg", "jpeg", "png"], "Only images allowed!")
    ])

    submit = SubmitField("Add Book")