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


# @app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
# def edit_college(college_id):
#     form = forms.AddCollegeForm()
#     college = models.College.query.get(college_id)
#     print(college)
#     if college:
#         if form.validate_on_submit():
#             university = db.session.query(models.University).filter(models.University.name == form.university.data)[0]
#             college.name = form.name.data
#             college.acronym = form.acronym.data
#             college.address = form. address.data
#             college.location = form.location.data
#             college.university = university
#             college.university_id = university.id

#             db.session.commit()
#             flash('College updated')
#             return redirect(url_for('colleges'))
#         form.name.data = college.name
#         form.acronym.data = college.acronym
#         form.university.data = college.university.name
#         form.address.data = college.address
#         form.location.data = college.location
#         return render_template('edit/edit_college.html', form=form, college_id=college_id)
#     flash(f'College with id {college_id} does not exit')
#     return redirect(url_for('colleges'))


# @app.route('/delete_transaction/<int:transaction_id>', methods=['GET', 'POST'])
# def delete_college(college_id):
#     form = forms.DeleteForm()
#     college = models.College.query.get(college_id)
#     if college:
#         if form.validate_on_submit():
#             if form.submit.data:
#                 db.session.delete(college)
#                 db.session.commit()
#                 flash('College deleted')
#             return redirect(url_for('colleges'))
#         return render_template('delete/delete_college.html', form=form, college_id=college_id, acronym=college.acronym)
#     flash(f'College with id {college_id} does not exit')
#     return redirect(url_for('colleges'))
