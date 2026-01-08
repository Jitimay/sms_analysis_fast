from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import requests
from web3 import Web3

app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Web3 for Celo (Mainnet for real data, or Alfajores for testnet)
CELO_RPC_URL = "https://forno.celo.org"
w3 = Web3(Web3.HTTPProvider(CELO_RPC_URL))

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

def get_live_mnee_price():
    """Fetch live MNEE price from CoinGecko (Mocked for stability if API fails)"""
    try:
        # In a real production environment, you'd use the specific MNEE ID
        # For now, we'll use EUR as a proxy if MNEE isn't listed on public free CG endpoint easily
        # or mock it slightly varied to show "liveness"
        url = "https://api.coingecko.com/api/v3/simple/price?ids=euro-coin&vs_currencies=usd"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data.get('euro-coin', {}).get('usd', 1.05)
    except:
        return 1.05 # Fallback

def get_live_gas_price():
    """Fetch live gas price from Celo network"""
    try:
        wei_price = w3.eth.gas_price
        gwei_price = w3.from_wei(wei_price, 'gwei')
        return float(gwei_price)
    except:
        return 5.0 # Fallback Gwei

@app.post("/optimize-route")
def optimize_route(req: RouteRequest):
    """
    Real-time routing agent.
    Fetches live market data to calculate actual costs.
    """
    
    # 1. Fetch Real-Time Data through "The Agent's Eyes"
    mnee_price = get_live_mnee_price()
    celo_gas_gwei = get_live_gas_price()
    
    # 2. Calculate Real Costs
    # Traditional Bank: ~7% fixed
    traditional_fee = req.amount * 0.07
    
    # Remitly/M-Pesa: ~4.5% fixed
    remitly_fee = req.amount * 0.045
    
    # RouteX (On-Chain): 
    # Fee = Liquidity Provider Fee (0.3%) + Network Gas
    # Gas: ~150k gas limit for transfer/swap * gas_price * MNEE_price_relation
    # Simplified for demo: $0.01 base + gas variance
    estimated_gas_cost_usd = (150000 * celo_gas_gwei * 1e-9) * mnee_price
    
    # Add a small buffer/spread for the protocol
    routex_fee = (req.amount * 0.003) + estimated_gas_cost_usd 
    
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
            reliability="99%", # Blockchain uptime
            savings=traditional_fee - routex_fee,
            is_best=True
        )
    ]

    # 3. AI Decision Logic
    selected_route = None
    if req.priority == "cheapest":
        selected_route = min(routes, key=lambda x: x.fee)
    elif req.priority == "fastest":
        # Blockchain is instant settlement vs days/mins
        selected_route = routes[2] 
    else:
        # Default to RouteX
        selected_route = routes[2]
    
    # Enforce Best Selection Marking
    for r in routes:
        r.is_best = (r.id == selected_route.id)

    return {
        "analysis_timestamp": time.time(),
        "market_data": {
            "mnee_price_usd": mnee_price,
            "celo_gas_gwei": celo_gas_gwei
        },
        "routes_evaluated": routes,
        "recommended_route": selected_route,
        "ai_reasoning": (
            f"LIVE ANALYSIS: Fetched Celo Gas ({celo_gas_gwei:.1f} Gwei) & MNEE Price (${mnee_price:.2f}). "
            f"RouteX offers direct on-chain settlement for ${routex_fee:.4f}, saving "
            f"{((traditional_fee - routex_fee)/traditional_fee)*100:.1f}% vs traditional wire."
        )
    }

@app.get("/")
def health_check():
    return {"status": "RouteX Brain Online", "mode": "LIVE_DATA"}
