
FROM python:3.10

# Expose Flask port and Prometheus exporter port
EXPOSE 8080 8000

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install flask prometheus_client

# Copy application files
COPY . .

# Command to run Flask app
CMD ["python", "APP_Email_Server.py"]

