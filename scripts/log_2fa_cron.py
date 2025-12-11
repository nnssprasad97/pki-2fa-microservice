#!/usr/bin/env python3
import os
import sys
import base64
import pyotp
from datetime import datetime, timezone

# Path to the persistent seed
SEED_FILE = "/data/seed.txt"

def main():
    # 1. Get current UTC timestamp
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # 2. Check for seed
    if not os.path.exists(SEED_FILE):
        print(f"{now_utc} - Error: Seed file not found at {SEED_FILE}")
        return

    try:
        # 3. Read Seed
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        # 4. Generate TOTP (Hex -> Bytes -> Base32)
        seed_bytes = bytes.fromhex(hex_seed)
        base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
        
        totp = pyotp.TOTP(base32_seed, interval=30)
        code = totp.now()

        # 5. Output formatted log line
        # This goes to stdout, which cron redirects to /cron/last_code.txt
        print(f"{now_utc} - 2FA Code: {code}")

    except Exception as e:
        sys.stderr.write(f"{now_utc} - Error: {str(e)}\n")

if __name__ == "__main__":
    main()
