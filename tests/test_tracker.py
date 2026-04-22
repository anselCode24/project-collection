import pytest
from datetime import date
from unittest.mock import patch

from student_finance_tracker.models import Category, TransactionType
from student_finance_tracker.tracker import FinanceTracker


@pytest.fixture
def tracker(tmp_path):
    data_file = tmp_path / "data.json"
    with patch("student_finance_tracker.storage.DATA_FILE", data_file):
        yield FinanceTracker()


def add_expense(tracker, amount, category=Category.FOOD, desc="test"):
    return tracker.add_transaction(TransactionType.EXPENSE, amount, category, desc)


def add_income(tracker, amount, category=Category.SALARY, desc="test"):
    return tracker.add_transaction(TransactionType.INCOME, amount, category, desc)


class TestAddTransaction:
    def test_adds_income(self, tracker):
        txn = add_income(tracker, 500)
        assert txn.amount == 500
        assert txn.type == TransactionType.INCOME

    def test_adds_expense(self, tracker):
        txn = add_expense(tracker, 20.50)
        assert txn.amount == 20.50
        assert txn.type == TransactionType.EXPENSE

    def test_ids_are_unique(self, tracker):
        t1 = add_expense(tracker, 10)
        t2 = add_expense(tracker, 20)
        assert t1.id != t2.id

    def test_rejects_zero_amount(self, tracker):
        with pytest.raises(ValueError):
            add_expense(tracker, 0)

    def test_rejects_negative_amount(self, tracker):
        with pytest.raises(ValueError):
            add_expense(tracker, -5)

    def test_defaults_to_today(self, tracker):
        txn = add_expense(tracker, 10)
        assert txn.date == date.today()

    def test_rounds_to_two_decimal_places(self, tracker):
        txn = add_expense(tracker, 9.999)
        assert txn.amount == 10.0


class TestDeleteTransaction:
    def test_deletes_existing(self, tracker):
        txn = add_expense(tracker, 10)
        assert tracker.delete_transaction(txn.id) is True
        assert txn not in tracker.get_all_transactions()

    def test_returns_false_for_missing_id(self, tracker):
        assert tracker.delete_transaction(9999) is False


class TestMonthlySummary:
    def test_income_and_expense_totals(self, tracker):
        today = date.today()
        add_income(tracker, 1000)
        add_expense(tracker, 200)
        add_expense(tracker, 50)

        summary = tracker.monthly_summary(today.year, today.month)
        assert summary["income"] == 1000
        assert summary["expenses"] == 250
        assert summary["net"] == 750

    def test_empty_month_returns_zeros(self, tracker):
        summary = tracker.monthly_summary(2000, 1)
        assert summary["income"] == 0
        assert summary["expenses"] == 0
        assert summary["net"] == 0

    def test_only_includes_correct_month(self, tracker):
        tracker.add_transaction(
            TransactionType.INCOME, 500, Category.SALARY, "jan", date(2025, 1, 15)
        )
        tracker.add_transaction(
            TransactionType.INCOME, 300, Category.SALARY, "feb", date(2025, 2, 15)
        )
        summary = tracker.monthly_summary(2025, 1)
        assert summary["income"] == 500

    def test_by_category_groups_correctly(self, tracker):
        today = date.today()
        add_expense(tracker, 30, Category.FOOD)
        add_expense(tracker, 20, Category.FOOD)
        add_expense(tracker, 100, Category.RENT)

        summary = tracker.monthly_summary(today.year, today.month)
        assert summary["by_category"][Category.FOOD] == 50
        assert summary["by_category"][Category.RENT] == 100


class TestBudget:
    def test_set_and_get_budget(self, tracker):
        tracker.set_budget(Category.FOOD, 300)
        budget = tracker.get_budget(Category.FOOD)
        assert budget is not None
        assert budget.monthly_limit == 300

    def test_updating_budget_replaces_old(self, tracker):
        tracker.set_budget(Category.FOOD, 300)
        tracker.set_budget(Category.FOOD, 500)
        assert tracker.get_budget(Category.FOOD).monthly_limit == 500

    def test_budget_status_shows_over_budget(self, tracker):
        today = date.today()
        tracker.set_budget(Category.FOOD, 50)
        add_expense(tracker, 80, Category.FOOD)

        summary = tracker.monthly_summary(today.year, today.month)
        status = summary["budget_status"][Category.FOOD]
        assert status["over_budget"] is True
        assert status["remaining"] == -30

    def test_budget_status_within_limit(self, tracker):
        today = date.today()
        tracker.set_budget(Category.FOOD, 200)
        add_expense(tracker, 80, Category.FOOD)

        summary = tracker.monthly_summary(today.year, today.month)
        status = summary["budget_status"][Category.FOOD]
        assert status["over_budget"] is False
        assert status["remaining"] == 120

    def test_rejects_negative_budget(self, tracker):
        with pytest.raises(ValueError):
            tracker.set_budget(Category.FOOD, -10)
