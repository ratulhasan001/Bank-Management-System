"""Interactive command-line front end for the bank simulation."""

from __future__ import annotations

from account import ACCOUNT_TYPES, Account, BankError
from admin import Admin

LINE = "-" * 40


def ask(prompt: str) -> str:
    """Read one line of input with surrounding whitespace removed."""
    return input(prompt).strip()


def ask_int(prompt: str, minimum: int | None = None, maximum: int | None = None) -> int:
    """Keep asking until the user enters a whole number in [minimum, maximum]."""
    while True:
        text = ask(prompt)
        try:
            value = int(text)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if minimum is not None and value < minimum:
            print(f"Please enter a number of at least {minimum}.")
        elif maximum is not None and value > maximum:
            print(f"Please enter a number no greater than {maximum}.")
        else:
            return value


def choose(title: str, options: list[str]) -> int:
    """Print a numbered menu and return the chosen option number (1-based)."""
    print(f"\n{LINE}\n{title}\n{LINE}")
    for number, label in enumerate(options, start=1):
        print(f"  {number}. {label}")
    return ask_int("Choose an option: ", 1, len(options))


def create_account_from_input(bank: Admin) -> Account | None:
    name = ask("Name: ")
    email = ask("E-mail: ")
    account_type = ask(f"Account type ({'/'.join(ACCOUNT_TYPES)}): ")
    try:
        account = bank.create_an_account(name, email, account_type)
    except BankError as error:
        print(f"Could not create account: {error}")
        return None
    print(f"Account created. Account number: {account.account_number}")
    return account


def admin_menu(bank: Admin) -> None:
    options = [
        "Create an account",
        "Delete an account",
        "Show all accounts",
        "Show total available balance",
        "Show total loan amount",
        "Turn on loan facility",
        "Turn off loan facility",
        "Log out",
    ]
    while True:
        choice = choose(f"{bank.name} - Admin", options)
        try:
            if choice == 1:
                create_account_from_input(bank)
            elif choice == 2:
                number = ask_int("Account number to delete: ", 1)
                account = bank.delete_an_account(number)
                print(f"Deleted {account}. Paid out {account.balance} Tk.")
            elif choice == 3:
                if not bank.accounts:
                    print("No accounts yet.")
                for account in bank.accounts:
                    print(f"  {account.account_number:>4}  {account.name:<20} {account.type:<8} "
                          f"{account.balance:>10} Tk")
            elif choice == 4:
                print(f"Total available balance: {bank.total_balance} Tk")
            elif choice == 5:
                print(f"Total loan amount: {bank.total_loan_amount} Tk")
            elif choice == 6:
                bank.turn_on_loan()
                print("Loan facility is now ON.")
            elif choice == 7:
                bank.turn_off_loan()
                print("Loan facility is now OFF.")
            else:
                print("Logged out.")
                return
        except BankError as error:
            print(f"Error: {error}")


def customer_menu(bank: Admin, account: Account) -> None:
    options = [
        "Deposit",
        "Withdraw",
        "Check balance",
        "Transaction history",
        "Take a loan",
        "Transfer money",
        "Log out",
    ]
    while True:
        choice = choose(f"{bank.name} - {account}", options)
        try:
            if choice == 1:
                account.deposit(ask_int("Amount to deposit: ", 1))
                print(f"Deposited. New balance: {account.balance} Tk")
            elif choice == 2:
                account.withdraw(ask_int("Amount to withdraw: ", 1))
                print(f"Withdrawn. New balance: {account.balance} Tk")
            elif choice == 3:
                print(f"Name:       {account.name}")
                print(f"Account no: {account.account_number} ({account.type})")
                print(f"Balance:    {account.balance} Tk")
                print(f"Loans:      {account.loan_count} taken, {account.loan_amount} Tk in total")
            elif choice == 4:
                if not account.transactions:
                    print("No transactions yet.")
                for transaction in account.transactions:
                    print("  " + transaction.describe())
            elif choice == 5:
                account.take_loan(ask_int("Loan amount: ", 1))
                print(f"Loan approved. New balance: {account.balance} Tk")
            elif choice == 6:
                number = ask_int("Receiver's account number: ", 1)
                amount = ask_int("Amount to transfer: ", 1)
                receiver = account.transfer(number, amount)
                print(f"Transferred {amount} Tk to {receiver}. New balance: {account.balance} Tk")
            else:
                print("Logged out.")
                return
        except BankError as error:
            print(f"Error: {error}")


def run(bank: Admin) -> None:
    """Top-level loop: choose to log in, register, open the admin menu or quit."""
    while True:
        print(f"\n{LINE}\nWelcome to {bank.name}\n{LINE}")
        print("  L. Log in with your account number")
        print("  R. Register a new account")
        print("  A. Admin menu")
        print("  Q. Quit")
        option = ask("Choose an option: ").upper()
        if option == "L":
            account = bank.find_account(ask_int("Account number: ", 1))
            if account is None:
                print("No account found with that number.")
            else:
                customer_menu(bank, account)
        elif option == "R":
            account = create_account_from_input(bank)
            if account is not None:
                customer_menu(bank, account)
        elif option == "A":
            admin_menu(bank)
        elif option == "Q":
            print("Goodbye!")
            return
        else:
            print("Please enter L, R, A or Q.")


def main() -> None:
    try:
        run(Admin("World Bank"))
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
