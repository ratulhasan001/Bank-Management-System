"""Customer accounts: balance, deposits, withdrawals, transfers, loans and history."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # avoid a circular import at runtime
    from admin import Admin


ACCOUNT_TYPES = ("Savings", "Current")
MAX_LOANS = 3


class BankError(Exception):
    """Raised when a banking operation is not allowed (bad amount, low balance, ...)."""


@dataclass(frozen=True)
class Transaction:
    """One entry in an account's transaction history."""

    id: int
    kind: str  # "deposit", "withdraw", "loan", "transfer out" or "transfer in"
    amount: int
    counterparty: str | None = None  # the other account for transfers

    def describe(self) -> str:
        text = f"#{self.id}  {self.kind:<12} {self.amount:>10} Tk"
        if self.kind == "transfer out":
            text += f"  to {self.counterparty}"
        elif self.kind == "transfer in":
            text += f"  from {self.counterparty}"
        return text


class Account:
    """A customer account held at a bank (an ``Admin`` instance).

    Amounts are whole taka. Every method that changes money either succeeds
    completely or raises ``BankError`` without changing anything.
    """

    def __init__(self, bank: Admin, account_number: int, name: str, email: str,
                 account_type: str) -> None:
        self.bank = bank
        self.account_number = account_number
        self.name = name
        self.email = email
        self.type = account_type
        self.balance = 0
        self.loan_count = 0
        self.loan_amount = 0
        self.transactions: list[Transaction] = []
        self._next_transaction_id = account_number * 10000

    def __str__(self) -> str:
        return f"{self.name} (account {self.account_number})"

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _check_amount(amount: int) -> None:
        if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            raise BankError("Amount must be a positive whole number.")

    def _record(self, kind: str, amount: int, counterparty: str | None = None) -> Transaction:
        self._next_transaction_id += 1
        transaction = Transaction(self._next_transaction_id, kind, amount, counterparty)
        self.transactions.append(transaction)
        return transaction

    # --------------------------------------------------------------- operations
    def deposit(self, amount: int) -> None:
        """Add ``amount`` to the account and to the bank's cash."""
        self._check_amount(amount)
        self.balance += amount
        self.bank.total_balance += amount
        self._record("deposit", amount)

    def withdraw(self, amount: int) -> None:
        """Take ``amount`` out; limited by the account balance and the bank's cash."""
        self._check_amount(amount)
        if amount > self.balance:
            raise BankError(f"Insufficient balance. Your balance is {self.balance} Tk.")
        if amount > self.bank.total_balance:
            raise BankError("The bank does not have enough cash right now. Please try a smaller amount.")
        self.balance -= amount
        self.bank.total_balance -= amount
        self._record("withdraw", amount)

    def transfer(self, account_number: int, amount: int) -> Account:
        """Move ``amount`` to another account at the same bank and return that account."""
        self._check_amount(amount)
        receiver = self.bank.find_account(account_number)
        if receiver is None:
            raise BankError(f"Account {account_number} does not exist.")
        if receiver is self:
            raise BankError("You cannot transfer money to your own account.")
        if amount > self.balance:
            raise BankError(f"Insufficient balance. Your balance is {self.balance} Tk.")
        self.balance -= amount
        receiver.balance += amount
        self._record("transfer out", amount, str(receiver))
        receiver._record("transfer in", amount, str(self))
        return receiver

    def take_loan(self, amount: int) -> None:
        """Borrow ``amount`` from the bank; it is credited to this account.

        Allowed only while the bank's loan facility is on, at most ``MAX_LOANS``
        times per account, and never for more than the bank's available cash.
        """
        self._check_amount(amount)
        if not self.bank.loan_feature:
            raise BankError("The loan facility is currently turned off.")
        if self.loan_count >= MAX_LOANS:
            raise BankError(f"Loan limit reached: at most {MAX_LOANS} loans per account.")
        if amount > self.bank.total_balance:
            raise BankError(f"The bank can lend at most {self.bank.total_balance} Tk right now.")
        self.loan_count += 1
        self.loan_amount += amount
        self.balance += amount
        self.bank.total_loan_amount += amount
        self._record("loan", amount)
