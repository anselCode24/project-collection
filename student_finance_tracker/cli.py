import sys
from datetime import date

from .models import Category, TransactionType
from .tracker import FinanceTracker
from . import reports


def _pick(prompt: str, options: list, labels: list = None) -> int:
    labels = labels or [str(o) for o in options]
    for i, label in enumerate(labels, 1):
        print(f"  {i}. {label}")
    while True:
        raw = input(f"{prompt} (1-{len(options)}): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw) - 1
        print("  Invalid choice, try again.")


def _input_amount(prompt: str) -> float:
    while True:
        raw = input(prompt).strip().lstrip("$")
        try:
            val = float(raw)
            if val > 0:
                return val
            print("  Amount must be positive.")
        except ValueError:
            print("  Please enter a valid number.")


def _input_date(prompt: str) -> date:
    while True:
        raw = input(f"{prompt} (YYYY-MM-DD, or Enter for today): ").strip()
        if not raw:
            return date.today()
        try:
            return date.fromisoformat(raw)
        except ValueError:
            print("  Invalid date format. Use YYYY-MM-DD.")


def cmd_add(tracker: FinanceTracker):
    print("\n  Add Transaction")
    print("  -----------------")

    type_idx = _pick("  Type", list(TransactionType))
    txn_type = list(TransactionType)[type_idx]

    cats = Category.income_categories() if txn_type == TransactionType.INCOME else Category.expense_categories()
    cat_idx = _pick("  Category", cats, [c.value for c in cats])
    category = cats[cat_idx]

    amount = _input_amount("  Amount: $")
    description = input("  Description: ").strip() or "-"
    txn_date = _input_date("  Date")

    txn = tracker.add_transaction(txn_type, amount, category, description, txn_date)
    print(f"\n  Transaction #{txn.id} added successfully.\n")


def cmd_list(tracker: FinanceTracker):
    txns = tracker.get_all_transactions()
    reports.print_transactions(txns)


def cmd_delete(tracker: FinanceTracker):
    raw = input("\n  Transaction ID to delete: ").strip()
    if not raw.isdigit():
        print("  Invalid ID.\n")
        return
    removed = tracker.delete_transaction(int(raw))
    print(f"  {'Deleted.' if removed else 'Transaction not found.'}\n")


def cmd_summary(tracker: FinanceTracker):
    today = date.today()
    raw_year = input(f"\n  Year (Enter for {today.year}): ").strip()
    raw_month = input(f"  Month 1-12 (Enter for {today.month}): ").strip()

    year = int(raw_year) if raw_year.isdigit() else today.year
    month = int(raw_month) if raw_month.isdigit() and 1 <= int(raw_month) <= 12 else today.month

    summary = tracker.monthly_summary(year, month)
    reports.print_summary(summary)


def cmd_budget(tracker: FinanceTracker):
    print("\n  Set Monthly Budget")
    print("  ------------------")
    cats = Category.expense_categories()
    idx = _pick("  Category", cats, [c.value for c in cats])
    category = cats[idx]

    existing = tracker.get_budget(category)
    if existing:
        print(f"  Current limit: ${existing.monthly_limit:.2f}")

    limit = _input_amount("  New monthly limit: $")
    tracker.set_budget(category, limit)
    print(f"  Budget for '{category.value}' set to ${limit:.2f}/month.\n")


MENU = [
    ("Add income or expense",   cmd_add),
    ("List all transactions",   cmd_list),
    ("Monthly summary & charts",cmd_summary),
    ("Set category budget",     cmd_budget),
    ("Delete a transaction",    cmd_delete),
    ("Quit",                    None),
]


def run():
    tracker = FinanceTracker()
    print("\n  ============================")
    print("    Student Finance Tracker")
    print("  ============================")

    while True:
        print("  Main Menu")
        print("  ---------")
        for i, (label, _) in enumerate(MENU, 1):
            print(f"  {i}. {label}")

        raw = input("\n  Choose (1-{n}): ".format(n=len(MENU))).strip()
        if not raw.isdigit() or not (1 <= int(raw) <= len(MENU)):
            print("  Invalid choice.\n")
            continue

        _, handler = MENU[int(raw) - 1]
        if handler is None:
            print("\n  Goodbye!\n")
            break

        try:
            handler(tracker)
        except KeyboardInterrupt:
            print("\n  Cancelled.\n")
        except Exception as e:
            print(f"\n  Error: {e}\n")
