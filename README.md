# Bank Management System

A command-line bank simulation written in Python to practise object-oriented design. An `Admin` class models the bank (accounts, total balance, total loans, loan on/off switch) and an `Account` class models a customer account (balance, transactions, loans). A menu-driven loop in `main.py` lets an admin manage accounts and lets customers register, log in by account number and perform transactions. All data is kept in memory for the duration of a run.

## Features

**Admin menu**
- Create and delete accounts
- List all account holders with their account numbers
- View the bank's total available balance and total loan amount
- Turn the loan facility on or off

**Customer menu**
- Register (name, e-mail, account type) or log in with an account number
- Deposit and withdraw (withdrawals are limited by both the account balance and the bank's total balance)
- Check balance
- Transfer money to another account by account number
- Take a loan (only while the bank's loan facility is on; at most 3 loans per account)
- View transaction history (deposits, withdrawals, loans and transfers, each with a transaction ID)

## Tech stack

- Python 3 (standard library only)

## Project structure

```
Bank-Management-System/
├── account.py   # Account class: deposit, withdraw, transfer, loan, history
├── admin.py     # Admin class: the bank; account management and bank-wide totals
└── main.py      # Interactive menu loop (entry point)
```

## Getting started

```bash
git clone https://github.com/ratulhasan001/Bank-Management-System.git
cd Bank-Management-System
python3 main.py
```

On start-up the bank creates an `admin` account (account number 1) and the session begins in the admin menu. Choose `8` to log out, then:

- `R` to register a new customer account (account numbers are assigned sequentially: 2, 3, ...), or
- `L` to log in with an existing account number (log in with `1` to return to the admin menu).

Menu options are chosen by entering their number.

## Limitations

- Data is not persisted; everything is lost when the program exits.
- There is no password or other authentication; logging in only requires an account number.
- Admin access is decided by the account name `admin`.
- Numeric prompts use `int(input())`, so non-numeric input raises an error and ends the program.

---

Ratul Hasan · [ratulhasan.dev](https://ratulhasan.dev)
