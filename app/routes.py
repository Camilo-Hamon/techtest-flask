from flask import Blueprint, render_template, request

from io import TextIOWrapper

import csv

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
          and prints each row to the console.

    Returns:
        - If GET: Renders the 'upload.html' template with the upload form.
        - If POST:
            - 400 Bad Request if no file is uploaded.
            - 200 OK if file is successfully processed.
    """
    if request.method == 'POST':
        # Attempt to retrieve the uploaded file from the form field named 'file'
        file = request.files.get('file')

        if not file:
            # No file was uploaded or field was empty
            return "No file was uploaded", 400

        # Wrap the uploaded file in a TextIOWrapper to treat it as a text stream
        # This is necessary because Flask handles uploaded files as binary streams
        wrapped_file = TextIOWrapper(file, encoding='utf-8')

        # Use Python's built-in CSV reader to iterate over the rows
        reader = csv.reader(wrapped_file)

        print("CSV file content:")
        for row in reader:
            print(row)  # Print each row to the server console

        return "File received and processed successfully", 200

    # For GET requests, show the upload form
    return render_template('upload.html')
