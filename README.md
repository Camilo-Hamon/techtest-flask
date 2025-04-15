# 🕵️‍♂️ Flask Fraud Detection API

This project is an API built with **Flask** for managing financial transactions, with an integrated **fraud detection** system. It also allows importing data from CSV files and simulates task queues similar to Google Cloud Tasks.

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
- ✅ Unit tests with `unittest`

---

## ⚙️ 🚀 Deploy with Docker (option 1)

### 1. Build the Docker Image

```bash
docker build . -t image-technical-test
```
### 2. Run the Docker Container

```bash
docker run -d --name ct-technical-test -p 8080:8080 \  
    -e FLASK_ENV=development \  
    -e SECRET_KEY=technicaltest2025 \  
    -e DATABASE_URL=sqlite:///app.db \  
    image-technical-test
```

### 🧾 Docker Run Command Explanation

| Argument                       | Description                                                                 |
|-------------------------------|-----------------------------------------------------------------------------|
| `-d`                          | Runs the container in **detached mode** (in the background).               |
| `--name ct-technical-test`    | Names the container **ct-technical-test**.                                 |
| `-p 8080:8080`                | Maps port **8080** on your machine to port **8080** in the container.       |
| `-e`                          | Sets **environment variables** needed for the Flask app to run.            |
| `image-technical-test`        | The name of the **Docker image** built in the previous step.               |


### Stopping the Container

```bash
docker stop ct-technical-test && docker rm ct-technical-test
```

## ⚙️ Local Installation (option 2)

### 1. Clone the repository

```bash
git clone https://github.com/Camilo-Hamon/techtest-flask.git
cd techtest-flask
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


## 📬 How to Use the API Endpoints with Postman

This section explains how to interact with the main API endpoints of the project using [Postman](https://www.postman.com/).

⚙️ Main Endpoints

| Method | Path          | Description                                    |
|--------|---------------|------------------------------------------------|
| POST   | /upload       | Upload CSV file with transactions.         |
| POST   | /detect-fraud | Trigger detection of suspicious transactions. |
| POST   | /tasks        | Simulate asynchronous task execution.        |
| POST   | /process-fraud| Process and save transactions marked as suspicious. |

---

### 📤 `/upload` – Upload CSV File

**Method**: `POST`  
**URL**: `http://localhost:8080/upload`  
**Description**: Allows you to upload a CSV file containing transactions to be imported into the database.

#### 🔧 Postman Setup

1. Open Postman and create a new request.
2. Set the method to `POST` and enter the URL: `http://localhost:8080/upload`.
3. Go to the **Body** tab.
4. Choose **form-data**.
5. Add a key named `file`, set its type to **File**, and upload your CSV file.
6. Click **Send**.

#### ✅ Expected Response

- `200 OK` if all transactions were successfully imported.
- `207 Multi-Status` if some rows failed and others succeeded.
- `400 Bad Request` if no file is sent.
- `500 Internal Server Error` if something goes wrong during processing.

---

### 🕵️‍♀️ `/detect-fraud` – Detect Fraudulent Transactions

**Method**: `POST`  
**URL**: `http://localhost:8080/detect-fraud`  
**Description**: Triggers fraud detection on all stored transactions based on predefined rules.

#### 🔧 Postman Setup

1. Open Postman and create a new request.
2. Set the method to `POST` and enter the URL: `http://localhost:8080/detect-fraud`.
3. No body is needed for this request.
4. Click **Send**.

#### ✅ Expected Response

- `200 OK` with a JSON response like:
  ```json
  {
    "message": "5 suspicious transactions detected."
  }

---

## ⚙️ Deployment on Google Cloud Run

### Configure GCP

```bash
gcloud config set project TU_ID_PROYECTO
gcloud config set run/region us-central1
gcloud services enable run.googleapis.com artifactregistry.googleapis.com
```
### Create Docker repository on GCP

```bash
gcloud artifacts repositories create my-repo \
    --repository-format=docker \
    --location=us-central1
```

### Build and upload image

```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/TU_ID_PROYECTO/my-repo/flask-app
```

### Deploy to Cloud Run

```bash
gcloud run deploy flask-app \
  --image us-central1-docker.pkg.dev/TU_ID_PROYECTO/my-repo/flask-app \
  --platform managed \
  --allow-unauthenticated \
  --region us-central1

```

### Update environment variables (if applicable)

```bash
gcloud run services update flask-app \
  --update-env-vars DATABASE_URL="..."
```
