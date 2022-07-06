from email_sender_app import app, db
from flask import render_template, url_for, flash, redirect

import models
from models import *
import forms

@app.route('/')
def base():
    return render_template('base.html')

@app.route('/users')
def users():
    users = models.User.query.all()
    return render_template('users.html', users=users)

@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    form = forms.AddUserForm()
    if form.validate_on_submit():
        user = models.User(name=form.name.data,
                           lastname=form.lastname.data,
                           email=form.email.data
                                )
        db.session.add(user)
        db.session.commit()
        flash('User added')
        return redirect(url_for('users'))
    return render_template('adduser.html', form=form)


@app.route('/transactions/<int:user_id>', methods=['POST','GET'])
def transactions(user_id):
    transactions = models.Transaction.query.filter_by(user_id = user_id)
    print(transactions)
    if transactions.first() == 0:
        flash(f'The User with ID {user_id} has no transactions to show.')
        return redirect(url_for('users'))
    
    return render_template('transactions.html')
