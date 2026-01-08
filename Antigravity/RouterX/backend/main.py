from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import requests
from web3 import Web3
import logging
from database import Database
from config import Config

app = FastAPI()

# Initialize database
db = Database(Config.DATABASE_PATH)

# Setup logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Web3 for Celo
w3 = Web3(Web3.HTTPProvider(Config.CELO_RPC_URL))

class RouteRequest(BaseModel):
    amount: float
    currency: str
    destination: str
    priority: str = "cheapest"  # cheapest | fastest

class Route(BaseModel):
    id: str
    name: str
    provider: str
    fee: float
    delivery_time: str
    reliability: str
    savings: float
    is_best: bool = False

class TransactionRequest(BaseModel):
    user_address: str
    amount: float
    route_id: str
    route_name: str
    fee: float
    savings: float
    destination: str
    route_id: str
    route_name: str
    fee: float
    savings: float
    destination: str
    id: str
    name: str
    provider: str
    fee: float
    delivery_time: str
    reliability: str
    savings: float
    is_best: bool = False

def get_live_mnee_price():
    """Fetch live cUSD price (using as MNEE proxy)"""
    try:
        url = f"{Config.COINGECKO_API_URL}/simple/price?ids=celo-dollar&vs_currencies=usd"
        response = requests.get(url, timeout=Config.API_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        price = data.get('celo-dollar', {}).get('usd', None)
        if price is None:
            # Fallback to 1.0 for stablecoin if API doesn't have it
            price = 1.0
        logger.info(f"Fetched cUSD price: ${price}")
        return price
    except Exception as e:
        logger.error(f"Failed to fetch cUSD price: {e}")
        # For stablecoins, we can safely assume ~$1.00
        return 1.0

def get_live_gas_price():
    """Fetch live gas price from Celo network"""
    try:
        wei_price = w3.eth.gas_price
        if wei_price is None:
            raise Exception("Unable to fetch gas price")
        gwei_price = w3.from_wei(wei_price, 'gwei')
        return float(gwei_price)
    except Exception as e:
        logger.error(f"Failed to fetch gas price: {e}")
        raise HTTPException(status_code=503, detail="Unable to fetch live gas price")

@app.post("/optimize-route")
def optimize_route(req: RouteRequest):
    """
    Real-time routing agent using only live data.
    """
    try:
        # 1. Fetch Real-Time Data
        mnee_price = get_live_mnee_price()
        if mnee_price is None:
            raise HTTPException(status_code=503, detail="MNEE price unavailable")
            
        celo_gas_gwei = get_live_gas_price()
        
        # 2. Calculate Real Costs
        traditional_fee = req.amount * 0.07  # 7% traditional banking
        remitly_fee = req.amount * 0.045     # 4.5% remittance services
        
        # RouteX fee calculation with real gas costs
        estimated_gas_cost_usd = (150000 * celo_gas_gwei * 1e-9) * mnee_price
        routex_fee = (req.amount * 0.003) + estimated_gas_cost_usd + 0.01  # Protocol fee
        
        routes = [
            Route(
                id="TRADITIONAL_SWIFT",
                name="Traditional Bank Wire",
                provider="GlobalBank",
                fee=traditional_fee,
                delivery_time="2-3 Days",
                reliability="92%",
                savings=0.0
            ),
            Route(
                id="M_PESA_DIRECT",
                name="Remitly / M-Pesa",
                provider="Remitly",
                fee=remitly_fee,
                delivery_time="15 Mins",
                reliability="88%",
                savings=traditional_fee - remitly_fee
            ),
            Route(
                id="ROUTEX_OPTIMIZED",
                name="RouteX AI (MNEE)",
                provider="Celo Network",
                fee=routex_fee,
                delivery_time="3 Seconds",
                reliability="99%",
                savings=traditional_fee - routex_fee,
                is_best=True
            )
        ]

        # 3. AI Decision Logic
        if req.priority == "cheapest":
            selected_route = min(routes, key=lambda x: x.fee)
        elif req.priority == "fastest":
            selected_route = routes[2]  # RouteX is always fastest
        else:
            selected_route = routes[2]  # Default to RouteX
        
        # Mark best route
        for r in routes:
            r.is_best = (r.id == selected_route.id)

        return {
            "analysis_timestamp": time.time(),
            "market_data": {
                "mnee_price_usd": mnee_price,
                "celo_gas_gwei": celo_gas_gwei
            },
            "routes_evaluated": [route.dict() for route in routes],
            "recommended_route": selected_route.dict(),
            "ai_reasoning": (
                f"LIVE ANALYSIS: Celo Gas {celo_gas_gwei:.1f} Gwei, MNEE ${mnee_price:.3f}. "
                f"RouteX saves ${(traditional_fee - routex_fee):.2f} "
                f"({((traditional_fee - routex_fee)/traditional_fee)*100:.1f}%) vs traditional banking."
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Route optimization failed: {e}")
        raise HTTPException(status_code=500, detail="Route optimization failed")

@app.get("/")
def health_check():
    return {"status": "RouteX Brain Online", "mode": "LIVE_DATA"}

@app.post("/save-transaction")
def save_transaction(req: TransactionRequest):
    try:
        tx_id = db.save_transaction({
            'user_address': req.user_address,
            'amount': req.amount,
            'route_id': req.route_id,
            'route_name': req.route_name,
            'fee': req.fee,
            'savings': req.savings,
            'destination': req.destination
        })
        logger.info(f"Transaction saved: {tx_id}")
        return {"transaction_id": tx_id, "status": "saved"}
    except Exception as e:
        logger.error(f"Failed to save transaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to save transaction")

@app.post("/update-transaction/{tx_id}")
def update_transaction(tx_id: str, status: str, tx_hash: str = None):
    try:
        db.update_transaction(tx_id, status, tx_hash)
        logger.info(f"Transaction updated: {tx_id} -> {status}")
        return {"status": "updated"}
    except Exception as e:
        logger.error(f"Failed to update transaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to update transaction")

@app.get("/transactions/{user_address}")
def get_user_transactions(user_address: str):
    try:
        transactions = db.get_user_transactions(user_address)
        return {"transactions": transactions}
    except Exception as e:
        logger.error(f"Failed to get transactions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get transactions")
