import asyncio
import logging
from core.cex_feed import CEXFeed
from web3_modules.on_chain import OnChainMonitor
from core.sentiment import SentimentEngine

logger = logging.getLogger(__name__)

class DataNexus:
    def __init__(self):
        self.cex = CEXFeed()
        self.on_chain = OnChainMonitor()
        self.sentiment = SentimentEngine()

    async def start(self):
        logger.info("Initializing Universal Data Nexus...")
        await asyncio.gather(
            self.cex.start(),
            self.on_chain.start(),
            self.sentiment.start()
        )

    async def stop(self):
        logger.info("Stopping Data Nexus...")
        await self.cex.stop()
        await self.on_chain.stop()
        await self.sentiment.stop()
