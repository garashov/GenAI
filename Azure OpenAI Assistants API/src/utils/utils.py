import os
from src.logging import logging

def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
        logging.info(f"Directory '{path}' created successfully.")
    else:
        logging.info(f"Directory '{path}' already exists.")
