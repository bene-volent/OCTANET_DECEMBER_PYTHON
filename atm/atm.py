import sqlite3
import os
import hashlib
from .user import User 
import time
import datetime
from random import randint
from getpass import getpass

# Define constant paths
ROOT_PATH = os.getcwd()
DB_PATH = os.path.join(ROOT_PATH, 'atm_db', 'atm.db')

# Custom exception for database not found error
class DB_NOT_FOUND_ERROR(FileNotFoundError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# ATM class for managing ATM operations
class ATM:
    def __init__(self) -> None:
        # Check if the database exists
        if not os.path.exists(DB_PATH):
            raise DB_NOT_FOUND_ERROR("ATM Database not found.")

        # Connect to the database
        self.db_connection = sqlite3.connect(DB_PATH)
        self.db_cursor = self.db_connection.cursor()
        self._current_user = None

    # Prompt user for account information
    def prompt_user_info(self):
        user_id = input("Enter your account number #####: ")
        user_password = getpass("Enter your 4 digit PIN: ")
        return (user_id, user_password)

    # Get user from the database based on provided account information
    def get_user(self):
        user_id, user_password = self.prompt_user_info()
        fetched_user_info = self.db_cursor.execute(
            '''
            SELECT * FROM User WHERE user_id = ? and user_pin = ?;
            ''', (user_id, user_password)
        )
        fetched_info = fetched_user_info.fetchone()
        if fetched_info:
            return User(fetched_info[0], bool(fetched_info[2]), fetched_info[3])
        return None

    # Get anonymous user information based on user_id
    def get_anon_user(self, user_id):
        fetched_user_info = self.db_cursor.execute(
            '''
            SELECT user_id, balance FROM User WHERE user_id = ?;
            ''', (user_id,)
        )
        fetched_info = fetched_user_info.fetchone()
        if fetched_info:
            return User(fetched_info[0], False, fetched_info[1])
        return None

    # Debit specified amount from the user's balance
    def debit_amount(self, amount: float, user: User = None) -> None:
        """
        Debits the specified amount from the user's balance.

        Args:
            amount: The amount to be debited.
            user: User. If the user is not given, the system assumes the user to be the current user.

        Raises:
            ValueError: If the amount is negative or exceeds the available balance.
        """
        if user is None:
            user = self._current_user

        if amount > user.balance:
            raise ValueError("Insufficient balance.")

        user.balance -= amount
        self.db_cursor.execute("UPDATE User SET balance = ? where user_id = ?", (user.balance, user.id))

    # Credit specified amount to the user's balance
    def credit_amount(self, amount: float, user: User = None) -> None:
        """
        Credits the specified amount to the user's balance.

        Args:
            amount: The amount to be credited.
            user: User. If the user is not given, the system assumes the user to be the current user.
        """
        if user is None:
            user = self._current_user

        user.balance += amount
        self.db_cursor.execute("UPDATE User SET balance = ? where user_id = ?", (user.balance, user.id))

    # Withdraw money from the user's account
    def withdraw(self) -> bool:
        amount = float(input("Enter the amount: "))

        if amount < 0:
            raise ValueError("Amount cannot be negative.")

        try:
            self.debit_amount(amount)
            self.add_transaction(0, amount, self._current_user.id)
            self.db_connection.commit()
            return True
        except ValueError as error:
            print("Error: ", error)
            return False

    # Deposit money to the user's account
    def deposit(self) -> bool:
        amount = float(input("Enter the amount: "))

        if amount < 0:
            raise ValueError("Amount cannot be negative.")

        try:
            self.credit_amount(amount)
            self.add_transaction(1, amount, self._current_user)
            self.db_connection.commit()
            return True
        except ValueError as error:
            print("Error: ", error)
            return False

    # Transfer money between two user accounts
    def transfer(self) -> bool:
        userID_to_send = input("Enter the recipient's ID #####: ")

        if userID_to_send == self._current_user.id:
            raise Exception("Cannot transfer to self.")

        user_to_send = self.get_anon_user(userID_to_send)

        if user_to_send is None:
            raise LookupError("Entered user {} not present".format(userID_to_send))

        amount = float(input("Enter the amount to transfer: "))

        if amount < 0:
            raise ValueError("Amount cannot be negative!")

        try:
            self.debit_amount(amount)
            self.credit_amount(amount, user_to_send)
            self.add_transaction(0, amount, self._current_user, user_to_send)
            self.add_transaction(1, amount, self._current_user, user_to_send, user=user_to_send)
            self.db_connection.commit()
            return True
        except ValueError as error:
            print("Error: ", error)
            return False

    # Add a transaction record to the database
    def add_transaction(self, is_credit: bool, amount: float, fromID: User = None, toID: User = None, user: User = None):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if toID is None:
            self.db_cursor.execute(
                "INSERT INTO Transactions(is_credit,user_id,from_id,amount,timestamp) VALUES (?,?,?,?,?)",
                (is_credit, self._current_user.id if user is None else user.id, fromID.id, amount, timestamp))
        else:
            self.db_cursor.execute(
                "INSERT INTO Transactions(is_credit,user_id,from_id,to_id,amount,timestamp) VALUES (?,?,?,?,?,?)",
                (is_credit, self._current_user.id if user is None else user.id, fromID.id, toID.id, amount, timestamp))

    # Display transaction history for the current user
    def show_transactions(self):
        user_id = self._current_user.id
        transaction_cursor = self.db_cursor.execute("SELECT * FROM Transactions where user_id = ? ORDER BY timestamp DESC",
                                                   (user_id,))
        transactions = transaction_cursor.fetchall()
        for index, transaction in enumerate(transactions):
            print(
                f"Transaction No.: {index + 1}\tType: {'Credit' if transaction[0] else 'Debit'}\tFrom: {transaction[1]}\tTo: {transaction[2]}\tAmount: {transaction[3]:.2f}\tTimestamp: {transaction[4]}")

    # List all user accounts (admin only)
    def list_all_accounts(self):
        if not self._current_user.is_admin:
            return print("You do not have admin privileges!")

        users_cursor = self.db_cursor.execute("SELECT * FROM user where user_id != ?;", (self._current_user.id,))
        users = users_cursor.fetchall()
        for index, user in enumerate(users):
            print(f"UserID: {user[0]}\tBalance: {user[3]:.2f}")

    # Add a new user account (admin only)
    def add_new_account(self):
        if not self._current_user.is_admin:
            return print("You do not have admin privileges!")

        new_user_id = str(randint(0, 99999)).ljust(5, '0')

        print("Creating Credentials for a new user!")

        for i in range(3, 0, -1):
            time.sleep(1)
            print(f"\rPlease wait for {i} seconds", end='')

        print("\nYour new User ID: ", new_user_id)
        new_user_pin = getpass("Enter your new pin: ")

        self.db_cursor.execute("INSERT INTO User VALUES (?,?,?,?)", (new_user_id, new_user_pin, 0, 0.00))
        self.db_connection.commit()

        print("Kindly remember your credentials!")

    # Display current user balance
    def show_balance(self):
        print(f"\nCurrent Balance: Rs. {self._current_user.balance:.2f}")

    # Start the ATM application
    def start(self):
        session_ended = 0
        while not session_ended:
            os.system("cls")
            print("\nWelcome to ABC ATM: ")
            print("1. Login")
            print("2. Quit")

            login_choice = input("Enter your choice: ")

            if login_choice == '2' or login_choice.lower() == 'quit' or login_choice.lower() == 'q':
                session_ended = 1

            elif login_choice == "1":
                self._current_user = self.get_user()

                if self._current_user is None:
                    print("Invalid User. Try Again")
                    continue

                while True:
                    os.system("cls")
                    print("\nATM Menu:")
                    print("1. Transactions History")
                    print("2. Show Balance")
                    print("3. Withdraw")
                    print("4. Deposit")
                    print("5. Transfer")
                    if self._current_user.is_admin:
                        print("6. Add New Account")
                        print("7. List All Accounts")
                    print("Q. Quit")

                    choice = input("Enter your choice: ")

                    if choice == '1':
                        self.show_transactions()
                        input("\n\nPress any key...")

                    elif choice == '2':
                        self.show_balance()
                        input("\n\nPress any key...")

                    elif choice == '3':
                        self.withdraw()
                        input("\n\nPress any key...")

                    elif choice == '4':
                        self.deposit()
                        input("\n\nPress any key...")

                    elif choice == '5':
                        self.transfer()
                        input("\n\nPress any key...")

                    elif choice.lower() == 'q':
                        break

                    elif choice == '6':
                        self.add_new_account()
                        input("\n\nPress any key...")

                    elif choice == '7':
                        self.list_all_accounts()
                        input("\n\nPress any key...")
            else:
                print("Invalid Choice. Choose Again!")
                time.sleep(2)
