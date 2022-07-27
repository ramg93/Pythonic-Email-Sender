from email_sender_app import app, db
from flask import render_template, url_for, flash, redirect

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
from models import *
import forms

import pickle
import os
from email_functions import *

@app.route('/')
def base():
    return render_template('base.html')

# ***************************************************** Users **************************************************
@app.route('/users')
def users():
    users = models.User.query.all()
    return render_template('users.html', users=users)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
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
    return render_template('add_user.html', form=form)

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
        return render_template('edit_user.html', form=form, user_id=user_id)
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
        return render_template('delete_user.html', form=form, user_id=user_id)
    flash(f'User with id {user_id} does not exit')
    return redirect(url_for('users'))

# ***************************************************** Transactions **************************************************
@app.route('/transactions')
def transactions():
    transactions = models.Transaction.query.all()
    return render_template('transactions.html', transactions=transactions)

@app.route('/add_transaction/<int:user_id>', methods=['GET', 'POST'])
def add_transaction(user_id):
    form = forms.AddTransactionForm()
    if form.validate_on_submit():
        user = db.session.query(models.User).filter(models.User.id == user_id)[0]
        transaction = models.Transaction(transaction=form.transaction.data, 
                                user_id=user.id,
                                user=user
                                )
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added')
        return redirect(url_for('transactions_user', user_id = user_id))
    return render_template('add_transaction.html', form=form, user_id = user_id)

@app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    form = forms.AddTransactionForm()
    transaction = models.Transaction.query.get(transaction_id)
    user_id = transaction.user_id
    print(transaction)
    if transaction:
        if form.validate_on_submit():
            transaction.transaction = form.transaction.data

            db.session.commit()
            flash('Transaction updated')
            return redirect(url_for('transactions_user', user_id = user_id))
        form.transaction.data = transaction.transaction
        return render_template('edit_transaction.html',
                               form=form,
                               transaction_id=transaction_id,
                               user_id = user_id)
    flash(f'Transaction with id {transaction_id} does not exit')
    return redirect(url_for('transactions_user', user_id = user_id))

@app.route('/delete_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def delete_transaction(transaction_id):
    form = forms.DeleteForm()
    transaction = models.Transaction.query.get(transaction_id)
    user_id = transaction.user_id
    if transaction:
        if form.validate_on_submit():
            if form.submit.data:
                db.session.delete(transaction)
                db.session.commit()
                flash('Transaction deleted')
            return redirect(url_for('transactions_user',
                                    user_id = user_id))
        return render_template('delete_transaction.html',
                               form=form,
                               transaction_id=transaction_id,
                               user_id = user_id)
    flash(f'Transaction with id {transaction_id} does not exit')
    return redirect(url_for('transactions_user', user_id = user_id))

# ***************************************************** Transactions User *********************************************

@app.route('/transactions_user/<int:user_id>', methods=['GET', 'POST'])
def transactions_user(user_id):
    
    engine = create_engine("sqlite:///esa.db")
    
    Session = sessionmaker(bind = engine)
    session = Session()
    
    query = session.query(Transaction.transaction,
                     Transaction.created_at, Transaction.id).filter_by(
        user_id = user_id).statement

    df = pd.read_sql_query(query, engine)
    session.close()

    trxns, total_balance, avg_credit, avg_debit, monthly_summary, _ = df2Summary(df)
    
    transactions = models.Transaction.query.filter_by(user_id = user_id).all()
    user = models.User.query.get(user_id)
    name = user.name
    lastname = user.lastname
    print(trxns)
    
    return render_template('transaction_user.html',
                           name = name,
                           user_id = user_id,
                           lastname = lastname,
                           total_balance = total_balance,
                           avg_credit = avg_credit,
                           avg_debit = avg_debit,
                           monthly_summary = monthly_summary,
                           df = trxns,
                           transactions = transactions)

@app.route('/send_summary/<int:user_id>', methods=['GET', 'POST'])
def send_summary(user_id):
    user = models.User.query.get(user_id)
    credentials=pickle.load(open('secret_credentials.pkl','rb'))
    
    engine = create_engine("sqlite:///esa.db")
    
    Session = sessionmaker(bind = engine)
    session = Session()
    
    query = session.query(Transaction.transaction,
                     Transaction.created_at, Transaction.id).filter_by(
    user_id = user_id).statement

    df = pd.read_sql_query(query, engine)
    session.close()

    filename = f"Transactions_Summary_User_{user_id}.csv"
    df.to_csv(filename)
    print(filename)
    
    receiver_email = user.email
    trxns, total_balance, avg_credit, avg_debit, _, monthly_summary_email = df2Summary(df)
    message = createTrxnsSummaryMessage(total_balance, avg_credit, avg_debit, monthly_summary_email)
    response = sendEmailTLS(credentials, receiver_email, "Transactions Summary", message, filename)
    flash(response)
    os.remove(filename)
    return redirect(url_for('transactions_user', user_id = user_id))
