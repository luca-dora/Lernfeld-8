"""Integration tests for CurrencyConverter class using real yfinance data."""
import sys
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from market_data import CurrencyConverter


def test_usd_as_eur_integration():
    """Integration test with real yfinance data.
    
    Note: This test requires internet connection and will use real market data.
    Use mocked tests for unit testing to avoid network dependency.
    """
    try:
        converter = CurrencyConverter()

        # Get current EUR/USD rate
        rate = converter.get_exchange_rate("USD", "EUR")
        print(f"Current EUR/USD rate: {rate}")
        
        # Test conversion
        usd_amount = 100
        eur_amount = converter.convert_amount(usd_amount, "USD", "EUR")

        print(f"{usd_amount} USD = {eur_amount:.2f} EUR")
        
        # Basic validations
        assert isinstance(eur_amount, (float, int)), "Result should be numeric"
        assert eur_amount > 0, "Converted amount should be positive for positive input"
        assert eur_amount > usd_amount * 0.8, "EUR amount should be reasonable (rough sanity check)"
        assert eur_amount < usd_amount * 1.5, "EUR amount should be reasonable (rough sanity check)"
        
        print("✓ Integration test passed!")
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        raise


if __name__ == "__main__":
    test_usd_as_eur_integration()

