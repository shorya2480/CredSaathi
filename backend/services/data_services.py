import requests
from typing import Optional, Dict, List
from models.customer import Customer, CRMData, CreditScore, Offer

DUMMY_SERVER_URL = "http://localhost:8001"


class CRMService:
    """Fetches customer KYC data from CRM API"""
    
    def __init__(self):
        self.crm_data: Optional[Dict] = None
        self._load_data()
    
    def _load_data(self):
        """Load CRM data from dummy server"""
        try:
            response = requests.get(f"{DUMMY_SERVER_URL}/crm", timeout=5)
            response.raise_for_status()
            self.crm_data = response.json()
            print(f"✅ CRM data loaded: {len(self.crm_data)} records")
        except requests.RequestException as e:
            print(f"⚠️ Warning: Could not load CRM data from dummy server: {e}")
            print(f"   Make sure dummy server is running on {DUMMY_SERVER_URL}")
            self.crm_data = {}
    
    def verify_customer(self, phone: str) -> Optional[CRMData]:
        """
        Verify customer KYC details by phone number.
        
        Args:
            phone: Customer phone (e.g., "+917835414968")
        
        Returns:
            CRMData if found, None otherwise
        """
        if not self.crm_data:
            self._load_data()
        
        data = self.crm_data.get(phone)
        if data:
            return CRMData(**data)
        return None


class CreditBureauService:
    """Fetches credit scores from Credit Bureau API"""
    
    def __init__(self):
        self.credit_data: Optional[Dict] = None
        self._load_data()
    
    def _load_data(self):
        """Load credit bureau data from dummy server"""
        try:
            response = requests.get(f"{DUMMY_SERVER_URL}/credit-bureau", timeout=5)
            response.raise_for_status()
            self.credit_data = response.json()
            print(f"✅ Credit bureau data loaded: {len(self.credit_data)} records")
        except requests.RequestException as e:
            print(f"⚠️ Warning: Could not load credit data from dummy server: {e}")
            self.credit_data = {}
    
    def get_credit_score(self, phone: str) -> Optional[int]:
        """
        Fetch credit score for a customer.
        
        Args:
            phone: Customer phone number
        
        Returns:
            Credit score (300-900) or None
        """
        if not self.credit_data:
            self._load_data()
        
        data = self.credit_data.get(phone)
        if data:
            return data["credit_score"]
        return None


class CustomerService:
    """Fetches customer profile from Customers API"""
    
    def __init__(self):
        self.customers: Optional[List[Dict]] = None
        self.customer_by_name: Optional[Dict] = None
        self._load_data()
    
    def _load_data(self):
        """Load customer data from dummy server"""
        try:
            response = requests.get(f"{DUMMY_SERVER_URL}/customers", timeout=5)
            response.raise_for_status()
            self.customers = response.json()
            
            # Create a lookup by name for easier searching
            self.customer_by_name = {c["name"]: c for c in self.customers}
            print(f"✅ Customer data loaded: {len(self.customers)} customers")
        except requests.RequestException as e:
            print(f"⚠️ Warning: Could not load customer data from dummy server: {e}")
            self.customers = []
            self.customer_by_name = {}
    
    def get_customer_by_name(self, name: str) -> Optional[Customer]:
        """
        Get customer details by name.
        
        Args:
            name: Customer name (e.g., "Amit Sharma")
        
        Returns:
            Customer object or None
        """
        if not self.customer_by_name:
            self._load_data()
        
        data = self.customer_by_name.get(name)
        if data:
            return Customer(**data)
        return None


class OfferService:
    """Fetches pre-approved offers from Offers API"""
    
    def __init__(self):
        self.offers: Optional[List[Dict]] = None
        self.offer_by_phone: Optional[Dict] = None
        self._load_data()
    
    def _load_data(self):
        """Load offers data from dummy server"""
        try:
            response = requests.get(f"{DUMMY_SERVER_URL}/offers", timeout=5)
            response.raise_for_status()
            self.offers = response.json()
            
            # Create lookup by phone
            self.offer_by_phone = {o["phone"]: o for o in self.offers}
            print(f"✅ Offers data loaded: {len(self.offers)} offers")
        except requests.RequestException as e:
            print(f"⚠️ Warning: Could not load offers data from dummy server: {e}")
            self.offers = []
            self.offer_by_phone = {}
    
    def get_offer(self, phone: str) -> Optional[Offer]:
        """
        Get pre-approved offer for a customer.
        
        Args:
            phone: Customer phone number
        
        Returns:
            Offer object or None
        """
        if not self.offer_by_phone:
            self._load_data()
        
        data = self.offer_by_phone.get(phone)
        if data:
            return Offer(**data)
        return None


crm_service = CRMService()
credit_bureau_service = CreditBureauService()
customer_service = CustomerService()
offer_service = OfferService()