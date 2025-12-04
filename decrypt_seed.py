#!/usr/bin/env python3
"""
Decrypt the encrypted seed using RSA/OAEP with SHA-256.
"""

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import base64


def load_private_key(private_key_path: str):
    """Load RSA private key from PEM file."""
    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )
    return private_key


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP with SHA-256.
    
    Args:
        encrypted_seed_b64: Base64-encoded ciphertext from API
        private_key: RSA private key object
    
    Returns:
        Decrypted hex seed (64-character hexadecimal string)
    
    Raises:
        ValueError: If decryption fails or seed format is invalid
    """
    try:
        # Step 1: Base64 decode the encrypted seed
        encrypted_seed_bytes = base64.b64decode(encrypted_seed_b64)
        
        # Step 2: RSA/OAEP decrypt with SHA-256
        decrypted_bytes = private_key.decrypt(
            encrypted_seed_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Step 3: Decode bytes to UTF-8 string
        seed_hex = decrypted_bytes.decode("utf-8")
        
        # Step 4: Validate format
        if len(seed_hex) != 64:
            raise ValueError(f"Invalid seed length: {len(seed_hex)}, expected 64")
        
        # Check all characters are valid hex
        valid_hex_chars = set("0123456789abcdef")
        if not all(c in valid_hex_chars for c in seed_hex.lower()):
            raise ValueError("Seed contains non-hexadecimal characters")
        
        # Step 5: Return validated seed
        return seed_hex
    
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")


def main():
    """Test decryption with encrypted_seed.txt"""
    print("Testing decryption...")
    
    try:
        # Load private key
        private_key = load_private_key("student_private.pem")
        print("✓ Private key loaded")
        
        # Read encrypted seed
        with open("encrypted_seed.txt", "r") as f:
            encrypted_seed = f.read().strip()
        print("✓ Encrypted seed read from file")
        
        # Decrypt
        seed = decrypt_seed(encrypted_seed, private_key)
        print(f"✓ Seed decrypted successfully!")
        print(f"  Seed: {seed}")
        print(f"  Length: {len(seed)} (expected 64)")
        
        # Save to file
        with open("seed.txt", "w") as f:
            f.write(seed)
        print("✓ Seed saved to seed.txt")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
