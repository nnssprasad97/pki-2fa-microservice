# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# 1. Install System Dependencies
# 'cron' is required for the background job
# 'tzdata' is required to set the timezone to UTC
RUN apt-get update && apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# 2. Configure Timezone to UTC (Critical for TOTP)
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/ /etc/localtime && echo  > /etc/timezone

WORKDIR /app

# 3. Copy Python Dependencies from Builder Stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 4. Copy Application Code
COPY . .

# 5. Create Volume Mount Points
# These folders will be mapped to external volumes in docker-compose
RUN mkdir -p /data /cron

# 6. Setup Cron Job
# Copy the config file (we will create this in Step 10)
COPY cron/2fa-cron /etc/cron.d/2fa-cron

# CRITICAL: Cron files must be owned by root and have permissions 0644
RUN chmod 0644 /etc/cron.d/2fa-cron
RUN crontab /etc/cron.d/2fa-cron

# Ensure the script is executable
RUN chmod +x scripts/log_2fa_cron.py

# 7. Expose the API Port
EXPOSE 8080

# 8. Start Command
# Starts the cron daemon in the background AND the API server
CMD ["sh", "-c", "cron && uvicorn app:app --host 0.0.0.0 --port 8080"]
