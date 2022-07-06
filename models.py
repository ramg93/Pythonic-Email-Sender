from email_sender_app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.Date, nullable = False, default=datetime.utcnow())
    name = db.Column(db.String(255), nullable = False)
    lastname = db.Column(db.String(255), nullable = False)
    email = db.Column(db.String(255), nullable = False)
    # relationships 
    transactions = db.relationship('Transaction', back_populates='user', cascade="all,delete")# one2many
    
    def __repr__(self):
        return f'id = {self.id}: {self.name} {self.lastname}, {self.created_at}'


class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.Date, nullable = False, default=datetime.utcnow())
    transaction = db.Column(db.String(255), nullable = False)
    # relationships
    user_id = db.Column(db.Integer,  db.ForeignKey("user.id"))# many2one
    user = db.relationship("User", back_populates="transactions")
    
    def __repr__(self):
        return f'id = {self.id}: {self.name}, {self.created_at}'
