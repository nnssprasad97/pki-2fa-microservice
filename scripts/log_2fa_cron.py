#!/usr/bin/env python3
"""
Cron job script for logging 2FA activity
Runs every minute and logs current TOTP generation
"""

import os
from datetime import datetime

LOG_FILE = "/cron/2fa_cron.log"

def log_2fa_activity():
    """Log 2FA cron job execution."""
    timestamp = datetime.utcnow().isoformat()
    message = f"[{timestamp}] 2FA cron job executed\n"
    
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(message)
    except Exception as e:
        print(f"Error logging: {e}")

if __name__ == "__main__":
    log_2fa_activity()
