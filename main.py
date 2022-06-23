from flask import Flask, render_template, redirect, url_for, flash, abort
import os
from flask_bootstrap import Bootstrap
from datetime import date
from functools import wraps

from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import LoginForm, RegisterForm, AddTransactionForm


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# app.config['SECRET_KEY'] = 'my_secret_key'
Bootstrap(app)

##CONNECT TO DB
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI",  "sqlite:///cashlogger.db")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CONFIGURE TABLE
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    transaction = relationship("Transaction", back_populates="client")


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    client = relationship("User", back_populates="transaction")
    name = db.Column(db.String(250), nullable=False)
    sum = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250))
    date = db.Column(db.String(250), nullable=False)


db.create_all()

#
# def admin_only(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if current_user.id != 1:
#             return abort(403)
#         return f(*args, **kwargs)
#     return decorated_function
#
#
@app.route('/')
def home():
    return render_template("index.html", current_user=current_user)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            #User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))

    return render_template("signup.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('add_transaction'))
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/history')
def show_history():
    if current_user.is_authenticated:
        chart_data = db.session.query(func.sum(Transaction.sum).label('total'), Transaction.date).filter(Transaction.client_id == current_user.id).group_by(Transaction.date).all()
        transactions = Transaction.query.filter(Transaction.client_id == current_user.id).order_by(Transaction.date.desc()).all()
        return render_template("show_history.html", transactions=transactions, current_user=current_user, chart_data=chart_data)
    else:
        return redirect(url_for('login'))


# @app.route("/post/<int:post_id>", methods=["GET", "POST"])
# def show_post(post_id):
#     form = CommentForm()
#     requested_post = BlogPost.query.get(post_id)
#
#     if form.validate_on_submit():
#         if not current_user.is_authenticated:
#             flash("You need to login or register to comment.")
#             return redirect(url_for("login"))
#
#         new_comment = Comment(
#             text=form.comment_text.data,
#             comment_author=current_user,
#             parent_post=requested_post
#         )
#         db.session.add(new_comment)
#         db.session.commit()
#
#     return render_template("post.html", post=requested_post, form=form, current_user=current_user)


@app.route("/add-transaction", methods=["GET", "POST"])
def add_transaction():
    if current_user.is_authenticated:
        form = AddTransactionForm()
        if form.validate_on_submit():
            end_sum = form.sum.data
            if not bool(int(form.type.data)):
                end_sum = form.sum.data * -1
            new_transaction = Transaction(
                client_id=current_user.id,
                name=form.name.data,
                sum=end_sum,
                description=form.description.data,
                date=form.date.data
            )
            db.session.add(new_transaction)
            db.session.commit()
            return redirect(url_for('show_history'))

        return render_template("add_transaction.html", form=form, current_user=current_user)
    else:
        return redirect(url_for('login'))




# @app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
# @admin_only
# def edit_post(post_id):
#     post = BlogPost.query.get(post_id)
#     edit_form = CreatePostForm(
#         title=post.title,
#         subtitle=post.subtitle,
#         img_url=post.img_url,
#         author=current_user,
#         body=post.body
#     )
#     if edit_form.validate_on_submit():
#         post.title = edit_form.title.data
#         post.subtitle = edit_form.subtitle.data
#         post.img_url = edit_form.img_url.data
#         post.body = edit_form.body.data
#         db.session.commit()
#         return redirect(url_for("show_post", post_id=post.id))
#
#     return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


# @app.route("/delete/<int:post_id>")
# @admin_only
# def delete_post(post_id):
#     post_to_delete = BlogPost.query.get(post_id)
#     db.session.delete(post_to_delete)
#     db.session.commit()
#     return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    # app.run(debug=True)
