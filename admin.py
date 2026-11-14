"""The bank itself, as managed by its admin: accounts, totals and the loan switch."""

from __future__ import annotations

from account import ACCOUNT_TYPES, Account, BankError


class Admin:
    """A bank and the admin operations on it.

    ``total_balance`` is the cash the bank holds (deposits minus withdrawals);
    ``total_loan_amount`` is the sum of all loans it has given out.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.accounts: list[Account] = []
        self.total_balance = 0
        self.total_loan_amount = 0
        self.loan_feature = True
        self._next_account_number = 1

    def create_an_account(self, name: str, email: str, account_type: str) -> Account:
        """Open a new account and return it. Account numbers start at 1."""
        name, email = name.strip(), email.strip()
        if not name:
            raise BankError("Name cannot be empty.")
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            raise BankError("Please enter a valid e-mail address.")
        matches = [t for t in ACCOUNT_TYPES if t.lower() == account_type.strip().lower()]
        if not matches:
            raise BankError(f"Account type must be one of: {', '.join(ACCOUNT_TYPES)}.")
        account = Account(self, self._next_account_number, name, email, matches[0])
        self._next_account_number += 1
        self.accounts.append(account)
        return account

    def find_account(self, account_number: int) -> Account | None:
        """Return the account with this number, or ``None``."""
        for account in self.accounts:
            if account.account_number == account_number:
                return account
        return None

    def delete_an_account(self, account_number: int) -> Account:
        """Close an account, paying out its remaining balance, and return it."""
        account = self.find_account(account_number)
        if account is None:
            raise BankError(f"No account found with number {account_number}.")
        if account.balance > self.total_balance:
            raise BankError("The bank does not have enough cash to pay out this account's balance.")
        self.total_balance -= account.balance
        self.accounts.remove(account)
        return account

    def turn_on_loan(self) -> None:
        self.loan_feature = True

    def turn_off_loan(self) -> None:
        self.loan_feature = False
