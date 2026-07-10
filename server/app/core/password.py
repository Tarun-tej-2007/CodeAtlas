from pwdlib import PasswordHash
from pwdlib.exceptions import PwdlibError

class PasswordService:
    """
    Reusable utility service wrapping the modern pwdlib hash manager.
    
    Argon2id is selected as the default algorithm because it is the current OWASP 
    recommendation, offering excellent memory-hard resistance against GPU/ASIC-based 
    brute-forcing attacks and side-channel timing leaks.
    """
    _hasher = PasswordHash.recommended()

    @classmethod
    def hash_password(cls, password: str) -> str:
        """
        Hashes a raw password using the recommended Argon2id crypt parameters.
        """
        return cls._hasher.hash(password)

    @classmethod
    def verify_password(cls, password: str, hashed_password: str) -> bool:
        """
        Validates a raw password input against a stored hash record.
        """
        try:
            return cls._hasher.verify(password, hashed_password)
        except PwdlibError:
            # Handles hash mismatch, malformed hash inputs, or verification failures
            return False
