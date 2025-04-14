import unittest
import io
from unittest.mock import patch
from app import create_app, db  # Asume que tienes una factoría de aplicación
from app.routes import main  # o desde donde registras los blueprints

class UploadFileViewTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_upload_form(self):
        """Should return the upload HTML form"""
        response = self.client.get('/upload')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<form', response.data)

    def test_post_upload_no_file(self):
        """Should return 400 when no file is provided"""
        response = self.client.post('/upload', data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No file was uploaded', response.data)

    def test_post_upload_valid_csv(self):
        """Should return 200 and import transactions if CSV is valid"""
        valid_csv = io.BytesIO(
            b"transaction_id,amount,currency,locantion_country,timestamp,user_id,is_suspicious,reason\n"
            b"1000,120.00,USD,USA,2023-01-01 10:00:00,1,,\n"
        )
        data = {'file': (valid_csv, 'valid.csv')}
        response = self.client.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'transactions imported successfully', response.data)

    def test_post_upload_partial_success(self):
        """Should return 207 if some rows fail and some succeed"""
        mixed_csv = io.BytesIO(
            b"transaction_id,amount,currency,locantion_country,timestamp,user_id,is_suspicious,reason\n"
            b"1000,120.00,USD,USA,2023-01-01 10:00:00,1,,\n"
            b"2000,INVALID,USD,USA,2023-01-01 10:02:00,1,,\n"
        )
        data = {'file': (mixed_csv, 'mixed.csv')}
        response = self.client.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 207)
        self.assertIn(b'1 transactions imported. 1 rows failed.', response.data)

    def test_post_upload_raises_exception(self):
        """Should return 500 if an exception occurs during import"""
        invalid_csv = io.BytesIO(b"")  # Empty file

        with patch('app.routes.import_transactions_from_csv', side_effect=Exception("Simulated failure")):
            data = {'file': (invalid_csv, 'broken.csv')}
            response = self.client.post('/upload', data=data, content_type='multipart/form-data')
            self.assertEqual(response.status_code, 500)
            self.assertIn(b'Import failed: Simulated failure', response.data)
    
    @patch('app.routes.detect_fraudulent_transactions')
    def test_detect_fraud_success(self, mock_detect_fraudulent_transactions):
        """
        Test the /detect-fraud POST endpoint to ensure it detects and returns the correct count.
        """
        # Simulates that 5 suspicious transactions were detected
        mock_detect_fraudulent_transactions.return_value = 5

        response = self.client.post('/detect-fraud')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"5 suspicious transactions detected", response.data)

    def test_detect_fraud_invalid_method(self):
        """
        Ensure GET is not allowed on /detect-fraud.
        """
        response = self.client.get('/detect-fraud')
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    @patch('app.routes.forward_to_process_fraud')
    def test_simulate_task_queue_valid_payload(self, mock_forward):
        """
        Test /tasks endpoint with a valid payload.
        Should return 202 and dispatch the task.
        """
        payload = {
            "transaction_id": "1001",
            "user_id": 1,
            "date": "2025-04-11 15:00:00",
            "amount": 6000,
            "country": "US",
            "reason": "Test reason"
        }

        response = self.client.post('/tasks', json=payload)

        self.assertEqual(response.status_code, 202)
        self.assertIn(b"Task accepted", response.data)
        mock_forward.assert_called_once_with(payload)

    @patch('app.routes.save_suspicious_transactions')
    def test_process_fraud_valid_payload(self, mock_save):
        """
        Test /process-fraud with valid fraud data.
        """
        payload = {
            "transaction_id": "1002",
            "user_id": 2,
            "date": "2025-04-11 14:45:00",
            "amount": 5100,
            "country": "BR",
            "reason": "High-value transaction"
        }

        mock_save.return_value = "Suspicious transaction saved"

        response = self.client.post('/process-fraud', json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Suspicious transaction saved", response.data)
        mock_save.assert_called_once_with(payload)

    def test_process_fraud_no_json(self):
        """
        Test /process-fraud with no JSON payload.
        Should return 200 with no crash.
        """
        response = self.client.post('/process-fraud', json={})

        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
