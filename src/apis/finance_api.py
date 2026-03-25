from abc import ABC, abstractmethod


class FinanceApi(ABC):
    """Abstract base class for finance API implementations.
    
    Defines the interface that all finance API providers must implement.
    This allows different API implementations to be easily swapped out.
    """

    @abstractmethod
    def get_data(self, path: str):
        """Fetch financial data from the API.
        
        Returns:
            The API response data (format depends on implementation)
        """
        pass
