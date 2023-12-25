# Import the ATM class from ATM Module 
from atm.atm import ATM

# Define the main entry point of the program
def main():
    # Create an instance of the ATM class to represent the ATM object
    atm = ATM()

    # Initiate the ATM's functionality
    atm.start()
    
    
# Ensure the main function is only executed when the script runs directly
if __name__ == "__main__":
    main()