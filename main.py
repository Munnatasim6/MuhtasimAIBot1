import logging
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Existing Core Imports
from backend.brain.swarm_manager import SwarmManager
from core.scrapers.social_scraper import SocialScraper
from core.macro_correlator import MacroCorrelator
from core.meta_brain.evolution import EvolutionEngine

# Singularity Module Imports
from core.meta_brain.local_llm import LocalStrategyGenerator
from core.scrapers.dao_tracker import GovernanceWatcher
from web3_modules.liquidation_bot import LiquidationMonitor
from core.aggregator.global_book import GlobalLiquidityWall
from core.macro.trends_engine import TrendsEngine
from web3_modules.stablecoin_watch import StablecoinWatch
from core.fundamental.github_tracker import GithubTracker
from web3_modules.exchange_flow import ExchangeFlow

# Market Maker Grade Imports (Previous Upgrade)
from core.fundamental.defillama_tracker import DefiLlamaTracker
from core.market.options_sentiment import OptionsSentiment
from strategies.funding_arb import FundingArbScanner
from web3_modules.gas_watcher import GasWatcher
from core.macro.correlation_engine import CorrelationEngine

# --- ULTIMATE HEDGE FUND UPGRADE (NEW MODULES) ---
from core.macro.news_trader import NewsTrader
from core.scrapers.telegram_alpha import TelegramAlpha
from web3_modules.bridge_watcher import BridgeWatcher
from web3_modules.graph_liquidity import GraphLiquidityAnalyzer
from core.scrapers.discord_sentiment import DiscordSentiment
# ------------------------------------------------

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniTradeCore")

app = FastAPI(title="OmniTrade AI Core", version="4.0.0 (Ultimate Hedge Fund)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize All Managers
swarm_manager = SwarmManager()
social_scraper = SocialScraper()
macro_correlator = MacroCorrelator()
evolution_engine = EvolutionEngine()
local_llm = LocalStrategyGenerator() 
governance_watcher = GovernanceWatcher()
global_liquidity = GlobalLiquidityWall()
trends_engine = TrendsEngine()
github_tracker = GithubTracker()

# Initialize Market Maker Modules
defillama_tracker = DefiLlamaTracker()
options_sentiment = OptionsSentiment()
funding_scanner = FundingArbScanner()
gas_watcher = GasWatcher()
correlation_engine = CorrelationEngine()

# Initialize Ultimate Modules
news_trader = NewsTrader()
telegram_alpha = TelegramAlpha()
# Ensure you have a valid RPC for BridgeWatcher
bridge_watcher = BridgeWatcher(rpc_url="https://eth.public-rpc.com") 
graph_analyzer = GraphLiquidityAnalyzer()
discord_sentiment = DiscordSentiment()

# Config for Web3 Modules
POLYGON_RPC = "https://polygon-rpc.com"
ETH_RPC = "https://eth.public-rpc.com"
AAVE_V3_POOL_POLYGON = "0x794a61358D6845594F94dc1DB02A252b5b4814aD"
liquidation_monitor = LiquidationMonitor(POLYGON_RPC, AAVE_V3_POOL_POLYGON)
stablecoin_watch = StablecoinWatch(ETH_RPC)
exchange_flow = ExchangeFlow(ETH_RPC)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting OmniTrade AI Core (Ultimate Hedge Fund Level)...")
    
    # --- 1. Start Singularity & Core Tasks ---
    asyncio.create_task(social_scraper.start_stream())
    asyncio.create_task(run_macro_analysis())
    asyncio.create_task(run_evolution_cycle())
    asyncio.create_task(run_governance_watch())
    asyncio.create_task(run_liquidity_monitor())
    asyncio.create_task(run_global_book_analysis())
    asyncio.create_task(run_trends_analysis())
    asyncio.create_task(run_stablecoin_watch())
    asyncio.create_task(run_github_tracking())
    asyncio.create_task(run_exchange_flow_monitor())
    
    # --- 2. Start Market Maker Tasks ---
    asyncio.create_task(run_defillama_tracker())
    asyncio.create_task(run_options_sentiment())
    asyncio.create_task(run_funding_arb_scan())
    asyncio.create_task(run_gas_watcher())
    asyncio.create_task(run_correlation_engine())
    
    # --- 3. Start Ultimate Hedge Fund Tasks ---
    asyncio.create_task(run_news_trader())
    asyncio.create_task(run_bridge_watcher())
    asyncio.create_task(run_graph_analyzer())
    
    # Note: Telegram and Discord require blocking loops or specific handling
    # launching them as tasks works but they need credentials to be active.
    asyncio.create_task(telegram_alpha.start()) 
    asyncio.create_task(discord_sentiment.start_service())
    
    logger.info("✅ All Systems Operational: Alpha, Macro, Web3, & Sentiment Active.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
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

async def run_news_trader():
    """Polls economic calendar every 5 minutes."""
    while True:
        try: await news_trader.run_cycle()
        except Exception as e: logger.error(f"News Trader failed: {e}")
        await asyncio.sleep(300) 

async def run_bridge_watcher():
    """Checks L2 bridges every minute."""
    while True:
        try: await bridge_watcher.run_cycle()
        except Exception as e: logger.error(f"Bridge Watcher failed: {e}")
        await asyncio.sleep(60)

async def run_graph_analyzer():
    """Checks DEX liquidity every hour."""
    while True:
        try: await graph_analyzer.run_cycle()
        except Exception as e: logger.error(f"Graph Analyzer failed: {e}")
        await asyncio.sleep(3600)

@app.get("/")
def read_root():
    return {"status": "active", "system": "OmniTrade AI Core v4.0", "level": "Ultimate Hedge Fund"}

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
