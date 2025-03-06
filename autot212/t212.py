from typing import List, Dict, Any, Optional
import requests
import time
import re
import random

class PieAllocator:
    """Manage Trading 212 pies"""
    
    def __init__(self, api_key: str, base_url: str = "https://live.trading212.com/api/v0", retry_delay: int = 5):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"{self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_instruments(self) -> Optional[str]:
        """Get all instruments available on Trading 212"""
        endpoint = f"{self.base_url}/equity/metadata/instruments"
        response = self._make_request(50, "GET", endpoint)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching instruments: {response.status_code}")
            print(response.text)
            return None

    def _make_request(self, retry_delay, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Helper method to make API requests with retry logic"""
        retries = 3

        for attempt in range(retries):
            response = requests.request(method, endpoint, headers=self.headers, **kwargs)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                print(f"Rate limit hit, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                break
        
        return response
    
    def get_existing_pies(self) -> List[Dict[str, Any]]:
        """Get all existing pies from Trading 212 account"""
        endpoint = f"{self.base_url}/equity/pies"
        response = self._make_request(30, "GET", endpoint)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching pies: {response.status_code}")
            print(response.text)
            return []
    
    def create_pie(self, pie_name: str) -> Optional[Dict[str, Any]]:
        """Create a new pie with given name and description"""
        endpoint = f"{self.base_url}/equity/pies"

        payload = {
            "dividendCashAction": "REINVEST",
            "endDate": "2029-08-24T14:15:22Z",
            "goal": 0,
            "icon": "Coins",
            "instrumentShares": {
                "AAPL_US_EQ": 1
            },
            "name": pie_name
        }   
        
        response = self._make_request(5, "POST", endpoint, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error creating pie: {response.status_code}")
            print(response.text)
            return None
    
    def extract_ticker(self, text):
        match = re.search(r'ticker (\S+)', text)
        return match.group(1) if match else None

    def update_pie_allocations(self, pie_id: str, holdings: List[Dict[str, Any]]) -> bool:
        """Update a pie's allocations based on holdings data"""
        endpoint = f"{self.base_url}/equity/pies/{pie_id}"
        
        # Format the holdings data into the required structure for Trading 212
        pie_items = {}
        for holding in holdings:

            # Manual overrides for specific symbols
            if holding["symbol"] == "META":
                holding["symbol"] = "FB"
            elif holding["symbol"] == "HHH":
                holding["symbol"] = "HHC"
            elif holding["symbol"] == "BN":
                holding["symbol"] = "BAM"
            elif holding["symbol"] == "MAGN":
                holding["symbol"] = "GLT"
            elif holding["symbol"] == "PARA":
                holding["symbol"] = "CBS"
            elif holding["symbol"] == "KIND":
                holding["symbol"] = "KVSB"
            elif holding["symbol"] == "AXON":
                holding["symbol"] = "AAXN"
            elif holding["symbol"] == "DKNG":
                holding["symbol"] = "DEAC"
            elif holding["symbol"] == "UAA":
                holding["symbol"] = "UA"
            elif holding["symbol"] == "RUM":
                holding["symbol"] = "CFVI"


            pie_items[f"{holding['symbol']}_US_EQ"] = holding["percentOfPortfolio"]
        
        while True:
            # Rebalance pie items if their total percentage does not equal 1
            pie_items = self.rebalance_pie_items(pie_items)
            
            # Add new pie items
            response = self._make_request(5, "POST", endpoint, json={"instrumentShares": pie_items})
            
            if response.status_code == 200:
                return True
            elif response.status_code == 400 and "Instrument with ticker" in response.json().get("code", ""):
                error_message = response.json().get("code", "")
                ticker = self.extract_ticker(error_message)
                if ticker in pie_items:
                    print(f"Removing {ticker} from pie items due to error: {error_message}")
                    del pie_items[ticker]
                else:
                    print(f"Error updating pie allocations: {response.status_code}")
                    print(response.text)
                    return False
            else:
                print(f"Error updating pie allocations: {response.status_code}")
                print(response.text)
                return False

    def rebalance_pie_items(self, pie_items: Dict[str, float]) -> Dict[str, float]:
        """Rebalance pie items so that their total percentage equals exactly 1.0"""
        total_percentage = sum(pie_items.values())

        if total_percentage == 1.0:
            return {k: round(v, 4) for k, v in pie_items.items()}

        # Normalize and round to 4 decimal places
        pie_items = {k: round(v / total_percentage, 4) for k, v in pie_items.items()}

        # Adjust the last item to ensure the total is exactly 1.0
        total_percentage = sum(pie_items.values())
        difference = round(1.0 - total_percentage, 4)
        
        if difference != 0.0:
            random_key = random.choice(list(pie_items.keys()))
            pie_items[random_key] = round(pie_items[random_key] + difference, 4)

        return pie_items
    
    def get_or_create_pie(self, pie_name: str) -> Optional[Dict[str, Any]]:
        """Get a pie by name or create if it doesn't exist"""
        existing_pies = self.get_existing_pies()
        
        # Check if pie already exists
        for pie in existing_pies:
            pie_details = self._make_request(5, "GET", f"{self.base_url}/equity/pies/{pie['id']}")
            
            if pie_details.status_code == 200 and pie_details.json()["settings"]["name"] == pie_name:
                return pie
        
        # Create new pie if it doesn't exist
        return self.create_pie(pie_name)
    
    def sync_pie_with_holdings(self, pie_name: str, holdings: List[Dict[str, Any]]) -> bool:
        """Sync a pie with the provided holdings data"""
        # Get or create the pie
        pie = self.get_or_create_pie(pie_name)
        
        if not pie:
            return False
        
        # Update the pie allocations
        pie_id = pie["id"] if "id" in pie else pie.get("settings").get("id")
        return self.update_pie_allocations(pie_id, holdings)