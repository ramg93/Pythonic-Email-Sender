from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email


class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')


class AddUserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')
    

class AddTransactionForm(FlaskForm):
    transaction = StringField('Transaction', validators=[DataRequired()])
    submit = SubmitField('Submit')
