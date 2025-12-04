#!/usr/bin/env python3
"""
Cron job script for logging 2FA codes every minute
"""

import os
import sys
from datetime import datetime
import base64

# Add parent directory to path to import app modules
sys.path.insert(0, '/app')

LOG_FILE = "/cron/last_code.txt"

def log_2fa_activity():
    """Read seed, generate TOTP code, and log it."""
    try:
        # 1. Read hex seed from persistent storage
        seed_file = "/data/seed.txt"
        if not os.path.exists(seed_file):
            print(f"[ERROR] Seed file not found: {seed_file}")
            return
        
        with open(seed_file, "r") as f:
            hex_seed = f.read().strip()
        
        # 2. Generate current TOTP code
        import pyotp
        seed_bytes = bytes.fromhex(hex_seed)
        seed_b32 = base64.b32encode(seed_bytes).decode().rstrip("=")
        totp = pyotp.TOTP(seed_b32)
        code = totp.now()
        
        # 3. Get current UTC timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        # 4. Output formatted line
        message = f"{timestamp} - 2FA Code: {code}\n"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        
        # Write to log file
        with open(LOG_FILE, "a") as f:
            f.write(message)
        
        print(f"? Logged at {timestamp}: {code}")
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    log_2fa_activity()
