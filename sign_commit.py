from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import subprocess

# get latest commit hash
commit_hash = subprocess.check_output(
    ["git", "log", "-1", "--format=%H"], text=True
).strip()
commit_bytes = commit_hash.encode()

with open("student_private.pem", "rb") as f:
    student_priv = serialization.load_pem_private_key(f.read(), password=None)

with open("instructor_public.pem", "rb") as f:
    instructor_pub = serialization.load_pem_public_key(f.read())

# sign hash with student private key
signature = student_priv.sign(
    commit_bytes,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH,
    ),
    hashes.SHA256(),
)

# encrypt signature with instructor public key
encrypted = instructor_pub.encrypt(
    signature,
    padding.OAEP(
        mgf=padding.MGF1(hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)

print(base64.b64encode(encrypted).decode("utf-8"))
