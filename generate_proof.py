#!/usr/bin/env python3
"""
Generate proof of work (commit hash + RSA signature)
"""

import subprocess
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend


def get_latest_commit_hash():
    """Get latest commit hash from git."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()


def sign_commit_hash(commit_hash: str, private_key_path: str) -> str:
    """Sign commit hash with RSA private key."""
    # Load private key
    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )
    
    # Sign the commit hash with RSA-PSS and SHA-256
    signature = private_key.sign(
        commit_hash.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    # Return base64-encoded signature
    return base64.b64encode(signature).decode()


def main():
    print("Generating proof of work...")
    
    # Get commit hash
    commit_hash = get_latest_commit_hash()
    print(f"? Commit hash: {commit_hash}")
    
    # Sign it
    signature = sign_commit_hash(commit_hash, "student_private.pem")
    print(f"? Signature generated (length: {len(signature)})")
    
    # Save proof
    import json
    proof = {
        "commit_hash": commit_hash,
        "signature": signature
    }
    
    with open("proof.json", "w") as f:
        json.dump(proof, f, indent=2)
    
    print("\n? Proof saved to proof.json")
    print(f"\nSubmission Information:")
    print(f"GitHub URL: https://github.com/nnssprasad97/pki-2fa-microservice")
    print(f"Commit Hash: {commit_hash}")
    print(f"Signature: {signature[:80]}...")


if __name__ == "__main__":
    main()
