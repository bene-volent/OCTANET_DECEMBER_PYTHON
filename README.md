# ATM System

This is a simple command-line ATM (Automated Teller Machine) system implemented in Python. The system uses SQLite as a database to manage user accounts and transactions.

## Features

- **User Authentication:** Users can log in with their account number and PIN.
- **Balance Inquiry:** Users can check their account balance.
- **Withdrawal:** Users can withdraw money from their account.
- **Deposit:** Users can deposit money into their account.
- **Transfer:** Users can transfer money to another account.
- **Transaction History:** Users can view their transaction history.
- **Admin Features:** Admin users can add new accounts, list all accounts, and perform administrative tasks.

## Requirements

- Python 3.x
- SQLite3

## Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/bene-volent/OCTANET_DECEMBER_PYTHON.git
   cd OCTANET_DECEMBER_PYTHON
    ```
## How to run
```bash
    python main.py
```
## Sample Accounts
| Account Type | User ID | User PIN |
|--------------|---------|----------|
| ADMIN | 12345 | 0000 |
| BASIC | 43814 | 1234 |

## Usage
Follow the on-screen prompts to interact with the ATM system. Users can perform various operations such as checking balance, withdrawing money, depositing money, transferring funds, and viewing transaction history.

___Note: Admin features are available only for users with admin privileges___