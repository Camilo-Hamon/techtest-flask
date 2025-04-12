# app/services/transaction_importer.py
from ..models import Transaction
from ..models import User
from ..utils.logger import logger
from .. import db

from datetime import datetime
import csv

def validate_transaction_row(row):
    required_fields = ['date', 'description', 'amount']

    for field in required_fields:
        if not row.get(field):
            return False, f"Missing required field: {field}"

    try:
        float(row['amount'])
    except ValueError:
        return False, f"Invalid amount value: {row['amount']}"

    # Validate transaction_type
    if row.get('transaction_type') and row['transaction_type'] not in ['income', 'expense']:
        return False, f"Invalid transaction_type: {row['transaction_type']}"

    # Validate date format
    try:
        datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')  # Example: 2024-12-31
    except ValueError:
        return False, f"Invalid date format: {row['date']} (expected YYYY-MM-DD HH:MM:SS)"

    return True, None

def import_transactions_from_csv(file_stream):
    """
    Parses a CSV file with transactions for multiple users, validates and stores them in the database.
    If a user doesn't exist, it creates the user on-the-fly using the user_id from each row.

    Args:
        file_stream (file-like object): The uploaded CSV file stream.

    Returns:
        tuple:
            - int: Number of successfully imported transactions.
            - list: Error logs in the format [(row_number, error_message, row_data)].
    """
    reader = csv.DictReader(file_stream)
    transactions = []
    error_logs = []
    known_users = {}  # Cache of user_id to avoid duplicate DB checks

    for idx, row in enumerate(reader, start=1):
        # Validate row
        is_valid, error_msg = validate_transaction_row(row)

        if not is_valid:
            logger.warning(f"[Row {idx}] {error_msg} — Data: {row}")
            error_logs.append((idx, error_msg, row))
            continue

        try:
            user_id = int(row['user_id'])

            # Check if user is already known/created in this session
            if user_id not in known_users:
                user = db.session.get(User, user_id)
                if not user:
                    user = User(
                        id=user_id,
                        username=f"user{user_id}",
                        email=f"user{user_id}@example.com"
                    )
                    db.session.add(user)
                    logger.info(f"Created new user with id {user_id}")
                known_users[user_id] = user  # Cache user

            date_str = row['date']
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

            # Create transaction
            transaction = Transaction(
                date=parsed_date,
                description=row['description'],
                amount=float(row['amount']),
                category=row.get('category'),
                payment_method=row.get('payment_method'),
                transaction_type=row.get('transaction_type'),
                currency=row.get('currency', 'USD'),
                location_country=row.get('location_country'),
                user_id=user_id
            )
            transactions.append(transaction)

        except Exception as e:
            msg = f"Unexpected error: {e}"
            logger.error(f"[Row {idx}] {msg} — Data: {row}")
            error_logs.append((idx, msg, row))

    try:
        db.session.add_all(transactions)
        db.session.commit()
        return len(transactions), error_logs

    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Database commit failed: {e}")