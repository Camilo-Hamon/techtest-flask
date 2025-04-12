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
    transactions = Transaction.query.order_by(Transaction.user_id, Transaction.date).all()

    user_activity = defaultdict(list)
    flagged = []

    for tx in transactions:
        user_id = tx.user_id
        #timestamp = datetime.strptime(tx.date, '%Y-%m-%d %H:%M:%S')  # Ensure datetime format
        timestamp = tx.date
        amount = tx.amount
        country = tx.location_country or "Unknown"

        # Add to user history
        user_activity[user_id].append((timestamp, country, tx))

        # Rule 1: High frequency (more than 3 in 1 minute)
        recent_tx = [t for t in user_activity[user_id] if timestamp - t[0] <= timedelta(minutes=1)]
        if len(recent_tx) > 3:
            flagged.append(SuspiciousTransaction(
                transaction_id=tx.id,
                user_id=user_id,
                reason="More than 3 transactions in under 1 minute"
            ))
            enqueue_fraud_simulated(tx.id, "More than 3 transactions in under 1 minute")

        # Rule 2: Large amount
        if amount > 5000:
            flagged.append(SuspiciousTransaction(
                transaction_id=tx.id,
                user_id=user_id,
                reason="Transaction amount exceeds $5000"
            ))
            enqueue_fraud_simulated(tx.id, "Transaction amount exceeds $5000")

        # Rule 3: Different countries within 5 minutes
        for prev_time, prev_country, _ in user_activity[user_id]:
            if prev_country != country and abs((timestamp - prev_time).total_seconds()) <= 300:
                flagged.append(SuspiciousTransaction(
                    transaction_id=tx.id,
                    user_id=user_id,
                    reason="Transactions from different countries within 5 minutes"
                ))
                enqueue_fraud_simulated(tx.id, "Transactions from different countries within 5 minutes")
                break

    # Store unique flagged transactions
    for suspicion in flagged:
        already_flagged = SuspiciousTransaction.query.filter_by(
            transaction_id=suspicion.transaction_id,
            reason=suspicion.reason
        ).first()

        if not already_flagged:
            db.session.add(suspicion)

    db.session.commit()
    return len(flagged)

def enqueue_fraud_simulated(transaction_id, reason):
    payload = {
        "transaction_id": transaction_id,
        "reason": reason
    }

    try:
        response = requests.post("http://localhost:5000/tasks", json=payload)
        status_code = response.status_code

        # Log success
        logger.info(f"Enqueued task | Transaction ID: {transaction_id} | Reason: {reason} | Status: {status_code}")
        print(f"[Task Enqueued] Status: {status_code} - Payload: {payload}")



    except Exception as e:
        # Log failure
        logger.error(f"Failed to enqueue task | Transaction ID: {transaction_id} | Reason: {reason} | Error: {e}")
        print(f"[Task Enqueue Error] Failed to simulate task: {e}")