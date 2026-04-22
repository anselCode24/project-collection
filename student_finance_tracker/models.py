from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Category(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    RENT = "rent"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    CLOTHING = "clothing"
    SAVINGS = "savings"
    SALARY = "salary"
    FREELANCE = "freelance"
    SCHOLARSHIP = "scholarship"
    OTHER = "other"

    @classmethod
    def expense_categories(cls):
        return [
            cls.FOOD, cls.TRANSPORT, cls.RENT, cls.EDUCATION,
            cls.ENTERTAINMENT, cls.HEALTH, cls.CLOTHING, cls.OTHER,
        ]

    @classmethod
    def income_categories(cls):
        return [cls.SALARY, cls.FREELANCE, cls.SCHOLARSHIP, cls.OTHER]


@dataclass
class Transaction:
    id: int
    type: TransactionType
    amount: float
    category: Category
    description: str
    date: date

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "amount": self.amount,
            "category": self.category.value,
            "description": self.description,
            "date": self.date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        return cls(
            id=data["id"],
            type=TransactionType(data["type"]),
            amount=data["amount"],
            category=Category(data["category"]),
            description=data["description"],
            date=date.fromisoformat(data["date"]),
        )


@dataclass
class Budget:
    category: Category
    monthly_limit: float

    def to_dict(self) -> dict:
        return {"category": self.category.value, "monthly_limit": self.monthly_limit}

    @classmethod
    def from_dict(cls, data: dict) -> "Budget":
        return cls(
            category=Category(data["category"]),
            monthly_limit=data["monthly_limit"],
        )
