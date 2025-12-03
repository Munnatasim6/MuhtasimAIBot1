import logging
import requests
import asyncio

logger = logging.getLogger("OmniTrade.Options")

class OptionsSentiment:
    def __init__(self):
        self.base_url = "https://www.deribit.com/api/v2/public"
        self.currencies = ["BTC", "ETH"]

    async def get_book_summary(self, currency):
        """Fetch public options data from Deribit."""
        try:
            url = f"{self.base_url}/get_book_summary_by_currency?currency={currency}&kind=option"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()['result']
            return []
        except Exception as e:
            logger.error(f"Deribit API error: {e}")
            return []

    def calculate_sentiment(self, data, currency):
        """
        Logic: 
        1. Put/Call Ratio > 1.0 = Bearish Fear.
        2. Rising IV = Expecting Big Move.
        """
        if not data:
            return "NO_DATA"

        total_put_oi = 0
        total_call_oi = 0
        avg_iv = 0
        count = 0

        for instrument in data:
            oi = instrument.get('open_interest', 0)
            instrument_name = instrument['instrument_name']
            
            # Determine if Put or Call
            is_put = instrument_name.endswith('P')
            is_call = instrument_name.endswith('C')
            
            if is_put:
                total_put_oi += oi
            elif is_call:
                total_call_oi += oi
            
            # Aggregate IV (Bid/Ask IV)
            iv = instrument.get('mark_iv', 0)
            if iv > 0:
                avg_iv += iv
                count += 1

        avg_iv = avg_iv / count if count > 0 else 0
        
        # Calculate PCR
        pc_ratio = total_put_oi / total_call_oi if total_call_oi > 0 else 1.0
        
        sentiment = "NEUTRAL"
        
        # IMPLEMENTING YOUR SPECIFIC LOGIC:
        if pc_ratio > 1.0:
            sentiment = "BEARISH (High Fear)"
        elif pc_ratio < 0.6:
            sentiment = "BULLISH (Extreme Greed)"
            
        logger.info(f"OPTIONS ALPHA [{currency}]: PCR={pc_ratio:.2f} | Avg IV={avg_iv:.2f}% | Sentiment={sentiment}")
        
        return {
            "currency": currency,
            "pc_ratio": pc_ratio,
            "implied_volatility": avg_iv,
            "sentiment": sentiment
        }

    async def run_cycle(self):
        """Main execution loop."""
        results = {}
        for curr in self.currencies:
            data = await self.get_book_summary(curr)
            results[curr] = self.calculate_sentiment(data, curr)
        return results
