class User:
    """Represents a user of an ATM."""

    def __init__(self, user_id: int, is_admin: bool, balance: float) -> None:
        """Initializes a new User instance.

        Args:
            user_id: The unique identifier of the user.
            is_admin: Indicates whether the user has administrative privileges.
            balance: The current account balance of the user.

        Raises:
            ValueError: If the balance is negative.
        """

        self.id = user_id
        self.is_admin = is_admin

        if balance < 0:
            raise ValueError("Balance cannot be negative.")
        self.balance = balance

    
    
    
        
