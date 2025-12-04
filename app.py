#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, base64, time
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import pyotp

app = FastAPI(title="PKI 2FA Microservice", version="1.0.0")
DATA_DIR = Path("/data")
SEED_FILE = DATA_DIR / "seed.txt"
PRIVATE_KEY_FILE = Path("student_private.pem")
DATA_DIR.mkdir(exist_ok=True)

def generate_totp_code(hex_seed: str) -> str:
    seed_bytes = bytes.fromhex(hex_seed)
    seed_b32 = base64.b32encode(seed_bytes).decode().rstrip("=")
    return pyotp.TOTP(seed_b32).now()

def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    seed_bytes = bytes.fromhex(hex_seed)
    seed_b32 = base64.b32encode(seed_bytes).decode().rstrip("=")
    return pyotp.TOTP(seed_b32).verify(code, valid_window=valid_window)

def get_remaining_seconds() -> int:
    return 30 - (int(time.time()) % 30)

class DecryptSeedRequest(BaseModel):
    encrypted_seed: str

class VerifyCodeRequest(BaseModel):
    code: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "service": "PKI 2FA Microservice"}

@app.post("/decrypt-seed")
async def decrypt_seed(request: DecryptSeedRequest):
    try:
        with open(PRIVATE_KEY_FILE, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
        encrypted_bytes = base64.b64decode(request.encrypted_seed)
        decrypted_bytes = private_key.decrypt(encrypted_bytes, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
        hex_seed = decrypted_bytes.decode('utf-8').strip()
        if len(hex_seed) != 64: raise ValueError(f"Invalid seed length: {len(hex_seed)}")
        bytes.fromhex(hex_seed)
        with open(SEED_FILE, "w") as f: f.write(hex_seed)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")

@app.get("/generate-2fa")
async def generate_2fa():
    try:
        if not SEED_FILE.exists(): raise HTTPException(status_code=500, detail="Seed not decrypted yet")
        with open(SEED_FILE, "r") as f: hex_seed = f.read().strip()
        code = generate_totp_code(hex_seed)
        valid_for = get_remaining_seconds()
        return {"code": code, "valid_for": valid_for}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/verify-2fa")
async def verify_2fa(request: VerifyCodeRequest):
    try:
        if not request.code: raise HTTPException(status_code=400, detail="Missing code")
        if not SEED_FILE.exists(): raise HTTPException(status_code=500, detail="Seed not decrypted yet")
        with open(SEED_FILE, "r") as f: hex_seed = f.read().strip()
        is_valid = verify_totp_code(hex_seed, request.code, valid_window=1)
        return {"valid": is_valid}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
