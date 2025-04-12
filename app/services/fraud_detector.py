# services/fraud_detector.py

from datetime import datetime, timedelta
from collections import defaultdict
from ..models import Transaction, SuspiciousTransaction
from .. import db

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

        # Rule 2: Large amount
        if amount > 5000:
            flagged.append(SuspiciousTransaction(
                transaction_id=tx.id,
                user_id=user_id,
                reason="Transaction amount exceeds $5000"
            ))

        # Rule 3: Different countries within 5 minutes
        for prev_time, prev_country, _ in user_activity[user_id]:
            if prev_country != country and abs((timestamp - prev_time).total_seconds()) <= 300:
                flagged.append(SuspiciousTransaction(
                    transaction_id=tx.id,
                    user_id=user_id,
                    reason="Transactions from different countries within 5 minutes"
                ))
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
