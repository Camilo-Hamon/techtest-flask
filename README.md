# 🕵️‍♂️ Flask Fraud Detection API

his project is an API built with **Flask** for managing financial transactions, with an integrated **fraud detection** system. It also allows importing data from CSV files and simulates task queues similar to Google Cloud Tasks.

---

## 🚀 Main Features

- ✅ Transaction import from CSV files
- ✅ Automatic association of transactions to users
- ✅ Fraud detection rules:
  - More than 3 transactions in less than 1 minute
  - Transaction greater than $5000
  - Transactions from different countries in less than 5 minutes
- ✅ Google Cloud Tasks simulation
- ✅ REST API to trigger and process fraud detection
- ✅ Support for deployment on **Google Cloud Run**
- ✅ Centralized logger
- ✅ Unit tests with `unittest` + `Flask test client`

---

## ⚙️ Local Installation

### 1. Clone the repository

```bash
git clone https://github.com/tuusuario/flask-fraud-api.git
cd flask-fraud-api
```


### 2. Create virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create .env file in the program's path with the following variables
FLASK_ENV=development
SECRET_KEY=technicaltest2025
DATABASE_URL=sqlite:///app.db

### 4. Run the application
```bash
python run.py
```

---

## ⚙️ Main Endpoints
Method	Path	        Description
POST	/upload	        Upload CSV file
POST	/detect-fraud	Detect suspicious transactions
POST	/tasks	        Simulate Google Cloud Task
POST	/process-fraud	Process and save a suspicious transaction