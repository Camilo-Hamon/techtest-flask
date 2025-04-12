from .services.transaction_importer import import_transactions_from_csv

from flask import Blueprint, render_template, request

from io import TextIOWrapper

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