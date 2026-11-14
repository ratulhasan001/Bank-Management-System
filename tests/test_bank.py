"""Unit tests for the Account and Admin classes."""

import unittest

from account import MAX_LOANS, BankError
from admin import Admin


class BankTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.bank = Admin("Test Bank")
        self.alice = self.bank.create_an_account("Alice", "alice@example.com", "Savings")
        self.bob = self.bank.create_an_account("Bob", "bob@example.com", "current")


class TestAccountCreation(BankTestCase):
    def test_account_numbers_are_sequential_per_bank(self):
        self.assertEqual((self.alice.account_number, self.bob.account_number), (1, 2))
        other_bank = Admin("Other")
        first = other_bank.create_an_account("Carol", "carol@example.com", "Savings")
        self.assertEqual(first.account_number, 1)

    def test_account_type_is_normalised(self):
        self.assertEqual(self.bob.type, "Current")

    def test_invalid_details_are_rejected(self):
        with self.assertRaises(BankError):
            self.bank.create_an_account("  ", "x@example.com", "Savings")
        with self.assertRaises(BankError):
            self.bank.create_an_account("Dan", "not-an-email", "Savings")
        with self.assertRaises(BankError):
            self.bank.create_an_account("Dan", "dan@example.com", "Gold")
        self.assertEqual(len(self.bank.accounts), 2)

    def test_delete_account_pays_out_balance(self):
        self.alice.deposit(300)
        self.bank.delete_an_account(1)
        self.assertIsNone(self.bank.find_account(1))
        self.assertEqual(self.bank.total_balance, 0)

    def test_delete_missing_account(self):
        with self.assertRaises(BankError):
            self.bank.delete_an_account(99)


class TestDepositWithdraw(BankTestCase):
    def test_deposit_updates_account_and_bank(self):
        self.alice.deposit(500)
        self.assertEqual(self.alice.balance, 500)
        self.assertEqual(self.bank.total_balance, 500)

    def test_non_positive_or_non_integer_amounts_are_rejected(self):
        for amount in (0, -100, 10.5, "100", True):
            with self.subTest(amount=amount):
                with self.assertRaises(BankError):
                    self.alice.deposit(amount)
        self.assertEqual(self.alice.balance, 0)
        self.assertEqual(self.alice.transactions, [])

    def test_withdraw(self):
        self.alice.deposit(500)
        self.alice.withdraw(200)
        self.assertEqual(self.alice.balance, 300)
        self.assertEqual(self.bank.total_balance, 300)

    def test_withdraw_more_than_balance_is_rejected(self):
        self.alice.deposit(100)
        self.bob.deposit(1000)
        with self.assertRaises(BankError):
            self.alice.withdraw(101)
        self.assertEqual(self.alice.balance, 100)

    def test_withdraw_negative_amount_is_rejected(self):
        self.alice.deposit(100)
        with self.assertRaises(BankError):
            self.alice.withdraw(-50)
        self.assertEqual(self.alice.balance, 100)

    def test_withdraw_limited_by_bank_cash(self):
        self.alice.deposit(100)
        self.alice.take_loan(100)  # balance 200, bank cash still 100
        with self.assertRaises(BankError):
            self.alice.withdraw(150)
        self.alice.withdraw(100)
        self.assertEqual(self.bank.total_balance, 0)

    def test_transaction_ids_are_unique(self):
        self.alice.deposit(100)
        self.alice.withdraw(50)
        self.alice.deposit(10)
        ids = [t.id for t in self.alice.transactions]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual([t.kind for t in self.alice.transactions], ["deposit", "withdraw", "deposit"])


class TestTransfer(BankTestCase):
    def test_transfer_moves_money_and_records_both_sides(self):
        self.alice.deposit(500)
        receiver = self.alice.transfer(2, 200)
        self.assertIs(receiver, self.bob)
        self.assertEqual((self.alice.balance, self.bob.balance), (300, 200))
        self.assertEqual(self.bank.total_balance, 500)
        self.assertEqual(self.alice.transactions[-1].kind, "transfer out")
        self.assertEqual(self.bob.transactions[-1].kind, "transfer in")

    def test_transfer_to_missing_account_is_rejected(self):
        self.alice.deposit(500)
        with self.assertRaises(BankError):
            self.alice.transfer(42, 100)
        self.assertEqual(self.alice.balance, 500)

    def test_transfer_to_self_is_rejected(self):
        self.alice.deposit(500)
        with self.assertRaises(BankError):
            self.alice.transfer(1, 100)

    def test_transfer_more_than_balance_is_rejected(self):
        self.alice.deposit(100)
        with self.assertRaises(BankError):
            self.alice.transfer(2, 101)
        self.assertEqual((self.alice.balance, self.bob.balance), (100, 0))

    def test_negative_transfer_cannot_pull_money(self):
        self.bob.deposit(500)
        with self.assertRaises(BankError):
            self.alice.transfer(2, -200)
        self.assertEqual((self.alice.balance, self.bob.balance), (0, 500))


class TestLoan(BankTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.bob.deposit(10_000)

    def test_loan_is_credited_and_counted(self):
        self.alice.take_loan(1000)
        self.assertEqual(self.alice.balance, 1000)
        self.assertEqual(self.alice.loan_count, 1)
        self.assertEqual(self.alice.loan_amount, 1000)
        self.assertEqual(self.bank.total_loan_amount, 1000)

    def test_loan_limit(self):
        for _ in range(MAX_LOANS):
            self.alice.take_loan(100)
        with self.assertRaises(BankError):
            self.alice.take_loan(100)
        self.assertEqual(self.alice.loan_count, MAX_LOANS)

    def test_loan_rejected_when_feature_off(self):
        self.bank.turn_off_loan()
        with self.assertRaises(BankError):
            self.alice.take_loan(100)
        self.bank.turn_on_loan()
        self.alice.take_loan(100)
        self.assertEqual(self.alice.loan_count, 1)

    def test_loan_cannot_exceed_bank_cash(self):
        with self.assertRaises(BankError):
            self.alice.take_loan(10_001)

    def test_invalid_loan_amount(self):
        with self.assertRaises(BankError):
            self.alice.take_loan(-5)
        self.assertEqual(self.alice.loan_count, 0)


if __name__ == "__main__":
    unittest.main()
