# src/tools/get_information_from_url.py
import requests
from src.logs.logger import Logger
logger = Logger(__name__)

def get_information_from_url_impl(url: str):
    url_to_fetch = url
    logger.info(f"Attempting to fetch data from: \n{url_to_fetch}") # Để debug
    try:
        response = requests.get(url_to_fetch)
        response.raise_for_status() 
        return response.content.decode('utf-8')
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        raise e