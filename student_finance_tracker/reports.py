from datetime import date
from typing import List

from .models import Category, Transaction, TransactionType


BAR_WIDTH = 30
CURRENCY = "$"


def _fmt(amount: float) -> str:
    return f"{CURRENCY}{amount:,.2f}"


def _bar(value: float, max_value: float, width: int = BAR_WIDTH) -> str:
    if max_value == 0:
        return " " * width
    filled = min(int((value / max_value) * width), width)
    return "█" * filled + "░" * (width - filled)


def print_summary(summary: dict):
    year, month = summary["year"], summary["month"]
    month_name = date(year, month, 1).strftime("%B %Y")

    print(f"\n{'─' * 50}")
    print(f"  Financial Summary — {month_name}")
    print(f"{'─' * 50}")
    print(f"  Income    : {_fmt(summary['income'])}")
    print(f"  Expenses  : {_fmt(summary['expenses'])}")
    net = summary["net"]
    sign = "+" if net >= 0 else ""
    print(f"  Net       : {sign}{_fmt(net)}")
    print(f"{'─' * 50}")

    if summary["by_category"]:
        print("\n  Spending by Category:")
        max_val = max(summary["by_category"].values(), default=1)
        for cat, amount in sorted(
            summary["by_category"].items(), key=lambda x: x[1], reverse=True
        ):
            bar = _bar(amount, max_val)
            print(f"  {cat.value:<14} {bar} {_fmt(amount)}")

    if summary["budget_status"]:
        print("\n  Budget Status:")
        for cat, status in summary["budget_status"].items():
            flag = " ⚠ OVER BUDGET" if status["over_budget"] else ""
            pct = (status["spent"] / status["limit"] * 100) if status["limit"] else 0
            bar = _bar(status["spent"], status["limit"])
            print(
                f"  {cat.value:<14} {bar} {_fmt(status['spent'])} / {_fmt(status['limit'])} ({pct:.0f}%){flag}"
            )

    print()


def print_transactions(transactions: List[Transaction], limit: int = 20):
    if not transactions:
        print("\n  No transactions found.\n")
        return

    print(f"\n{'─' * 70}")
    print(f"  {'ID':<5} {'Date':<12} {'Type':<10} {'Category':<15} {'Amount':<12} Description")
    print(f"{'─' * 70}")
    for t in transactions[:limit]:
        sign = "+" if t.type == TransactionType.INCOME else "-"
        print(
            f"  {t.id:<5} {t.date.isoformat():<12} {t.type.value:<10} "
            f"{t.category.value:<15} {sign}{_fmt(t.amount):<12} {t.description}"
        )
    if len(transactions) > limit:
        print(f"\n  ... and {len(transactions) - limit} more.")
    print()
