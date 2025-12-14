from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

BASE_DIR = Path(__file__).resolve().parent.parent / "generated_data"

app = FastAPI(title="Cred Saathi Dummy Data API")

# Allow local frontend / other tools to call this API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for demo purposes; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_json_file(relative_name: str) -> Any:
    """Load a JSON file from the generated_data directory."""
    file_path = BASE_DIR / relative_name
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"File {relative_name} not found")

    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


@app.get("/credit-bureau", summary="Get all credit bureau entries")
def get_credit_bureau() -> Dict[str, Dict[str, int]]:
    """Return the full credit_bureau.json content."""
    data = load_json_file("credit_bureau.json")
    return data


@app.get("/crm", summary="Get all CRM entries")
def get_crm() -> Dict[str, Dict[str, str]]:
    """Return the full crm.json content."""
    data = load_json_file("crm.json")
    return data


@app.get("/customers", summary="Get all customers")
def get_customers() -> List[Dict[str, Any]]:
    """Return the full customers.json content."""
    data = load_json_file("customers.json")
    return data


@app.get("/offers", summary="Get all offers")
def get_offers() -> List[Dict[str, Any]]:
    """Return the full offers.json content."""
    data = load_json_file("offers.json")
    return data


if __name__ == "__main__":
    # Run with: python fastapi_server.py
    uvicorn.run(app, host="0.0.0.0", port=8001)
