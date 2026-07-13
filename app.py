from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)

from sqlalchemy import or_

from models import db, User, Book
from forms import RegisterForm, LoginForm, BookForm
from werkzeug.security import generate_password_hash, check_password_hash

import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "static/uploads"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

app.config['SECRET_KEY'] = '30590'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# მთავარი გვერდი
@app.route("/")
def home():
    return render_template("index.html")


# რეგისტრაცია
@app.route("/register", methods=["GET", "POST"])
def register():

    form = RegisterForm()

    if form.validate_on_submit():

        existing_user = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_user:
            flash("ეს ელფოსტა უკვე გამოყენებულია.")
            return redirect(url_for("register"))

        user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data)
        )

        db.session.add(user)
        db.session.commit()

        flash("რეგისტრაცია წარმატებით დასრულდა!")

        return redirect(url_for("login"))

    return render_template(
        "register.html",
        form=form
    )

# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and check_password_hash(
            user.password,
            form.password.data
        ):
            login_user(user)
            flash("თქვენ წარმატებით შეხვედით")

            return redirect(url_for("home"))

        else:
            flash("არასწორი მონაცემები")
    return render_template(
        "login.html",
        form=form
    )

# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("თქვენ გამოხვედით ანგარიშიდან")
    return redirect(url_for("home"))

# წიგნის დამატება
@app.route("/add_book", methods=["GET", "POST"])
@login_required
def add_book():
    form = BookForm()

    if form.validate_on_submit():

        image_filename = None

        if form.image.data:
            image = form.image.data
            image_filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    image_filename
                )
            )

        book = Book(
            title=form.title.data,
            author=form.author.data,
            review=form.review.data,
            rating=form.rating.data,
            image=image_filename,
            user_id=current_user.id
        )

        db.session.add(book)
        db.session.commit()

        flash("წიგნი დაემატა!")
        return redirect(url_for("books"))

    return render_template("add_book.html", form=form)

# ყველა წიგნის ნახვა
from sqlalchemy import or_

@app.route("/books")
@login_required
def books():
    search = request.args.get("search")

    if search:
        books = Book.query.filter(
            or_(
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%")
            )
        ).all()
    else:
        books = Book.query.all()

    return render_template(
        "books.html",
        books=books
    )

@app.route("/book/<int:id>")
def book_detail(id):
    book = Book.query.get_or_404(id)

    return render_template(
        "book_detail.html",
        book=book
    )

# პროფილი
@app.route("/profile")
@login_required
def profile():

    return render_template(
        "profile.html",
        user=current_user
    )

# Admin შემოწმება
def admin_required():

    return current_user.is_authenticated and current_user.is_admin

# წიგნის წაშლა (მხოლოდ Admin)
@app.route("/delete_book/<int:id>")
@login_required
def delete_book(id):

    if not admin_required():

        flash("ამ მოქმედების უფლება არ გაქვთ")

        return redirect(url_for("books"))

    book = Book.query.get_or_404(id)

    db.session.delete(book)
    db.session.commit()
    flash("წიგნი წაიშალა")
    return redirect(url_for("books"))

@app.route("/edit_book/<int:id>", methods=["GET", "POST"])
@login_required
def edit_book(id):
    book = Book.query.get_or_404(id)

    # მხოლოდ საკუთარი წიგნის რედაქტირება
    if book.user_id != current_user.id:
        flash("ამ წიგნის რედაქტირების უფლება არ გაქვთ.")
        return redirect(url_for("books"))

    form = BookForm(obj=book)

    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.review = form.review.data
        book.rating = form.rating.data

        db.session.commit()

        flash("წიგნი წარმატებით განახლდა!")
        return redirect(url_for("books"))

    return render_template("add_book.html", form=form)

# ბაზის შექმნა
with app.app_context():

    db.create_all()

if __name__ == "__main__":

    app.run(debug=True)