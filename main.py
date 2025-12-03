import logging
import asyncio
import json
import subprocess
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.brain.swarm_manager import SwarmManager
from core.data_nexus import DataNexus
from core.macro_correlator import MacroCorrelator
from core.meta_brain.evolution import EvolutionEngine

# Singularity Module Imports (Phase 1)
from core.meta_brain.local_llm import LocalStrategyGenerator
from core.scrapers.dao_tracker import GovernanceWatcher
from web3_modules.liquidation_bot import LiquidationMonitor
from core.aggregator.global_book import GlobalLiquidityWall

# Singularity Module Imports (Phase 2 - Free Tier)
from core.macro.trends_engine import TrendsEngine
from web3_modules.stablecoin_watch import StablecoinWatch
from core.fundamental.github_tracker import GithubTracker
from web3_modules.exchange_flow import ExchangeFlow

# --- MARKET MAKER GRADE UPGRADE (NEW IMPORTS) ---
from core.fundamental.defillama_tracker import DefiLlamaTracker
from core.market.options_sentiment import OptionsSentiment
from strategies.funding_arb import FundingArbScanner
from web3_modules.gas_watcher import GasWatcher
from core.macro.correlation_engine import CorrelationEngine
# -----------------------------------------------

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniTradeCore")

app = FastAPI(title="OmniTrade AI Core", version="3.0.0 (Market Maker Grade)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Swarm Manager
swarm_manager = SwarmManager()

# Initialize Data Nexus (Listener)
data_nexus = DataNexus()

# Initialize Singularity Modules
macro_correlator = MacroCorrelator()
evolution_engine = EvolutionEngine()
local_llm = LocalStrategyGenerator() # Assumes Ollama is running
governance_watcher = GovernanceWatcher()
global_liquidity = GlobalLiquidityWall()

# Phase 2 Modules
trends_engine = TrendsEngine()
github_tracker = GithubTracker()

# --- MARKET MAKER MODULE INITIALIZATION ---
defillama_tracker = DefiLlamaTracker()
options_sentiment = OptionsSentiment()
funding_scanner = FundingArbScanner()
gas_watcher = GasWatcher()
correlation_engine = CorrelationEngine()
# -------------------------------------------

# Config for Web3 Modules (Public RPCs)
POLYGON_RPC = "https://polygon-rpc.com"
ETH_RPC = "https://eth.public-rpc.com"

AAVE_V3_POOL_POLYGON = "0x794a61358D6845594F94dc1DB02A252b5b4814aD"
liquidation_monitor = LiquidationMonitor(POLYGON_RPC, AAVE_V3_POOL_POLYGON)
stablecoin_watch = StablecoinWatch(ETH_RPC)
exchange_flow = ExchangeFlow(ETH_RPC)

class ScaleRequest(BaseModel):
    replicas: int

@app.post("/api/system/scale-scraper")
async def scale_scraper(request: ScaleRequest):
    """
    Scales the scraper microservice.
    Minimum replicas: 4
    """
    if request.replicas < 4:
        raise HTTPException(status_code=400, detail="Minimum scraper count is 4.")
    
    logger.info(f"⚖️ Scaling Scraper Service to {request.replicas} replicas...")
    
    try:
        # Execute docker compose scale command
        # Note: This requires the container to have access to the host docker socket
        # and the docker CLI installed.
        cmd = [
            "docker", "compose", "-f", "/app/docker-compose.yml", 
            "up", "-d", "--scale", f"scraper={request.replicas}", "--no-recreate"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Docker Scale Error: {result.stderr}")
            raise HTTPException(status_code=500, detail=f"Scaling failed: {result.stderr}")
            
        logger.info("✅ Scaling successful.")
        return {"status": "success", "replicas": request.replicas, "message": "Scraper scaled successfully."}
        
    except Exception as e:
        logger.error(f"Scaling Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    logger.info("Starting OmniTrade AI Core (Singularity Level - Phase 2)...")
    # Start Data Nexus (Listener)
    asyncio.create_task(data_nexus.start())
    
    # Start Macro Analysis Background Task
    asyncio.create_task(run_macro_analysis())
    
    # Start Evolution Engine Background Task
    asyncio.create_task(run_evolution_cycle())

    # Start Singularity Background Tasks (Phase 1)
    asyncio.create_task(run_governance_watch())
    asyncio.create_task(run_liquidity_monitor())
    asyncio.create_task(run_global_book_analysis())
    
    # Start Singularity Background Tasks (Phase 2)
    asyncio.create_task(run_trends_analysis())
    asyncio.create_task(run_stablecoin_watch())
    asyncio.create_task(run_github_tracking())
    asyncio.create_task(run_exchange_flow_monitor())
    
    # --- NEW MARKET MAKER TASKS ---
    asyncio.create_task(run_defillama_tracker())
    asyncio.create_task(run_options_sentiment())
    asyncio.create_task(run_funding_arb_scan())
    asyncio.create_task(run_gas_watcher())
    asyncio.create_task(run_correlation_engine())
    logger.info("New Market Maker Modules Activated: DeFiLlama, Options, Funding Arb, Gas, Macro Matrix.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    await data_nexus.stop()

# --- NEW MARKET MAKER BACKGROUND TASKS ---

async def run_defillama_tracker():
    """Checks protocol health/undervalued gems daily."""
    while True:
        try:
            await defillama_tracker.run_cycle()
        except Exception as e:
            logger.error(f"DeFiLlama Tracker failed: {e}")
        await asyncio.sleep(86400) # Daily

async def run_options_sentiment():
    """Checks options flows hourly."""
    while True:
        try:
            await options_sentiment.run_cycle()
        except Exception as e:
            logger.error(f"Options Sentiment failed: {e}")
        await asyncio.sleep(3600) # Hourly

async def run_funding_arb_scan():
    """Scans for funding arbitrage every 4 hours."""
    while True:
        try:
            await funding_scanner.run_cycle()
        except Exception as e:
            logger.error(f"Funding Arb Scan failed: {e}")
        await asyncio.sleep(14400) # 4 Hours

async def run_gas_watcher():
    """Watches gas prices in real-time (every 30s)."""
    while True:
        try:
            await gas_watcher.run_cycle()
        except Exception as e:
            logger.error(f"Gas Watcher failed: {e}")
        await asyncio.sleep(30)

async def run_correlation_engine():
    """Calculates macro correlations daily."""
    while True:
        try:
            await correlation_engine.run_cycle()
        except Exception as e:
            logger.error(f"Correlation Engine failed: {e}")
        await asyncio.sleep(86400) # Daily (Market Close)

# -----------------------------------------

async def run_macro_analysis():
    """Background task to update macro correlations periodically."""
    while True:
        try:
            await macro_correlator.fetch_macro_data()
            correlations = macro_correlator.calculate_correlations()
            risk_regime = macro_correlator.analyze_risk_regime(correlations)
            logger.info(f"Current Risk Regime: {risk_regime}")
        except Exception as e:
            logger.error(f"Macro analysis failed: {e}")
        await asyncio.sleep(3600)

async def run_evolution_cycle():
    """Background task to run genetic evolution of agents."""
    while True:
        try:
            evolution_engine.evolve()
        except Exception as e:
            logger.error(f"Evolution cycle failed: {e}")
        await asyncio.sleep(86400)

async def run_governance_watch():
    """Background task to watch DAO proposals."""
    while True:
        try:
            governance_watcher.run_cycle()
        except Exception as e:
            logger.error(f"Governance Watcher failed: {e}")
        await asyncio.sleep(3600)

async def run_liquidity_monitor():
    """Background task to monitor liquidation opportunities."""
    users_to_monitor = ["0x0000000000000000000000000000000000000000"] 
    while True:
        try:
            liquidation_monitor.monitor_users(users_to_monitor)
        except Exception as e:
            logger.error(f"Liquidation Monitor failed: {e}")
        await asyncio.sleep(60)

async def run_global_book_analysis():
    """Background task to analyze global liquidity."""
    while True:
        try:
            await global_liquidity.run_analysis()
        except Exception as e:
            logger.error(f"Global Liquidity Analysis failed: {e}")
        await asyncio.sleep(10)

# --- Phase 2 Background Tasks ---

async def run_trends_analysis():
    """Background task for Google Trends."""
    while True:
        try:
            trends_engine.analyze_sentiment()
        except Exception as e:
            logger.error(f"Trends Analysis failed: {e}")
        await asyncio.sleep(3600) # Check hourly

async def run_stablecoin_watch():
    """Background task for Stablecoin Minting."""
    while True:
        try:
            stablecoin_watch.check_recent_mints()
        except Exception as e:
            logger.error(f"Stablecoin Watch failed: {e}")
        await asyncio.sleep(60)

async def run_github_tracking():
    """Background task for GitHub activity."""
    while True:
        try:
            # Mock price trends for now
            trends = {"ETH": "UP", "SOL": "UP"} 
            github_tracker.analyze_activity(trends)
        except Exception as e:
            logger.error(f"GitHub Tracking failed: {e}")
        await asyncio.sleep(86400) # Check daily

async def run_exchange_flow_monitor():
    """Background task for Exchange Flows."""
    while True:
        try:
            exchange_flow.check_flows()
        except Exception as e:
            logger.error(f"Exchange Flow Monitor failed: {e}")
        await asyncio.sleep(15)

@app.get("/")
def read_root():
    return {"status": "active", "system": "OmniTrade AI Core v3.0", "level": "Market Maker Grade"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket Client Connected")
    try:
        while True:
            market_data = {
                "orderbook_features": [0.5] * 10,
                "ohlcv_features": [0.5] * 10,
                "portfolio_value": 10000.0,
                "positions": []
            }
            decision = await swarm_manager.get_swarm_decision(market_data)
            payload = {
                "pnl": 0.0,
                "active_agents": decision["active_agents"],
                "signals": {
                    "action": decision["action"],
                    "confidence": decision["confidence"],
                    "agent_decisions": decision["agent_decisions"]
                },
                "timestamp": "2025-11-30T00:00:00Z"
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info("WebSocket Client Disconnected")
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        await websocket.close()
