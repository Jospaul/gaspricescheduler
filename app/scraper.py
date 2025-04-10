import requests
from bs4 import BeautifulSoup
import re
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_gasbuddy_prices(url):
    # Rotating User-Agents
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0'
    ]
    
    # Set up session with retries
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504, 403]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.google.com/'
    }
    
    try:
        # Random delay
        time.sleep(random.uniform(1, 3))
        
        response = session.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find price elements using the specified class
        price_containers = soup.find_all('span', class_='FuelTypePriceDisplay-module__price___3iizb')
        
        if not price_containers:
            return "Price elements not found on the page. The class might have changed."
            
        prices = {}
        for container in price_containers:
            price_text = container.get_text(strip=True).replace('$', '')
            # Get the fuel type from nearby elements
            parent = container.find_parent()
            if parent:
                fuel_type_elem = parent.find_previous('div', class_='FuelTypePriceDisplay-module__fuelType___2hygg')
                if fuel_type_elem:
                    fuel_type = fuel_type_elem.get_text(strip=True).lower()
                    if 'regular' in fuel_type:
                        prices['Regular Gas'] = price_text
                    elif 'premium' in fuel_type:
                        prices['Premium Gas'] = price_text
        
        # Fallback if specific fuel types aren't identified
        if not prices and price_containers:
            prices['Regular Gas'] = price_containers[0].get_text(strip=True).replace('$', '') if len(price_containers) > 0 else 'Not found'
            prices['Premium Gas'] = price_containers[1].get_text(strip=True).replace('$', '') if len(price_containers) > 1 else 'Not found'
        
        return prices if prices else "No gas prices found"
        
    except requests.exceptions.ConnectionError as e:
        return f"Connection error: {str(e)}"
    except requests.exceptions.Timeout as e:
        return f"Timeout error: {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"Request error: {str(e)}"
    except Exception as e:
        return f"Error processing data: {str(e)}"

def scraper():
    url = "https://www.gasbuddy.com/station/142028"
    print("Attempting to fetch gas prices from GasBuddy...")
    
    prices = get_gasbuddy_prices(url)
    
    if isinstance(prices, dict):
        print("Current Gas Prices at Costco (via GasBuddy):")
        return prices
    else:
        print(prices)
