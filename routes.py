from email_sender_app import app, db
from flask import render_template, url_for, flash, redirect

import models
from models import *
import forms

@app.route('/')
def base():
    return render_template('base.html')

# ***************************************************** Users **************************************************
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

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    form = forms.AddUserForm()
    user = models.User.query.get(user_id)
    print(user)
    if user:
        if form.validate_on_submit():
            user.name = form.name.data
            user.lastname = form.lastname.data
            user.email = form. email.data

            db.session.commit()
            flash('User updated')
            return redirect(url_for('users'))
        
        form.name.data = user.name
        form.lastname.data = user.lastname
        form.email.data = user.email
        return render_template('edituser.html', form=form, user_id=user_id)
    flash(f'User with id {user_id} does not exit')
    return redirect(url_for('users'))


@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    form = forms.DeleteForm()
    user = models.User.query.get(user_id)
    if user:
        if form.validate_on_submit():
            if form.submit.data:
                db.session.delete(user)
                db.session.commit()
                flash('User deleted')
            return redirect(url_for('users'))
        return render_template('deleteuser.html', form=form, user_id=user_id)
    flash(f'User with id {user_id} does not exit')
    return redirect(url_for('users'))

# ***************************************************** Transactions **************************************************
@app.route('/transactions')
def transactions():
    transactions = models.Transaction.query.all()
    return render_template('transactions.html', transactions=transactions)

@app.route('/addtransaction', methods=['GET', 'POST'])
def addtransaction():
    form = forms.AddTransactionForm()
    if form.validate_on_submit():
        user = db.session.query(models.User).filter(models.User.id == form.user.data)[0]
        transaction = models.Transaction(transaction=form.transaction.data, 
                                user_id=user.id,
                                user=user
                                )
# add code to determine university id
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added')
        return redirect(url_for('transactions'))
    return render_template('addtransaction.html', form=form)

@app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    form = forms.AddTransactionForm()
    transaction = models.Transaction.query.get(transaction_id)
    print(transaction)
    if transaction:
        if form.validate_on_submit():
            user = db.session.query(models.User).filter(models.User.id == form.user.data)[0]
            transaction.transaction = form.transaction.data
            transaction.user = user
            transaction.user_id = user.id

            db.session.commit()
            flash('Transaction updated')
            return redirect(url_for('transactions'))
        form.transaction.data = transaction.transaction
        form.user.data = transaction.user.id
        return render_template('edittransaction.html', form=form, transaction_id=transaction_id)
    flash(f'Transaction with id {transaction_id} does not exit')
    return redirect(url_for('transaction'))

@app.route('/delete_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def delete_transaction(transaction_id):
    form = forms.DeleteForm()
    transaction = models.Transaction.query.get(transaction_id)
    if transaction:
        if form.validate_on_submit():
            if form.submit.data:
                db.session.delete(transaction)
                db.session.commit()
                flash('Transaction deleted')
            return redirect(url_for('transactions'))
        return render_template('deletetransaction.html', form=form, transaction_id=transaction_id)
    flash(f'Transaction with id {transaction_id} does not exit')
    return redirect(url_for('transactions'))
