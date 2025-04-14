# app/services/transaction_importer.py
from ..models import Transaction
from ..models import User
from ..utils.logger import logger
from .. import db

from datetime import datetime
import csv


def validate_transaction_row(row):
    """
    Validates a dictionary representing a transaction row from a CSV file.

    This function ensures that required fields are present, that the `amount` is a valid number,
    and that the `date` field matches the expected datetime format.

    Parameters:
    ----------
    row : dict
        A dictionary representing a single transaction row, typically parsed from a CSV file.

    Returns:
    -------
    tuple
        A tuple in the form (is_valid, error_message). 
        - If the row is valid, returns (True, None).
        - If invalid, returns (False, error_message) with a description of the validation issue.

    Expected Fields:
    ----------------
    - 'transaction_id' : str or int
    - 'user_id'        : str or int
    - 'amount'         : float-compatible string
    - 'currency'       : string
    - 'timestamp'      : string in format '%Y-%m-%d %H:%M:%S'
    """

    required_fields = ['transaction_id', 'user_id',
                       'amount', 'currency', 'timestamp']

    # Check required fields are present and not empty
    for field in required_fields:
        if not row.get(field):
            return False, f"Missing required field: {field}"

    # Validate amount is a number
    try:
        float(row['amount'])
    except ValueError:
        return False, f"Invalid amount value: {row['amount']}"

    # Validate timestamp format
    try:
        datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return False, f"Invalid timestamp format: {row['timestamp']} (expected YYYY-MM-DD HH:MM:SS)"

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
            date_str = row['timestamp']
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

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

            # Create transaction
            transaction = Transaction(
                transaction_id=float(row['transaction_id']),
                user_id=user_id,
                amount=float(row['amount']),
                currency=row.get('currency', 'USD'),
                location_country=row.get('country'),
                date=parsed_date,
                is_suspicious=bool(row['is_suspicious']),
                reason=row.get('reason')
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
