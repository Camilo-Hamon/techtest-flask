from .services.transaction_importer import import_transactions_from_csv
from .services.fraud_detector import detect_fraudulent_transactions

from flask import Blueprint, render_template, request, jsonify

from io import TextIOWrapper

import threading
import requests

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')


@main.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """
    Handles CSV file upload via a POST request.

    GET: Renders a simple HTML form to upload a CSV file.
    POST: Processes the uploaded file, reads its content using the csv module,
          parses its content, and stores each transaction in the database.
          Expected CSV columns:
          date, description, amount, category, payment_method, transaction_type, currency

    Returns:
        - If GET: Renders the 'upload.html' template with the upload form.
        - If POST:
            - 400 Bad Request if no file is uploaded.
            - 200 OK if file is successfully processed.
    """
    if request.method == 'POST':
        file = request.files.get('file')

        if not file:
            return "No file was uploaded", 400

        wrapped_file = TextIOWrapper(file, encoding='utf-8')
        user_id = 1  # Temporal

        try:
            success_count, error_rows = import_transactions_from_csv(wrapped_file)

            if error_rows:
                error_msg = f"{success_count} transactions imported. {len(error_rows)} rows failed."
                print("Errores encontrados:")
                for i, err, row in error_rows:
                    print(f"Row {i}: {err} — {row}")
                return error_msg, 207  # 207: Multi-Status (partially success)
            
            return f"{success_count} transactions imported successfully!", 200

        except Exception as e:
            return f"Import failed: {e}", 500

    return render_template('upload.html')

@main.route('/detect-fraud', methods=['POST'])
def detect_fraud():
    """
    Endpoint to detect fraudulent transactions based on pre-defined rules.
    Saves suspicious transactions in the SuspiciousTransaction table.

    Returns:
        JSON: Number of suspicious transactions detected.
    """
    count = detect_fraudulent_transactions()
    return {"message": f"{count} suspicious transactions detected."}, 200

@main.route('/tasks', methods=['POST'])
def simulate_task_queue():
    """
    Simulates Google Cloud Task delivery by receiving the task payload and 
    dispatching it asynchronously to the real processing endpoint (/process-fraud).
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid payload"}), 400

    # Dispatch asynchronously
    thread = threading.Thread(target=forward_to_process_fraud, args=(data,))
    thread.start()

    return jsonify({"message": "Task accepted and will be processed"}), 202

def forward_to_process_fraud(data):
    """
    Sends the task payload to the /process-fraud endpoint asynchronously.
    """
    try:
        requests.post("http://localhost:5000/process-fraud", json=data)
        print(f"Task dispatched to /process-fraud: {data}")
    except Exception as e:
        print(f"Failed to forward task: {e}")


@main.route('/process-fraud', methods=['POST'])
def process_fraud():
    """
    Endpoint to process a fraudulent transaction that was enqueued via the task queue.
    """
    data = request.get_json()
    transaction_id = data.get('transaction_id')
    reason = data.get('reason')

    print(f"🚨 Processing fraud case: Transaction {transaction_id} - Reason: {reason}")
    # Aquí puedes extender la lógica para alertas, auditorías, etc.

    return '', 200
