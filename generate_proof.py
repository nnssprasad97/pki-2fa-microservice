#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate commit proof:
1) Get latest commit hash
2) Sign it with student private key using RSA-PSS-SHA256
3) Encrypt signature with instructor public key using RSA/OAEP-SHA256
4) Base64-encode encrypted signature
"""

import subprocess
import base64
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend


def get_latest_commit_hash() -> str:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def load_private_key(path: str):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend(),
        )


def load_public_key(path: str):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(
            f.read(),
            backend=default_backend(),
        )


def sign_message(message: str, private_key) -> bytes:
    """
    Sign ASCII commit hash with RSA-PSS-SHA256.
    """
    return private_key.sign(
        message.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )


def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypt data using RSA/OAEP with SHA-256.
    """
    return public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def main():
    print("Generating encrypted commit proof...")

    commit_hash = get_latest_commit_hash()
    print(f"Commit hash: {commit_hash}")

    student_priv = load_private_key("student_private.pem")
    instructor_pub = load_public_key("instructor_public.pem")

    signature = sign_message(commit_hash, student_priv)
    encrypted_sig = encrypt_with_public_key(signature, instructor_pub)
    encrypted_sig_b64 = base64.b64encode(encrypted_sig).decode("utf-8")

    proof = {
        "commit_hash": commit_hash,
        "encrypted_signature": encrypted_sig_b64,
    }

    with open("proof.json", "w") as f:
        json.dump(proof, f, indent=2)

    print("\n✓ Proof saved to proof.json")
    print("\nSubmission values:")
    print(f"Commit Hash: {commit_hash}")
    print(f"Encrypted Signature (single line):\n{encrypted_sig_b64}")


if __name__ == "__main__":
    main()
