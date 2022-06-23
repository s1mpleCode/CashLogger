from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email
from flask_ckeditor import CKEditorField


##WTForm
class AddTransactionForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    sum = IntegerField("Sum", validators=[DataRequired()])
    type = SelectField(u'Type', choices=[('1', 'Income'), ('0', 'Loss')])
    description = StringField("Description")
    date = DateField("Date", validators=[DataRequired()])
    submit = SubmitField("Save")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")
