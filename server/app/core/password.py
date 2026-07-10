import bcrypt

class PasswordService:
    """
    Reusable utility service wrapping the standard bcrypt hashing library.
    
    Bcrypt is selected for secure password hashing and verification to ensure 
    compatibility and resistance against hardware brute-forcing attacks.
    """

    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hashes a raw password string using bcrypt with a randomized salt.
        Never logs the raw password or its parameters.
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @classmethod
    def verify_password(cls, password: str, hashed_password: str) -> bool:
        """
        Verifies a raw password against its stored bcrypt hash.
        Never logs raw password credentials or comparison states.
        """
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )
        except Exception:
            # Catch comparison errors or malformed hash structures safely without logging details
            return False
