from datetime import date
from typing import List, Optional

from .models import Budget, Category, Transaction, TransactionType
from . import storage


class FinanceTracker:
    def __init__(self):
        self._transactions, self._budgets = storage.load_data()
        self._next_id = max((t.id for t in self._transactions), default=0) + 1

    def add_transaction(
        self,
        type: TransactionType,
        amount: float,
        category: Category,
        description: str,
        transaction_date: Optional[date] = None,
    ) -> Transaction:
        if amount <= 0:
            raise ValueError("Amount must be positive.")

        txn = Transaction(
            id=self._next_id,
            type=type,
            amount=round(amount, 2),
            category=category,
            description=description,
            date=transaction_date or date.today(),
        )
        self._transactions.append(txn)
        self._next_id += 1
        self._save()
        return txn

    def delete_transaction(self, transaction_id: int) -> bool:
        before = len(self._transactions)
        self._transactions = [t for t in self._transactions if t.id != transaction_id]
        if len(self._transactions) < before:
            self._save()
            return True
        return False

    def set_budget(self, category: Category, monthly_limit: float):
        if monthly_limit < 0:
            raise ValueError("Budget limit cannot be negative.")
        # Replace existing budget for this category
        self._budgets = [b for b in self._budgets if b.category != category]
        self._budgets.append(Budget(category=category, monthly_limit=monthly_limit))
        self._save()

    def get_budget(self, category: Category) -> Optional[Budget]:
        return next((b for b in self._budgets if b.category == category), None)

    def get_all_transactions(self) -> List[Transaction]:
        return sorted(self._transactions, key=lambda t: t.date, reverse=True)

    def get_transactions_for_month(self, year: int, month: int) -> List[Transaction]:
        return [
            t for t in self._transactions
            if t.date.year == year and t.date.month == month
        ]

    def monthly_summary(self, year: int, month: int) -> dict:
        txns = self.get_transactions_for_month(year, month)
        income = sum(t.amount for t in txns if t.type == TransactionType.INCOME)
        expenses = sum(t.amount for t in txns if t.type == TransactionType.EXPENSE)

        by_category: dict[Category, float] = {}
        for t in txns:
            by_category[t.category] = by_category.get(t.category, 0) + t.amount

        budget_status = {}
        for budget in self._budgets:
            spent = by_category.get(budget.category, 0)
            budget_status[budget.category] = {
                "limit": budget.monthly_limit,
                "spent": spent,
                "remaining": budget.monthly_limit - spent,
                "over_budget": spent > budget.monthly_limit,
            }

        return {
            "year": year,
            "month": month,
            "income": income,
            "expenses": expenses,
            "net": income - expenses,
            "by_category": by_category,
            "budget_status": budget_status,
        }

    def _save(self):
        storage.save_data(self._transactions, self._budgets)
