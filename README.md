# 🕵️‍♂️ Flask Fraud Detection API

Este proyecto es una API construida con **Flask** para la gestión de transacciones financieras, con un sistema integrado de **detección de fraudes**. También permite importar datos desde archivos CSV y simula colas de tareas similares a Google Cloud Tasks.

---

## 📁 Estructura del Proyecto

project-root/
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   ├── services/
│   ├── fraud_detector.py
│   ├── transaction_importer.py
│   ├── utils/
│   ├── logger.py
├── requirements.txt             # Librerías necesarias
├── Dockerfile                   # Instrucciones para construir la imagen
├── .dockerignore                # Archivos que no se deben copiar al contenedor
├── run.py                      # Punto de entrada a la app
├── tests/ 
│   ├── __init__.py
│   ├── test_views.py
├── .gitignore
├── .env                      # variables de entorno

## 🚀 Características principales

- ✅ Importación de transacciones desde archivos CSV
- ✅ Asociación automática de transacciones a usuarios
- ✅ Reglas de detección de fraude:
  - Más de 3 transacciones en menos de 1 minuto
  - Transacción mayor a $5000
  - Transacciones desde países distintos en menos de 5 minutos
- ✅ Simulación de Google Cloud Tasks
- ✅ API REST para disparar y procesar detección de fraude
- ✅ Soporte para despliegue en **Google Cloud Run**
- ✅ Logger centralizado
- ✅ Pruebas unitarias con `unittest` + `Flask test client`

---

## ⚙️ Instalación local

### 1. Clonar el repositorio

```bash
git clone https://github.com/tuusuario/flask-fraud-api.git
cd flask-fraud-api

### 2. Crear entorno virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

### 3. Crear archivo .env en la ruta del programa con las siguientes variables
FLASK_ENV=development
SECRET_KEY=technicaltest2025
DATABASE_URL=sqlite:///app.db

### 4. Ejecuta la aplicacion
```bash
python run.py