import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger("OmniTrade.NewsTrader")

class NewsTrader:
    def __init__(self):
        # Using a reliable economic calendar source (investing.com structure simulation)
        self.url = "https://www.investing.com/economic-calendar/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.high_impact_keywords = ["CPI", "GDP", "Nonfarm Payrolls", "Fed Interest Rate Decision"]

    async def fetch_calendar(self):
        """Scrapes economic calendar for real-time data."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.text()
                    return None
            except Exception as e:
                logger.error(f"Calendar fetch failed: {e}")
                return None

    def analyze_event(self, html):
        """
        Parses the HTML to find 'Actual' vs 'Forecast' values.
        Logic: 
        - Positive Deviation (Actual > Forecast) usually Bullish for Currency, Bearish for Risk Assets (depending on event).
        - CPI Lower than Forecast -> Bullish for Crypto (Risk-On).
        """
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        events = soup.find_all('tr', class_='js-event-item')

        for event in events:
            try:
                # Extract event details (Simplified scraping logic)
                impact_icon = event.find('td', class_='sentiment')
                if not impact_icon or 'high' not in str(impact_icon).lower():
                    continue # Skip low impact

                title = event.find('td', class_='event').text.strip()
                if not any(k in title for k in self.high_impact_keywords):
                    continue

                actual_text = event.find('td', class_='act').text.strip()
                forecast_text = event.find('td', class_='fore').text.strip()

                # Trigger only if 'Actual' data is newly released
                if actual_text and actual_text != '&nbsp;' and forecast_text:
                    self._generate_signal(title, actual_text, forecast_text)
                    
            except AttributeError:
                continue

    def _generate_signal(self, title, actual, forecast):
        # Normalize and compare
        try:
            act_val = float(actual.replace('%', '').replace('K', ''))
            fore_val = float(forecast.replace('%', '').replace('K', ''))
            
            signal = "HOLD"
            
            # CPI Logic: Lower is Better for Crypto
            if "CPI" in title:
                if act_val < fore_val:
                    signal = "BUY (Inflation Cooling)"
                elif act_val > fore_val:
                    signal = "SELL (Inflation Hot)"
            
            # NFP Logic: Higher is Strong Dollar -> Bad for Crypto
            elif "Nonfarm" in title:
                if act_val > fore_val:
                    signal = "SELL (Strong USD)"
                else:
                    signal = "BUY (Weak USD)"

            if signal != "HOLD":
                logger.info(f"📰 NEWS ALPHA: {title} | Act: {actual} vs Fore: {forecast} -> {signal}")
                # In production: await execution_engine.execute_fast_trade(signal)

        except ValueError:
            pass

    async def run_cycle(self):
        """Polls specifically around event times (simulated loop)."""
        logger.info("Running Economic Event Scanner...")
        html = await self.fetch_calendar()
        self.analyze_event(html)
