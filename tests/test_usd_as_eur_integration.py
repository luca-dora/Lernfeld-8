"""Integration tests for usd_as_eur function using real yfinance data."""
import sys
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from yfinance_abfrage import usd_as_eur, get_usd_eur


def test_usd_as_eur_integration():
    """Integration test with real yfinance data.
    
    Note: This test requires internet connection and will use real market data.
    Use mocked tests for unit testing to avoid network dependency.
    """
    try:
        # Get current EUR/USD rate
        rate = get_usd_eur()
        print(f"Current EUR/USD rate: {rate}")
        
        # Test conversion
        usd_amount = 100
        eur_amount = usd_as_eur(usd_amount)
        
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

