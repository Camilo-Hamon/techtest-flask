# app/utils/logger.py

import logging
import os

# Create logs directory if not exists
os.makedirs('logs', exist_ok=True)

# Set up the logger
logger = logging.getLogger('transaction_importer')
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler('logs/transaction_import.log')
file_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger (only once)
if not logger.hasHandlers():
    logger.addHandler(file_handler)
