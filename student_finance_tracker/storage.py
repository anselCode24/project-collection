import json
from pathlib import Path
from typing import List

from .models import Budget, Transaction


DATA_FILE = Path.home() / ".student_finance" / "data.json"


def _ensure_data_dir():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_data() -> tuple[List[Transaction], List[Budget]]:
    _ensure_data_dir()
    if not DATA_FILE.exists():
        return [], []

    with open(DATA_FILE) as f:
        raw = json.load(f)

    transactions = [Transaction.from_dict(t) for t in raw.get("transactions", [])]
    budgets = [Budget.from_dict(b) for b in raw.get("budgets", [])]
    return transactions, budgets


def save_data(transactions: List[Transaction], budgets: List[Budget]):
    _ensure_data_dir()
    payload = {
        "transactions": [t.to_dict() for t in transactions],
        "budgets": [b.to_dict() for b in budgets],
    }
    with open(DATA_FILE, "w") as f:
        json.dump(payload, f, indent=2)
