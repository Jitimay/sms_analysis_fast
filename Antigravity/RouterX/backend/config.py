import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Use Ethereum mainnet with real USDC
    ETHEREUM_RPC_URL = os.getenv('ETHEREUM_RPC_URL', 'https://ethereum.publicnode.com')
    USDC_CONTRACT = os.getenv('USDC_CONTRACT', '0xA0b86a33E6441b8435b662f0E2d0B8A0E4B2B8B0')  # Real USDC
    COINGECKO_API_URL = os.getenv('COINGECKO_API_URL', 'https://api.coingecko.com/api/v3')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'routex.db')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')
    
    # Development settings
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '5'))
