from abc import ABC, abstractmethod
import pandas as pd

class FinanceApi(ABC):
    """Abstrakte "mock Klasse" / Interface für Finanzdaten API Implementation.
    Erlaubt ggf. Austausch der Datenquelle ohne die business logic zu stören.
    """

    @abstractmethod
    def get_data(self, tickers: list[str], period: str) -> pd.DataFrame:
        """Fetch financial data from the API.
        
        Args:
            tickers: Eine Liste von Symbolen (z.B.["BZ=F", "NG=F"])
            period: Der Zeitraum (z.B. "5d" für 5 Tage)
            
        Returns:
            pd.DataFrame: Eine Tabelle mit den historischen Kursen
        """
        pass