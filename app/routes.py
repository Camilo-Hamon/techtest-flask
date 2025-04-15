from .services.transaction_importer import import_transactions_from_csv
from .services.fraud_detector import detect_fraudulent_transactions
from .services.fraud_detector import forward_to_process_fraud
from .services.fraud_detector import save_suspicious_transactions

from flask import Blueprint, render_template, request, jsonify

from io import TextIOWrapper

from concurrent.futures import ThreadPoolExecutor
#ThreadPoolExecutor implementar

main = Blueprint('main', __name__)
executor = ThreadPoolExecutor(max_workers=5)

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

        try:
            success_count, error_rows = import_transactions_from_csv(wrapped_file)

            if error_rows:
                error_msg = f"{success_count} transactions imported. {len(error_rows)} rows failed."
                print("Errors found:")
                for i, err, row in error_rows:
                    print(f"Row {i}: {err} — {row}")
                return error_msg, 207  # 207: Multi-Status (partially success)
            
            return f"{success_count} transactions imported successfully!", 200

        except Exception as e:
            return f"Import failed: {e}", 500

    return render_template('upload.html')


@main.route('/detect-fraud', methods=['GET'])
def detect_fraud_get():
    """
    Renders a simple page with a button to manually trigger fraud detection.
    """
    return render_template('detect_fraud.html')


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
        return jsonify({"error": "Invalid payload"}), 415

    # Dispatch asynchronously
    executor.submit(forward_to_process_fraud, data)

    return jsonify({"message": "Task accepted and will be processed"}), 202


@main.route('/process-fraud', methods=['POST'])
def process_fraud():
    """
    Endpoint to process a fraudulent transaction that was enqueued via the task queue.

    This endpoint expects a JSON payload with at least the following fields:
    - transaction_id (str or int)
    - user_id (str or int)
    - reason (str)
    - date (str, format 'YYYY-MM-DD HH:MM:SS')

    Returns:
        - 200 OK if the transaction was successfully saved.
        - 400 Bad Request if the payload is missing or incomplete.
        - 500 Internal Server Error if saving fails due to an unexpected error.
    """
    data = request.get_json()

    # Check if any data was received
    if not data:
        return jsonify({"error": "No data received"}), 200

    # Required fields for a suspicious transaction
    required_fields = ['transaction_id', 'user_id', 'reason', 'date']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    try:
        message = save_suspicious_transactions(data)
        print(message)
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to process fraud: {str(e)}"}), 500
