# scripts/generate_data.py
import json
import os
import random

BASE_DIR = os.path.dirname(__file__)  # backend/data/scripts
OUTPUT_DIR = os.path.join(BASE_DIR, "../generated_data")

os.makedirs(OUTPUT_DIR, exist_ok=True)

names = [
    "Amit Sharma", "Riya Patel", "Kunal Verma", "Sneha Mehta", "Arjun Singh",
    "Priya Nair", "Rahul Khanna", "Neha Desai", "Vikram Rao", "Ananya Bose"
]

cities = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai"]

customers = []
crm = {}
credit_bureau = {}
offers = []

for i, name in enumerate(names, start=1):

    age = random.randint(22, 55)
    city = random.choice(cities)
    phone = f"+91{random.randint(6000000000, 9999999999)}"
    credit_score = random.randint(650, 900)
    pre_limit = random.choice([50000, 100000, 150000, 200000, 300000])

    customers.append({
        "customer_id": i,
        "name": name,
        "age": age,
        "city": city,
        "current_loan_details": random.choice(["None", "Car Loan", "Bike Loan", "Personal Loan"]),
        "credit_score": credit_score,
        "pre_approved_limit": pre_limit
    })

    crm[phone] = {
        "name": name,
        "phone": phone,
        "address": f"House No {random.randint(1, 300)}, {city}"
    }

    credit_bureau[phone] = {
        "credit_score": credit_score
    }

    offers.append({
        "phone": phone,
        "offer_amount": pre_limit,
        "interest_rate": round(random.uniform(10.0, 15.0), 2),
        "tenure_months": random.choice([12, 18, 24, 36])
    })

with open(os.path.join(OUTPUT_DIR, "customers.json"), "w") as f:
    json.dump(customers, f, indent=2)

with open(os.path.join(OUTPUT_DIR, "crm.json"), "w") as f:
    json.dump(crm, f, indent=2)

with open(os.path.join(OUTPUT_DIR, "credit_bureau.json"), "w") as f:
    json.dump(credit_bureau, f, indent=2)

with open(os.path.join(OUTPUT_DIR, "offers.json"), "w") as f:
    json.dump(offers, f, indent=2)
