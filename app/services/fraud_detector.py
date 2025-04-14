# services/fraud_detector.py

from datetime import datetime, timedelta
from collections import defaultdict
from ..models import Transaction, SuspiciousTransaction
from .. import db
from ..utils.logger import logger

import requests


def detect_fraudulent_transactions():
    """
    Detects fraudulent transactions based on multiple rules:
    1. More than 3 purchases in less than 1 minute by the same user.
    2. Purchases greater than $5000.
    3. Transactions from different countries in less than 5 minutes.

    Stores suspicious transactions in a separate table with the reason.
    """
    transactions = Transaction.query.order_by(
        Transaction.user_id, Transaction.date).all()

    user_activity = defaultdict(list)
    count = 0

    for tx in transactions:

        user_id = tx.user_id
        transaction_id = tx.transaction_id
        timestamp = tx.date
        amount = tx.amount
        country = tx.location_country or "Unknown"

        # Add to user history
        user_activity[user_id].append((timestamp, country, tx))

        # Rule 1: High frequency (more than 3 in 1 minute)
        recent_tx = get_recent_transactions(user_id, timestamp, user_activity)
        # recent_tx = [t for t in user_activity[user_id] if timestamp - t[0] <= timedelta(minutes=1)]
        if len(recent_tx) >= 3:
            count += 1

            enqueue_fraud_simulated({
                "user_id": user_id,
                "transaction_id": transaction_id,
                "date": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "amount": amount,
                "country": country,
                "reason": "More than 3 transactions in under 1 minute"
            })

        # Rule 2: Large amount
        if amount > 5000:
            count += 1

            enqueue_fraud_simulated({
                "user_id": user_id,
                "transaction_id": transaction_id,
                "date": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "amount": amount,
                "country": country,
                "reason": "Transaction amount exceeds $5000"
            })

        # Rule 3: Different countries within 5 minutes
        for prev_time, prev_country, _ in user_activity[user_id]:
            if prev_country != country and abs((timestamp - prev_time).total_seconds()) <= 300:
                count += 1

                enqueue_fraud_simulated({
                    "user_id": user_id,
                    "transaction_id": transaction_id,
                    "date": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    "amount": amount,
                    "country": country,
                    "reason": "Transactions from different countries within 5 minutes"
                })
                break

    return count


def enqueue_fraud_simulated(data_suspicious_transaction):

    try:
        # Update the original transaction record
        transaction = Transaction.query.get(
            data_suspicious_transaction["transaction_id"])
        if transaction:
            transaction.is_suspicious = True
            if (len(transaction.reason) > 0):
                if (data_suspicious_transaction["reason"] in transaction.reason):
                    pass
                else:
                    transaction.reason = transaction.reason + \
                        " // "+data_suspicious_transaction["reason"]
            else:
                transaction.reason = data_suspicious_transaction["reason"]

        # Commit changes to the database
        db.session.commit()

        response = requests.post(
            "http://localhost:5000/tasks", json=data_suspicious_transaction)
        status_code = response.status_code

        # Log success
        logger.info("Enqueued task | Transaction ID: "+str(
            data_suspicious_transaction["transaction_id"])+" | Reason: "+data_suspicious_transaction["reason"]+f" | Status: {status_code}")
        print(
            "[Task Enqueued] Status: {status_code} - Payload: "+str(data_suspicious_transaction))

    except Exception as e:
        # Log failure
        logger.error("Failed to enqueue task | Transaction ID: "+str(
            data_suspicious_transaction["transaction_id"])+" | Reason: "+data_suspicious_transaction["reason"]+f" | Error: {e}")
        print(f"[Task Enqueue Error] Failed to simulate task: {e}")


def forward_to_process_fraud(data):
    """
    Sends the task payload to the /process-fraud endpoint asynchronously.
    """
    try:
        response = requests.post(
            "http://localhost:5000/process-fraud", json=data)
        logger.info(
            f"Task dispatched to /process-fraud | Status: {response.status_code} | Data: {data}")
        print(f"Task dispatched to /process-fraud: {data}")
    except Exception as e:
        logger.error(
            f"Failed to forward task to /process-fraud | Error: {e} | Data: {data}")
        print(f"Failed to forward task: {e}")


def save_suspicious_transactions(data_suspicious_transaction):
    """
    Saves a suspicious transaction to the database if it does not already exist.

    This function checks whether a transaction with the same transaction ID and reason
    already exists in the 'SuspiciousTransaction' table. If it doesn't, it adds the 
    transaction to the database and logs the action. 

    Args:
        data_suspicious_transaction (SuspiciousTransaction): 
            An object containing details of the suspicious transaction to be stored.

    Returns:
        return: message
    """

    message = ""

    date_str = data_suspicious_transaction['date']
    parsed_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

    # Check if the suspicious transaction with the same ID and reason already exists
    already_flagged = SuspiciousTransaction.query.filter_by(
        transaction_id=data_suspicious_transaction["transaction_id"],
        reason=data_suspicious_transaction["reason"]
    ).first()

    # If not already stored, add it to the database
    if not already_flagged:

        db.session.add(SuspiciousTransaction(
            transaction_id=data_suspicious_transaction["transaction_id"],
            user_id=data_suspicious_transaction["user_id"],
            reason=data_suspicious_transaction["reason"],
            timestamp=parsed_date
        ))

        message = "Suspicious transaction saved - Transaction ID: " + \
            str(data_suspicious_transaction["transaction_id"]) + \
            ", Reason: "+data_suspicious_transaction["reason"]+""

        # Log the save action
        logger.info(
            message
        )
    else:
        message = "Suspicious transaction already in database - Transaction ID: " + \
            str(data_suspicious_transaction["transaction_id"])

    # Commit changes to the database
    db.session.commit()
    return message


def get_recent_transactions(user_id, current_timestamp, user_activity):
    """
    Retrieves the list of transactions for a given user that occurred within the last minute
    relative to the current transaction timestamp.

    Args:
        user_id (int): The ID of the user whose transactions are being checked.
        current_timestamp (datetime): The timestamp of the current transaction being evaluated.
        user_activity (dict): A dictionary mapping user IDs to a list of past transactions.
                              Each transaction is expected to be a tuple where the first element is a datetime object.

    Returns:
        List[Tuple]: A list of transaction tuples that occurred within the last 60 seconds.
    """
    # Get all past transactions for the user
    previous_transactions = user_activity.get(user_id, [])

    # Filter and return only those within the last 1 minute
    recent_transactions = [
        tx for tx in previous_transactions
        if (current_timestamp - tx[0]) <= timedelta(minutes=1)
    ]

    return recent_transactions
