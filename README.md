# Bank Management System

One of my first Python projects, written in January 2024 while I was learning object-oriented programming. It is a small command-line bank simulation: an admin manages the bank, and customers register, log in by account number and move money around. All data lives in memory for the duration of a run.

## What I practised

- Modelling a problem with classes: `Admin` represents the bank (its accounts, cash, loans and the loan on/off switch) and `Account` represents one customer account (balance, loans, transaction history).
- Keeping rules inside the classes: every operation either succeeds completely or raises a `BankError` and changes nothing.
- Keeping the menu code (`main.py`) separate from the logic so the logic can be tested.

## Features

Admin menu
- Create and delete accounts (deleting pays out the remaining balance)
- List all accounts with type and balance
- Show the bank's total available balance and total loan amount
- Turn the loan facility on or off

Customer menu
- Register (name, e-mail, account type Savings or Current) or log in with an account number
- Deposit and withdraw whole taka amounts; a withdrawal is limited by both the account balance and the bank's available cash
- Check balance and loan summary
- Transfer money to another existing account (not to yourself); both sides get a history entry
- Take a loan while the facility is on: at most 3 loans per account and never more than the bank's available cash; the loan is credited to the balance
- View the transaction history, each entry with a unique ID

Invalid input (letters where a number is expected, negative or zero amounts, unknown menu options or account numbers) shows a message and asks again instead of crashing.

## Project structure

```
Bank-Management-System/
├── account.py        # Account, Transaction and BankError
├── admin.py          # Admin: the bank, account management and bank-wide totals
├── main.py           # Interactive menus (entry point)
└── tests/
    └── test_bank.py  # unittest tests for the banking rules
```

## How to run

Requires Python 3.10 or newer; standard library only.

```bash
git clone https://github.com/ratulhasan001/Bank-Management-System.git
cd Bank-Management-System
python3 main.py
```

The start screen offers `L` (log in), `R` (register), `A` (admin menu) and `Q` (quit). Account numbers are assigned in order starting from 1. Inside a menu, choose an option by its number.

## How to test

```bash
python3 -m unittest discover -s tests -v
```

## Sample session

```
Welcome to World Bank
  L. Log in with your account number
  R. Register a new account
  A. Admin menu
  Q. Quit
Choose an option: R
Name: Alice
E-mail: alice@example.com
Account type (Savings/Current): savings
Account created. Account number: 1

World Bank - Alice (account 1)
  1. Deposit
  2. Withdraw
  ...
  7. Log out
Choose an option: 1
Amount to deposit: 500
Deposited. New balance: 500 Tk
Choose an option: 2
Amount to withdraw: abc
Please enter a whole number.
Amount to withdraw: 900
Error: Insufficient balance. Your balance is 500 Tk.
Choose an option: 6
Receiver's account number: 9
Amount to transfer: 100
Error: Account 9 does not exist.
Choose an option: 7
Logged out.
Choose an option: Q
Goodbye!
```

(Menus are reprinted after each action; they are shortened here.)

## Later improvements

I revisited this project in 2026 to fix bugs and add tests while keeping the original class design:

- Taking a loan now actually credits the account (before, it was only recorded).
- Negative transfer amounts could pull money from another account; amounts must now be positive everywhere.
- Transfers to a missing account or to yourself are rejected, and the receiver now gets a history entry.
- A withdrawal no longer shares its transaction ID with the next transaction.
- Non-numeric input no longer crashes the program; Ctrl-D or Ctrl-C exits cleanly, and there is a Quit option.
- Admin access no longer depends on an account being named "admin"; it has its own menu entry.
- Account numbers are now per bank instead of a global counter, which makes the classes testable.
- Fixed typos in the menus ("Tolal", "Tarnsfer", "transictions"), added type hints, docstrings and unit tests.

## Limitations

- Data is not saved; everything is lost when the program exits.
- There are no passwords: logging in only needs an account number, and the admin menu is open to anyone at the start screen.

---

Ratul Hasan · [ratulhasan.dev](https://ratulhasan.dev)
