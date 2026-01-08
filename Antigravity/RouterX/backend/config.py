import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CELO_RPC_URL = os.getenv('CELO_RPC_URL', 'https://forno.celo.org')
    MNEE_CONTRACT = os.getenv('MNEE_CONTRACT', '0x8ccedbAe4916b79da7F3F612EfB2EB93A2bFD6cF')
    COINGECKO_API_URL = os.getenv('COINGECKO_API_URL', 'https://api.coingecko.com/api/v3')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'routex.db')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')
    
    # Development settings
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '5'))
