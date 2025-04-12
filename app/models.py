from datetime import datetime

from . import db

class User(db.Model):
    """
    User model representing an account in the system.

    Each user can have multiple transactions associated with them.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Relationship to transactions
    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

class Transaction(db.Model):
    """
    Transaction model representing a financial transaction.

    Each transaction is linked to a specific user.
    """
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    category = db.Column(db.String(100), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    transaction_type = db.Column(db.String(20), nullable=True)  # "income" or "expense"
    currency = db.Column(db.String(10), nullable=True, default="USD")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<Transaction {self.id} - {self.description}>"
